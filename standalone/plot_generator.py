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
    
    n_avg = int(params.get('n_avg', 51))
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
    npdd_all = _collect_files(runs, '*NPDOverTempNPD*.csv')
    npdd_25C = _collect_files(runs, '*NPDOverTempNPD*ambient*.csv')
    npdd_64C = _collect_files(runs, '*NPDOverTempNPD*hot*.csv')
    npdd_n38C = _collect_files(runs, '*NPDOverTempNPD*cold*.csv')

    spar_all = _collect_files(runs, '*VSWR*', '.s2p')
    spar_25C = _collect_files(runs, '*VSWR*ambient*', '.s2p')
    spar_64C = _collect_files(runs, '*VSWR*hot*', '.s2p')
    spar_n38C = _collect_files(runs, '*VSWR*cold*', '.s2p')

    # === Process Math & Render ===

    def process_and_render_npd(data, temp, is_density, ub_offset, lb_offset):
        if not data: return None
        math_data = math_v3.process_NPD(data, n_avg, is_density=is_density)
        suffix = 'Density' if is_density else 'Power'
        NPD_GT_functions.render_NPD_plot(math_data, ub_offset, lb_offset, temp, f"Noise {suffix}", freq_min, freq_max, reqS11Val, folder_path, show_plot)
        return math_data

    # NPD Density
    process_and_render_npd(npdd_all, 'All', True, u_bound_npd+1, l_bound_npd+1)
    nd25 = process_and_render_npd(npdd_25C, '25C', True, u_bound_npd, l_bound_npd)
    nd64 = process_and_render_npd(npdd_64C, '64C', True, u_bound_npd, l_bound_npd)
    ndn38 = process_and_render_npd(npdd_n38C, '-38C', True, u_bound_npd, l_bound_npd)

    # NP Power
    process_and_render_npd(npdd_all, 'All', False, u_bound_npd+1, l_bound_npd+1)
    np25 = process_and_render_npd(npdd_25C, '25C', False, u_bound_npd, l_bound_npd)
    np64 = process_and_render_npd(npdd_64C, '64C', False, u_bound_npd, l_bound_npd)
    npn38 = process_and_render_npd(npdd_n38C, '-38C', False, u_bound_npd, l_bound_npd)

    def process_and_render_s21(data, temp, ub_offset, lb_offset):
        if not data: return None
        math_data = math_v3.process_S21(data)
        NPD_GT_functions.render_S21_plot(math_data, temp, "Test Hat S21", freq_min, freq_max, folder_path, show_plot)
        return math_data

    # S21
    process_and_render_s21(spar_all, 'All', u_bound_s21+3, l_bound_s21+3)
    sp25 = process_and_render_s21(spar_25C, '25C', u_bound_s21, l_bound_s21)
    sp64 = process_and_render_s21(spar_64C, '64C', u_bound_s21, l_bound_s21)
    spn38 = process_and_render_s21(spar_n38C, '-38C', u_bound_s21, l_bound_s21)

    # Temp Diff function
    def render_temp_diff(d25, d64, dn38, title):
        if d25 and d64 and dn38:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                freq = d25['freq_ref']
                # Interpolate to ensure same shapes
                trace_64 = np.interp(freq, d64['freq_ref'], d64['avg_trace'])
                trace_n38 = np.interp(freq, dn38['freq_ref'], dn38['avg_trace'])
                diff1 = np.abs(d25['avg_trace'] - trace_64)
                diff2 = np.abs(d25['avg_trace'] - trace_n38)
                diff3 = np.abs(trace_64 - trace_n38)

                plt.figure(figsize=(10, 6), dpi=150)
                plt.plot(freq, diff1, label='|25C - 64C|')
                plt.plot(freq, diff2, label='|25C - (-38C)|')
                plt.plot(freq, diff3, label='|64C - (-38C)|')
                plt.xlim(freq[0], freq[-1])
                plt.grid(True)
                plt.title(title)
                plt.xlabel('Frequency (GHz)')
                plt.ylabel('Delta')
                plt.legend()
                
                safe_title = title.replace(" ", "_").replace(":", "") + ".png"
                plt.savefig(os.path.join(folder_path, safe_title), dpi=300)
                plt.close()
            except Exception as e:
                print(f"Error in {title}:", e)

    render_temp_diff(nd25, nd64, ndn38, "NPD Density Temp Delta")
    render_temp_diff(np25, np64, npn38, "Noise Power Temp Delta")
    render_temp_diff(sp25, sp64, spn38, "S21 Temp Delta")

    png_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if fnmatch.fnmatch(f, '*.png')]
    return png_files

