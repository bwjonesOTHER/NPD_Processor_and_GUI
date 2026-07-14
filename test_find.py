import os
import subprocess

def search_files_os(root_dir, filename_part):
    matches = []
    if os.name == 'nt':
        # Windows
        cmd = f'dir /b /s "{root_dir}\\*{filename_part}*"'
        try:
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            matches = [line.strip() for line in output.split('\n') if line.strip()]
        except subprocess.CalledProcessError:
            pass # No files found
    else:
        # Mac/Linux
        cmd = f'find "{root_dir}" -type f -name "*{filename_part}*"'
        try:
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            matches = [line.strip() for line in output.split('\n') if line.strip()]
        except subprocess.CalledProcessError:
            pass
    return matches

print(search_files_os(".", ".py"))
