from flask import Flask, render_template, make_response, jsonify
from chat import init_chat_routes
import os
from os import environ
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Starting application...")

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/chat": {
        "origins": ["*"],  # Allow all origins in development
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "X-Requested-With"]
    }
})

# Check for API key in different locations
api_key = environ.get('OPENAI_API_KEY')
if not api_key:
    api_key = os.getenv('OPENAI_API_KEY')
logger.info("API Key status: " + ("Found" if api_key else "Not found"))

print("Flask app initialized")

# Initialize chat routes
init_chat_routes(app)
print("Chat routes initialized")

@app.route('/check-static')
def check_static():
    import os
    static_path = os.path.join(app.root_path, 'static', 'images')
    files = os.listdir(static_path)
    return {'files': files}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500

@app.after_request
def after_request(response):
    # Log the response status
    logger.info(f"Response status: {response.status}")
    if response.status_code >= 400:
        logger.error(f"Error response: {response.get_data(as_text=True)}")
    return response

if __name__ == '__main__':
    # Make sure OPENAI_API_KEY is set in Replit secrets
    if not environ.get('OPENAI_API_KEY'):
        print("\033[91mWarning: OPENAI_API_KEY is not set in Replit secrets!\033[0m")
        print("\033[93mPlease add your OpenAI API key to the Secrets tab in your Replit project:\033[0m")
        print("\033[93m1. Click on 'Tools' in the left sidebar\033[0m")
        print("\033[93m2. Click on 'Secrets'\033[0m")
        print("\033[93m3. Add a new secret with key 'OPENAI_API_KEY' and your API key as the value\033[0m")
    else:
        print("\033[92mOPENAI_API_KEY is set in Replit secrets ✓\033[0m")

    print("Starting Flask development server...")
    # Use Replit's port
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
