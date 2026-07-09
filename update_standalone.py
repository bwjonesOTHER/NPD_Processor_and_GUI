import os
with open('backend/app.py', 'r') as f:
    backend_code = f.read()

standalone_imports = """import os
import sys
import shutil
import subprocess
import base64
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

# Inject local packages folder into Python path so portable python can find them
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'packages'))
sys.path.insert(0, os.path.join(current_dir, 'python', 'Lib', 'site-packages'))

# Find the absolute path to the directory this script is in
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

dist_folder = os.path.join(application_path, 'dist')
app = Flask(__name__, static_folder=dist_folder, static_url_path='/')
CORS(app)

BASE_DIR = application_path

def write_txt(filename, content):
    with open(os.path.join(BASE_DIR, filename), "w") as f:
        f.write(content)

def read_txt(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return ""

def hydrate_directory(directory_path):
    if not directory_path or not os.path.exists(directory_path):
        return
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Reading 1 byte forces Windows OneDrive to download the file on-demand
                with open(file_path, "rb") as f:
                    f.read(1)
            except Exception:
                pass

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
"""

# Find where @app.route('/api/connect' starts in backend/app.py
idx = backend_code.find("@app.route('/api/connect'")
backend_routes = backend_code[idx:]

# Remove the __main__ block from backend_routes and replace it with standalone run
main_idx = backend_routes.find("if __name__ == '__main__':")
backend_routes = backend_routes[:main_idx]

standalone_end = """if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
"""

with open('standalone/app.py', 'w') as f:
    f.write(standalone_imports + "\n" + backend_routes + "\n" + standalone_end)

