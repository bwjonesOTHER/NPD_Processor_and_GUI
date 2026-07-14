import os
import re
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
from colorama import init, Fore

import glob

def generate_plots(params):
    """Input Params"""
    # Edge:L110172, Center:L110173

    def get_PMA_area_path():
        try:
            with open("PMA_Area.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    pma_area = get_PMA_area_path()

    RunA = r'NPDoverTemp'
    RunB = r'BenchNPD'+'\\'+ f"{pma_area}"


    freq_min = float(params.get('freq_min', 2.7))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Ns = [700,2100]
    reqS11Val = float(params.get('reqS11Val', -10))
    reqS21Val = float(params.get('reqS21Val', -14))

    n_avg = int(params.get('n_avg', 20))
    show_plot = 0
    generated_plots = []

    def search_files(root_dir, filename_part, SN_value):
        import subprocess
        import os
        matches = []
        # Use OS-level search to completely bypass Python's os.scandir,
        # preventing OneDrive from downloading unrelated files like images.
        if os.name == 'nt':
            cmd = f'dir /b /s "{root_dir}\\*{filename_part}*"'
            try:
                output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.split('\n'):
                    file = line.strip()
                    if file and SN_value.lower() in os.path.basename(file).lower():
                        matches.append(file)
            except subprocess.CalledProcessError:
                pass
        else:
            cmd = f'find "{root_dir}" -type f -name "*{filename_part}*"'
            try:
                output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.split('\n'):
                    file = line.strip()
                    if file and SN_value.lower() in os.path.basename(file).lower():
                        matches.append(file)
            except subprocess.CalledProcessError:
                pass
        return matches


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

    def get_saved_path():
        try:
            with open("path.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def get_SN_path():
        try:
            with open("SN.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def get_LMO_Number():
        try:
            with open("LMO_Number.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    """Collect and categorize files"""
    folder_path = get_saved_path() #\L110475\SN0001\Pre-TSS\PRI
    serial_number = get_SN_path() or ""
    lmo_number = get_LMO_Number()
    pma_area = get_PMA_area_path() or ""
    
    # Format the folder names based on user feedback
    area_folder = pma_area
    lmo_folder = f"LMO{lmo_number}" if not lmo_number.upper().startswith("LMO") else lmo_number

    output_folder = params.get('outputFolder') or folder_path
    lmoFolderA = os.path.join(folder_path, RunA)
    if not os.path.exists(lmoFolderA) and os.path.exists(folder_path):
        area_type = pma_area[-1].upper() if pma_area else 'C'
        found_alt = False
        for d in os.listdir(folder_path):
            if d.startswith("Run") and os.path.isdir(os.path.join(folder_path, d)):
                run_dir = os.path.join(folder_path, d)
                for sub in os.listdir(run_dir):
                    if sub.startswith(area_type + "_SN") and f"{serial_number}" in sub and str(lmo_number) in sub:
                        lmoFolderA = os.path.join(run_dir, sub)
                        RunA = d # Update RunA name for the plot titles
                        found_alt = True
                        break
            if found_alt:
                break
                
    try:
        filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR_ambient',f"{serial_number}")
    except FileNotFoundError:
        filesSparA = []
    if not filesSparA:
        try:
            filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR',f"{serial_number}")
        except FileNotFoundError:
            filesSparA = []
    
    try:
        filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD_ambient',f"{serial_number}")
    except FileNotFoundError:
        filesNPDA = []
        
    if not filesNPDA:
        try:
            filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD',f"{serial_number}")
        except FileNotFoundError:
            filesNPDA = []
    lmoFolderB = os.path.join(folder_path, area_folder, lmo_folder)
    filesSparB = search_files(lmoFolderB, '.s2p', f"{serial_number}")#'BenchtopNPDS'
    if not filesSparB and serial_number: filesSparB = search_files(lmoFolderB, '.s2p', "")
    filesNPDB = search_files(lmoFolderB, '.csv', f"{serial_number}")#'BenchtopNPDN'
    if not filesNPDB and serial_number: filesNPDB = search_files(lmoFolderB, '.csv', "")

    def extract_serial(filename):
        match = re.search(r'EM-\d+', filename)
        return match.group(0) if match else filename


    """Plot Functions"""

    def plotNPD(filesA, filesB):
        plt.figure(figsize=(8, 4), dpi=150)

        all_freqs = []
        all_noise = []
        all_labels = []

        # ---- Helper to load and smooth ---- #
        def load_np_data(file):
            df_all = pd.read_csv(file)
            num_df = df_all.apply(pd.to_numeric, errors='coerce')

            freq = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise = remove_nan(num_df.values[:, 1], remove_infinite=True)

            if n_avg > 1:
                noise = np.convolve(noise, np.ones(n_avg) / n_avg, mode='valid')
                freq = freq[int(n_avg / 2):int(1 - n_avg / 2):1]

            return freq, noise

        # ---- load files from both folders ---- #
        for file in filesA + filesB:
            serial = extract_serial(file)
            freq, noise = load_np_data(file)

            plt.plot(freq, noise, label=f'{serial[-21:-4:1]}')

            all_freqs.append(freq)
            all_noise.append(noise)
            all_labels.append(serial[-21:-4:1])

        if not all_freqs:
            return
        
        from scipy.interpolate import interp1d
        common_freq = np.linspace(freq_min, freq_max, 1000)
        all_noise_win = []
        for i in range(len(all_freqs)):
            f_interp = interp1d(all_freqs[i], all_noise[i], bounds_error=False, fill_value=np.nan)
            all_noise_win.append(f_interp(common_freq))
            
        all_noise_win = np.array(all_noise_win)
        ref_freq_win = common_freq

        # ---- compute average + bounds ---- #
        avg = np.nanmean(all_noise_win, axis=0)
        upper = avg + 2
        lower = avg - 2

        # ---- pass/fail only evaluated in 700–2100 ---- #
        fail_mask = (all_noise_win > upper) | (all_noise_win < lower)
        failed_indices = np.where(fail_mask.any(axis=1))[0]

        if len(failed_indices) > 0:
            status = "Failed"
            failed_units = np.array(all_labels)[failed_indices]
            print("Failed units:", failed_units)
        else:
            status = "Passed"

        # ---- plot bounds only in window ---- #
        plt.plot(ref_freq_win, lower, color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
        plt.plot(ref_freq_win, upper,  color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')

        # ---- formatting ---- #
        plt.xlim(all_freqs[0][0], all_freqs[0][-1])
        plt.ylim(-130, -90)
        plt.grid(True)

        title = f'Before and After: Noise Power, {status}'
        plt.title(title)
        plt.xlabel('Frequency (GHz)')
        plt.ylabel('NP (dBm)')

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')

        plt.axvline(x=freq_min, color='g')
        plt.axvline(x=freq_max, color='g')
        plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], 'r')

        plt.subplots_adjust(right=0.7)

        # ---- save file ---- #
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y%m%d")
        filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
        output_dir = output_folder
        save_path = os.path.join(output_dir, f"{formatted_date}_{filename_safe_title}")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        generated_plots.append(save_path)
        print(f"Plot saved to {save_path}")

        if show_plot == 1:
            plt.show()

    def plotNPDdiff(files):
        plt.figure(figsize=(7, 4), dpi=150)

        for i in range(0, 2, 1): # start=0, stop=2, step=1
            print(i)
            print(i + 2)
            serial1 = extract_serial(files[i])
            serial2 = extract_serial(files[i + 2])
            df_all1 = pd.read_csv(files[i])  # Read CSV with headers automatically detected
            df_all2 = pd.read_csv(files[int(2 * i + 1)])  # Read CSV with headers automatically detected
            num_df1 = df_all1.apply(pd.to_numeric, errors='coerce')  # 'raise' 'coerce' 'ignore'
            num_df2 = df_all2.apply(pd.to_numeric, errors='coerce')  # 'raise' 'coerce' 'ignore'
            freq_ghz1 = remove_nan(num_df1.values[:, 0], remove_infinite=True)
            freq_ghz2 = remove_nan(num_df2.values[:, 0], remove_infinite=True)
            noise_pow1 = remove_nan(num_df1.values[:, 1], remove_infinite=True)
            noise_pow2 = remove_nan(num_df2.values[:, 1], remove_infinite=True)
            if n_avg > 1:
                noise_pow1 = np.convolve(noise_pow1, np.ones(n_avg) / n_avg, mode='valid')
                noise_pow2 = np.convolve(noise_pow2, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz1 = freq_ghz1[int(n_avg / 2):int(1 - n_avg / 2):1]
                freq_ghz2 = freq_ghz2[int(n_avg / 2):int(1 - n_avg / 2):1]
            if np.all(freq_ghz2-freq_ghz1 == 0):
                np_diff = noise_pow2 - noise_pow1
                plt.plot(freq_ghz1, np_diff, label=f'{serial1[-14:-4:1]}')
            else:
                print("The frequencies are not the same")
        """
        maxOSi = np.argmax(abs(MR.s_db[reqS11Ns[0]:reqS11Ns[1]:1, 1, 0]))
        plt.plot(freq_ghz, MR.s_db[:, 1, 0],
                 label=f'{serial[-17:-11:1]}:max offset={MR.s_db[maxOSi + reqS11Ns[0], 1, 0]:.2f}dB')
        """
        plt.xlim(freq_ghz1[0], freq_ghz1[-1])
        plt.ylim(-10, 10)
        plt.grid(True)  # Enable grid lines

        title = f'{RunA},{RunB}: Noise Power Difference Pre-TSS vs Post-Burn In'
        plt.title(title)
        plt.xlabel('Frequency (GHz)')  # , fontsize='x-small'
        plt.ylabel('Noise Power Ratio (dB)')  # , fontsize='x-small'

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
        plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
        plt.axvline(x=freq_min, color='g', label='axvline - full height')
        plt.axvline(x=freq_max, color='g', label='axvline - full height')
        plt.subplots_adjust(right=0.7)
        # Save the figure
        current_date = datetime.now()  # Get the current date
        formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
        filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
        output_dir = output_folder
        save_path = os.path.join(output_dir, f"{formatted_date}_{filename_safe_title}")
        plt.savefig(save_path, dpi=300)
        generated_plots.append(save_path)
        print(Fore.BLUE + f"Plot saved to {save_path}")

        if show_plot == 1:  # View Plot
            plt.show()

    def plotS21(filesA,filesB):

        avg_collection = []
        file_coll = []
        ref_freq_ghz = None

        plt.figure(figsize=(7, 4), dpi=150)
        for file in filesA:
            #file_path = os.path.join(lmoFolder, file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9  # Convert to GHz
            serial = extract_serial(file)
            plt.plot(freq_ghz, net.s_db[:, 1, 0], label=f'{serial[-21:-4:1]}')
            
            from scipy.interpolate import interp1d
            common_freq = np.linspace(freq_min, freq_max, 1000)
            f_interp = interp1d(freq_ghz, net.s_db[:, 1, 0], bounds_error=False, fill_value=np.nan)
            avg_collection.append(f_interp(common_freq))
            file_coll.append(serial[-21:-4:1])
        ref_freq_ghz = freq_ghz if len(filesA) > 0 else None
        for file in filesB:
            #file_path = os.path.join(lmoFolder, file)
            net = rf.Network(file)
            freq_ghz = net.f / 1e9  # Convert to GHz
            serial = extract_serial(file)
            plt.plot(freq_ghz, net.s_db[:, 1, 0], label=f'{serial[-21:-4:1]}')
            
            from scipy.interpolate import interp1d
            common_freq = np.linspace(freq_min, freq_max, 1000)
            f_interp = interp1d(freq_ghz, net.s_db[:, 1, 0], bounds_error=False, fill_value=np.nan)
            avg_collection.append(f_interp(common_freq))
            file_coll.append(serial[-21:-4:1])
            if ref_freq_ghz is None: ref_freq_ghz = freq_ghz

        #--------PASS or FAIL--------#
        s21_avg = np.array(avg_collection)
        files_collected = np.array(file_coll)
        avg = np.nanmean(s21_avg, axis=0)
        ref_freq_ghz = np.linspace(freq_min, freq_max, 1000)
        upper_bound = avg + 2
        lower_bound = avg - 2
        fail_mask = (s21_avg > upper_bound) | (s21_avg < lower_bound)

        # Indices of failed datasets
        failed_indices = np.where(fail_mask.any(axis=1))[0]

        if len(failed_indices) > 0:
            status = "Failed"
            failed_files = files_collected[failed_indices]
            print("Failed files:", failed_files)
        else:
            status = "Passed"

        lb = lower_bound.copy()
        ub = upper_bound.copy()

        plt.plot(ref_freq_ghz, lb, color='red', alpha=1,
                 marker='o', markersize=5, markevery=100, label='Lower bound')

        plt.plot(ref_freq_ghz, ub, color='red', alpha=1,
                 marker='x', markersize=5, markevery=100, label='Upper bound')

        plt.xlim(freq_ghz[0], freq_ghz[-1])
        plt.ylim(-40, 40)
        plt.grid(True)  # Enable grid lines

        title = f'Before and After: Test Hat S21, {status}'
        plt.title(title)
        plt.xlabel('Frequency (GHz)')#, fontsize='x-small'
        plt.ylabel('S21 (dB)')#, fontsize='x-small'

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
        plt.axvline(x=freq_min, color='g', label='axvline - full height')
        plt.axvline(x=freq_max, color='g', label='axvline - full height')
        #plt.tight_layout()
        plt.subplots_adjust(right=0.8)
        # Save the figure
        current_date = datetime.now()  # Get the current date
        formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
        filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
        output_dir = output_folder
        save_path = os.path.join(output_dir, f"{formatted_date}_{filename_safe_title}")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        generated_plots.append(save_path)
        print(Fore.BLUE + f"Plot saved to {save_path}")
        print(status)

        if show_plot == 1:  # View Plot
            plt.show()

    def plotS11(files):
        plt.figure(figsize=(8, 4), dpi=150)
        i = 0
        for file in files:
            #file_path = os.path.join(lmoFolder, file)
            #net = rf.Network(file_path)
            print(i)
            i += 1
            net = rf.Network(file)
            freq_ghz = net.f / 1e9  # Convert to GHz
            maxS11 = max(net.s_db[reqS11Ns[0]:reqS11Ns[1]:1, 0, 0])
            serial = extract_serial(file)
            plt.plot(freq_ghz, net.s_db[:, 0, 0], label=f'{serial[-14:-4:1]}:max(S11)={maxS11:.2f}dB')

        plt.xlim(freq_ghz[0],freq_ghz[-1])
        plt.ylim(-30,0)
        plt.grid(True)  # Enable grid lines

        title = f'{RunA},{RunB}: Output Reflection'
        plt.title(title)
        plt.xlabel('Frequency (GHz)')#, fontsize='x-small'
        plt.ylabel('S11 (dB)')#, fontsize='x-small'

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
        plt.plot([freq_min, freq_max], [reqS11Val, reqS11Val], color='r')
        plt.axvline(x=freq_min, color='g', label='axvline - full height')
        plt.axvline(x=freq_max, color='g', label='axvline - full height')
        plt.subplots_adjust(right=0.7)
        # Save the figure
        current_date = datetime.now()  # Get the current date
        formatted_date = current_date.strftime("%Y%m%d")  # Format the date as Year-Month-Day
        filename_safe_title = title.replace(" ", "_").replace(":", "") + ".png"
        file_name_full = f"{formatted_date}_{filename_safe_title}"  # Specify output file name
        save_path = os.path.join(output_folder, file_name_full)
        plt.savefig(save_path, dpi=300)
        generated_plots.append(save_path)
        print(f"Plot saved to {save_path}")

        if show_plot == 1:  # View Plot
            plt.show()

    # === Generate plots ===
    if filesNPDA or filesNPDB:
        plotNPD(filesNPDA,filesNPDB)
        #plotNPDdiff(filesNPD)

    if filesSparA or filesSparB:
        plotS21(filesSparA,filesSparB)

    return generated_plots