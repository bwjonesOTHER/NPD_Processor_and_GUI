import os
import re
import skrf as rf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
import itertools
from pathlib import Path
import math


def search_files(root_dir, filename_part=''):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"Directory '{root_dir}' does not exist.")
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename_part.lower() in filename.lower():
                files.append(os.path.join(dirpath, filename))
    return files


def remove_nan(arr, remove_infinite=False):
    """
    Remove NaN (and optionally infinite) values from a NumPy array.

    Parameters:
        arr (np.ndarray): Input array.
        remove_infinite (bool): If True, also remove inf and -inf values.

    Returns:
        np.ndarray: Cleaned array without NaN (and optionally inf) values.
    """
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a NumPy array.")

    if remove_infinite:
        # Keep only finite numbers (no NaN, no inf)
        mask = np.isfinite(arr)
    else:
        # Keep only non-NaN values
        mask = ~np.isnan(arr)

    return arr[mask]

def extract_serial(filename):
    match = re.search(r'EM-\d+', filename)
    return match.group(0) if match else filename

#Determine if primary or redundant info
def extract_pri_red(filename):
    string1='Pri'
    string2='Red'
    if string1 in filename:
        chain_type='PRI'
    else:
        chain_type='RED'
    return chain_type

def extract_serial_number(filename):
    exact_matches = re.search(r'\b\d{4}\b', filename)
    return exact_matches.group(0)


