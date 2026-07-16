"""
plot_generator.py
=================
Centralized plot generation script for Tests 1, 2, and 3.
Utilizes the modernized plotting logic to generate S-Parameter and NPD plots,
applies calibration losses, computes Pass/Fail status, and returns a list of
plot data dictionaries back to the Flask backend.
"""

import os
import re
import skrf as rf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
import glob

def remove_nan(arr, remove_infinite=False):
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a NumPy array.")
    if remove_infinite:
        mask = np.isfinite(arr)
    else:
        mask = ~np.isnan(arr)
    return arr[mask]

def extract_serial(filename):
    match = re.search(r'EM-\d+', filename)
    return match.group(0) if match else filename

def search_files(root_dir, filename_part, serial_number=None):
    matches = []
    if not root_dir or not os.path.isdir(root_dir):
        return matches
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if filename_part.lower() in file.lower():
                if serial_number:
                    import re
                    sn_clean = re.sub(r'^[SsnN0]+', '', serial_number)
                    if not sn_clean: sn_clean = serial_number
                    # Negative lookbehind for digit, optional SN/EM- prefix, optional leading zeros, exact SN, negative lookahead for digit
                    pattern = r'(?<!\d)(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
                    if not re.search(pattern, file, re.IGNORECASE):
                        continue
                matches.append(os.path.join(dirpath, file))
    return matches

