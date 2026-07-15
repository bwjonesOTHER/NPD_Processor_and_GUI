import os
import sys
import shutil
import subprocess
import base64

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

dist_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')
app = Flask(__name__, static_folder=dist_folder)
# Allow massive uploads (e.g., thousands of files in a directory)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024 # 16 GB
if hasattr(app.request_class, 'max_form_parts'):
    # Increase from default 1000 to a large number to support uploading large directories
    class CustomRequest(app.request_class):
        max_form_parts = 1000000
    app.request_class = CustomRequest

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

def hydrate_directory(directory_path):
    if not directory_path or not os.path.exists(directory_path):
        return
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.csv') or file.lower().endswith('.s2p'):
                file_path = os.path.join(root, file)
                try:
                    # Reading 1 byte forces Windows OneDrive to download the file on-demand
                    with open(file_path, "rb") as f:
                        f.read(1)
                except Exception:
                    pass
                pass


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
        run_num = data.get('runNumber', '').strip()
        cap_num = data.get('capNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        
        # Construct the requested folder structure: Run_[runNumber] [LMONumber]/Cap_[capNumber]
        # Using .strip() inside the f-string just in case any field was left blank, though it shouldn't be.
        run_folder = f"Run_{run_num} {lmo_num}".strip()
        cap_folder = f"Cap_{cap_num}".strip()
        
        upload_path = os.path.join(base_path, run_folder, cap_folder)
        os.makedirs(upload_path, exist_ok=True)
        write_txt("upload_path.txt", upload_path)
        
    elif test == 2:
        pma = data.get('pmaArea', '').strip()
        sn = data.get('serialNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        upload_mode = data.get('uploadMode', 'access')
        exact_lmo_folder = data.get('exactLmoFolder', '').strip()
        
        write_txt("PMA_Area.txt", pma)
        write_txt("serialNumber.txt", sn)
        write_txt("lmoNumber.txt", lmo_num)

        if upload_mode == 'upload':
            # Create the folder instead of searching for it
            pma_path = os.path.join(base_path, "BenchNPD", pma)
            if not os.path.exists(pma_path) and os.path.exists(os.path.join(base_path, pma)):
                pma_path = os.path.join(base_path, pma)
            
            # Format lmo_num properly (LMOXXXX)
            lmo_folder = f"LMO{lmo_num}" if not lmo_num.upper().startswith("LMO") else lmo_num
            upload_path = os.path.join(pma_path, lmo_folder)
            os.makedirs(upload_path, exist_ok=True)
            
            write_txt("upload_path.txt", upload_path)
            write_txt("path.txt", base_path)
            
            return jsonify({
                "status": "success",
                "success": True,
                "upload_path": upload_path
            })

        if exact_lmo_folder:
            lmo_num = exact_lmo_folder
        else:
            # Search for matching folders
            import glob
            pma_path = os.path.join(base_path, "BenchNPD", pma)
            if not os.path.exists(pma_path):
                # Fallback if BenchNPD isn't in the path explicitly
                pma_path = os.path.join(base_path, pma)
                
            if os.path.exists(pma_path):
                # Look for directories containing the LMO number
                try:
                    all_dirs = [d for d in os.listdir(pma_path) if os.path.isdir(os.path.join(pma_path, d))]
                    matches = [d for d in all_dirs if lmo_num.lower() in d.lower()]
                    
                    # Filter by SN if provided
                    if sn:
                        filtered_matches = []
                        for match in matches:
                            match_path = os.path.join(pma_path, match)
                            found_sn = False
                            for root, dirs, files in os.walk(match_path):
                                if any(sn in f for f in files) or any(sn in d for d in dirs):
                                    found_sn = True
                                    break
                            if found_sn:
                                filtered_matches.append(match)
                        
                        with open("debug_log.txt", "a") as f_dbg:
                            f_dbg.write(f"Original matches: {matches}\n")
                            f_dbg.write(f"Filtered by SN '{sn}': {filtered_matches}\n")
                        
                        # Only apply the filter if it found at least one match (to avoid breaking things if SN format was weird)
                        if len(filtered_matches) > 0:
                            matches = filtered_matches
                    
                    with open("debug_log.txt", "a") as f_dbg:
                        f_dbg.write(f"Search base: {base_path}\n")
                        f_dbg.write(f"Search pma: {pma}\n")
                        f_dbg.write(f"Search lmo_num: {lmo_num}\n")
                        f_dbg.write(f"Search pma_path: {pma_path}\n")
                        f_dbg.write(f"All dirs: {all_dirs}\n")
                        f_dbg.write(f"Matches: {matches}\n")

                    if len(matches) > 1:
                        return jsonify({"success": False, "requireLmoSelection": True, "options": matches})
                    elif len(matches) == 1:
                        lmo_num = matches[0]
                except Exception as e:
                    print("Error scanning for LMO folders:", e)
                    with open("debug_log.txt", "a") as f_dbg:
                        f_dbg.write(f"Search error: {e}\n")
            else:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"Search pma_path DOES NOT EXIST: {pma_path}\n")
        
        write_txt("PMA_Area.txt", pma)
        write_txt("SN.txt", sn)
        write_txt("LMO_Number.txt", lmo_num)
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)
        
    elif test == 3:
        sn = data.get('serialNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        sn_folder = f"SN{int(sn):04d}_LMO{lmo_num}"
        upload_path = os.path.join(base_path, sn_folder)
        
        upload_mode = data.get('uploadMode', 'access')
        if upload_mode == 'upload':
            run_entry = data.get('runEntry', '').strip()
            if run_entry:
                upload_path = os.path.join(upload_path, run_entry)
                
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
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            saved_files.append(file.filename)
            
    return jsonify({"status": "success", "saved": saved_files})

@app.route('/api/upload_run', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
def upload_run_files():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    if request.method == 'GET':
        return jsonify({"error": "Please use POST for uploading runs."}), 400
        
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files')
    paths = request.form.getlist('paths')
    run_index = request.form.get('run_index', '0')
    folder_name = request.form.get('folder_name', '')
    chunk_index = request.form.get('chunk_index', '0')
    base_path = read_txt("upload_path.txt")
    if not base_path:
        base_path = read_txt("path.txt")
    if not base_path:
        base_path = os.path.join(os.getcwd(), 'uploads')
        
    if folder_name:
        dest_folder = os.path.join(base_path, folder_name)
    else:
        dest_folder = os.path.join(base_path, f'Run_{run_index}')
    
    # Clean up old files to conserve disk space ONLY on the first chunk
    if chunk_index == '0' and os.path.exists(dest_folder):
        shutil.rmtree(dest_folder)
        
    os.makedirs(dest_folder, exist_ok=True)
    
    saved_files = []
    for idx, file in enumerate(files):
        if file.filename:
            # Reconstruct relative path if provided, otherwise just base filename
            relative_path = paths[idx] if idx < len(paths) else os.path.basename(file.filename)
            if folder_name and relative_path.startswith(folder_name + "/"):
                relative_path = relative_path[len(folder_name)+1:]
            elif folder_name and relative_path.startswith(folder_name + "\\"):
                relative_path = relative_path[len(folder_name)+1:]
            filepath = os.path.join(dest_folder, relative_path)
            
            # Ensure subdirectories exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            file.save(filepath)
            saved_files.append(relative_path)
            
    return jsonify({"status": "success", "upload_path": dest_folder, "saved": saved_files})

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
    
    if 'runs' in data:
        with open("SelectedRuns.txt", "w") as f:
            for run in data['runs']:
                if run:
                    f.write(run + "\n")
    
    # Legacy support for Test 3
    if 'runA' in data and 'runB' in data:
        # Test 2 / 3
        write_txt("RunA_Path.txt", data['runA'])
        write_txt("RunB_Path.txt", data['runB'])
        
        calPath = data.get('calPath', '')
        if calPath:
            write_txt("Cal_Path.txt", calPath)
            
        return jsonify({"status": "success"})
        
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


@app.route('/api/debug-tree', methods=['GET'])
def debug_tree():
    base_path = request.args.get('path', read_txt("path.txt") or read_txt("upload_path.txt") or '')
    if not base_path or not os.path.exists(base_path):
        return jsonify({"error": f"Path not found: {base_path}"})
    
    def get_tree(path, depth=0, max_depth=3):
        if depth > max_depth: return "..."
        tree = {}
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    tree[item] = get_tree(full_path, depth + 1, max_depth)
                else:
                    tree[item] = "FILE"
        except Exception as e:
            return str(e)
        return tree
        
    return jsonify({
        "base_path": base_path,
        "tree": get_tree(base_path, max_depth=4)
    })

@app.route('/api/generate_plots', methods=['POST'])
def api_generate_plots():
    test = request.args.get('testType', type=int)
    params = request.json or {}
    
    import tempfile
    import shutil
    temp_out_dir = tempfile.mkdtemp(prefix="npd_plots_")
    
    # We need to set folder_path and runs for Test 1
    if test == 1:
        import plot_generator
        runs = []
        if os.path.exists("SelectedRuns.txt"):
            with open("SelectedRuns.txt", "r") as f:
                runs = [line.strip() for line in f if line.strip()]
        else:
            run_a = read_txt("RunA_Path.txt")
            run_b = read_txt("RunB_Path.txt")
            runs = [run for run in [run_a, run_b] if run]
            
        if runs:
            folder_path = runs[0]
        else:
            folder_path = read_txt("upload_path.txt")
            if not folder_path:
                folder_path = read_txt("path.txt")
            
        params['folder_path'] = temp_out_dir
        params['runs'] = runs
        
        if folder_path:
            pass
        if runs:
            pass
        
        try:
            png_files = plot_generator.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"EXCEPTION in generate_plots: {e}\n")
                f_dbg.write(traceback.format_exc() + "\n")
            return jsonify({"success": False, "error": str(e)}), 500
            
    elif test == 2:
        import Macallan_PMA_BenchtopNPD_PlotData_v2
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        if path:
            with open("path.txt", "w") as f:
                f.write(path)
            # Removed hydrate_directory to prevent OneDrive image downloads
        params['outputFolder'] = temp_out_dir
        try:
            png_files = Macallan_PMA_BenchtopNPD_PlotData_v2.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"EXCEPTION in generate_plots: {e}\n")
                f_dbg.write(traceback.format_exc() + "\n")
            return jsonify({"success": False, "error": str(e)}), 500
            
    elif test == 3:
        import Macallan_PMA_Array_BenchtopNPD_PlotData_v2
        path1 = read_txt("path.txt")
        path2 = read_txt("upload_path.txt")
        if path1: params['path1'] = path1
        if path2: params['path2'] = path2
        params['outputFolder'] = temp_out_dir
        try:
            png_files = Macallan_PMA_Array_BenchtopNPD_PlotData_v2.generate_plots(params)
        except Exception as e:
            import traceback
            traceback.print_exc()
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"EXCEPTION in generate_plots: {e}\n")
                f_dbg.write(traceback.format_exc() + "\n")
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
                    
    shutil.rmtree(temp_out_dir, ignore_errors=True)
    
    return jsonify({"success": True, "images": results})

@app.route('/api/save_plots', methods=['POST'])
def save_plots():
    data = request.json or {}
    output_folder = data.get('outputFolder')
    plots = data.get('plots', [])
    if not output_folder:
        return jsonify({"success": False, "error": "No output folder specified"})
        
    output_folder = os.path.join(output_folder, "Eng_review")
    
    try:
        os.makedirs(output_folder, exist_ok=True)
        saved_files = []
        for plot in plots:
            base64_data = plot['data'].split(',')[1] if ',' in plot['data'] else plot['data']
            file_path = os.path.join(output_folder, plot['filename'])
            with open(file_path, "wb") as fh:
                fh.write(base64.b64decode(base64_data))
            saved_files.append(file_path)
        return jsonify({"success": True, "saved": saved_files})
    except Exception as e:
        import traceback
        with open("debug_log.txt", "a") as f_dbg:
            f_dbg.write(f"EXCEPTION in save_plots: {e}\n")
            f_dbg.write(traceback.format_exc() + "\n")
        return jsonify({"success": False, "error": str(e)}), 500

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
    app.run(host='0.0.0.0', debug=True, port=5001)
