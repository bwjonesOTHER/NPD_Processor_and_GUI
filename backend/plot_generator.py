"""
plot_generator.py
=================
Centralized plot generation script for Tests 1, 2, 3, and 4.
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
                filepath = os.path.join(dirpath, file)
                matches.append(filepath)
                # Force Windows OneDrive to download the file on-demand
                try:
                    with open(filepath, "rb") as f:
                        f.read(1)
                except Exception:
                    pass
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

def get_calibration_loss(filepath, cal_folder, chain_override=None):
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
        if chain_override:
            chain_type = chain_override
        else:
            chain_type = "Pri" if "PRI" in filepath_upper else "Red" if "RED" in filepath_upper else None
        
        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
                for f in files:
                    name = f.lower()
                    if not name.endswith(".s2p"): continue
                    
                    if chain_type == "Pri" and "pathloss_base" in name and not any("pathloss_base" in os.path.basename(p).lower() for p in cal_files_to_load):
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type == "Red" and "pathloss_cap" in name and not any("pathloss_cap" in os.path.basename(p).lower() for p in cal_files_to_load):
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type is None and "pathloss_base" in name and not any("pathloss_base" in os.path.basename(p).lower() for p in cal_files_to_load):
                        cal_files_to_load.append(os.path.join(root, f))
                        
                    if "speca" in name and not any("speca" in os.path.basename(p).lower() for p in cal_files_to_load):  # Matches specan or speca
                        cal_files_to_load.append(os.path.join(root, f))
                        
                    if chain_type == "Pri" and name.startswith("pri") and "bulkhead" not in name and not any(os.path.basename(p).lower().startswith("pri") for p in cal_files_to_load):
                        cal_files_to_load.append(os.path.join(root, f))
                    elif chain_type == "Red" and name.startswith("red") and "bulkhead" not in name and not any(os.path.basename(p).lower().startswith("red") for p in cal_files_to_load):
                        cal_files_to_load.append(os.path.join(root, f))
            if cal_files_to_load:
                cal_files_to_load = list(set(cal_files_to_load))
                break

    debug_path = os.path.expanduser("~/Desktop/debug_cal_loss.txt")
    try:
        with open(debug_path, "a") as f:
            f.write(f"\n--- Cal for {filepath} ---\n")
            f.write(f"cal_folder: {cal_folder}\n")
            f.write(f"search_dirs: {search_dirs}\n")
            f.write(f"cal_files_to_load: {cal_files_to_load}\n")
    except:
        pass

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
            
    try:
        with open("debug_cal_loss.txt", "a") as f:
            f.write(f"\n--- Cal for {filepath} ---\n")
            f.write(f"cal_files_to_load: {cal_files_to_load}\n")
            f.write(f"total_loss_db (mean): {np.mean(total_loss) if total_loss is not None else 'None'}\n")
    except:
        pass

    return freq_ref, total_loss

def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True, test_type=1, average_data_path=""):
    all_files = filesA + filesB
    if not all_files:
        return None

    common_chain = None
    for f in all_files:
        if "PRI" in f.upper():
            common_chain = "Pri"
            break
        elif "RED" in f.upper():
            common_chain = "Red"
            break

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
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder, common_chain)
            is_runA = file in filesA
            should_apply_cal = apply_cal
                
            # Apply Calibration
            if freq_cal is not None and should_apply_cal:
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

        # -- USER UPLOADED AVERAGE OVERRIDE -- #
        if average_data_path and os.path.exists(average_data_path) and (test_type != 1 or title_suffix == "Ambient"):
            try:
                avg_df = pd.read_csv(average_data_path, header=None)
                avg_num_df = avg_df.apply(pd.to_numeric, errors='coerce')
                user_avg_freq = remove_nan(avg_num_df.values[:, 0], remove_infinite=True)
                user_avg_noise = remove_nan(avg_num_df.values[:, 1], remove_infinite=True)
                
                if not plot_density:
                    # Convert NPD (dBm/Hz) to NP (dBm) based on 10 kHz bandwidth (+40 dB)
                    user_avg_noise = user_avg_noise + 40
                    
                # Interpolate the user average onto ref_freq_win to match dimensions for bounds
                from scipy.interpolate import interp1d
                f_avg_interp = interp1d(user_avg_freq, user_avg_noise, bounds_error=False, fill_value=np.nan)
                avg = f_avg_interp(ref_freq_win)
                
                plt.plot(user_avg_freq, user_avg_noise, color='black', linewidth=2.5, linestyle='--', label='User Average')
            except Exception as e:
                print(f"Failed to load user average: {e}")

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

    common_chain = None
    for f in all_files:
        if "PRI" in f.upper():
            common_chain = "Pri"
            break
        elif "RED" in f.upper():
            common_chain = "Red"
            break

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
            freq_cal, total_loss_db = get_calibration_loss(fpath, cal_folder, common_chain)
        
        is_runA = fpath in filesA
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

# ============================================================
# TEST 4: NPD OVER TEMP ARRAY
# Ported from NPD_Over_Temp_Array_Plotter.py. Given a single root folder
# containing Ambient/Cold/Hot measurement folders (each optionally paired
# with a "...2" repeat run) plus a Cable Loss folder of SpecAn/Base/Hat
# S2P calibration files, generates per-temperature Noise Power / Noise
# Power Density / S21 plots and overlay comparisons between the two runs
# at each temperature.
# CSV format (Siglent SSA export): instrument metadata rows, then
# Freq(GHz), Raw Data (dBm at 10 kHz RBW), dBm/Hz.
# ============================================================
_OTA_COLORS = ["blue", "orange", "green", "red", "purple", "cyan", "magenta", "brown", "gold", "black"]
_OTA_NP_YLIM = (-130, -80)
_OTA_NPD_YLIM = (-170, -120)
_OTA_S21_YLIM = (-105, 5)
_OTA_XLIM = (2.0, 5.0)

def _ota_matches(name, keywords):
    lname = name.lower()
    return any(k in lname for k in keywords)

def _ota_resolve_data_root(base_folder, max_descend=3):
    """Skips past wrapper folders (e.g. upload staging dirs) to find the level containing Ambient/Cold/Hot/Cable Loss."""
    current = base_folder
    for _ in range(max_descend):
        if not current or not os.path.isdir(current):
            return current
        try:
            entries = [e for e in os.listdir(current) if os.path.isdir(os.path.join(current, e))]
        except OSError:
            return current
        if any(_ota_matches(e, ("ambient", "cold", "hot", "cable")) for e in entries):
            return current
        if len(entries) == 1:
            current = os.path.join(current, entries[0])
            continue
        return current
    return current

def _ota_find_dir(base, keywords):
    if not base or not os.path.isdir(base):
        return None
    for name in sorted(os.listdir(base)):
        full = os.path.join(base, name)
        if os.path.isdir(full) and _ota_matches(name, keywords):
            return full
    return None

def _ota_find_cal_file(folder, must_include, must_exclude=()):
    if not folder or not os.path.isdir(folder):
        return None
    files = sorted(glob.glob(os.path.join(folder, "*.s2p")) + glob.glob(os.path.join(folder, "*.S2P")))
    for f in files:
        name = os.path.basename(f).lower()
        if all(tok in name for tok in must_include) and not any(tok in name for tok in must_exclude):
            return f
    return None

def _ota_get_files(folder, ext, limit=2):
    if not folder or not os.path.isdir(folder):
        return []
    raw = glob.glob(os.path.join(folder, f"*{ext}")) + glob.glob(os.path.join(folder, f"*{ext.upper()}"))
    # De-dupe: on case-insensitive filesystems (Windows), "*.csv" and "*.CSV"
    # both match the same file, so combining the two globs returns it twice.
    seen = set()
    files = []
    for f in sorted(raw):
        key = os.path.normcase(os.path.abspath(f))
        if key not in seen:
            seen.add(key)
            files.append(f)

    # Prefer one Pri file + one Red file (the two redundant chains) over
    # picking the first two matches, which could both land on the same chain.
    pri = [f for f in files if "pri" in os.path.basename(f).lower()]
    red = [f for f in files if "red" in os.path.basename(f).lower()]
    if pri and red:
        return [pri[0], red[0]]
    return files[:limit]

def _ota_smooth(x, n_avg):
    if n_avg <= 1 or len(x) < n_avg:
        return x
    return np.convolve(x, np.ones(n_avg) / n_avg, mode="valid")

def _ota_load_s2p(filepath):
    net = rf.Network(filepath)
    freq = net.f / 1e9
    s21 = net.s_db[:, 1, 0]
    return freq, s21

def _ota_load_s12(filepath):
    net = rf.Network(filepath)
    freq = net.f / 1e9
    s12 = net.s_db[:, 0, 1]
    return freq, s12

def _ota_equal_len(freq, val):
    n = min(len(freq), len(val))
    return freq[:n], val[:n]

def _ota_load_cal(filepath, n_avg):
    if not filepath or not os.path.isfile(filepath):
        return None, None
    freq, s21 = _ota_load_s2p(filepath)
    s21 = _ota_smooth(s21, n_avg)
    freq, s21 = _ota_equal_len(freq, s21)
    return freq, s21

def _ota_load_specan_cal(filepath, n_avg):
    # The SpecAn assembly has an amplifier inline, so it's non-reciprocal:
    # S21 is its heavily-isolated reverse path (tens of dB of loss), while
    # S12 is the actual forward path the NP/NPD signal travels through (the
    # amplifier's real gain figure). Base/Hat are passive and reciprocal
    # (S21 == S12), so only SpecAn needs this S12 read.
    if not filepath or not os.path.isfile(filepath):
        return None, None
    net = rf.Network(filepath)
    freq = net.f / 1e9
    s12 = net.s_db[:, 0, 1]
    s12 = _ota_smooth(s12, n_avg)
    freq, s12 = _ota_equal_len(freq, s12)
    return freq, s12

def _ota_load_csv(filepath, col):
    """Loads a Siglent NPD CSV, skipping instrument metadata rows.
    col 1 = Raw Data (Noise Power, dBm at 10 kHz RBW), col 2 = dBm/Hz (NPD)."""
    df = pd.read_csv(filepath, header=None, names=range(6), on_bad_lines='skip', encoding='latin1', engine='python')
    num = df.apply(pd.to_numeric, errors='coerce')
    freq = num.iloc[:, 0].values
    val = num.iloc[:, col].values
    mask = np.isfinite(freq) & np.isfinite(val)
    return freq[mask], val[mask]

def _ota_plot_noise(files, title_suffix, freq_min, freq_max, n_avg, cal, output_folder, plot_density=False, apply_cal=False, date_str=None):
    if not files:
        return None
    date_str = date_str or datetime.now().strftime('%Y%m%d')
    specan_freq, specan_s12 = cal["specan"]
    base_freq, base_s21 = cal["base"]
    hat_freq, hat_s21 = cal["hat"]

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(_OTA_COLORS)

    plotted = 0
    for f in files:
        freq, raw = _ota_load_csv(f, 2 if plot_density else 1)
        if len(freq) == 0:
            continue
        smoothed = _ota_smooth(raw, n_avg)
        freq_smooth = freq[:len(smoothed)]

        # NP/NPD's full signal chain is DUT -> Base cable -> Hat cable ->
        # SpecAn amplifier assembly -> analyzer, so all three cal files
        # apply, not just SpecAn. SpecAn's assembly had an amplifier inline
        # when its pathloss file was made — so it's non-reciprocal: S21 is
        # the amp's heavily-isolated reverse path (not usable here), while
        # S12 is the actual forward path the signal travels (a real gain
        # figure; loaded in _ota_load_specan_cal) and gets subtracted back
        # out. Base/Hat are passive cables in the same path, so — same as
        # S21's correction — their loss gets added back (abs() makes this
        # correct regardless of the S2P's sign convention).
        corrected = smoothed
        if apply_cal:
            if specan_freq is not None:
                corrected = corrected - np.abs(np.interp(freq_smooth, specan_freq, specan_s12))
            if base_freq is not None:
                corrected = corrected + np.abs(np.interp(freq_smooth, base_freq, base_s21))
            if hat_freq is not None:
                corrected = corrected + np.abs(np.interp(freq_smooth, hat_freq, hat_s21))

        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))
        plotted += 1

    if plotted == 0:
        plt.close()
        return None

    cal_suffix = "Calibrated" if apply_cal else "Raw"
    plt.grid(True)
    if plot_density:
        plt.title(f"{date_str} Noise Power Density {title_suffix} ({cal_suffix})")
        plt.ylabel("NPD (dBm/Hz)")
        plt.ylim(_OTA_NPD_YLIM)
    else:
        plt.title(f"{date_str} Noise Power {title_suffix} ({cal_suffix})")
        plt.ylabel("Noise Power (dBm)")
        plt.ylim(_OTA_NP_YLIM)
    plt.xlabel("Frequency (GHz)")
    plt.xlim(_OTA_XLIM)
    plt.axvline(x=freq_min, color='g')
    plt.axvline(x=freq_max, color='g')

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=1, fontsize="8")

    prefix = "NPD" if plot_density else "NP"
    filename_safe_title = f"{date_str}_{prefix}_{title_suffix}".replace(" ", "_") + ".png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.subplots_adjust(bottom=0.45)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    return {"path": save_path, "status": "passed"}

def _ota_plot_s21(files, title_suffix, freq_min, freq_max, n_avg, cal, output_folder, date_str=None):
    if not files:
        return None
    date_str = date_str or datetime.now().strftime('%Y%m%d')
    base_freq, base_s21 = cal["base"]
    hat_freq, hat_s21 = cal["hat"]

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(_OTA_COLORS)

    for f in files:
        freq, s21 = _ota_load_s2p(f)
        s21_smooth = _ota_smooth(s21, n_avg)
        freq_smooth = freq[:len(s21_smooth)]

        # S21 is measured directly through the Base/Hat cables (no amplifier
        # in that chain), so Base/Hat calibrate S21 — SpecAn doesn't apply
        # here (see _ota_plot_noise for the NP/NPD side of this split).
        corrected = s21_smooth
        if base_freq is not None:
            corrected = corrected + np.abs(np.interp(freq_smooth, base_freq, base_s21))
        if hat_freq is not None:
            corrected = corrected + np.abs(np.interp(freq_smooth, hat_freq, hat_s21))

        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{date_str} S21 {title_suffix}")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("S21 (dB)")
    plt.xlim(_OTA_XLIM)
    plt.ylim(_OTA_S21_YLIM)
    plt.axvline(x=freq_min, color='g')
    plt.axvline(x=freq_max, color='g')

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=1, fontsize="8")

    filename_safe_title = f"{date_str}_S21_{title_suffix}".replace(" ", "_") + ".png"
    save_path = os.path.join(output_folder, filename_safe_title)
    plt.subplots_adjust(bottom=0.45)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    return {"path": save_path, "status": "passed"}

def generate_over_temp_array_plots(base_folder, freq_min, freq_max, n_avg, output_folder, apply_npd_cal=False):
    generated = []
    base_folder = _ota_resolve_data_root(base_folder)
    if not base_folder or not os.path.isdir(base_folder):
        return generated

    date_str = datetime.now().strftime('%Y%m%d')

    ambient = _ota_find_dir(base_folder, ["ambient"])
    cold = _ota_find_dir(base_folder, ["cold"])
    hot = _ota_find_dir(base_folder, ["hot"])
    cable = _ota_find_dir(base_folder, ["cable"])

    ambient2 = _ota_find_dir(ambient, ["2"]) if ambient else None
    cold2 = _ota_find_dir(cold, ["2"]) if cold else None
    hot2 = _ota_find_dir(hot, ["2"]) if hot else None

    # NP/NPD's chain runs through Base, Hat, and the SpecAn amplifier
    # assembly, so all three cal files apply (see _ota_plot_noise). S21 is
    # measured directly through the passive Base/Hat cables only — SpecAn
    # doesn't apply there (see _ota_plot_s21).
    base_file = _ota_find_cal_file(cable, ["base"], must_exclude=["specan"])
    hat_file = _ota_find_cal_file(cable, ["hat"])
    specan_file = _ota_find_cal_file(cable, ["specan"])

    cal = {
        "base": _ota_load_cal(base_file, n_avg),
        "hat": _ota_load_cal(hat_file, n_avg),
        "specan": _ota_load_specan_cal(specan_file, n_avg),
    }

    folder_specs = [
        ("Ambient", ambient), ("Ambient2", ambient2),
        ("Cold", cold), ("Cold2", cold2),
        ("Hot", hot), ("Hot2", hot2),
    ]
    for label, folder in folder_specs:
        if not folder:
            continue
        npd_files = _ota_get_files(folder, ".csv")
        s21_files = _ota_get_files(folder, ".s2p")
        p = _ota_plot_noise(npd_files, label, freq_min, freq_max, n_avg, cal, output_folder, plot_density=True, apply_cal=apply_npd_cal, date_str=date_str)
        if p: generated.append(p)
        p = _ota_plot_s21(s21_files, label, freq_min, freq_max, n_avg, cal, output_folder, date_str=date_str)
        if p: generated.append(p)

    for label, folder1, folder2 in [("Ambient", ambient, ambient2), ("Cold", cold, cold2), ("Hot", hot, hot2)]:
        if not folder1 or not folder2:
            continue
        npd_files = _ota_get_files(folder1, ".csv") + _ota_get_files(folder2, ".csv")
        s21_files = _ota_get_files(folder1, ".s2p") + _ota_get_files(folder2, ".s2p")
        p = _ota_plot_noise(npd_files, f"{label} Overlay", freq_min, freq_max, n_avg, cal, output_folder, plot_density=True, apply_cal=apply_npd_cal, date_str=date_str)
        if p: generated.append(p)
        p = _ota_plot_s21(s21_files, f"{label} Overlay", freq_min, freq_max, n_avg, cal, output_folder, date_str=date_str)
        if p: generated.append(p)

    return generated


def generate_plots(params):
    test_type = int(params.get('testType', 1))
    runs = params.get('runs', [])
    
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
    average_data_path = params.get('average_data_path', '')

    # Figure out calibration folder
    cal_folder = params.get('calFolder', "")
    if not cal_folder and len(runs) > 2 and runs[2]:
        cal_folder = runs[2]
    elif not cal_folder and os.path.exists("Cal_Path.txt"):
        with open("Cal_Path.txt", "r") as f:
            cal_folder = f.read().strip()
    if not cal_folder and folderA:
        inner_cal_sn = os.path.join(folderA, "Cable Loss", "SN006")
        inner_cal = os.path.join(folderA, "Cable Loss")
        if os.path.exists(inner_cal_sn):
            cal_folder = inner_cal_sn
        elif os.path.exists(inner_cal):
            cal_folder = inner_cal
        else:
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
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True, average_data_path=average_data_path)
            if p1: 
                generated_plots.append(p1)
                np_averages[name] = (p1.get("freq"), p1.get("avg"))
                
            p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True, apply_cal=True, average_data_path=average_data_path)
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

    elif test_type == 4:
        # NPD Over Temp Array: folderA is the single root folder containing
        # Ambient/Cold/Hot measurement folders and a Cable Loss folder.
        apply_npd_cal = bool(params.get('apply_npd_cal', False))
        generated_plots = generate_over_temp_array_plots(folderA, freq_min, freq_max, n_avg, output_folder, apply_npd_cal=apply_npd_cal)

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

        
        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True, test_type=test_type, average_data_path=average_data_path)
        if p1: generated_plots.append(p1)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=test_type, apply_cal=True)
        if p2: generated_plots.append(p2)

    return generated_plots
