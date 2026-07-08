import os
import sys
import shutil
import subprocess
import base64
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
    path = read_txt("upload_path.txt") # Use upload_path so Test 3 looks inside the SN folder
    if not path:
        path = read_txt("path.txt")
    if path:
        path = path.strip('"').strip("'").strip()
        
    folders = []
    if path and os.path.exists(path) and os.path.isdir(path):
        try:
            folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and 'run' in f.lower()]
        except Exception as e:
            print("Error in get_folders:", str(e))
    else:
        print(f"Path does not exist or is not a directory: {path}")
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

@app.route('/api/choose_directory', methods=['GET'])
def choose_directory():
    try:
        import sys
        import os
        import subprocess
        
        if sys.platform == 'win32':
            # Use native Python ctypes in a subprocess for instant load time.
            # Explicitly define restype and argtypes to prevent 64-bit pointer truncation (which caused the OSError).
            py_script = """
import ctypes
from ctypes import wintypes

shell32 = ctypes.windll.shell32
user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

shell32.SHBrowseForFolderW.restype = ctypes.c_void_p
shell32.SHBrowseForFolderW.argtypes = [ctypes.c_void_p]

shell32.SHGetPathFromIDListW.restype = wintypes.BOOL
shell32.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, wintypes.LPWSTR]

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetForegroundWindow.argtypes = []

ole32.CoTaskMemFree.restype = None
ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]

class BROWSEINFO(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", wintypes.HWND),
        ("pidlRoot", wintypes.LPVOID),
        ("pszDisplayName", wintypes.LPWSTR),
        ("lpszTitle", wintypes.LPCWSTR),
        ("ulFlags", wintypes.UINT),
        ("lpfn", wintypes.LPVOID),
        ("lParam", wintypes.LPARAM),
        ("iImage", wintypes.INT),
    ]

ole32.CoInitialize(None)

bi = BROWSEINFO()
bi.hwndOwner = user32.GetForegroundWindow() # Attach to active browser window to force TopMost
bi.pidlRoot = None

display_name_buffer = ctypes.create_unicode_buffer(260)
bi.pszDisplayName = ctypes.cast(display_name_buffer, wintypes.LPWSTR)
bi.lpszTitle = "Select Base Path"
bi.ulFlags = 0x00000041  # BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
bi.lpfn = None
bi.lParam = 0
bi.iImage = 0

pidl = shell32.SHBrowseForFolderW(ctypes.byref(bi))
path = ""
if pidl:
    path_buffer = ctypes.create_unicode_buffer(260)
    if shell32.SHGetPathFromIDListW(pidl, path_buffer):
        path = path_buffer.value
    ole32.CoTaskMemFree(pidl)

ole32.CoUninitialize()
print(path)
"""
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            result = subprocess.run(
                [sys.executable, "-c", py_script],
                capture_output=True, text=True, env=env
            )
            folder_path = result.stdout.strip()
        else:
            # macOS / Linux fallback using tkinter in subprocess
            script = """
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
folder_path = filedialog.askdirectory(title="Select Base Path")
root.destroy()
print(folder_path)
"""
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=env)
            folder_path = result.stdout.strip()
            
            if result.returncode != 0:
                return jsonify({"success": False, "error": result.stderr.strip()})
        
        if folder_path:
            return jsonify({"success": True, "path": folder_path})
        else:
            return jsonify({"success": False, "error": "No directory selected"})
    except Exception as e:
        print("Error in choose_directory:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate_plots', methods=['POST'])
def api_generate_plots():
    test = request.args.get('testType', type=int)
    params = request.json or {}
    
    # We need to set folder_path and runs for Test 1
    if test == 1:
        import plot_generator
        folder_path = read_txt("path.txt")
        run_a = read_txt("RunA_Path.txt")
        run_b = read_txt("RunB_Path.txt")
        params['folder_path'] = folder_path
        params['runs'] = [run for run in [run_a, run_b] if run]
        
        try:
            png_files = plot_generator.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500
            
    elif test == 2:
        import Macallan_PMA_BenchtopNPD_PlotData_v2
        try:
            png_files = Macallan_PMA_BenchtopNPD_PlotData_v2.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500
            
    elif test == 3:
        import Macallan_PMA_Array_BenchtopNPD_PlotData_v2
        try:
            png_files = Macallan_PMA_Array_BenchtopNPD_PlotData_v2.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "Invalid test type"}), 400

    results = []
    if png_files:
        for file_path in png_files:
            if os.path.exists(file_path):
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    results.append({
                        "filename": os.path.basename(file_path),
                        "data": f"data:image/png;base64,{encoded_string}"
                    })
    
    return jsonify({"success": True, "images": results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
