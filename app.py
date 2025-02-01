from flask import Flask, render_template
from chat import init_chat_routes
import os

print("Starting application...")

# Initialize Flask app
app = Flask(__name__)
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

if __name__ == '__main__':
    # Make sure OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("\033[91mWarning: OPENAI_API_KEY environment variable is not set!\033[0m")
        print("\033[93mPlease add your OpenAI API key to the Secrets tab in Replit\033[0m")
    else:
        print("\033[92mOPENAI_API_KEY is set ✓\033[0m")
    
    print("Starting Flask development server...")
    # Use Replit's port
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
