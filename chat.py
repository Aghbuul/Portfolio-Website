from flask import jsonify, request
import openai
from openai import OpenAI
import os
from os import environ
import logging
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import deque
import time
import re

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = None

def init_chat_routes(app):
    global limiter

    # Initialize rate limiter with memory storage
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["5 per minute", "100 per day"],
        storage_uri="memory://"
    )

    # Store context content and embeddings in memory
    context_content = {}
    content_embeddings = {}
    recent_queries = deque(maxlen=1000)  # Store recent queries for abuse detection

    def get_api_key():
        """Get API key from environment, with fallback options"""
        api_key = environ.get('OPENAI_API_KEY')
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        return api_key

    def moderate_content(text):
        """Use OpenAI's moderation endpoint to check for inappropriate content"""
        try:
            api_key = get_api_key()
            if not api_key:
                logger.error("API key not found in any location")
                return False

            client = OpenAI(api_key=api_key)
            response = client.moderations.create(input=text)
            return not response.results[0].flagged
        except Exception as e:
            logger.error(f"Moderation error: {e}")
            return False

    def get_embedding(text, client):
        """Get embedding for a piece of text"""
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
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

    def load_context_files():
        """Load and process context files from the context_data directory"""
        try:
            if not context_content:
                context_dir = os.path.join(os.path.dirname(__file__), 'context_data')

                # Create context directory if it doesn't exist
                if not os.path.exists(context_dir):
                    os.makedirs(context_dir)

                # Get API key for embeddings
                api_key = get_api_key()
                if not api_key:
                    logger.error("API key not found")
                    return

                client = OpenAI(api_key=api_key)

                # Process each .txt or .md file in the context directory
                for filename in os.listdir(context_dir):
                    if filename.endswith(('.txt', '.md')):
                        file_path = os.path.join(context_dir, filename)
                        context_key = os.path.splitext(filename)[0]

                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()

                            # Chunk the content
                            chunks = chunk_text(content)
                            context_content[context_key] = chunks
                            content_embeddings[context_key] = []

                            # Generate embeddings for each chunk
                            for chunk in chunks:
                                embedding = get_embedding(chunk, client)
                                if embedding:
                                    content_embeddings[context_key].append(embedding)

                        except Exception as e:
                            logger.error(f"Error processing context file {filename}: {e}")

                if not context_content:
                    logger.warning("No context files found in context_data directory")
                    # Create an example context file
                    example_path = os.path.join(context_dir, 'example.txt')
                    if not os.path.exists(example_path):
                        with open(example_path, 'w', encoding='utf-8') as f:
                            f.write("This is an example context file. Replace this with your actual knowledge base content.")

            return context_content, content_embeddings
        except Exception as e:
            logger.error(f"Error loading context files: {e}")
            return {}, {}

    def find_relevant_context(query_embedding, content_embeddings, top_k=3):
        """Find most relevant content chunks using cosine similarity"""
        max_similarity = -1
        relevant_chunks = []

        for source, embeddings in content_embeddings.items():
            for i, emb in enumerate(embeddings):
                similarity = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(emb).reshape(1, -1)
                )[0][0]

                if similarity > max_similarity:
                    max_similarity = similarity
                    relevant_chunks = [(context_content[source][i], similarity)]
                elif len(relevant_chunks) < top_k:
                    relevant_chunks.append((context_content[source][i], similarity))
                    relevant_chunks.sort(key=lambda x: x[1], reverse=True)

        # Only return chunks with similarity above threshold
        threshold = 0.3
        filtered_chunks = [chunk for chunk, sim in relevant_chunks if sim > threshold]

        return filtered_chunks if filtered_chunks else ["I can only provide information based on my knowledge base. Could you please rephrase your question?"]

    def check_query_abuse(query):
        """Check for potential abuse patterns in queries"""
        similar_queries = sum(1 for recent_query in recent_queries 
                            if similar_text(query, recent_query) > 0.9)
        if similar_queries > 5:
            return False

        recent_queries.append(query)
        return True

    def similar_text(a, b):
        """Simple similarity check between two texts"""
        return len(set(a.lower().split()) & set(b.lower().split())) / \
               max(len(set(a.lower().split())), len(set(b.lower().split())))

    @app.route('/chat', methods=['POST'])
    @limiter.limit("5 per minute")
    def chat():
        try:
            logger.info("=== Starting new chat request ===")

            # Get API key
            api_key = get_api_key()
            if not api_key:
                logger.error("API key not found")
                return jsonify({"error": "Service temporarily unavailable"}), 500

            # Get user message
            data = request.get_json()
            if not data or 'message' not in data:
                logger.error("No message provided in request")
                return jsonify({"error": "Invalid request"}), 400

            user_message = data['message']

            # Check for abuse/spam
            if not check_query_abuse(user_message):
                return jsonify({"error": "Too many similar requests"}), 429

            # Moderate content
            if not moderate_content(user_message):
                return jsonify({"error": "Message not allowed"}), 400

            logger.info(f"Received message: {user_message}")

            # Configure OpenAI client
            client = OpenAI(api_key=api_key)

            # Load context if not already loaded
            context_content, content_embeddings = load_context_files()
            if not context_content:
                return jsonify({"error": "Context not available"}), 500

            # Get query embedding
            query_embedding = get_embedding(user_message, client)
            if not query_embedding:
                return jsonify({"error": "Could not process query"}), 500

            # Find relevant context
            relevant_context = find_relevant_context(query_embedding, content_embeddings)

            # Prepare conversation with context
            conversation = [
                {"role": "system", "content": """You are an AI assistant for a personal portfolio website. Your responses should be:
                1. Accurate and based solely on the provided context
                2. Professional yet approachable in tone
                3. Clear about where information can be found on the website
                4. Protective of private information
                5. Helpful in directing users to appropriate resources

                When discussing projects or experience:
                - Reference specific locations in the portfolio
                - Mention GitHub repositories when relevant
                - Point out live demos where available
                - Follow the contact policy for inquiries

                If you cannot find relevant information in the context, politely say so and suggest what information you can provide instead."""},
                {"role": "system", "content": "Context: " + " ".join(relevant_context)},
                {"role": "user", "content": user_message}
            ]

            # Get response from GPT
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation,
                    temperature=0.7,
                    max_tokens=500
                )

                bot_response = response.choices[0].message.content
                return jsonify({"response": bot_response})

            except Exception as e:
                logger.error(f"Error getting GPT response: {e}")
                return jsonify({"error": "Could not generate response"}), 500

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({"error": "An error occurred"}), 500

    return app 