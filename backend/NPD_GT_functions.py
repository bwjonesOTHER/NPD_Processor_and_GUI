import os
import re
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
import itertools
from pathlib import Path
import math

def search_files(root_dir, filename_part):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"Directory '{root_dir}' does not exist.")
    if not os.path.isdir(root_dir):
        raise NotADirectoryError(f"'{root_dir}' is not a directory.")

    matches = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if filename_part.lower() in file.lower():
                matches.append(os.path.join(dirpath, file))
    return matches

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
    return 'RED'

def extract_serial_number(filename):
    exact_matches = re.search(r'\b\d{4}\b', filename)
    return exact_matches.group(0) if exact_matches else ""

def cap_search(filename, lmoFolder):
    match = re.search(r'Cap_\d+', filename)
    loss, loss_bulkhead = None, None
    if match:
        loss_path = os.path.join(lmoFolder, match.group(0))
        try:
            last_filename = extract_pri_red(filename)
            res_loss = search_files(loss_path, f'Base_{last_filename}')
            if not res_loss:
                res_loss = search_files(loss_path, 'Base')
                
            res_bulk = search_files(loss_path, 'Bulkhead')
            if not res_bulk:
                res_bulk = search_files(loss_path, 'fixture')
                
            if res_loss: loss = res_loss[0]
            if res_bulk: loss_bulkhead = res_bulk[0]
        except Exception:
            pass
    return loss, loss_bulkhead

def _get_title(runs_data, temperature, suffix):
    names = " ".join([r['name'] for r in runs_data])
    if len(names) > 50:
        return f"N={len(runs_data)} Runs {temperature}: {suffix}"
    return f"{names} {temperature}: {suffix}"