def find_cal_file(folders, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    try:
        cap_num_int = int(cap_num)
    except (ValueError, TypeError):
        return None
        
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if not file.lower().endswith('.s2p'):
                    continue
                if cal_type_lower in file.lower():
                    # Extract number after SN
                    match = re.search(r'sn0*(\d+)', file.lower())
                    sn_match = False
                    if match:
                        if int(match.group(1)) == cap_num_int:
                            sn_match = True
                            
                    # Check path for cap folder
                    path_lower = os.path.join(root, file).lower()
                    folder_match = False
                    if f"cap_0{cap_num_int}" in path_lower or f"cap_{cap_num_int}" in path_lower:
                        folder_match = True
                        
                    if sn_match or folder_match:
                        return os.path.join(root, file)
                    
    return None

def get_calibration_loss(filepath, cal_folder):
    search_dirs = []
    if cal_folder and os.path.isdir(cal_folder):
        search_dirs.append(cal_folder)
        
    run_folder = os.path.dirname(filepath)
    if run_folder and os.path.isdir(run_folder):
        search_dirs.append(run_folder)
        
    parent_run_folder = os.path.dirname(run_folder)
    if parent_run_folder and os.path.isdir(parent_run_folder):
        search_dirs.append(parent_run_folder)
        
    if not search_dirs:
        return None, None
        
    cal_files_to_load = []
    
    # 1. Cap_XX Search (for Test 1)
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        if f"Cap_{n}" in filepath:
            cap_num = n
            break
            
    
    if cap_num is not None:
        base_file = find_cal_file(search_dirs, cap_num, "Base")
        if base_file: cal_files_to_load.append(base_file)
        
        bulkhead_file = find_cal_file(search_dirs, cap_num, "Bulkhead")
        if bulkhead_file: cal_files_to_load.append(bulkhead_file)
        
        # SpecA
        found = False
        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
                for file in files:
                    if 'speca' in file.lower() and file.lower().endswith('.s2p'):
                        cal_files_to_load.append(os.path.join(root, file))
                        found = True
                        break
                if found: break
            if found: break
            
    else:
        # 2. Benchtop Search (Fallback)
        filepath_upper = filepath.upper()
        chain_type = "Pri" if "PRI" in filepath_upper else "Red" if "RED" in filepath_upper else None
        
        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
                for f in files:
                    name = f.lower()
                    if not name.endswith(".s2p"): continue
                    
                    if chain_type == "Pri" and "pathloss_base" in name:
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type == "Red" and "pathloss_cap" in name:
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type is None and "pathloss_base" in name:
                        cal_files_to_load.append(os.path.join(root, f))
                        
                    if "speca" in name:  # Matches specan or speca
                        cal_files_to_load.append(os.path.join(root, f))
                        
                    if chain_type == "Pri" and name.startswith("pri") and "bulkhead" not in name:
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type == "Red" and name.startswith("red") and "bulkhead" not in name:
                        cal_files_to_load.append(os.path.join(root, f))

    if not cal_files_to_load:
        return None, None
        
    freq_ref = None
    total_loss = None
    
    for f in cal_files_to_load:
        try:
            net = rf.Network(f)
            freq_ghz = net.f / 1e9
            loss_db = -net.s_db[:, 1, 0]
            
            
            if freq_ref is None:
                freq_ref = freq_ghz
                total_loss = np.zeros_like(freq_ref)
                
            ls_interp = np.interp(freq_ref, freq_ghz, loss_db)
            total_loss += ls_interp
        except Exception as e:
            pass
            
    return freq_ref, total_loss

def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True, test_type=1):
    all_files = filesA + filesB
    if not all_files:
        return None

    plt.figure(figsize=(8, 4), dpi=150)
    all_noise = []
    all_noise_win = []
    all_labels = []
    all_freqs = []

    def load_np_data(file):
        df_all = pd.read_csv(file, on_bad_lines='skip', encoding='latin1', engine='python', names=range(10))
        num_df = df_all.apply(pd.to_numeric, errors='coerce')
        freq = remove_nan(num_df.values[:, 0], remove_infinite=True)
        if plot_density:
            try:
                noise = remove_nan(num_df.values[:, 2], remove_infinite=True)
            except IndexError:
                noise = np.array([])
        else:
            noise = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if len(noise) == 0 or len(freq) == 0:
            return np.array([]), np.array([])
            
        if apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            is_runA = file in filesA
            should_apply_cal = apply_cal
            # Test 3 Run A is Thermal, do not apply benchtop calibration to it
            if test_type == 3 and is_runA:
                should_apply_cal = False
                
            # Apply Calibration
            if freq_cal is not None and should_apply_cal and test_type == 1:
                loss_interp = np.interp(freq, freq_cal, total_loss_db)
                noise = noise + loss_interp
            
        if n_avg > 1:
            noise = np.convolve(noise, np.ones(n_avg) / n_avg, mode='valid')
            freq = freq[int(n_avg / 2):int(1 - n_avg / 2):1]
        return freq, noise

    ref_freq_full = None
    for file in all_files:
        serial = extract_serial(file)
        freq, noise = load_np_data(file)
        if len(freq) == 0:
            continue
            
        if ref_freq_full is None:
            ref_freq_full = freq
        else:
            if len(freq) != len(ref_freq_full) or not np.allclose(freq, ref_freq_full):
                noise = np.interp(ref_freq_full, freq, noise)
                freq = ref_freq_full

        plt.plot(freq, noise, label=f'{serial[-21:-4:1]}')
        all_freqs.append(freq)
        all_noise.append(noise)
        
        # Window points for Pass/Fail
        start_idx = np.searchsorted(freq, freq_min)
        end_idx = np.searchsorted(freq, freq_max)
        if start_idx == end_idx:
            # If data is out of bounds, use all data just in case
            all_noise_win.append(noise)
        else:
            all_noise_win.append(noise[start_idx:end_idx])
        all_labels.append(serial[-21:-4:1])

    if not all_freqs:
        plt.close()
        return None

    all_noise_win = np.array([x for x in all_noise_win if len(x) > 0])
    
    start_idx = np.searchsorted(ref_freq_full, freq_min)
    end_idx = np.searchsorted(ref_freq_full, freq_max)
    if test_type != 3:
        if start_idx != end_idx:
            ref_freq_win = ref_freq_full[start_idx:end_idx]
        else:
            ref_freq_win = ref_freq_full
    else:
        # We will interpolate in the next step, so we just set ref_freq_win to full here temporarily
        ref_freq_win = ref_freq_full
    
    status = "Passed"
    if len(all_noise_win) > 0 or (test_type == 3 and len(all_noise) > 0):
        if test_type == 3:
            from scipy.interpolate import interp1d
            common_freq = np.linspace(freq_min, freq_max, 1000)
            all_noise_interp = []
            for i in range(len(all_noise)):
                f_interp = interp1d(all_freqs[i], all_noise[i], bounds_error=False, fill_value=np.nan)
                all_noise_interp.append(f_interp(common_freq))
            all_noise_win = np.array(all_noise_interp)
            ref_freq_win = common_freq
            avg = np.nanmean(all_noise_win, axis=0)
        else:
            avg = np.mean(all_noise_win, axis=0)

        # Using requested bounds
        upper = avg + u_bound_npd
        lower = avg - l_bound_npd

        fail_mask = (all_noise_win > upper) | (all_noise_win < lower)
        failed_indices = np.where(fail_mask.any(axis=1))[0]
        if len(failed_indices) > 0:
            status = "Failed"

        if len(ref_freq_win) == len(lower):
            plt.plot(ref_freq_win, lower, color='red', alpha=1, marker='o', markersize=3, markevery=100, label='Lower bound')
            plt.plot(ref_freq_win, upper, color='red', alpha=1, marker='x', markersize=3, markevery=100, label='Upper bound')

    plt.xlim(ref_freq_full[0], ref_freq_full[-1])
    plt.axvline(x=freq_min, color='g')
    plt.axvline(x=freq_max, color='g')
    plt.grid(True)
    if plot_density:
        plt.ylim(-170, -110)
    else:
        plt.ylim(-130, -90)
    
    title = f'Noise Power Density {title_suffix}, {status}' if plot_density else f'Noise Power {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NPD (dBm/Hz)') if plot_density else plt.ylabel('NP (dBm)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.subplots_adjust(right=0.7)

    filename_safe_title = title.replace(" ", "_").replace(":", "").replace(",", "") + ".png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    full_avg = None
    if len(all_noise) > 0:
        min_len = min(len(x) for x in all_noise)
        full_avg = np.mean([x[:min_len] for x in all_noise], axis=0)
        ref_freq_full = ref_freq_full[:min_len]
        
    return {"path": save_path, "status": status.lower(), "freq": ref_freq_full if full_avg is not None else None, "avg": full_avg}


def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=1, apply_cal=True):
    all_files = filesA + filesB
    if not all_files:
        return None

    avg_collection = []
    all_s21_full = []
    file_coll = []
    plt.figure(figsize=(7, 4), dpi=150)
    
    ref_freq_ghz = None
    for fpath in all_files:
        net = rf.Network(fpath)
        freq_ghz = net.f / 1e9
        raw_s21 = net.s_db[:, 1, 0]
        serial = extract_serial(fpath)

        freq_cal, total_loss_db = None, None
        if test_type != 1 and apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(fpath, cal_folder)
        
        is_runA = fpath in filesA
        should_apply_cal = apply_cal
        # Apply cal
        if freq_cal is not None and should_apply_cal and test_type != 2:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_corr = raw_s21 + loss_interp
        else:
            s21_corr = raw_s21

        plt.plot(freq_ghz, s21_corr, label=f'{serial[-21:-4:1]}')
        
        start_idx = np.searchsorted(freq_ghz, freq_min)
        end_idx = np.searchsorted(freq_ghz, freq_max)
        
        if ref_freq_ghz is None:
            ref_freq_ghz = freq_ghz
            
            start_idx = np.searchsorted(ref_freq_ghz, freq_min)
            end_idx = np.searchsorted(ref_freq_ghz, freq_max)
            if start_idx != end_idx:
                ref_freq_win = ref_freq_ghz[start_idx:end_idx]
            else:
                ref_freq_win = ref_freq_ghz
        else:
            if len(freq_ghz) != len(ref_freq_ghz) or not np.allclose(freq_ghz, ref_freq_ghz):
                s21_interp = np.interp(ref_freq_ghz, freq_ghz, s21_corr)
                
        start_idx = np.searchsorted(ref_freq_ghz, freq_min)
        end_idx = np.searchsorted(ref_freq_ghz, freq_max)
        if start_idx != end_idx:
            s21_window = s21_interp[start_idx:end_idx] if "s21_interp" in locals() else s21_corr[start_idx:end_idx]
        else:
            s21_window = s21_corr

        avg_collection.append(s21_window)
        all_s21_full.append(s21_interp if "s21_interp" in locals() else s21_corr)
        file_coll.append(serial[-21:-4:1])

    s21_avg = np.array([x for x in avg_collection if len(x) > 0])
    status = "Passed"
    
    if len(s21_avg) > 0:
        avg = np.mean(s21_avg, axis=0)
        upper_bound = avg + u_bound_s21
        lower_bound = avg - l_bound_s21

        fail_mask = (s21_avg > upper_bound) | (s21_avg < lower_bound)
        failed_indices = np.where(fail_mask.any(axis=1))[0]
        if len(failed_indices) > 0:
            status = "Failed"
            
        if ref_freq_ghz is not None and len(ref_freq_win) == len(lower_bound):
            plt.plot(ref_freq_win, lower_bound, 'ro-', markersize=3, markevery=100, label='Lower bound')
            plt.plot(ref_freq_win, upper_bound, 'rx-', markersize=3, markevery=100, label='Upper bound')

    if ref_freq_ghz is not None:
        plt.xlim(ref_freq_ghz[0], ref_freq_ghz[-1])
    else:
        plt.xlim(freq_min, freq_max)
    plt.axvline(x=freq_min, color='g')
    plt.axvline(x=freq_max, color='g')
    plt.grid(True)
    if (test_type != 1 and test_type != 3) and apply_cal:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'
    else:
        plt.ylim(-40, 40)
        title = f'S21 {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.subplots_adjust(right=0.8)

    filename_safe_title = title.replace(" ", "_").replace(":", "").replace(",", "") + ".png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    full_avg = None
    if len(all_s21_full) > 0:
        min_len = min(len(x) for x in all_s21_full)
        full_avg = np.mean([x[:min_len] for x in all_s21_full], axis=0)
        ref_freq_ghz = ref_freq_ghz[:min_len]
        
    return {"path": save_path, "status": status.lower(), "freq": ref_freq_ghz if full_avg is not None else None, "avg": full_avg}




