"""
app.py
======
Flask backend application serving the React frontend.
Provides API endpoints to manage files, upload test runs, and trigger the plotting scripts.
"""
import os
import sys
import shutil
import subprocess
import base64

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Auto-install any missing Python dependencies before importing them, so a
# fresh checkout (or an environment where requirements.txt was never run)
# doesn't fail with a bare ModuleNotFoundError/ImportError deep inside a
# request handler. Only stdlib is used here since nothing else is guaranteed
# to be installed yet.
def _ensure_dependencies():
    import importlib
    # module name -> pip package name (only differ for flask-cors/scikit-rf)
    required = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'skrf': 'scikit-rf',
        'openpyxl': 'openpyxl',
        'xlrd': 'xlrd',
    }
    missing = []
    for module_name, pip_name in required.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return

    print(f"[startup] Installing missing Python dependencies: {', '.join(missing)}")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q'] + missing, check=True, timeout=600)
        print("[startup] Dependency installation complete.")
        importlib.invalidate_caches()
    except Exception as e:
        print(f"[startup] WARNING: automatic dependency installation failed: {e}")
        print("[startup] Please run manually: pip install -r requirements.txt")

_ensure_dependencies()

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'frontend', 'dist'))
CORS(app)
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
    """Writes content to a text file in the current directory."""
    with open(os.path.join(BASE_DIR, filename), "w") as f:
        f.write(content)