def plotNPD_multi(runs_data, n_avg, u_bound_npd, l_bound_npd, temperature, freq_min, freq_max, reqS11Val, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            
            loss, loss_bulkhead = cap_search(file, run['folder'])
            
            if loss:
                UUT_cable = rf.Network(loss)
                UUT_cable_s21 = UUT_cable.s_db[:,1,0]
            else:
                UUT_cable_s21 = 0
                
            if loss_bulkhead:
                UUT_bulkhead = rf.Network(loss_bulkhead)
                UUT_bulkhead_s21 = UUT_bulkhead.s_db[:,1,0]
            else:
                UUT_bulkhead_s21 = 0
            
            specA_cables = search_files(run['folder'], 'SpecA')
            if specA_cables:
                specA_cable_loss = rf.Network(specA_cables[0])
                specA_s21 = specA_cable_loss.s_db[:, 1, 0]
            else:
                specA_s21 = 0
            
            df_all = pd.read_csv(file)
            num_df = df_all.apply(pd.to_numeric, errors='coerce')
            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            
            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
                if isinstance(UUT_cable_s21, np.ndarray):
                    UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(specA_s21, np.ndarray):
                    specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(UUT_bulkhead_s21, np.ndarray):
                    UUT_bulkhead_s21 = np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
                
            noise_pow_mod = noise_pow - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21
            if freq_ghz_out is None:
                freq_ghz_out = freq_ghz
            else:
                noise_pow_mod = np.interp(freq_ghz_out, freq_ghz, noise_pow_mod)
                freq_ghz = freq_ghz_out
            all_files_avg.append(noise_pow_mod)
            freq_ghz_out = freq_ghz
            
            c = next(color_cycle)
            label = f"{serial[-34:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            plt.plot(freq_ghz, noise_pow_mod, label=label, color=c, linestyle=line_style)
            
    if len(all_files_avg) > 0:
        file_avg = np.mean(np.column_stack(all_files_avg), axis=1)
    else:
        return None, None
        
    lower_bound_data = file_avg + u_bound_npd
    upper_bound_data = file_avg - l_bound_npd
    
    plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    plt.ylim(-130, -90)
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'Noise Power')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NP (dBm)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz_out, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
    plt.plot(freq_ghz_out, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, file_avg

def plotNPD_density_multi(runs_data, n_avg, u_bound_npd, l_bound_npd, temperature, freq_min, freq_max, reqS11Val, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            
            loss, loss_bulkhead = cap_search(file, run['folder'])
            
            if loss:
                UUT_cable = rf.Network(loss)
                UUT_cable_s21 = UUT_cable.s_db[:,1,0]
            else:
                UUT_cable_s21 = 0
                
            if loss_bulkhead:
                UUT_bulkhead = rf.Network(loss_bulkhead)
                UUT_bulkhead_s21 = UUT_bulkhead.s_db[:,1,0]
            else:
                UUT_bulkhead_s21 = 0
            
            specA_cables = search_files(run['folder'], 'SpecA')
            if specA_cables:
                specA_cable_loss = rf.Network(specA_cables[0])
                specA_s21 = specA_cable_loss.s_db[:, 1, 0]
            else:
                specA_s21 = 0
            
            df_all = pd.read_csv(file)
            num_df = df_all.apply(pd.to_numeric, errors='coerce')
            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True) # Density is index 2
            
            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
                if isinstance(UUT_cable_s21, np.ndarray):
                    UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(specA_s21, np.ndarray):
                    specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(UUT_bulkhead_s21, np.ndarray):
                    UUT_bulkhead_s21 = np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
                
            noise_pow_mod = noise_pow - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21
            if freq_ghz_out is None:
                freq_ghz_out = freq_ghz
            else:
                noise_pow_mod = np.interp(freq_ghz_out, freq_ghz, noise_pow_mod)
                freq_ghz = freq_ghz_out
            all_files_avg.append(noise_pow_mod)
            freq_ghz_out = freq_ghz
            
            c = next(color_cycle)
            label = f"{serial[-34:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            plt.plot(freq_ghz, noise_pow_mod, label=label, color=c, linestyle=line_style)
            
    if len(all_files_avg) > 0:
        file_avg = np.mean(np.column_stack(all_files_avg), axis=1)
    else:
        return None, None
        
        
    lower_bound_data = file_avg + u_bound_npd
    upper_bound_data = file_avg - l_bound_npd
    
    plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    plt.ylim(-170, -110)
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'Noise Power Density')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NPD (dBm/Hz)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz_out, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
    plt.plot(freq_ghz_out, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, file_avg

def plotS21_multi(runs_data, u_bound_s21, l_bound_s21, temperature, freq_min, freq_max, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            chain_type = extract_pri_red(file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            serial = extract_serial(file)
            
            c = next(color_cycle)
            label = f"{serial[-16:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            s21_data = net.s_db[:, 1, 0]
            if freq_ghz_out is None:
                freq_ghz_out = freq_ghz
            else:
                s21_data = np.interp(freq_ghz_out, freq_ghz, s21_data)
                freq_ghz = freq_ghz_out
            plt.plot(freq_ghz, s21_data, label=label, color=c, linestyle=line_style)
            all_files_avg.append(s21_data)
            
    if len(all_files_avg) > 0:
        file_avg = np.mean(np.column_stack(all_files_avg), axis=1)
    else:
        return None, None
        
    lower_bound_data = file_avg + u_bound_s21
    upper_bound_data = file_avg - l_bound_s21
    
    try:
        plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    except:
        pass
    plt.ylim(-40, 40)
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'Test Hat S21')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz_out, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
    plt.plot(freq_ghz_out, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, file_avg

def npd_density_temp_diff_plot(NPD25, NPD64, NPDn38, num_runs, freq_min, freq_max, folder_path, show_plot):
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    color_cycle = itertools.cycle(my_colors)
    
    fig, ax1 = plt.subplots(figsize=(8,6))
    plt.ylim(-170, -110)
    plt.ylabel('Avg. NPD (dB/Hz)')
    plt.grid(True)
    
    title = 'NPD Over Temp and Deltas' if num_runs == 2 else 'NPD Over Temp'
    plt.title(title, fontsize=20)
    
    c = next(color_cycle)
    plt.plot(NPD25[0], NPD25[1], label="NPD 25", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(NPD64[0], NPD64[1], label="NPD 64", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(NPDn38[0], NPDn38[1], label="NPD n38", color=c, linestyle='solid')
    plt.legend(loc='upper left', fontsize='10')
    
    if num_runs == 2:
        diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1])
        diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1])
        diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1])
        
        ax2 = ax1.twinx()
        ax2.set_ylim(0, 5)
        plt.ylabel('Diff NPD (dB)')
        
        color_cycle = itertools.cycle(my_colors)
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd64_npdn38, label="Delta 64/n38", color=c, linestyle='--')
        plt.legend(loc='upper right', fontsize='10')

    try:
        plt.xlim(min(NPD25[0]), max(NPD25[0]))
    except:
        pass
    plt.axvline(x=freq_min, color='grey')
    plt.axvline(x=freq_max, color='grey')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()

