import os
import shutil

# Copy the entire backend directory into standalone/backend
backend_dest = 'standalone/backend'
if os.path.exists(backend_dest):
    shutil.rmtree(backend_dest)

def ignore_patterns(path, names):
    return [n for n in names if n in ['__pycache__', 'venv', '.env']]

shutil.copytree('backend', backend_dest, ignore=ignore_patterns)

standalone_app_code = """import os
import sys
from flask import send_from_directory

# Inject local packages folder into Python path so portable python can find them
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'packages'))
sys.path.insert(0, os.path.join(current_dir, 'python', 'Lib', 'site-packages'))
# Add the copied backend to the path
sys.path.insert(0, os.path.join(current_dir, 'backend'))

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

dist_folder = os.path.join(application_path, 'dist')

# Import the backend app robustly to avoid circular import (since this file is also app.py)
import importlib.util
backend_app_path = os.path.join(current_dir, 'backend', 'app.py')
spec = importlib.util.spec_from_file_location('backend_app', backend_app_path)
backend_module = importlib.util.module_from_spec(spec)
sys.modules['backend_app'] = backend_module
spec.loader.exec_module(backend_module)

app = backend_module.app

# Apply standalone configuration overrides
app.static_folder = dist_folder
app.static_url_path = '/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024 # 16 GB

if hasattr(app.request_class, 'max_form_parts'):
    class CustomRequest(app.request_class):
        max_form_parts = 1000000
    app.request_class = CustomRequest

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
"""

with open('standalone/app.py', 'w') as f:
    f.write(standalone_app_code)

print("Standalone app updated successfully. Backend files copied to standalone/backend/")
