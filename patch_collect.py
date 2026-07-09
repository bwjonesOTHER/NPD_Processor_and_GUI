with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_func = """    def _collect_files(runs_list, suffix, ext=None):
        runs_data = []
        for run in runs_list:
            lmo = os.path.join(folder_path, run)
            files = math_v3.search_files(lmo, suffix)
            if ext:
                files = [f for f in files if f.lower().endswith(ext.lower())]
            gains = math_v3.search_files(lmo, 'Gain')
            if files:
                runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
        return runs_data"""

new_func = """    def _collect_files(runs_list, suffix, ext=None):
        runs_data = []
        for run in runs_list:
            lmo = os.path.join(folder_path, run)
            files = math_v3.search_files(lmo, f"*{suffix}*")
            if ext:
                files = [f for f in files if f.lower().endswith(ext.lower())]
            gains = math_v3.search_files(lmo, '*Gain*')
            if files:
                runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
        return runs_data"""

content = content.replace(old_func, new_func)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