def plot_temp_deltas(data_dict, title, ylabel, output_folder, ax1_ylim=None, ax2_ylim=None):
    if "Ambient" not in data_dict or "Hot" not in data_dict or "Cold" not in data_dict:
        return None
    
    a_f, a_v = data_dict["Ambient"]
    h_f, h_v = data_dict["Hot"]
    c_f, c_v = data_dict["Cold"]
    
    if a_v is None or h_v is None or c_v is None:
        return None
        
    # Ensure they are same length
    min_len = min(len(a_v), len(h_v), len(c_v))
    a_v, h_v, c_v = a_v[:min_len], h_v[:min_len], c_v[:min_len]
    a_f = a_f[:min_len]

    plt.figure(figsize=(8, 5), dpi=150)
    ax1 = plt.gca()
    
    ax1.plot(a_f, a_v, label='Ambient', color='black', linestyle='solid')
    ax1.plot(a_f, h_v, label='Hot', color='red', linestyle='solid')
    ax1.plot(a_f, c_v, label='Cold', color='blue', linestyle='solid')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel(ylabel)
    ax1.grid(True)
    if ax1_ylim: ax1.set_ylim(ax1_ylim)
    
    ax2 = ax1.twinx()
    ax2.plot(a_f, np.abs(a_v - h_v), label='|Amb - Hot|', color='orange', linestyle='dashed')
    ax2.plot(a_f, np.abs(a_v - c_v), label='|Amb - Cold|', color='cyan', linestyle='dashed')
    ax2.plot(a_f, np.abs(h_v - c_v), label='|Hot - Cold|', color='purple', linestyle='dashed')
    ax2.set_ylabel('Delta (dB)')
    if ax2_ylim: ax2.set_ylim(ax2_ylim)
    
    # Combined legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center left', bbox_to_anchor=(1.1, 0.5), fontsize='8')
    
    plt.title(f'{title} Temp Deltas, Passed')
    plt.subplots_adjust(right=0.7)
    
    filename_safe_title = f"{title.replace(' ', '_')}_Temp_Deltas.png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {"path": save_path, "status": "passed"}

