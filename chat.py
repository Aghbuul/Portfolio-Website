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

# Load environment variables from .env file
load_dotenv()

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
        api_key = environ.get('OPENAI_API_KEY')
        logger.debug("Checking environ.get() for API key...")
        if api_key:
            logger.debug("Found API key in environ.get()")
        else:
            logger.debug("API key not found in environ.get(), checking os.getenv()...")
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                logger.debug("Found API key in os.getenv()")
            else:
                logger.debug("API key not found in os.getenv()")
        
        if api_key:
            # Log key details without making format assumptions
            logger.debug(f"API key found - length: {len(api_key)}")
            logger.debug(f"API key prefix: {api_key.split('-')[0] if '-' in api_key else 'unknown'}")
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
            result = response.results[0]
            
            # Log detailed moderation results
            logger.info(f"Moderation results: {result}")
            
            # Only block if flagged as severe
            return not (result.flagged and any([
                result.categories.hate,
                result.categories.hate_threatening,
                result.categories.self_harm,
                result.categories.sexual_abuse,
                result.categories.violence_graphic
            ]))
        except Exception as e:
            logger.error(f"Moderation error: {e}")
            return True  # Allow message if moderation fails

    def get_embedding(text, client):
        """Get embedding for a piece of text"""
        try:
            logger.debug(f"Attempting to get embedding for text: {text[:100]}...")
            logger.debug(f"Using OpenAI client with API key starting with: {client.api_key[:4] if client.api_key else 'None'}")
            
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            logger.debug("Successfully got embedding response")
            logger.debug(f"Response type: {type(response)}")
            
            embedding = response.data[0].embedding
            logger.debug(f"Successfully extracted embedding of length: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
            logger.debug(f"API Key found: {bool(api_key)}")
            logger.debug(f"API Key first 4 chars: {api_key[:4] if api_key else 'None'}")
            logger.debug(f"API Key length: {len(api_key) if api_key else 'None'}")
            
            if not api_key:
                logger.error("API key not found")
                return jsonify({"error": "Service temporarily unavailable"}), 500

            # Get user message
            try:
                data = request.get_json()
                logger.debug(f"Received request data: {data}")
            except Exception as e:
                logger.error(f"Error parsing JSON request: {e}")
                return jsonify({"error": "Invalid JSON"}), 400

            if not data or 'message' not in data:
                logger.error("No message provided in request")
                return jsonify({"error": "Invalid request"}), 400

            user_message = data['message']
            logger.info(f"Processing message: {user_message}")

            # Check for abuse/spam
            abuse_check = check_query_abuse(user_message)
            logger.debug(f"Abuse check result: {abuse_check}")
            if not abuse_check:
                logger.warning("Query abuse detected")
                return jsonify({"error": "Too many similar requests"}), 429

            # Moderate content
            logger.debug("Starting content moderation...")
            moderation_result = moderate_content(user_message)
            logger.debug(f"Moderation result: {moderation_result}")
            if not moderation_result:
                logger.warning("Message failed moderation check")
                return jsonify({"error": "Message not allowed - contains inappropriate content"}), 400

            # Configure OpenAI client
            try:
                logger.debug("Initializing OpenAI client...")
                client = OpenAI(api_key=api_key)
                logger.debug("OpenAI client initialized successfully")
                logger.debug(f"Client API key starts with: {client.api_key[:4] if client.api_key else 'None'}")
                
                # Test the API key with a simple moderation request
                logger.debug("Testing API key with moderation request...")
                test_response = client.moderations.create(input="test")
                logger.debug("API key test successful")
                
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Error args: {e.args}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({"error": "Error initializing AI service"}), 500

            # Load context if not already loaded
            logger.debug("Loading context files...")
            context_content, content_embeddings = load_context_files()
            logger.debug(f"Context loaded - Number of sources: {len(context_content)}")
            logger.debug(f"Available context keys: {list(context_content.keys())}")
            
            if not context_content:
                logger.error("Failed to load context files")
                return jsonify({"error": "Context not available"}), 500

            # Get query embedding
            logger.debug("Getting query embedding...")
            try:
                query_embedding = get_embedding(user_message, client)
                logger.debug(f"Query embedding obtained - Length: {len(query_embedding) if query_embedding else 'None'}")
            except Exception as e:
                logger.error(f"Error getting embedding: {str(e)}")
                return jsonify({"error": "Could not process query - Embedding failed"}), 500
                
            if not query_embedding:
                logger.error("Failed to get query embedding")
                return jsonify({"error": "Could not process query"}), 500

            # Find relevant context
            logger.debug("Finding relevant context...")
            try:
                relevant_context = find_relevant_context(query_embedding, content_embeddings)
                logger.debug(f"Found {len(relevant_context)} relevant context chunks")
                logger.debug(f"First chunk preview: {relevant_context[0][:100] if relevant_context else 'No context'}")
            except Exception as e:
                logger.error(f"Error finding relevant context: {str(e)}")
                return jsonify({"error": "Error processing context"}), 500

            try:
                # Prepare chat completion
                logger.debug("Preparing chat completion...")
                messages = [
                    {"role": "system", "content": "You are a helpful assistant providing information about Iqbal's portfolio, projects, and experience. Respond in a friendly and professional manner."},
                    {"role": "user", "content": f"Context about Iqbal: {relevant_context}\n\nUser question: {user_message}"}
                ]
                logger.debug(f"Messages prepared: {json.dumps(messages, indent=2)}")

                # Get chat completion
                logger.info("Requesting chat completion")
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                response = completion.choices[0].message.content
                logger.info("Chat completion received successfully")
                logger.debug(f"Response preview: {response[:100]}")
                
                return jsonify({"response": response})
                
            except Exception as e:
                logger.error(f"Error in chat completion: {str(e)}")
                return jsonify({"error": f"Error generating response: {str(e)}"}), 500
                
        except Exception as e:
            logger.error(f"Unexpected error in chat handler: {str(e)}")
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    return app