def find_cal_file(folder, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    try:
        cap_num_int = int(cap_num)
    except (ValueError, TypeError):
        return None
        
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

def cap_searchA(filename, lmoFolderA):
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06"]:
        if f"Cap_{n}" in filename:
            cap_num = n
            break
            
    if cap_num is None:
        return None, None
        
    loss = find_cal_file(lmoFolderA, cap_num, "Base")
    loss_bulkhead = find_cal_file(lmoFolderA, cap_num, "Bulkhead")
    return loss, loss_bulkhead

def cap_searchB(filename, lmoFolderB):
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06"]:
        if f"Cap_{n}" in filename:
            cap_num = n
            break
            
    if cap_num is None:
        return None, None
        
    loss = find_cal_file(lmoFolderB, cap_num, "Base")
    loss_bulkhead = find_cal_file(lmoFolderB, cap_num, "Bulkhead")
    return loss, loss_bulkhead

def plotNPD_single(filesA,lmoFolderA,n_avg, u_bound_npd,l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    file_avg = np.zeros([10000])

    for file in filesA:

        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        #serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0


        df_all = pd.read_csv(file)# Read CSV with headers automatically detected

        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(UUT_bulkhead_s21, np.ndarray):
                UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(specA_s21, np.ndarray):
                specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')

        c=next(color_cycle)

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21
        file_avg = np.zeros([len(noise_pow_mod)])
        file_avg=np.column_stack((file_avg,noise_pow_mod))

        #plt.plot(freq_ghz, noise_pow, label=f'{serial[-31:-8:1]} {chain_type}',color=c)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB

    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_npd
    upper_bound_data=file_avg-l_bound_npd

    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-130, -90)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: Noise Power'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('NP (dBm)')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotNPD(filesA,lmoFolderA,n_avg,filesB,lmoFolderB,u_bound_npd,l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    file_avg = np.zeros([10000])

    for file in filesA:
        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0

        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)


        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21

        file_avg = np.zeros([len(noise_pow_mod)])
        file_avg=np.column_stack((file_avg,noise_pow_mod))

        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB

    for file in filesB:

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchB(file,lmoFolderB)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderB, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0

        serial = extract_serial(file)
        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        chain_type=extract_pri_red(file)

        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21

        file_avg=np.column_stack((file_avg,noise_pow_mod))

        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB


    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_npd
    upper_bound_data=file_avg-l_bound_npd

    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-130, -90)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: Noise Power'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('NP (dBm)')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotNPD_density(filesA,lmoFolderA,n_avg,filesB,lmoFolderB,u_bound_npd,l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    file_avg = np.zeros([10000])

    for file in filesA:
        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0

        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True)


        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21

        file_avg = np.zeros([len(noise_pow_mod)])
        file_avg=np.column_stack((file_avg,noise_pow_mod))

        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB

    for file in filesB:

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchB(file,lmoFolderB)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderB, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0

        serial = extract_serial(file)
        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        chain_type=extract_pri_red(file)

        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True)
        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21

        file_avg=np.column_stack((file_avg,noise_pow_mod))

        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB

    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_npd
    upper_bound_data=file_avg-l_bound_npd


    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-170, -110)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: Noise Power Density'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('NPD (dBm/Hz)')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotNPD_density_single(filesA,lmoFolderA,n_avg,u_bound_npd,l_bound_npd, RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    file_avg = np.zeros([10000])

    for file in filesA:

        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        #serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0


        df_all = pd.read_csv(file)# Read CSV with headers automatically detected

        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True)
        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(UUT_bulkhead_s21, np.ndarray):
                UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(specA_s21, np.ndarray):
                specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')

        c=next(color_cycle)

        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21
        file_avg = np.zeros([len(noise_pow_mod)])
        file_avg=np.column_stack((file_avg,noise_pow_mod))

        #plt.plot(freq_ghz, noise_pow, label=f'{serial[-31:-8:1]} {chain_type}',color=c)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB
        plt.plot(freq_ghz, noise_pow_mod, label=f'{serial[-34:-8:1]} {chain_type}',color=c)#{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB

    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_npd
    upper_bound_data=file_avg-l_bound_npd

    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-170, -110)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: Noise Power Density'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('NPD (dBm/Hz)')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotGT(filesA,lmoFolderA,gainA,n_avg,filesB,lmoFolderB,gainB,RunA,temperature,freq_min,freq_max,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    for file in filesA:
        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0



        tile_serial=file[-16:-13]
        gain=[s for s in gainA if tile_serial in s]
        gain=gain[0]
        gain_values=np.array(pd.read_csv(gain))
        gain_values=gain_values[:,1]




        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
        noise_pow_den=remove_nan(num_df.values[:, 2], remove_infinite=True)

        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')


        noise_pow_mod=noise_pow_den-specA_s21-UUT_cable_s21-UUT_bulkhead_s21


        # Need to reduce span of noise to 2.6-4.1 to match the gain measurements


        idx_low=np.argwhere(freq_ghz==2.6)
        idx_high=np.argwhere(freq_ghz==4.1)
        idx_low=idx_low.item()
        idx_high=idx_high.item()
        freq_ghz_short=freq_ghz[idx_low:idx_high]
        noise_pow_mod_short=noise_pow_mod[idx_low:idx_high]



        new_gain_array=np.linspace(0,len(gain_values)-1,len(noise_pow_mod_short))
        new_gain_array_stretch=np.interp(new_gain_array,np.arange(len(gain_values)),gain_values)

        g_t=new_gain_array_stretch-noise_pow_mod_short-198.62
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz_short,g_t,label=f'{serial[-32:-8:1]} {chain_type}',color=c,linestyle=line)



    for file in filesB:
        serial = extract_serial(file)
        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        chain_type=extract_pri_red(file)

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderB)
        UUT_cable=rf.Network(loss)
        UUT_cable_s21=UUT_cable.s_db[:,1,0]

        UUT_bulkhead=rf.Network(loss_bulkhead)
        UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0


        tile_serial = file[-16:-13]
        gain = [s for s in gainB if tile_serial in s]
        gain = gain[0]
        gain_values = np.array(pd.read_csv(gain))
        gain_values = gain_values[:, 1]


        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
        noise_pow_den=remove_nan(num_df.values[:, 2], remove_infinite=True)
        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

        noise_pow_mod=noise_pow_den-specA_s21-UUT_cable_s21-UUT_bulkhead_s21
        idx_low=np.argwhere(freq_ghz==2.6)
        idx_high=np.argwhere(freq_ghz==4.1)
        idx_low=idx_low.item()
        idx_high=idx_high.item()
        freq_ghz_short=freq_ghz[idx_low:idx_high]
        noise_pow_mod_short=noise_pow_mod[idx_low:idx_high]



        new_gain_array=np.linspace(0,len(gain_values)-1,len(noise_pow_mod_short))
        new_gain_array_stretch=np.interp(new_gain_array,np.arange(len(gain_values)),gain_values)

        g_t=new_gain_array_stretch-noise_pow_mod_short-198.62

        g_t_goal=[]
        for i in range(len(freq_ghz_short)):
            x=20*math.log10(freq_ghz_short[i]/3)
            y=-8.33+x
            g_t_goal.append(y)
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz_short,g_t,label=f'{serial[-32:-8:1]} {chain_type}',color=c,linestyle=line)



    plt.xlim(freq_ghz_short[0], freq_ghz[idx_high+100])
    plt.ylim(-20, 10)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: G_T'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('G/T')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot(freq_ghz_short,g_t_goal,color='r',linewidth=3)
    #plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotGT_single(filesA,lmoFolderA,gainA,n_avg,RunA,temperature,freq_min,freq_max,folder_path,show_plot):
    plt.figure(figsize=(8, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    for file in filesA:
        serial = extract_serial(file)
        chain_type=extract_pri_red(file)
        serial_number=extract_serial_number

        'New search for correct cable'
        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0

        'SpecA cable loss'
        specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0



        tile_serial=file[-16:-13]
        gain=[s for s in gainA if tile_serial in s]
        gain=gain[0]
        gain_values=np.array(pd.read_csv(gain))
        gain_values=gain_values[:,1]




        df_all = pd.read_csv(file)# Read CSV with headers automatically detected
        num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
        freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
        noise_pow_den=remove_nan(num_df.values[:, 2], remove_infinite=True)

        if n_avg > 1:
            noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
            noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
            freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')


        noise_pow_mod=noise_pow_den-specA_s21-UUT_cable_s21-UUT_bulkhead_s21


        # Need to reduce span of noise to 2.6-4.1 to match the gain measurements


        idx_low=np.argwhere(freq_ghz==2.6)
        idx_high=np.argwhere(freq_ghz==4.1)
        idx_low=idx_low.item()
        idx_high=idx_high.item()
        freq_ghz_short=freq_ghz[idx_low:idx_high]
        noise_pow_mod_short=noise_pow_mod[idx_low:idx_high]



        new_gain_array=np.linspace(0,len(gain_values)-1,len(noise_pow_mod_short))
        new_gain_array_stretch=np.interp(new_gain_array,np.arange(len(gain_values)),gain_values)

        g_t=new_gain_array_stretch-noise_pow_mod_short-198.62
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz_short,g_t,label=f'{serial[-32:-8:1]} {chain_type}',color=c,linestyle=line)




    plt.xlim(freq_ghz_short[0], freq_ghz[idx_high+100])
    plt.ylim(-20, 10)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: G_T'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('G/T')  # , fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.plot(freq_ghz_short,g_t_goal,color='r',linewidth=3)
    #plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.subplots_adjust(right=0.7)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg


def plotS21(filesA,filesB,u_bound_s21, l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot):
    plt.figure(figsize=(7, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)

    file_avg=np.zeros([10000])
    for file in filesA:
        #file_path = os.path.join(lmoFolder, file)
        chain_type = extract_pri_red(file)
        net = rf.Network(file)
        freq_ghz = net.f / 1e9  # Convert to GHz
        serial = extract_serial(file)
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, net.s_db[:, 1, 0], label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)
        file_avg = np.zeros([len(net.s_db[:,1,0])])
        file_avg=np.column_stack((file_avg,net.s_db[:,1,0]))

    for file in filesB:
        #file_path = os.path.join(lmoFolder, file)
        chain_type = extract_pri_red(file)
        net = rf.Network(file)
        freq_ghz = net.f / 1e9  # Convert to GHz
        serial = extract_serial(file)
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, net.s_db[:, 1, 0], label=f'{serial[-34:-8:1]} {chain_type}',color=c,linestyle=line)
        file_avg=np.column_stack((file_avg,net.s_db[:,1,0]))


    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_s21
    upper_bound_data=file_avg-l_bound_s21


    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-40, 40)
    plt.grid(True)  # Enable grid lines



    title = f'{RunA} {temperature}: Test Hat S21'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')#, fontsize='x-small'
    plt.ylabel('S21 (dB)')#, fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    #plt.tight_layout()
    plt.subplots_adjust(right=0.8)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def plotS21_single(filesA,u_bound_s21, l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot):
    plt.figure(figsize=(7, 4), dpi=150)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    file_avg=np.zeros([10000])
    for file in filesA:
        #file_path = os.path.join(lmoFolder, file)
        chain_type = extract_pri_red(file)
        net = rf.Network(file)
        freq_ghz = net.f / 1e9  # Convert to GHz
        serial = extract_serial(file)
        c=next(color_cycle)
        line=next(line_styles_cycle)
        plt.plot(freq_ghz, net.s_db[:, 1, 0], label=f'{serial[-16:-8:1]} {chain_type}',color=c,linestyle=line)
        file_avg = np.zeros([len(net.s_db[:,1,0])])
        file_avg=np.column_stack((file_avg,net.s_db[:,1,0]))

    file_avg=np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    lower_bound_data=file_avg+u_bound_s21
    upper_bound_data=file_avg-l_bound_s21

    plt.xlim(freq_ghz[0], freq_ghz[-1])
    plt.ylim(-40, 40)
    plt.grid(True)  # Enable grid lines

    title = f'{RunA} {temperature}: Test Hat S21'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')#, fontsize='x-small'
    plt.ylabel('S21 (dB)')#, fontsize='x-small'

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='grey', label='axvline - full height')
    plt.axvline(x=freq_max, color='grey', label='axvline - full height')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=.15)
    plt.plot(freq_ghz, lower_bound_data, color='red', alpha=1, marker='o', markersize=5, markevery=100,  label='Lower bound')
    plt.plot(freq_ghz, upper_bound_data, color='red', alpha=1, marker='x', markersize=5, markevery=100,  label='Upper bound')
    #plt.tight_layout()
    plt.subplots_adjust(right=0.8)
    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

    return freq_ghz,file_avg

