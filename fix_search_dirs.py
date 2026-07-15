content = open('backend/plot_generator.py', 'r').read()

old_search_dirs = """    search_dirs = []
    if cal_folder and os.path.isdir(cal_folder):
        search_dirs.append(cal_folder)
        
    run_folder = os.path.dirname(filepath)
    if run_folder and os.path.isdir(run_folder):
        search_dirs.append(run_folder)"""

new_search_dirs = """    search_dirs = []
    if cal_folder and os.path.isdir(cal_folder):
        search_dirs.append(cal_folder)
        
    run_folder = os.path.dirname(filepath)
    if run_folder and os.path.isdir(run_folder):
        search_dirs.append(run_folder)
        
    parent_run_folder = os.path.dirname(run_folder)
    if parent_run_folder and os.path.isdir(parent_run_folder):
        search_dirs.append(parent_run_folder)"""

content = content.replace(old_search_dirs, new_search_dirs)
open('backend/plot_generator.py', 'w').write(content)
