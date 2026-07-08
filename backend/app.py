import os
import shutil
import subprocess
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# We will run this server from the root of the project
# or from the backend folder. Let's assume root of the project.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def write_txt(filename, content):
    with open(os.path.join(BASE_DIR, filename), "w") as f:
        f.write(content)

def read_txt(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return ""

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
    
    # Store base path based on input
    write_txt("path.txt", base_path)
    
    upload_path = ""
    
    if test == 1:
        # For Test 1, the Tkinter app had a hardcoded path and didn't write it to upload_path explicitly before upload_data
        # But wait, in upload_data it did: upload_path = os.path.join(r"File Path for Inputs")
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
        write_txt("path.txt", upload_path) # Overwrites path.txt with upload_path as in original code
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
            ['python3', script_path],
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
    app.run(debug=True, port=5000)
