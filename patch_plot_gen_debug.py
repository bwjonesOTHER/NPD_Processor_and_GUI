with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

debug_func = """    def _collect_files(runs_list, pattern, ext=None):
        runs_data = []
        with open("debug_log.txt", "a") as f_dbg:
            f_dbg.write(f"\\n--- _collect_files called with pattern: {pattern} ---\\n")
            f_dbg.write(f"runs_list: {runs_list}\\n")
            for run in runs_list:
                lmo = os.path.join(folder_path, run)
                f_dbg.write(f"lmo: {lmo}\\n")
                files = math_v3.search_files(lmo, pattern)
                f_dbg.write(f"Found {len(files)} files before ext filter.\\n")
                if ext:
                    files = [f for f in files if f.lower().endswith(ext.lower())]
                gains = math_v3.search_files(lmo, '*Gain*')
                if files:
                    runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
                    f_dbg.write(f"Added run {run} with {len(files)} files.\\n")
                else:
                    f_dbg.write(f"Run {run} had 0 files after filtering.\\n")
        return runs_data"""

old_func = """    def _collect_files(runs_list, pattern, ext=None):
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

content = content.replace(old_func, debug_func)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