def generate_plots(params):
    runs = params.get('runs', [])
    test_type = params.get('testType', 1)
    
    # Process runs to actual directories
    resolved_runs = []
    for run in runs:
        if run and os.path.isdir(run):
            resolved_runs.append(run)
    
    folderA = resolved_runs[0] if len(resolved_runs) > 0 else ""
    folderB = resolved_runs[1] if len(resolved_runs) > 1 else folderA

    freq_min = float(params.get('freq_min', 2.7))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Val = float(params.get('reqS11Val', -10))
    n_avg = int(params.get('n_avg', 20))
    u_bound_s21 = float(params.get('u_bound_s21', 2))
    l_bound_s21 = float(params.get('l_bound_s21', 2))
    u_bound_npd = float(params.get('u_bound_npd', 2))
    l_bound_npd = float(params.get('l_bound_npd', 2))
    output_folder = params.get('outputFolder', '/tmp')

    # Figure out calibration folder (look in parent directory)
    cal_folder = ""
    if len(runs) > 2 and runs[2]:
        cal_folder = runs[2]
    elif os.path.exists("Cal_Path.txt"):
        with open("Cal_Path.txt", "r") as f:
            cal_folder = f.read().strip()
    if not cal_folder and folderA:
        cal_folder = os.path.join(os.path.dirname(folderA), "Cable Loss")
    
    generated_plots = []

    # File searches based on test type
    if test_type == 1:
        # Thermal
        temp_tags = [
            ("Ambient", "_ambient"),
            ("Hot", "_hot"),
            ("Cold", "_cold"),
            ("All Temps", "")
        ]
        
        np_averages = {}
        npd_averages = {}
        s21_averages = {}
        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True)
            if p1: 
                generated_plots.append(p1)
                np_averages[name] = (p1.get("freq"), p1.get("avg"))
                
            p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True, apply_cal=True)
            if p1_den and p1_den.get("freq") is not None:
                generated_plots.append(p1_den)
                npd_averages[name] = (p1_den.get("freq"), p1_den.get("avg"))
                
            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, apply_cal=True)
            if p2: 
                generated_plots.append(p2)
                s21_averages[name] = (p2.get("freq"), p2.get("avg"))
                
        dp1 = plot_temp_deltas(np_averages, "Noise Power", "NP (dBm)", output_folder, ax1_ylim=(-130, -90), ax2_ylim=(0, 5))
        if dp1: generated_plots.append(dp1)
        dp1_den = plot_temp_deltas(npd_averages, "Noise Power Density", "NPD (dBm/Hz)", output_folder, ax1_ylim=(-170, -110), ax2_ylim=(0, 5))
        if dp1_den: generated_plots.append(dp1_den)
        dp2 = plot_temp_deltas(s21_averages, "S21", "S21 (dB)", output_folder, ax1_ylim=(-40, 40), ax2_ylim=(0, 30))
        if dp2: generated_plots.append(dp2)
            
    else:
        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        search_dirA = folderA
        search_dirB = folderB
        
        pma = None
        lmo = None
        if test_type == 2:
            pma = params.get('pma')
            
            def get_subfolder(base_d, target_name):
                if not os.path.exists(base_d): return None
                for d in os.listdir(base_d):
                    if os.path.isdir(os.path.join(base_d, d)) and target_name.lower() in d.lower().replace("_", ""):
                        return os.path.join(base_d, d)
                return None
                
            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                import re
                pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma_area).lower()
                for d in os.listdir(base_d):
                    if not os.path.isdir(os.path.join(base_d, d)): continue
                    d_norm = re.sub(r'[^a-zA-Z0-9]', '', d).lower()
                    match = pma_norm in d_norm
                    if not match and pma_norm:
                        last_char = pma_norm[-1]
                        if last_char.isalpha():
                            if f"area{last_char}" in d_norm:
                                match = True
                    if match:
                        return os.path.join(base_d, d)
                # If a specific PMA Area was requested but we couldn't find its folder, 
                # log what we actually saw so we can debug this!
                try:
                    with open("debug_log.txt", "a") as dbg:
                        dbg.write(f"\n--- DEBUG ---\n")
                        dbg.write(f"Failed to find PMA Area!\n")
                        dbg.write(f"pma_area: {pma_area}\n")
                        dbg.write(f"pma_norm: {pma_norm}\n")
                        dbg.write(f"base_d: {base_d}\n")
                        dbg.write(f"Directories in base_d: {os.listdir(base_d)}\n")
                except:
                    pass
                # just return the base directory (e.g. OverTemp might not have Area subfolders)
                return base_d
            
            lmo = params.get('lmo')
            
            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                if pma:
                    pma_folder = get_pma_folder(search_dirB, pma)
                    if pma_folder: search_dirB = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirB, lmo)
                    if lmo_folder: search_dirB = lmo_folder
            
            try:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"\n--- DRILLER DEBUG ---\n")
                    f_dbg.write(f"pma input: {pma}\n")
                    f_dbg.write(f"lmo input: {lmo}\n")
                    f_dbg.write(f"bench root: {bench}\n")
                    f_dbg.write(f"search_dirB final: {search_dirB}\n")
            except: pass
                
            temp = get_subfolder(folderA, "overtemp")
            if not temp: temp = get_subfolder(folderA, "temp")
            if temp:
                search_dirA = temp
                if pma:
                    pma_folder = get_pma_folder(search_dirA, pma)
                    if pma_folder: search_dirA = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirA, lmo)
                    if lmo_folder: search_dirA = lmo_folder
        
        with open("debug.txt", "a") as f_dbg:
            f_dbg.write(f"\n--- TEST 3 DEBUG ---\n")
            f_dbg.write(f"search_dirA: {search_dirA}\n")
            f_dbg.write(f"search_dirB: {search_dirB}\n")
            f_dbg.write(f"sn: {sn}\n")
            f_dbg.write(f"test_type: {test_type}\n")

        if test_type == 2:
            # S2P Search with fallbacks for Run A
            sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempS", sn)
            
            # NPD Search with fallbacks for Run A
            npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
            if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD_25C", sn)
            if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_ambient", sn)
            if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
        else: # test_type == 3
            sparA = search_files(search_dirA, ".s2p", sn)
            if not sparA and sn: sparA = search_files(search_dirA, ".s2p", "")
            
            npdA = search_files(search_dirA, ".csv", sn)
            if not npdA and sn: npdA = search_files(search_dirA, ".csv", "")
        
        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename
        if pma and search_dirA == temp: # only filter if we didn't successfully drill down into a PMA folder
            pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma).lower()
            
            def file_has_pma(f):
                fname = re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(f)).lower()
                if pma_norm in fname: return True
                # In case of typos in filename (e.g. L11072E instead of L110172E), match last character if the file has E or C
                last_char = pma_norm[-1]
                if last_char.isalpha():
                    # look for AreaE or AreaC in name
                    if f"area{last_char}" in fname: return True
                    # look for L11...E pattern
                    if re.search(rf'l11\d+{last_char}', fname): return True
                return False
                
            sparA = [f for f in sparA if file_has_pma(f)]
            npdA = [f for f in npdA if file_has_pma(f)]
        
        # Run B is usually pure benchtop, just search by extension and SN
        # IMPORTANT: Since folderB is the same root folder, it will accidentally find the NPDoverTemp files again.
        # We must filter out "NPDoverTemp" files from Run B.
        def filter_benchtop(files):
            import os
            # Only check the filename and immediate parent directory, not the entire path which might coincidentally contain 'npdovertemp'
            return [f for f in files if "npdovertemp" not in os.path.basename(f).lower()] if test_type == 2 else files
            
        raw_sparB = search_files(search_dirB, ".s2p", sn)
        if not raw_sparB and sn: raw_sparB = search_files(search_dirB, ".s2p", "")
        sparB_filt = [f for f in raw_sparB if "vswr" in os.path.basename(f).lower()]
        sparB = filter_benchtop(sparB_filt if sparB_filt else raw_sparB)
        
        raw_npdB = search_files(search_dirB, ".csv", sn)
        if not raw_npdB and sn: raw_npdB = search_files(search_dirB, ".csv", "")
        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)
        
        try:
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"\n--- FINAL FILES CHOSEN ---\n")
                f_dbg.write(f"Thermal S2P (sparA): {sparA}\n")
                f_dbg.write(f"Thermal CSV (npdA): {npdA}\n")
                f_dbg.write(f"Benchtop S2P (sparB): {sparB}\n")
                f_dbg.write(f"Benchtop CSV (npdB): {npdB}\n")
        except: pass
        
        with open("debug_test2_output.txt", "w") as f:
            f.write(f"Folder B: {folderB}\n")
            f.write(f"SN: {sn}\n")
            f.write(f"Raw CSV found: {raw_npdB}\n")
            f.write(f"Filtered npdB: {npdB}\n")
            f.write(f"Filtered sparB: {sparB}\n")
            f.write(f"npdA: {npdA}\n")

        
        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True, test_type=test_type)
        if p1: generated_plots.append(p1)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=test_type, apply_cal=True)
        if p2: generated_plots.append(p2)

    return generated_plots