def s21_temp_diff_plot(Spar_25, Spar_64, Spar_n38, num_runs, freq_min, freq_max, folder_path, show_plot):
    fig, ax1 = plt.subplots(figsize=(8, 6))
    plt.grid(True)
    
    title = 'S21 Over Temp and Deltas' if num_runs == 2 else 'S21 Over Temp'
    plt.title(title, fontsize=20)
    
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    color_cycle = itertools.cycle(my_colors)
    
    c = next(color_cycle)
    plt.plot(Spar_25[0], Spar_25[1], label="S21 25", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(Spar_64[0], Spar_64[1], label="S21 64", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(Spar_n38[0], Spar_n38[1], label="S21 n38", color=c, linestyle='solid')
    plt.legend(loc='upper left', fontsize='10')
    
    if num_runs == 2:
        diff_s25_s64 = np.abs(Spar_25[1] - Spar_64[1])
        diff_s25_sn38 = np.abs(Spar_25[1] - Spar_n38[1])
        diff_s64_sn38 = np.abs(Spar_64[1] - Spar_n38[1])
        
        ax2 = ax1.twinx()
        ax2.set_ylim(0, 3)
        plt.ylabel('Diff S21')
        color_cycle = itertools.cycle(my_colors)
        c = next(color_cycle)
        plt.plot(Spar_n38[0], diff_s25_s64, label="Delta 25/64", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(Spar_n38[0], diff_s25_sn38, label="Delta 25/n38", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(Spar_n38[0], diff_s64_sn38, label="Delta 64/n38", color=c, linestyle='--')
        plt.legend(loc='upper right', fontsize='10')

    try:
        plt.xlim(min(Spar_n38[0]), max(Spar_n38[0]))
    except:
        pass
    plt.ylim(0, 30)
    plt.axvline(x=2.7, color='grey')
    plt.axvline(x=4.1, color='grey')
    plt.axvspan(xmin=2.7, xmax=4.1, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Avg. S21 (dB)')
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()

def npd_temp_diff_plot(NPD25, NPD64, NPDn38, num_runs, freq_min, freq_max, folder_path, show_plot):
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    color_cycle = itertools.cycle(my_colors)
    
    fig, ax1 = plt.subplots(figsize=(8,6))
    plt.ylim(-130, -90)
    plt.ylabel('Avg. NP (dB)')
    plt.grid(True)
    
    title = 'NP Over Temp and Deltas' if num_runs == 2 else 'NP Over Temp'
    plt.title(title, fontsize=20)
    
    c = next(color_cycle)
    plt.plot(NPD25[0], NPD25[1], label="NP 25", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(NPD64[0], NPD64[1], label="NP 64", color=c, linestyle='solid')
    c = next(color_cycle)
    plt.plot(NPDn38[0], NPDn38[1], label="NP n38", color=c, linestyle='solid')
    plt.legend(loc='upper left', fontsize='10')
    
    if num_runs == 2:
        diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1])
        diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1])
        diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1])
        
        ax2 = ax1.twinx()
        ax2.set_ylim(0, 5)
        plt.ylabel('Diff NP (dB)')
        
        color_cycle = itertools.cycle(my_colors)
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38", color=c, linestyle='--')
        c = next(color_cycle)
        plt.plot(NPD25[0], diff_npd64_npdn38, label="Delta 64/n38", color=c, linestyle='--')
        plt.legend(loc='upper right', fontsize='10')

    try:
        plt.xlim(min(NPD25[0]), max(NPD25[0]))
    except:
        pass
    plt.axvline(x=freq_min, color='grey')
    plt.axvline(x=freq_max, color='grey')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()