def read_txt(filename):
    """Reads content from a text file in the current directory."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return ""

def hydrate_directory(directory_path):
    """Recursively hydrates the directory structure to build a JSON tree for the frontend browser."""
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
    """Endpoint to save SharePoint user credentials."""
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
    """Endpoint to handle the initial setup of file metadata and generate the upload path."""
    data = request.json
    test = data.get('testType')
    base_path = data.get('basePath', '').strip()
    
    lmo = data.get('lmoNumber', '').strip()
    
    # Store base path based on input
    write_txt("path.txt", base_path)
    
    if test == 1:
        # Test 1 files are handled entirely by upload_run API endpoints and don't need upload_path.txt
        return jsonify({"status": "success", "success": True, "upload_path": ""})
        
    elif test == 2:
        pma = data.get('pmaArea', '').strip()
        sn = data.get('serialNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        upload_mode = data.get('uploadMode', 'upload') or 'upload'
        exact_lmo_folder = data.get('exactLmoFolder', '').strip()
        
        write_txt("PMA_Area.txt", pma)
        write_txt("serialNumber.txt", sn)
        write_txt("lmoNumber.txt", lmo_num)

        if upload_mode == 'upload':
            base_path = os.path.join(os.getcwd(), 'uploads')
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
        sn_int = int(sn) if sn.isdigit() else 0
        sn_folder = f"SN{sn_int:04d}_LMO{lmo_num}" if sn else f"UnknownSN_LMO{lmo_num}"
        upload_path = os.path.join(base_path, sn_folder)
        
        upload_mode = data.get('uploadMode', 'upload') or 'upload'
        if upload_mode == 'upload':
            base_path = os.path.join(os.getcwd(), 'uploads')
            upload_path = os.path.join(base_path, sn_folder)
            run_entry = data.get('runEntry', '').strip()
            if run_entry:
                upload_path = os.path.join(upload_path, run_entry)
                
        os.makedirs(upload_path, exist_ok=True)
        write_txt("SN.txt", sn)
        write_txt("path.txt", upload_path) # Overwrites path.txt with upload_path as in original code
        write_txt("upload_path.txt", upload_path)

    elif test == 4:
        # Over Temp Array: base_path already points at the single root folder
        # (either browsed directly, or the destination of a folder upload).
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)

    return jsonify({"status": "success", "upload_path": upload_path})

@app.route('/api/upload_reference_file', methods=['POST'])
def upload_reference_file():
    """Endpoint to upload a single reference file (e.g. the Ambient NPD
    averaged-data .xlsx/.csv) directly from the browser's file picker, so it
    works regardless of whether the browser and backend are on the same
    machine — unlike the OS-native folder/file browse dialogs."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        return jsonify({"success": False, "error": "Expected a .xlsx, .xls, or .csv file"}), 400

    dest_folder = os.path.join(os.getcwd(), 'uploads', 'reference_files')
    os.makedirs(dest_folder, exist_ok=True)
    filepath = os.path.join(dest_folder, file.filename)
    file.save(filepath)
    return jsonify({"success": True, "path": filepath, "filename": file.filename})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Endpoint to handle generic file uploads."""
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


@app.route('/api/upload_test_data', methods=['POST'])
def upload_test_data():
    test_type = request.form.get('test_type')
    if not test_type:
        test_type = request.form.get('testType', '1')
    
    base_path = os.path.join(os.getcwd(), 'uploads', f'Test{test_type}')
    
    # Always clear the test directory before uploading new data
    if os.path.exists(base_path):
        import shutil
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=True)
    
    # Clean up previous state files to prevent cross-contamination
    import glob
    for txt_file in glob.glob("*.txt"):
        if txt_file not in ["requirements.txt", "debug_log.txt", "SelectedRuns.txt"]:
            try:
                os.remove(txt_file)
            except:
                pass
                
    additional_cal_path = os.path.join(os.getcwd(), 'uploads', 'AdditionalCal')
    if os.path.exists(additional_cal_path):
        try:
            shutil.rmtree(additional_cal_path)
        except:
            pass
                
    def save_files(files_list, subfolder):
        dest_folder = os.path.join(base_path, subfolder)
        os.makedirs(dest_folder, exist_ok=True)
        for file in files_list:
            if file.filename:
                # Keep original folder structure if present
                rel_path = file.filename
                if '/' in rel_path:
                    # Strip the first folder name to avoid nested roots
                    parts = rel_path.split('/')
                    if len(parts) > 1:
                        rel_path = '/'.join(parts[1:])
                
                filepath = os.path.join(dest_folder, rel_path)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
        return dest_folder
        
    paths = {}
    if test_type == '2':
        paths['bench'] = save_files(request.files.getlist('bench_files'), 'Bench')
        paths['temp'] = save_files(request.files.getlist('temp_files'), 'Temp')
        paths['cal'] = save_files(request.files.getlist('cal_files'), 'Bench_Cal')
        paths['tempCal'] = save_files(request.files.getlist('temp_cal_files'), 'Temp_Cal')
    elif test_type == '3':
        paths['runA'] = save_files(request.files.getlist('runA_files'), 'Run_0')
        paths['runB'] = save_files(request.files.getlist('runB_files'), 'Run_1')
        paths['cal'] = save_files(request.files.getlist('cal_files'), 'Run_2')
        paths['runs'] = [paths['runA'], paths['runB'], paths['cal']]
    else:
        paths['general'] = save_files(request.files.getlist('general_files'), 'Data')
        
    return jsonify({
        "success": True,
        "paths": paths,
        "debug_form_keys": list(request.form.keys()),
        "debug_files_keys": list(request.files.keys()),
        "debug_test_type": test_type
    })

@app.route('/api/upload_run', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
def upload_run_files():
    """Endpoint to handle uploading directories for test runs, recreating folder structure."""
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
    test_type = request.form.get('testType', '1')
    
    # Completely sever ties to upload_path.txt and path.txt. 
    # Uploaded runs ALWAYS go into a strict, isolated local test folder.
    base_path = os.path.join(os.getcwd(), 'uploads', f'Test{test_type}')
        
    if folder_name:
        dest_folder = os.path.join(base_path, folder_name)
    else:
        dest_folder = os.path.join(base_path, f'Run_{run_index}')
    
    if chunk_index == '0':
        import glob
        for txt_file in glob.glob("*.txt"):
            if txt_file not in ["requirements.txt", "debug_log.txt", "SelectedRuns.txt"]:
                try:
                    os.remove(txt_file)
                except:
                    pass
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder)
            
        if run_index == '0':
            additional_cal_path = os.path.join(os.getcwd(), 'uploads', 'AdditionalCal')
            if os.path.exists(additional_cal_path):
                try:
                    shutil.rmtree(additional_cal_path)
                except:
                    pass
        
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

@app.route('/api/upload_additional_cal', methods=['POST'])
def upload_additional_cal():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files')
    dest_folder = os.path.join(os.getcwd(), 'uploads', 'AdditionalCal')
    
    # Clear directory to prevent stale additional cal files from leaking
    import shutil
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder, ignore_errors=True)
    os.makedirs(dest_folder, exist_ok=True)
    
    saved_count = 0
    for file in files:
        if file.filename:
            filepath = os.path.join(dest_folder, os.path.basename(file.filename))
            file.save(filepath)
            saved_count += 1
            
    return jsonify({"success": True, "count": saved_count})

@app.route('/api/delete_additional_cal', methods=['POST'])
def delete_additional_cal():
    dest_folder = os.path.join(os.getcwd(), 'uploads', 'AdditionalCal')
    import shutil
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder, ignore_errors=True)
    return jsonify({"success": True})

@app.route('/api/upload_generic', methods=['POST'])
def upload_generic():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    upload_type = request.form.get('type', 'data') # 'data' or 'cal'
    files = request.files.getlist('files')
    
    dest_folder = os.path.join(os.getcwd(), 'uploads', 'Generic', upload_type.capitalize())
    os.makedirs(dest_folder, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename:
            filepath = os.path.join(dest_folder, os.path.basename(file.filename))
            file.save(filepath)
            saved_files.append(os.path.basename(file.filename))
            
    # Return list of current files in directory
    current_files = os.listdir(dest_folder)
    return jsonify({"success": True, "files": current_files})

@app.route('/api/clear_generic', methods=['POST'])
def clear_generic():
    upload_type = request.args.get('type', 'data')
    dest_folder = os.path.join(os.getcwd(), 'uploads', 'Generic', upload_type.capitalize())
    import shutil
    if os.path.exists(dest_folder):
        shutil.rmtree(dest_folder, ignore_errors=True)
    return jsonify({"success": True})

@app.route('/api/folders', methods=['GET'])
def get_folders():
    """Endpoint to fetch directory structures for frontend browser tree."""
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
    """Endpoint to save the user-selected runs into text files."""
    data = request.json
    
    if 'runs' in data:
        with open("SelectedRuns.txt", "w") as f:
            for run in data['runs']:
                if run:
                    f.write(run + "\n")
    
    # Legacy support for Test 3
    if 'runA' in data and 'runB' in data:
        return jsonify({"status": "success"})
        
    return jsonify({"status": "success"})


@app.route('/api/choose_file', methods=['GET'])
def choose_file():
    """Endpoint to open an OS-level file chooser dialog (Tkinter)."""
    try:
        import sys
        import subprocess
        
        file_path = ""
        if sys.platform == 'darwin':
            # macOS native file picker using AppleScript
            script = 'tell app "System Events" to activate\ntell app "System Events" to return POSIX path of (choose file with prompt "Select Average Data File:")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            file_path = result.stdout.strip()
        elif sys.platform == 'win32':
            # Windows native file picker using PowerShell
            script = """
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object System.Windows.Forms.OpenFileDialog
$f.Title = "Select File"
if ($f.ShowDialog() -eq 'OK') {
    Write-Output $f.FileName
}
"""
            result = subprocess.run(['powershell', '-NoProfile', '-Command', script], capture_output=True, text=True)
            file_path = result.stdout.strip()
        else:
            # Fallback for Linux
            script = """
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
file_path = filedialog.askopenfilename(title="Select File")
root.destroy()
print(file_path)
"""
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=env)
            file_path = result.stdout.strip()

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                hint = " (tkinter is not installed on this server — type the file path in manually instead)" if "tkinter" in stderr.lower() else ""
                return jsonify({"success": False, "error": f"File browser failed to launch{hint}: {stderr.splitlines()[-1] if stderr else 'unknown error'}"})

        if file_path:
            return jsonify({"success": True, "path": file_path})
        else:
            return jsonify({"success": False, "error": "No file selected"})

    except Exception as e:
        print("Error in choose_file:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/choose_directory', methods=['GET'])
def choose_directory():
    """Endpoint to open an OS-level directory chooser dialog (Tkinter)."""
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
            # macOS / Linux fallback
            if sys.platform == 'darwin':
                script = 'tell app "System Events" to activate\ntell app "System Events" to return POSIX path of (choose folder with prompt "Select Base Path")'
                result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                folder_path = result.stdout.strip()
            else:
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
    """Endpoint to trigger the backend Python plotting scripts based on test type."""
    params = request.json or {}
    test = request.args.get('testType', type=int)
    if test is None:
        test = params.get('testType')
        if test is not None:
            test = int(test)
            
    import tempfile
    import shutil
    import math
    from datetime import datetime
    import plot_generator

    def sanitize_for_json(obj):
        if isinstance(obj, list):
            return [sanitize_for_json(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        return obj

    temp_out_dir = tempfile.mkdtemp(prefix="npd_plots_")
    params['folder_path'] = temp_out_dir
    params['outputFolder'] = temp_out_dir
    params['testType'] = test
    
    # Gather paths based on the test type for backward compatibility with existing text file logic
    if test == 1:
        if not params.get('runs'):
            runs = []
            if os.path.exists("SelectedRuns.txt"):
                with open("SelectedRuns.txt", "r") as f:
                    runs = [line.strip() for line in f if line.strip()]
            else:
                run_a = read_txt("RunA_Path.txt")
                run_b = read_txt("RunB_Path.txt")
                runs = [run for run in [run_a, run_b] if run]
            params['runs'] = runs

    elif test == 2:
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        params['runs'] = [path] if path else []
        
        # Auto-extract SN and Area if missing
        bench_dir = params.get('benchPath') or path
        if bench_dir and os.path.isdir(bench_dir):
            import re
            sn_pattern = re.compile(r'(?:SN|EM-)[_-]?(\d+)', re.IGNORECASE)
            area_pattern = re.compile(r'Area[_-]?(\d+)', re.IGNORECASE)
            for root, dirs, files in os.walk(bench_dir):
                for f in files:
                    if not params.get('serial_number'):
                        m = sn_pattern.search(f)
                        if m: params['serial_number'] = m.group(0)
                    if not params.get('pmaArea'):
                        m = area_pattern.search(f)
                        if m: params['pmaArea'] = f"Area{m.group(1)}"
                if params.get('serial_number') and params.get('pmaArea'):
                    break
        
        if not params.get('serial_number'):
            params['serial_number'] = read_txt("serialNumber.txt")
        if not params.get('pmaArea'):
            params['pmaArea'] = params.get('pma', read_txt("PMA_Area.txt"))
        if not params.get('lmo'):
            params['lmo'] = read_txt("LMO_Number.txt") or read_txt("lmoNumber.txt")

    elif test == 3:
        if not params.get('runs'):
            run_a = read_txt("RunA_Path.txt")
            run_b = read_txt("RunB_Path.txt")
            params['runs'] = [run for run in [run_a, run_b] if run]
            
        # Auto-extract SN and Area if missing
        if params.get('runs') and len(params.get('runs')) > 0:
            run_dir = params.get('runs')[0]
            if run_dir and os.path.isdir(run_dir):
                import re
                sn_pattern = re.compile(r'(?:SN|EM-)[_-]?(\d+)', re.IGNORECASE)
                area_pattern = re.compile(r'Area[_-]?(\d+)', re.IGNORECASE)
                for root, dirs, files in os.walk(run_dir):
                    for f in files:
                        if not params.get('serial_number'):
                            m = sn_pattern.search(f)
                            if m: params['serial_number'] = m.group(0)
                        if not params.get('pmaArea'):
                            m = area_pattern.search(f)
                            if m: params['pmaArea'] = f"Area{m.group(1)}"
                    if params.get('serial_number') and params.get('pmaArea'):
                        break
                        
        if not params.get('serial_number'):
            params['serial_number'] = read_txt("serialNumber.txt")
        
        cal_path = read_txt("Cal_Path.txt")
        if cal_path and not params.get('calFolder'):
            params['calFolder'] = cal_path

    elif test == 4:
        path = params.get('dataSource')
        if not path:
            path = read_txt("upload_path.txt") or read_txt("path.txt")
        params['runs'] = [path] if path else []

    try:
        if test == 5:
            data_folder = os.path.join(os.getcwd(), 'uploads', 'Generic', 'Data')
            cal_folder = os.path.join(os.getcwd(), 'uploads', 'Generic', 'Cal')
            # Extract generic plot params
            freq_min = float(params.get('freq_min')) if params.get('freq_min') not in [None, ""] else None
            freq_max = float(params.get('freq_max')) if params.get('freq_max') not in [None, ""] else None
            n_avg = int(params.get('n_avg', 1)) if params.get('n_avg') not in [None, ""] else 1
            plot_s12 = bool(params.get('plot_s12', False))
            plot_density = bool(params.get('plot_density', False))
            average_data_path = params.get('average_data_path', '')
            
            csv_plots, s21_plots, vswr_plots = plot_generator.plotGeneric(
                data_folder, cal_folder, temp_out_dir,
                freq_min=freq_min, freq_max=freq_max, n_avg=n_avg, plot_s12=plot_s12,
                plot_density=plot_density, average_data_path=average_data_path,
                u_bound_npd=params.get('u_bound_npd'), l_bound_npd=params.get('l_bound_npd'),
                u_bound_s21=params.get('u_bound_s21'), l_bound_s21=params.get('l_bound_s21')
            )
            shutil.rmtree(temp_out_dir, ignore_errors=True)
            return jsonify({
                "success": True, 
                "plots_csv": sanitize_for_json(csv_plots), 
                "plots_s21": sanitize_for_json(s21_plots),
                "plots_vswr": sanitize_for_json(vswr_plots),
                "warnings": plot_generator.get_warnings()
            })
            
        else:
            # Generate plots returns a list of dicts: [{'path': str, 'status': str}]
            generated_data = plot_generator.generate_plots(params)
    except Exception as e:
        import traceback
        traceback.print_exc()
        with open("debug_log.txt", "a") as f_dbg:
            f_dbg.write(f"EXCEPTION in generate_plots: {e}\n")
            f_dbg.write(traceback.format_exc() + "\n")
        return jsonify({"success": False, "error": str(e)}), 500

    results = []
    if generated_data:
        for item in generated_data:
            if item:
                results.append(item)
                    
    shutil.rmtree(temp_out_dir, ignore_errors=True)
    return jsonify({"success": True, "plots_data": sanitize_for_json(results), "warnings": plot_generator.get_warnings()})

@app.route('/api/save_plots', methods=['POST'])
def save_plots():
    """Endpoint to copy generated plots to a selected destination directory."""
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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
