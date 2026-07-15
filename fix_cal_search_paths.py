import re

content = open('backend/plot_generator.py', 'r').read()

old_func_start = """def get_calibration_loss(filepath, cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        print(f"DEBUG: No cal folder provided or not a dir: {cal_folder}")
        return None, None
        
    cal_files_to_load = []"""

new_func_start = """def get_calibration_loss(filepath, cal_folder):
    search_dirs = []
    if cal_folder and os.path.isdir(cal_folder):
        search_dirs.append(cal_folder)
        
    run_folder = os.path.dirname(filepath)
    if run_folder and os.path.isdir(run_folder):
        search_dirs.append(run_folder)
        
    if not search_dirs:
        print(f"DEBUG: No valid search directories found for {filepath}")
        return None, None
        
    cal_files_to_load = []"""
content = content.replace(old_func_start, new_func_start)

# Replace all os.walk(cal_folder) with iterating over search_dirs
old_speca = """        # SpecA
        for root, _, files in os.walk(cal_folder):
            for file in files:
                if 'speca' in file.lower() and file.lower().endswith('.s2p'):
                    cal_files_to_load.append(os.path.join(root, file))
                    break
            else:
                continue
            break"""
new_speca = """        # SpecA
        found = False
        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
                for file in files:
                    if 'speca' in file.lower() and file.lower().endswith('.s2p'):
                        cal_files_to_load.append(os.path.join(root, file))
                        found = True
                        break
                if found: break
            if found: break"""
content = content.replace(old_speca, new_speca)

old_benchtop = """        for root, _, files in os.walk(cal_folder):"""
new_benchtop = """        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):"""
content = content.replace(old_benchtop, new_benchtop)

# Update find_cal_file to take a list of folders
old_find_cal_file = """def find_cal_file(folder, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    try:
        cap_num_int = int(cap_num)
    except (ValueError, TypeError):
        return None
        
    for root, dirs, files in os.walk(folder):"""
new_find_cal_file = """def find_cal_file(folders, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    try:
        cap_num_int = int(cap_num)
    except (ValueError, TypeError):
        return None
        
    for folder in folders:
        for root, dirs, files in os.walk(folder):"""
content = content.replace(old_find_cal_file, new_find_cal_file)

content = content.replace('find_cal_file(cal_folder, cap_num', 'find_cal_file(search_dirs, cap_num')

open('backend/plot_generator.py', 'w').write(content)
