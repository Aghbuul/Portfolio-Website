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
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = None


def init_chat_routes(app):
    global limiter

    # Initialize rate limiter with memory storage
    limiter = Limiter(app=app,
                      key_func=get_remote_address,
                      default_limits=["5 per minute", "100 per day"],
                      storage_uri="memory://")

    # Store context content and embeddings in memory
    context_content = {}
    content_embeddings = {}
    recent_queries = deque(
        maxlen=1000)  # Store recent queries for abuse detection

    def get_api_key():
        """Get API key from environment, with fallback options"""
        # Try getting from Replit secrets first
        api_key = environ.get('OPENAI_API_KEY')

        # If not in Replit, try getting from .env file
        if not api_key:
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            logger.error("API key not found in environment or .env file")
            return None

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
            response = client.embeddings.create(model="text-embedding-ada-002",
                                                input=text)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None

    def chunk_text(text, chunk_size=500):
        """Split text into semantically meaningful chunks"""
        # Split into sections based on headers
        sections = re.split(r'(?m)^#{1,3}\s+', text)
        chunks = []

        for section in sections:
            if not section.strip():
                continue

            # Split section into smaller chunks if too large
            sentences = re.split(r'(?<=[.!?])\s+', section)
            current_chunk = []
            current_size = 0

            for sentence in sentences:
                sentence_size = len(sentence.split())
                # Keep related sentences together when possible
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
                context_dir = os.path.join(os.path.dirname(__file__),
                                           'context_data')

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
                            with open(file_path, 'r',
                                      encoding='utf-8') as file:
                                content = file.read()

                            # Chunk the content
                            chunks = chunk_text(content)
                            context_content[context_key] = chunks
                            content_embeddings[context_key] = []

                            # Generate embeddings for each chunk
                            for chunk in chunks:
                                embedding = get_embedding(chunk, client)
                                if embedding:
                                    content_embeddings[context_key].append(
                                        embedding)

                        except Exception as e:
                            logger.error(
                                f"Error processing context file {filename}: {e}"
                            )

                if not context_content:
                    logger.warning(
                        "No context files found in context_data directory")
                    # Create an example context file
                    example_path = os.path.join(context_dir, 'example.txt')
                    if not os.path.exists(example_path):
                        with open(example_path, 'w', encoding='utf-8') as f:
                            f.write(
                                "This is an example context file. Replace this with your actual knowledge base content."
                            )

            return context_content, content_embeddings
        except Exception as e:
            logger.error(f"Error loading context files: {e}")
            return {}, {}

    def find_relevant_context(query_embedding, content_embeddings, top_k=5):
        """Find most relevant content chunks using semantic similarity"""
        all_chunks = []
        logger.info("Finding relevant context for query")

        # Process each source and its embeddings
        for source, embeddings in content_embeddings.items():
            logger.info(f"Processing source: {source}")
            for i, emb in enumerate(embeddings):
                similarity = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(emb).reshape(1, -1))[0][0]

                # Store chunk with metadata
                all_chunks.append({
                    'text': context_content[source][i],
                    'similarity': similarity,
                    'source': source,
                    'section': identify_section(context_content[source][i])
                })

        # Sort all chunks by similarity
        all_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        logger.info(f"Found {len(all_chunks)} total chunks")

        # Get top k chunks with similarity above threshold
        threshold = 0.2
        top_chunks = [chunk for chunk in all_chunks[:top_k] if chunk['similarity'] > threshold]

        if not top_chunks:
            logger.warning("No relevant chunks found above threshold")
            return ["I don't have specific information about that in my current context. However, I can tell you about the projects, skills, or experience sections visible on the portfolio website."]

        # Log similarity scores and metadata for debugging
        for i, chunk in enumerate(top_chunks):
            logger.info(f"Chunk {i+1}:")
            logger.info(f"  Similarity: {chunk['similarity']:.3f}")
            logger.info(f"  Source: {chunk['source']}")
            logger.info(f"  Section: {chunk['section']}")
            logger.info(f"  Preview: {chunk['text'][:100]}...")

        # Organize chunks by section for coherent response
        organized_chunks = organize_chunks_by_section(top_chunks)
        return organized_chunks

    def identify_section(text):
        """Identify which section a chunk belongs to based on content analysis"""
        section_keywords = {
            'projects': ['project', 'built', 'developed', 'created', 'implemented'],
            'education': ['university', 'degree', 'studied', 'graduated', 'thesis'],
            'experience': ['worked', 'position', 'role', 'responsible', 'led'],
            'skills': ['proficient', 'experienced in', 'familiar with', 'expertise'],
            'awards': ['award', 'recognition', 'honored', 'received', 'winner']
        }

        text_lower = text.lower()
        max_matches = 0
        best_section = 'general'

        for section, keywords in section_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_section = section

        return best_section

    def organize_chunks_by_section(chunks):
        """Organize chunks into a coherent narrative"""
        # Group chunks by section
        sections = {}
        for chunk in chunks:
            section = chunk['section']
            if section not in sections:
                sections[section] = []
            sections[section].append(chunk['text'])

        # Combine chunks within each section
        organized_text = []
        for section in ['projects', 'education', 'experience', 'skills', 'awards', 'general']:
            if section in sections:
                organized_text.extend(sections[section])

        return organized_text

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
                return jsonify({"error":
                                "Service temporarily unavailable"}), 500

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
            relevant_context = find_relevant_context(query_embedding,
                                                     content_embeddings)

            # Prepare conversation with context
            relevant_context_text = " ".join(relevant_context)
            logger.info(f"Context length: {len(relevant_context_text)} characters")
            logger.info("Context preview: " + relevant_context_text[:200] + "...")

            conversation = [{
                "role": "system",
                "content": """You are an AI assistant for a personal portfolio website. Follow these rules strictly:

1. Context Usage:
   - Use ONLY the information provided in the context
   - Organize information logically based on sections (Projects, Education, Experience, etc.)
   - Present information in a way that directly answers the user's query
   - When information exists but is partial, share what you know and suggest where to find more

2. Response Format:
   - Start with a brief introduction or summary when appropriate
   - Add a blank line between different topics or sections for better readability
   - Use bullet points (•) for listing items within a section
   - Keep descriptions concise but informative

3. Markdown Formatting:
   - Use ### for main section headers (e.g., ### Web Development Projects)
   - Use `backticks` for technical terms, languages, and tools (appears in cyan)
   - Use **bold** for emphasis on important points
   - Use *asterisks* ONLY for featured project names
   - Format links as [text](url)
   - Use > for highlighting key information or quotes
   - Add horizontal lines (---) to separate major sections when needed

4. Project Descriptions:
   - Start with the project name and year
   - List key features with bullet points
   - Highlight technologies used with backticks
   - Include relevant links when available

5. Portfolio Navigation:
   - Direct users to specific sections when relevant
   - Mention when more details are available in the portfolio
   - Help users find the information they're looking for

Remember: Only mention information that is explicitly provided in the context. If you're not sure about something, say so rather than making assumptions.

Example Format:
### Web Development Projects
> Here are the relevant projects I found:

• *Portfolio Website* (2024)
  - Built with `HTML`, `CSS`, `JavaScript`, and `Flask`
  - Features interactive animations and responsive design
  - [View Repository](link)

---
"""
            }, {
                "role": "system",
                "content": f"Context (use ONLY this information for your response): {relevant_context_text}"
            }, {
                "role": "user",
                "content": user_message
            }]

            # Get response from GPT
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation,
                    temperature=0.7,
                    max_tokens=500)

                bot_response = response.choices[0].message.content
                return jsonify({"response": bot_response})

            except Exception as e:
                logger.error(f"Error getting GPT response: {e}")
                return jsonify({"error": "Could not generate response"}), 500

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({"error": "An error occurred"}), 500

    return app
