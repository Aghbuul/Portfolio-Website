from flask import jsonify, request
import openai
from openai import OpenAI
from bs4 import BeautifulSoup
import os
from os import environ
import requests
import logging
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import deque
import time
import re

# Set up logging with more detailed format
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = None

# Files and patterns to exclude from content extraction
EXCLUDED_FILES = {
    '.env', '.env.example', '.gitignore', 'requirements.txt', 'LICENSE',
    '.git', '__pycache__', '*.pyc', '.replit', 'replit.nix', 'uv.lock', '*.log'
}


def init_chat_routes(app):
    global limiter

    # Initialize rate limiter with memory storage
    limiter = Limiter(app=app,
                      key_func=get_remote_address,
                      default_limits=["5 per minute", "100 per day"],
                      storage_uri="memory://")

    # Store website content and embeddings in memory
    website_content = {}
    content_embeddings = {}
    recent_queries = deque(
        maxlen=1000)  # Store recent queries for abuse detection

    def moderate_content(text):
        """Use OpenAI's moderation endpoint to check for inappropriate content"""
        try:
            # Try to get API key from Replit secrets first, then fall back to environment variable
            api_key = environ.get('OPENAI_API_KEY')
            client = OpenAI(api_key=api_key)
            response = client.moderations.create(input=text)
            return not response.results[0].flagged
        except Exception as e:
            logger.error(f"Moderation error: {e}")
            return False

    def get_embedding(text, client):
        """Get embedding for a piece of text"""
        try:
            response = client.embeddings.create(model="text-embedding-ada-002",
                                                input=text)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None

    def chunk_text(text, chunk_size=500):
        """Split text into chunks of roughly equal size"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def extract_text_from_url(url):
        """Extract text content from a URL"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script, style elements, and navigation
            for element in soup(["script", "style", "nav", "header",
                                 "footer"]):
                element.decompose()

            # Extract main content sections
            main_content = []

            # Get content from specific sections
            for section in soup.find_all(['main', 'article', 'section',
                                          'div']):
                if section.get('id') in ['content', 'main-content', 'about', 'bio', 'profile'] or \
                   section.get('class') and any(cls in ['content', 'main', 'about', 'bio', 'profile'] for cls in section.get('class')):
                    main_content.append(
                        section.get_text(strip=True, separator=' '))

            # If no specific sections found, get all visible text
            if not main_content:
                main_content = [soup.get_text(strip=True, separator=' ')]

            return ' '.join(main_content)
        except Exception as e:
            logger.error(f"Error extracting text from URL: {e}")
            return ""

    def get_website_content(client):
        """Get and process website content with embeddings"""
        try:
            if not website_content:
                # Add main page content
                main_text = extract_text_from_url(request.url_root)
                chunks = chunk_text(main_text)

                website_content['main'] = chunks
                content_embeddings['main'] = []

                # Also extract content from about/profile pages if they exist
                about_url = request.url_root.rstrip('/') + '/about'
                profile_url = request.url_root.rstrip('/') + '/profile'

                for url, key in [(about_url, 'about'),
                                 (profile_url, 'profile')]:
                    try:
                        page_text = extract_text_from_url(url)
                        if page_text:
                            page_chunks = chunk_text(page_text)
                            website_content[key] = page_chunks
                            content_embeddings[key] = []
                            for chunk in page_chunks:
                                embedding = get_embedding(chunk, client)
                                if embedding:
                                    content_embeddings[key].append(embedding)
                    except Exception as e:
                        logger.warning(
                            f"Could not extract content from {url}: {e}")

                # Process main page chunks
                for chunk in chunks:
                    embedding = get_embedding(chunk, client)
                    if embedding:
                        content_embeddings['main'].append(embedding)

            return website_content, content_embeddings
        except Exception as e:
            logger.error(f"Error getting website content: {e}")
            return {"main": ""}, {}

    def find_relevant_context(query_embedding, content_embeddings, top_k=3):
        """Find most relevant content chunks using cosine similarity"""
        max_similarity = -1
        relevant_chunks = []

        for source, embeddings in content_embeddings.items():
            for i, emb in enumerate(embeddings):
                similarity = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(emb).reshape(1, -1))[0][0]

                if similarity > max_similarity:
                    max_similarity = similarity
                    relevant_chunks = [(website_content[source][i], similarity)
                                       ]
                elif len(relevant_chunks) < top_k:
                    relevant_chunks.append(
                        (website_content[source][i], similarity))
                    relevant_chunks.sort(key=lambda x: x[1], reverse=True)

        # Only return chunks with similarity above threshold
        threshold = 0.3  # Adjust this value as needed
        filtered_chunks = [
            chunk for chunk, sim in relevant_chunks if sim > threshold
        ]

        return filtered_chunks if filtered_chunks else [
            "I apologize, but I couldn't find relevant information about that in the website content."
        ]

    def check_query_abuse(query):
        """Check for potential abuse patterns in queries"""
        # Check if query is too similar to recent queries (potential DoS)
        similar_queries = sum(1 for recent_query in recent_queries
                              if similar_text(query, recent_query) > 0.9)
        if similar_queries > 5:
            return False

        # Add query to recent queries
        recent_queries.append(query)
        return True

    def similar_text(a, b):
        """Simple similarity check between two texts"""
        return len(set(a.lower().split()) & set(b.lower().split())) / \
               max(len(set(a.lower().split())), len(set(b.lower().split())))

    @app.route('/chat', methods=['POST'])
    @limiter.limit("5 per minute")  # Rate limiting
    def chat():
        try:
            logger.info("=== Starting new chat request ===")

            # Get API key from Replit secrets
            api_key = environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.error("OpenAI API key is not set in Replit secrets")
                return jsonify({
                    "error":
                    "OpenAI API key is not configured. Please add it to Replit secrets."
                }), 500

            # Get user message
            data = request.get_json()
            if not data or 'message' not in data:
                logger.error("No message provided in request")
                return jsonify({"error": "No message provided"}), 400

            user_message = data['message']

            # Check for abuse/spam
            if not check_query_abuse(user_message):
                return jsonify({"error": "Too many similar requests"}), 429

            # Moderate content
            if not moderate_content(user_message):
                return jsonify({"error":
                                "Message flagged as inappropriate"}), 400

            logger.info(f"Received message: {user_message}")

            # Configure OpenAI client
            try:
                client = OpenAI(api_key=api_key)
                logger.info("OpenAI client configured successfully")
            except Exception as e:
                logger.error(f"Error configuring OpenAI client: {e}")
                return jsonify({"error":
                                "Failed to configure API client"}), 500

            # Get website content and embeddings
            content, embeddings = get_website_content(client)

            # Get query embedding
            query_embedding = get_embedding(user_message, client)
            if not query_embedding:
                return jsonify({"error": "Failed to process query"}), 500

            # Find relevant context
            relevant_chunks = find_relevant_context(query_embedding,
                                                    embeddings)
            context = "\n".join(relevant_chunks)

            # Create messages array with enhanced context
            messages = [{
                "role":
                "system",
                "content":
                """You are a helpful AI assistant for Iqbal's personal portfolio website to assist visitors politely. Your role is to:
                    1. Answer questions STRICTLY based on the provided context about Iqbal
                    2. If the answer cannot be found in the context, politely say so and suggest what information you can provide
                    3. Do not make up information or use external knowledge
                    4. Be friendly, polite and helpful about Iqbal's work and achievements.
                    5. When discussing projects or experience, provide specific details from the context and guide the user to the relevant sections of the website.
                    6. If asked about contact information or personal details not in the context, politely decline
                    7. Prioritise effective and concise responses where possible.
                    8. If the user is being rude or inappropriate, politely decline to answer.
                    9. If the user is asking about Iqbal's availability for a project or collaboration, politely decline and suggest that the user contact Iqbal directly through LinkedIn.
                    10. If the user asks about the meaning behind the website's name "Akuane", ask them if anything in the background image stands out to them. 
                    11. Always answer in third person. Remember, you are not Iqbal, but his assistant.

                    Context from website:
                    """ + context
            }, {
                "role": "user",
                "content": user_message
            }]

            try:
                # Create chat completion
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7)

                bot_response = completion.choices[0].message.content
                logger.info("Successfully received response from OpenAI")

                return jsonify({"response": bot_response})

            except Exception as api_error:
                logger.error(f"OpenAI API call error: {str(api_error)}")
                return jsonify({"error": str(api_error)}), 500

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({"error": str(e)}), 500
