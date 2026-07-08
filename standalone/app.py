import os
import sys
import shutil
import subprocess
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

@app.route('/api/connect', methods=['POST'])
def connect_sharepoint():
    data = request.json
    first = data.get('firstName', '').strip().lower()
    last = data.get('lastName', '').strip().lower()
    password = data.get('password', '')
    
    user = f"{first}.{last}@webarea.com"
    content = f"{user}\n{password}"
    write_txt("user_credentials.txt", content)
    
    return jsonify({"status": "success", "message": "Connected to SharePoint!"})

@app.route('/api/file-info', methods=['POST'])
def submit_file_info():
    data = request.json
    test = data.get('testType')
    base_path = data.get('basePath', '').strip()
    
    lmo = data.get('lmoNumber', '').strip()
    
    write_txt("path.txt", base_path)
    
    upload_path = ""
    
    if test == 1:
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)
        
    elif test == 2:
        pma = data.get('pmaArea', '').strip()
        sn = data.get('serialNumber', '').strip()
        write_txt("PMA_Area.txt", pma)
        write_txt("SN.txt", sn)
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)
        
    elif test == 3:
        sn = data.get('serialNumber', '').strip()
        sn_folder = f"SN{int(sn):04d}_LMO{lmo}"
        upload_path = os.path.join(base_path, sn_folder)
        os.makedirs(upload_path, exist_ok=True)
        write_txt("SN.txt", sn)
        write_txt("path.txt", upload_path)
        write_txt("upload_path.txt", upload_path)
        
    return jsonify({"status": "success", "upload_path": upload_path})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files')
    dest_folder = read_txt("upload_path.txt")
    
    if not dest_folder:
        return jsonify({"error": "Upload path not set"}), 400
        
    os.makedirs(dest_folder, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename:
            filepath = os.path.join(dest_folder, file.filename)
            file.save(filepath)
            saved_files.append(file.filename)
            
    return jsonify({"status": "success", "saved": saved_files})

@app.route('/api/folders', methods=['GET'])
def get_folders():
    path = read_txt("path.txt")
    folders = []
    if os.path.exists(path) and os.path.isdir(path):
        try:
            folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        except Exception as e:
            pass
    return jsonify({"folders": folders})

@app.route('/api/select-runs', methods=['POST'])
def select_runs():
    data = request.json
    run_a = data.get('runA')
    run_b = data.get('runB')
    
    if run_a:
        write_txt("RunA_Path.txt", run_a)
    if run_b:
        write_txt("RunB_Path.txt", run_b)
        
    return jsonify({"status": "success"})

@app.route('/api/process', methods=['GET'])
def process_data():
    test = request.args.get('testType', type=int)
    
    script_map = {
        1: "Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py",
        2: "Macallan_PMA_BenchtopNPD_PlotData_v2.py",
        3: "Macallan_PMA_Array_BenchtopNPD_PlotData_v2.py"
    }
    
    script = script_map.get(test)
    if not script:
        return jsonify({"error": "Invalid test type"}), 400
        
    script_path = os.path.join(BASE_DIR, script)
    
    def generate():
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=BASE_DIR,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            yield f"data: {line}\n\n"
            
        process.stdout.close()
        process.wait()
        
        if process.returncode == 0:
            yield f"data: [PROCESS_COMPLETED]\n\n"
        else:
            yield f"data: [PROCESS_ERROR]\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
