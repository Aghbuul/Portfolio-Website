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


from werkzeug.serving import run_simple
import ssl

if __name__ == '__main__':
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)
