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

def search_files(root_dir, filename_part):
    matches = []
    if not root_dir or not os.path.isdir(root_dir):
        return matches
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if filename_part.lower() in file.lower():
                matches.append(os.path.join(dirpath, file))
    return matches

def load_calibration_loss(cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        return None, None
    cal_files = []
    for root, _, files in os.walk(cal_folder):
        for f in files:
            name = f.lower()
            if ("pathloss_base" in name or "pathloss_cap" in name or "specan_none" in name or "specanbase" in name or "specan_base" in name) and name.endswith(".s2p"):
                cal_files.append(os.path.join(root, f))
    if not cal_files:
        return None, None

    freq_list = []
    loss_list = []
    for f in cal_files:
        net = rf.Network(f)
        freq_ghz = net.f / 1e9
        loss_db = -net.s_db[:, 1, 0]
        freq_list.append(freq_ghz)
        loss_list.append(loss_db)
    
    freq_ref = freq_list[0]
    total_loss = np.zeros_like(freq_ref)
    for fr, ls in zip(freq_list, loss_list):
        ls_interp = np.interp(freq_ref, fr, ls)
        total_loss += ls_interp
    return freq_ref, total_loss

def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder):
    all_files = filesA + filesB
    if not all_files:
        return None

    plt.figure(figsize=(8, 4), dpi=150)
    all_noise = []
    all_noise_win = []
    all_labels = []
    all_freqs = []

    def load_np_data(file):
        df_all = pd.read_csv(file, on_bad_lines='skip', encoding='latin1', engine='python')
        num_df = df_all.apply(pd.to_numeric, errors='coerce')
        freq = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if n_avg > 1:
            noise = np.convolve(noise, np.ones(n_avg) / n_avg, mode='valid')
            freq = freq[int(n_avg / 2):int(1 - n_avg / 2):1]
        return freq, noise

    for file in all_files:
        serial = extract_serial(file)
        freq, noise = load_np_data(file)
        if len(freq) == 0:
            continue
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
    ref_freq_full = all_freqs[0]
    
    start_idx = np.searchsorted(ref_freq_full, freq_min)
    end_idx = np.searchsorted(ref_freq_full, freq_max)
    if start_idx != end_idx:
        ref_freq_win = ref_freq_full[start_idx:end_idx]
    else:
        ref_freq_win = ref_freq_full
    
    status = "Passed"
    if len(all_noise_win) > 0:
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
    title = f'Noise Power {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NP (dBm)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.subplots_adjust(right=0.7)

    filename_safe_title = title.replace(" ", "_").replace(":", "").replace(",", "") + ".png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return {"path": save_path, "status": status.lower()}

def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder):
    all_files = filesA + filesB
    if not all_files:
        return None

    avg_collection = []
    file_coll = []
    plt.figure(figsize=(7, 4), dpi=150)
    
    ref_freq_ghz = None
    for file in all_files:
        net = rf.Network(file)
        freq_ghz = net.f / 1e9
        raw_s21 = net.s_db[:, 1, 0]
        serial = extract_serial(file)

        if freq_cal is not None:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_corr = raw_s21 - loss_interp
        else:
            s21_corr = raw_s21

        plt.plot(freq_ghz, s21_corr, label=f'{serial[-21:-4:1]}')
        
        start_idx = np.searchsorted(freq_ghz, freq_min)
        end_idx = np.searchsorted(freq_ghz, freq_max)
        
        if start_idx != end_idx:
            s21_window = s21_corr[start_idx:end_idx]
            if ref_freq_ghz is None:
                ref_freq_ghz = freq_ghz
                ref_freq_win = freq_ghz[start_idx:end_idx]
        else:
            s21_window = s21_corr
            if ref_freq_ghz is None:
                ref_freq_ghz = freq_ghz
                ref_freq_win = freq_ghz
            
        avg_collection.append(s21_window)
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
    title = f'S21 Calibrated {title_suffix}, {status}'
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
    return {"path": save_path, "status": status.lower()}

def generate_plots(params):
    runs = params.get('runs', [])
    test_type = params.get('testType', 1)
    
    # Process runs to actual directories
    resolved_runs = []
    for run in runs:
        if run and os.path.isdir(run):
            resolved_runs.append(run)
    
    folderA = resolved_runs[0] if len(resolved_runs) > 0 else ""
    folderB = resolved_runs[1] if len(resolved_runs) > 1 else ""

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
    if os.path.exists("Cal_Path.txt"):
        with open("Cal_Path.txt", "r") as f:
            cal_folder = f.read().strip()
    if not cal_folder and folderA:
        cal_folder = os.path.join(os.path.dirname(folderA), "Cable Loss")
    freq_cal, total_loss_db = load_calibration_loss(cal_folder)
    
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
        
        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)
            if p1: generated_plots.append(p1)
                
            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder)
            if p2: generated_plots.append(p2)
            
    else:
        # Benchtop (Test 2 & 3)
        npdA = search_files(folderA, "NPD")
        npdB = search_files(folderB, "NPD")
        sparA = search_files(folderA, ".s2p")
        sparB = search_files(folderB, ".s2p")
        
        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)
        if p1: generated_plots.append(p1)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder)
        if p2: generated_plots.append(p2)

    return generated_plots
