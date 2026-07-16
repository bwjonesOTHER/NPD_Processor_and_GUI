import re
import sys

with open('backend/app.py', 'r') as f:
    content = f.read()

# Replace choose_file
new_choose_file = """@app.route('/api/choose_file', methods=['GET'])
def choose_file():
    \"\"\"Endpoint to open an OS-level file chooser dialog.\"\"\"
    try:
        import sys
        import subprocess
        
        file_path = ""
        if sys.platform == 'darwin':
            script = 'tell app "System Events" to activate\\ntell app "System Events" to return POSIX path of (choose file with prompt "Select File:")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            file_path = result.stdout.strip()
        else:
            script = \"\"\"
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
file_path = filedialog.askopenfilename(title="Select File")
root.destroy()
print(file_path)
\"\"\"
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=env)
            file_path = result.stdout.strip()
            
        if file_path:
            return jsonify({"success": True, "path": file_path})
        else:
            return jsonify({"success": False, "error": "No file selected"})
            
    except Exception as e:
        print("Error in choose_file:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
"""

content = re.sub(r"@app\.route\('/api/choose_file'.*?(?=@app\.route\('/api/choose_directory')", new_choose_file + "\n", content, flags=re.DOTALL)

# Replace choose_directory macOS fallback
content = re.sub(
    r"macOS / Linux fallback using tkinter in subprocess.*?result = subprocess\.run\(\[sys\.executable, '-c', script\], capture_output=True, text=True, env=env\)",
    r"""macOS / Linux fallback
        if sys.platform == 'darwin':
            script = 'tell app "System Events" to activate\\ntell app "System Events" to return POSIX path of (choose folder with prompt "Select Directory:")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            folder_path = result.stdout.strip()
        else:
            script = \"\"\"
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
folder_path = filedialog.askdirectory(title="Select Directory")
root.destroy()
print(folder_path)
\"\"\"
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=env)""",
    content,
    flags=re.DOTALL
)


with open('backend/app.py', 'w') as f:
    f.write(content)

