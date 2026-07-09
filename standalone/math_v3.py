import os
import re
import numpy as np
import pandas as pd
import skrf as rf
import fnmatch
import os

import fnmatch

def search_files(root_dir, pattern):
    matched_files = []
    pattern_lower = pattern.lower()
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if fnmatch.fnmatch(file.lower(), pattern_lower):
                matched_files.append(os.path.join(dirpath, file))
    return matched_files

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

def extract_pri_red(filename):
    if 'Pri' in filename:
        return 'PRI'
    else:
        return 'RED'

def cap_search(filename, lmoFolder):
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06"]:
        if f"Cap_{n}" in filename:
            cap_num = n
            break
    if cap_num is None:
        return None, None
    loss_path = os.path.join(lmoFolder, f"Cap_{cap_num}")
    base = search_files(loss_path, "*Base*")
    bulk = search_files(loss_path, "*Bulkhead*")
    return base[0] if base else None, bulk[0] if bulk else None

def load_specA(folder):
    files = search_files(folder, "*SpecA*")
    if not files:
        return None
    try:
        return rf.Network(files[0]).s_db[:, 1, 0]
    except:
        return None

def process_file_math(file, folder, specA_s21, n_avg, is_density=False):
    df = pd.read_csv(file)
    num = df.apply(pd.to_numeric, errors="coerce")

    freq_ghz = remove_nan(num.values[:, 0], remove_infinite=True)
    noise_pow = remove_nan(num.values[:, 2 if is_density else 1], remove_infinite=True)

    # Make sure freq and noise are same length right away to avoid any row misalignments
    min_len = min(len(freq_ghz), len(noise_pow))
    freq_ghz = freq_ghz[:min_len]
    noise_pow = noise_pow[:min_len]

    base_loss, bulk_loss = cap_search(file, folder)
    cable_s21 = rf.Network(base_loss).s_db[:, 1, 0] if base_loss else 0
    bulk_s21 = rf.Network(bulk_loss).s_db[:, 1, 0] if bulk_loss else 0
    spec_s21 = specA_s21 if isinstance(specA_s21, np.ndarray) else 0

    # Fallback to safely interpolate cable/bulk/spec if their sizes don't match noise_pow exactly before smoothing
    if isinstance(cable_s21, np.ndarray) and len(cable_s21) != len(noise_pow):
        cable_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(cable_s21)), cable_s21)
    if isinstance(bulk_s21, np.ndarray) and len(bulk_s21) != len(noise_pow):
        bulk_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(bulk_s21)), bulk_s21)
    if isinstance(spec_s21, np.ndarray) and len(spec_s21) != len(noise_pow):
        spec_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(spec_s21)), spec_s21)

    # Smoothing (exactly as in V3)
    if n_avg > 1:
        noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode="valid")
        freq_ghz = freq_ghz[int(n_avg / 2):int(1 - n_avg / 2)]

        if isinstance(cable_s21, np.ndarray):
            cable_s21 = np.convolve(cable_s21, np.ones(n_avg) / n_avg, mode="valid")
        if isinstance(bulk_s21, np.ndarray):
            bulk_s21 = np.convolve(bulk_s21, np.ones(n_avg) / n_avg, mode="valid")
        if isinstance(spec_s21, np.ndarray):
            spec_s21 = np.convolve(spec_s21, np.ones(n_avg) / n_avg, mode="valid")
            
        # Re-ensure lengths match in case n_avg was even, which causes mode="valid" length mismatches
        min_len = min(len(freq_ghz), len(noise_pow))
        freq_ghz = freq_ghz[:min_len]
        noise_pow = noise_pow[:min_len]
        if isinstance(cable_s21, np.ndarray): cable_s21 = cable_s21[:min_len]
        if isinstance(bulk_s21, np.ndarray): bulk_s21 = bulk_s21[:min_len]
        if isinstance(spec_s21, np.ndarray): spec_s21 = spec_s21[:min_len]

    noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21
    return freq_ghz, noise_mod

def process_NPD(runs_data, n_avg, is_density=False):
    freq_ref = None
    traces = []
    corrected_curves = []

    for run in runs_data:
        folder = run['folder']
        specA_s21 = load_specA(folder)
        
        for file in run['files']:
            if not os.path.exists(file): continue
            
            freq_ghz, noise_mod = process_file_math(file, folder, specA_s21, n_avg, is_density=is_density)
            
            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                noise_mod = np.interp(freq_ref, freq_ghz, noise_mod)
                
            corrected_curves.append(noise_mod)
            serial = extract_serial(file)
            chain = extract_pri_red(file)
            label = f"{serial[-16:-8]} {chain}"
            # Extract temp from filename
            f_lower = file.lower()
            if 'ambient' in f_lower or '25c' in f_lower:
                label += " (25C)"
            elif 'hot' in f_lower or '64c' in f_lower:
                label += " (64C)"
            elif 'cold' in f_lower or '38c' in f_lower:
                label += " (-38C)"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            traces.append({'label': label, 'y': noise_mod, 'file': file})

    if not corrected_curves:
        return None

    corrected_curves = np.array(corrected_curves)
    avg_trace = np.mean(corrected_curves, axis=0)
    
    return {
        'freq_ref': freq_ref,
        'traces': traces,
        'avg_trace': avg_trace,
    }

def process_S21(runs_data):
    freq_ref = None
    traces = []
    corrected_curves = []

    for run in runs_data:
        for file in run['files']:
            if not os.path.exists(file): continue

            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            s21 = net.s_db[:, 1, 0]

            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                s21 = np.interp(freq_ref, freq_ghz, s21)

            corrected_curves.append(s21)
            serial = extract_serial(file)
            chain = extract_pri_red(file)
            label = f"{serial[-16:-8]} {chain}"
            # Extract temp from filename
            f_lower = file.lower()
            if 'ambient' in f_lower or '25c' in f_lower:
                label += " (25C)"
            elif 'hot' in f_lower or '64c' in f_lower:
                label += " (64C)"
            elif 'cold' in f_lower or '38c' in f_lower:
                label += " (-38C)"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            traces.append({'label': label, 'y': s21, 'file': file})

    if not corrected_curves:
        return None

    corrected_curves = np.array(corrected_curves)
    avg_trace = np.mean(corrected_curves, axis=0)

    return {
        'freq_ref': freq_ref,
        'traces': traces,
        'avg_trace': avg_trace,
    }