def npd_temp_diff_plot(NPD25,NPD64,NPDn38,folder_path,show_plot):
    "Plot average npd and delta values"
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)

    diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1])
    diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1])
    diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1])

    fig,ax1=plt.subplots(figsize=(8,6))
    plt.ylim(-120, -90)
    plt.ylabel('Avg. NP (dB)')  # , fontsize='x-small'
    plt.grid(True)
    title = f'NP Over Temp and Deltas'
    plt.title(title,fontsize=20)
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0],NPD25[1],label="NP 25",color=c,linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD64[0], NPD64[1], label="NP 64",color=c,linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPDn38[0], NPDn38[1], label="NP n38",color=c,linestyle=line)
    plt.legend(loc='upper left', fontsize='10' )

    ax2=ax1.twinx()
    ax2.set_ylim(0,5)
    plt.ylabel('Diff NP (dB)')  # , fontsize='x-small'
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)
    plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64",color=c,linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38",color=c,linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd64_npdn38, label="Delta 64/n38",color=c,linestyle='--')
    plt.xlim(min(NPD25[0]), max(NPD25[0]))

    plt.axvline(x=2.7, color='grey')
    plt.axvline(x=4.1, color='grey')
    plt.axvspan(xmin=2.7, xmax=4.1, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'

    plt.legend(loc='upper right', fontsize='10' )


    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

def npd_density_temp_diff_plot(NPD25,NPD64,NPDn38,folder_path,show_plot):
    "Plot average npd and delta values"
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)

    diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1])
    diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1])
    diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1])

    fig,ax1=plt.subplots(figsize=(8,6))
    plt.ylim(-170, -110)
    plt.ylabel('Avg. NPD (dB/Hz)')  # , fontsize='x-small'
    plt.grid(True)
    title = f'NPD Over Temp and Deltas'
    plt.title(title,fontsize=20)
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0],NPD25[1],label="NPD 25",color=c,linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD64[0], NPD64[1], label="NPD 64",color=c,linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPDn38[0], NPDn38[1], label="NPD n38",color=c,linestyle=line)
    plt.legend(loc='upper left', fontsize='10' )

    ax2=ax1.twinx()
    ax2.set_ylim(0,5)
    plt.ylabel('Diff NPD (dB)')  # , fontsize='x-small'
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)
    plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64",color=c,linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38",color=c,linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd64_npdn38, label="Delta 64/n38",color=c,linestyle='--')
    plt.xlim(min(NPD25[0]), max(NPD25[0]))

    plt.axvline(x=2.7, color='grey')
    plt.axvline(x=4.1, color='grey')
    plt.axvspan(xmin=2.7, xmax=4.1, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'

    plt.legend(loc='upper right', fontsize='10' )


    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

def GT_temp_diff_plot(GT25, GT64, GTn38,folder_path,show_plot):
    "Plot average gt and delta values"
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)



    diff_GT25_GT64 = np.abs(GT25[1] - GT64[1])
    diff_GT25_GTn38 = np.abs(GT25[1] - GTn38[1])
    diff_GT64_GTn38 = np.abs(GT64[1] - GTn38[1])

    fig, ax1 = plt.subplots(figsize=(8, 6))
    plt.ylim(-120, -90)
    plt.ylabel('Avg. NPD (dB)')  # , fontsize='x-small'
    plt.grid(True)
    title = f'GT Over Temp and Deltas'
    plt.title(title, fontsize=20)
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], NPD25[1], label="GT 25", color=c, linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD64[0], NPD64[1], label="GT 64", color=c, linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPDn38[0], NPDn38[1], label="GT n38", color=c, linestyle=line)
    plt.legend(loc='upper left', fontsize='10')

    ax2 = ax1.twinx()
    ax2.set_ylim(0, 3)
    plt.ylabel('Diff GT')  # , fontsize='x-small'
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64", color=c, linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38", color=c, linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(NPD25[0], diff_npd64_npdn38, label="Delta 64/n38", color=c, linestyle='--')
    plt.xlim(min(NPD25[0]), max(NPD25[0]))

    plt.axvline(x=2.7, color='grey')
    plt.axvline(x=4.1, color='grey')
    plt.axvspan(xmin=2.7, xmax=4.1, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'

    plt.legend(loc='upper right', fontsize='10')


    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

def s21_temp_diff_plot(Spar_25, Spar_64, Spar_n38,folder_path,show_plot):
    "Plot average S21 and delta values"
    diff_s25_s64 = np.abs(Spar_25[1] - Spar_64[1])
    diff_s25_sn38 = np.abs(Spar_25[1] - Spar_n38[1])
    diff_s64_sn38 = np.abs(Spar_64[1] - Spar_n38[1])

    fig, ax1 = plt.subplots(figsize=(8, 6))
    plt.grid(True)
    title = f'S21 Over Temp and Deltas'
    plt.title(title, fontsize=20)
    my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
    my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                      'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed',
                      'dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(Spar_25[0], Spar_25[1], label="S21 25", color=c, linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(Spar_64[0], Spar_64[1], label="S21 64", color=c, linestyle=line)
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(Spar_n38[0], Spar_n38[1], label="S21 n38", color=c, linestyle=line)
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle = itertools.cycle(my_line_styles)
    plt.plot(Spar_n38[0], diff_s25_s64, label="Delta 25/64", color=c, linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(Spar_n38[0], diff_s25_sn38, label="Delta 25/n38", color=c, linestyle='--')
    c = next(color_cycle)
    line = next(line_styles_cycle)
    plt.plot(Spar_n38[0], diff_s64_sn38, label="Delta 64/n38", color=c, linestyle='--')
    plt.xlim(min(Spar_n38[0]), max(Spar_n38[0]))
    plt.ylim(0, 30)
    plt.axvline(x=2.7, color='grey')
    plt.axvline(x=4.1, color='grey')
    plt.axvspan(xmin=2.7, xmax=4.1, color='grey', alpha=.15)
    plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
    plt.ylabel('Avg. S21 (dB)')  # , fontsize='x-small'
    plt.legend(loc='upper left', fontsize='10')


    # Save the figure
    current_date = datetime.now()  # Get the current date
    formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
    filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
    save_path = os.path.join(folder_path, file_name_full)
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")

    if show_plot == 1:  # View Plot
        plt.show()

