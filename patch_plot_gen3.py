with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Modify _collect_files to take the EXACT pattern rather than wrapping it in asterisks
old_func = """    def _collect_files(runs_list, suffix, ext=None):
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

new_func = """    def _collect_files(runs_list, pattern, ext=None):
        runs_data = []
        for run in runs_list:
            lmo = os.path.join(folder_path, run)
            files = math_v3.search_files(lmo, pattern)
            if ext:
                files = [f for f in files if f.lower().endswith(ext.lower())]
            gains = math_v3.search_files(lmo, '*Gain*')
            if files:
                runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
        return runs_data"""

content = content.replace(old_func, new_func)

# Replace the calls
content = content.replace("_collect_files(runs, 'NPDOverTempNPD', '.csv')", "_collect_files(runs, '*NPDOverTempNPD*.csv')")
content = content.replace("_collect_files(runs, 'NPDOverTempNPD_ambient', '.csv')", "_collect_files(runs, '*NPDOverTempNPD*ambient*.csv')")
content = content.replace("_collect_files(runs, 'NPDOverTempNPD_hot', '.csv')", "_collect_files(runs, '*NPDOverTempNPD*hot*.csv')")
content = content.replace("_collect_files(runs, 'NPDOverTempNPD_cold', '.csv')", "_collect_files(runs, '*NPDOverTempNPD*cold*.csv')")

content = content.replace("_collect_files(runs, 'VSWR', '.s2p')", "_collect_files(runs, '*VSWR*.s2p')")
content = content.replace("_collect_files(runs, 'VSWR_ambient', '.s2p')", "_collect_files(runs, '*VSWR*ambient*.s2p')")
content = content.replace("_collect_files(runs, 'VSWR_hot', '.s2p')", "_collect_files(runs, '*VSWR*hot*.s2p')")
content = content.replace("_collect_files(runs, 'VSWR_cold', '.s2p')", "_collect_files(runs, '*VSWR*cold*.s2p')")

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