def plotS11_multi(runs_data, temperature, freq_min, freq_max, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            chain_type = extract_pri_red(file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            serial = extract_serial(file)
            
            c = next(color_cycle)
            label = f"{serial[-16:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            s11_data = net.s_db[:, 0, 0]
            if freq_ghz_out is None:
                freq_ghz_out = freq_ghz
            else:
                s11_data = np.interp(freq_ghz_out, freq_ghz, s11_data)
                freq_ghz = freq_ghz_out
            plt.plot(freq_ghz, s11_data, label=label, color=c, linestyle=line_style)
            all_files_avg.append(s11_data)
            
    if len(all_files_avg) == 0:
        return None, None
        
    try: plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    except: pass
    plt.ylim(-30, 0)
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'S11')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S11 (dB)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, all_files_avg

def plotS22_multi(runs_data, temperature, freq_min, freq_max, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            chain_type = extract_pri_red(file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            serial = extract_serial(file)
            
            c = next(color_cycle)
            label = f"{serial[-16:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            s22_data = net.s_db[:, 1, 1]
            if freq_ghz_out is None:
                freq_ghz_out = freq_ghz
            else:
                s22_data = np.interp(freq_ghz_out, freq_ghz, s22_data)
                freq_ghz = freq_ghz_out
            plt.plot(freq_ghz, s22_data, label=label, color=c, linestyle=line_style)
            all_files_avg.append(s22_data)
            
    if len(all_files_avg) == 0:
        return None, None
        
    try: plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    except: pass
    plt.ylim(-30, 0)
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'S22')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S22 (dB)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, all_files_avg

def plotGroupDelay_multi(runs_data, temperature, freq_min, freq_max, folder_path, show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    base_line_styles = ['solid', 'dashed', 'dotted', 'dashdot', (0, (3, 5, 1, 5, 1, 5))]
    
    all_files_avg = []
    freq_ghz_out = None

    for i, run in enumerate(runs_data):
        color_cycle = itertools.cycle(my_colors)
        line_style = base_line_styles[i % len(base_line_styles)]
        
        for file in run['files']:
            chain_type = extract_pri_red(file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            serial = extract_serial(file)
            
            group_delay = -np.gradient(np.unwrap(net.s_rad[:, 1, 0])) / np.gradient(net.f)
            group_delay_ns = group_delay * 1e9
            
            c = next(color_cycle)
            label = f"{serial[-16:-8:1]} {chain_type}"
            if len(runs_data) > 1: label += f" ({run['name']})"
            
            plt.plot(freq_ghz, group_delay_ns, label=label, color=c, linestyle=line_style)
            all_files_avg.append(group_delay_ns)
            
    if len(all_files_avg) == 0:
        return None, None
        
    try: plt.xlim(freq_ghz_out[0], freq_ghz_out[-1])
    except: pass
    plt.grid(True)
    
    title = _get_title(runs_data, temperature, 'Group Delay')
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Group Delay (ns)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{formatted_date}_{filename_safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot == 1: plt.show()
    plt.close()
    
    return freq_ghz_out, all_files_avg
