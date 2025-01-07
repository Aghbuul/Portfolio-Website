from flask import Flask, render_template

app = Flask(__name__)

@app.route('/check-static')
def check_static():
    import os
    static_path = os.path.join(app.root_path, 'static', 'images')
    files = os.listdir(static_path)
    return {'files': files}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
