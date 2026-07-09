import matplotlib
matplotlib.use('Agg')
import os
import glob
import numpy as np
from pathlib import Path
import NPD_GT_functions
import math_v3

def generate_plots(params):
    runs = params.get('runs', [])
    folder_path = params.get('folder_path')
    
    if not runs or not folder_path:
        raise ValueError("At least one run and folder_path are required.")

    freq_min = float(params.get('freq_min', 2.6))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Val = float(params.get('reqS11Val', -10))
    reqS21Val = float(params.get('reqS21Val', 10))
    
    n_avg = int(params.get('n_avg', 20))
    show_plot = 0
    
    u_bound_s21 = float(params.get('u_bound_s21', 1.0))
    l_bound_s21 = float(params.get('l_bound_s21', 1.0))
    u_bound_npd = float(params.get('u_bound_npd', 1.0))
    l_bound_npd = float(params.get('l_bound_npd', 1.0))

    import fnmatch
    for file in os.listdir(folder_path):
        if fnmatch.fnmatch(file, '*.png'):
            try: os.remove(os.path.join(folder_path, file))
            except: pass

    def _collect_files(runs_list, pattern, ext=None):
        runs_data = []
        with open("debug_log.txt", "a") as f_dbg:
            f_dbg.write(f"\n--- _collect_files called with pattern: {pattern} ---\n")
            f_dbg.write(f"runs_list: {runs_list}\n")
            for run in runs_list:
                lmo = os.path.join(folder_path, run)
                f_dbg.write(f"lmo: {lmo}\n")
                files = math_v3.search_files(lmo, pattern)
                f_dbg.write(f"Found {len(files)} files before ext filter.\n")
                if ext:
                    files = [f for f in files if f.lower().endswith(ext.lower())]
                gains = math_v3.search_files(lmo, '*Gain*')
                if files:
                    runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
                    f_dbg.write(f"Added run {run} with {len(files)} files.\n")
                else:
                    f_dbg.write(f"Run {run} had 0 files after filtering.\n")
        return runs_data

    # === Collect Data ===
    # V2 Logic: Collect ALL traces across all runs and plot them together
    npdd_all = _collect_files(runs, '*NPDOverTempNPD*.csv')
    spar_all = _collect_files(runs, '*VSWR*', '.s2p')

    # === Process Math & Render ===

    def process_and_render_npd(data, temp, is_density, ub_offset, lb_offset):
        if not data: return None
        math_data = math_v3.process_NPD(data, n_avg, is_density=is_density)
        suffix = 'Density' if is_density else 'Power'
        NPD_GT_functions.render_NPD_plot(math_data, ub_offset, lb_offset, temp, f"Noise {suffix}", freq_min, freq_max, reqS11Val, folder_path, show_plot)
        return math_data

    # NP Power (V2 Plotting Logic)
    process_and_render_npd(npdd_all, 'Before and After', False, u_bound_npd, l_bound_npd)

    def process_and_render_s21(data, temp, ub_offset, lb_offset):
        if not data: return None
        math_data = math_v3.process_S21(data)
        NPD_GT_functions.render_S21_plot(math_data, temp, "Test Hat S21", freq_min, freq_max, folder_path, show_plot)
        return math_data

    # S21 (V2 Plotting Logic)
    process_and_render_s21(spar_all, 'Before and After', u_bound_s21, l_bound_s21)
    png_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if fnmatch.fnmatch(f, '*.png')]
    return png_files

