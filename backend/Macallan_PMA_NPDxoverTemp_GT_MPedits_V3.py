"""
Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py
===========================================
Plot generation script for Test 1 (Thermal NPD).
Analyzes S-Parameter and NPD data over varying temperatures
and generates comprehensive comparison plots against limits.
"""
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
from glob import glob
from colorama import init, Fore


def generate_plots(params):
    """
    Generates plots by locating data files across temperatures,
    processing them, and saving output PNGs.
    
    Args:
        params (dict): Execution parameters passed from the frontend.
    """

    folder_path = params.get('folder_path', '')
    runs = params.get('runs', [])
    RunA = runs[0] if len(runs) > 0 else ""
    RunB = runs[1] if len(runs) > 1 else ""

    freq_min = float(params.get('freq_min', 2.7))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Ns = [700,2100]
    reqS11Val = float(params.get('reqS11Val', -10))
    reqS21Val = float(params.get('reqS21Val', -14))

    n_avg = int(params.get('n_avg', 20))
    show_plot = 0

    #Creates set of line colors and styles to cycle through when plotting
    my_colors=['black','blue','orange','green','purple','pink','brown','cyan','gold','violet']
    my_line_styles=['solid','solid','solid','solid','solid','solid','solid','solid','solid','solid','dashed','dashed','dashed','dashed','dashed','dashed','dashed','dashed','dashed','dashed']
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)

    def search_files(root_dir, pattern):
        return glob(os.path.join(root_dir, "**", pattern), recursive=True)

    def remove_nan(arr, remove_infinite=False):
        """Cleans NumPy arrays by removing NaN and optionally infinite values."""
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

    """Collect and categorize files"""
    if not folder_path:
        raise ValueError("folder_path is missing in params")


    lmoFolderA = folder_path+'\\'+RunA

    filesSparA = search_files(lmoFolderA, "*VSWR*.s2p")
    filesSparA_25C = search_files(lmoFolderA, "*VSWR*ambient*.s2p")
    filesSparA_64C = search_files(lmoFolderA, "*VSWR*hot*.s2p")
    filesSparA_n38C = search_files(lmoFolderA, "*VSWR*cold*.s2p")


    filesNPDA = search_files(lmoFolderA, "*NPDOverTempNPD*.csv")
    filesNPDA_25C = search_files(lmoFolderA, "*NPDOverTempNPD*ambient*.csv")
    filesNPDA_64C = search_files(lmoFolderA, "*NPDOverTempNPD*hot*.csv")
    filesNPDA_n38C = search_files(lmoFolderA, "*NPDOverTempNPD*cold*.csv")



    cable_lossA=search_files(lmoFolderA, 'Base')
    # gainA=search_files(lmoFolderA,'Gain')
    #
    #
    #
    # specA_cable_loss = rf.Network('SAcable_MP_TM18-S1S1-72-M_SN20806201-005_02272026.s2p')
    # specA_s21=specA_cable_loss.s_db[:,1,0]




    lmoFolderB = folder_path+'\\'+RunB

    filesSparB = search_files(lmoFolderB, "*VSWR*.s2p")
    filesSparB_25C = search_files(lmoFolderB, "*VSWR*ambient*.s2p")
    filesSparB_64C = search_files(lmoFolderB, "*VSWR*hot*.s2p")
    filesSparB_n38C = search_files(lmoFolderB, "*VSWR*cold*.s2p")



    filesNPDB = search_files(lmoFolderB, "*NPDOverTempNPD*.csv")
    filesNPDB_25C = search_files(lmoFolderB, "*NPDOverTempNPD*ambient*.csv")
    filesNPDB_64C = search_files(lmoFolderB, "*NPDOverTempNPD*hot*.csv")
    filesNPDB_n38C = search_files(lmoFolderB, "*NPDOverTempNPD*cold*.csv")

    cable_lossB=search_files(lmoFolderB, 'Base')
    gainB=search_files(lmoFolderB,'Gain')

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
                    import re
                    match = re.search(r'sn0*(\d+)', file.lower())
                    sn_match = False
                    if match:
                        if int(match.group(1)) == cap_num_int:
                            sn_match = True
                            
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

    def load_specA_loss(folder):
        spec_files = search_files(folder, "SpecA")
        if not spec_files:
            print(f"No SpecA cable loss file found in: {folder}")
            return None

        try:
            if not spec_files:
                return 0
            net = rf.Network(spec_files[0])
            return net.s_db[:, 1, 0] if len(net.s_db) > 0 else None
        except:
            print(f"Problem loading SpecA file: {spec_files[0]}")
            return None

    def extract_serial(filename):
        match = re.search(r'EM-\d+', filename)
        return match.group(0) if match else filename

    #Determine if primary or redundant info
    def safe_s21_interp(file_path, target_freq):
        import skrf as rf
        import numpy as np
        if not file_path: return 0
        try:
            net = rf.Network(file_path)
            if len(net.s_db) == 0: return 0
            s21 = net.s_db[:, 1, 0]
            if len(s21) != len(target_freq) and len(s21) > 1:
                return np.interp(target_freq, net.f / 1e9, s21)
            return s21
        except:
            return 0

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

    """Plot Functions"""

    def plotNPD_single(filesA, temperature):
        if not filesA:
            print(f"No NPD files found for temperature: {temperature}")
            return

        plt.figure(figsize=(8, 4), dpi=150)

        # ------------ OPTIONAL SpecA loader ------------
        def load_specA(folder):
            files = search_files(folder, "SpecA")
            if not files:
                return None
            try:
                if not files:
                    return 0
                return (lambda n: n.s_db[:, 1, 0] if len(n.s_db) > 0 else None)(rf.Network(files[0]))
            except:
                return None

        specA_s21 = load_specA(lmoFolderA)

        # To store corrected traces aligned on the same freq grid
        corrected_curves = []
        freq_ref = None

        # ------------- PROCESS ALL FILES -------------
        for file in filesA:

            if not os.path.exists(file):
                continue

            serial = extract_serial(file)
            chain_type = extract_pri_red(file)

            # Load CSV
            df = pd.read_csv(file)
            num = df.apply(pd.to_numeric, errors='coerce')

            freq_ghz = remove_nan(num.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num.values[:, 1], remove_infinite=True)

            # Cable + bulkhead selection
            base_loss, bulk_loss = cap_searchA(file, lmoFolderA)
            cable_s21 = safe_s21_interp(base_loss, freq_ghz)
            bulk_s21 = safe_s21_interp(bulk_loss, freq_ghz)
            spec_s21 = safe_s21_interp(specA_s21, freq_ghz)

            # Smoothing
            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg / 2):int(1 - n_avg / 2)]

                if isinstance(cable_s21, np.ndarray):
                    cable_s21 = np.convolve(cable_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(bulk_s21, np.ndarray):
                    bulk_s21 = np.convolve(bulk_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(spec_s21, np.ndarray):
                    spec_s21 = np.convolve(spec_s21, np.ones(n_avg) / n_avg, mode='valid')

            # Apply corrections
            noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21

            # Use first frequency grid as reference
            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                # Interpolate onto reference grid
                noise_mod = np.interp(freq_ref, freq_ghz, noise_mod)

            corrected_curves.append(noise_mod)

            c = next(color_cycle)
            plt.plot(freq_ref, noise_mod, color=c, label=f"{serial[-32:-8]} {chain_type}")

        # ---------- Compute per-frequency average ----------
        corrected_curves = np.array(corrected_curves)
        avg_trace = np.mean(corrected_curves, axis=0)
        upper_trace = avg_trace + 2
        lower_trace = avg_trace - 2

        # ---------- Slice 2.7–4.1 GHz band ----------
        mask = (freq_ref >= 2.7) & (freq_ref <= 4.1)
        band_ok = np.all(
            (corrected_curves[:, mask] >= lower_trace[mask]) &
            (corrected_curves[:, mask] <= upper_trace[mask])
        )

        # PASS / FAIL
        print("PASS" if band_ok else "FAIL")

        # ---------- Plot per-frequency bounds ----------

        mask = (freq_ref >= 2.7) & (freq_ref <= 4.1)

        plt.plot(freq_ref[mask], avg_trace[mask],
                 color='red', linestyle='--', label="Average")

        plt.plot(freq_ref[mask], upper_trace[mask],
                 color='red', alpha=1, marker='o', markersize=5, markevery=max(1, len(freq_ghz)//20),
                 label='Upper bound')

        plt.plot(freq_ref[mask], lower_trace[mask],
                 color='red', alpha=1, marker='x', markersize=5, markevery=max(1, len(freq_ghz)//20),
                 label='Lower bound')

                 # ---------- Final Plot Formatting ----------
        plt.xlim(freq_ref[0], freq_ref[-1])
        plt.ylim(-130, -90)
        plt.grid(True)

        title = f"{RunA} {RunB} {temperature}: Noise Power"
        plt.title(title)
        plt.xlabel("Frequency (GHz)")
        plt.ylabel("NP (dBm)")

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)

        plt.axvline(2.7, color='grey')
        plt.axvline(4.1, color='grey')
        plt.axvspan(2.7, 4.1, color='grey', alpha=0.15)

        plt.subplots_adjust(right=0.7)

        # Save
        date = datetime.now().strftime("%Y%m%d")
        safe = title.replace(" ", "_").replace(":", "") + ".png"
        save_path = os.path.join(folder_path, f"{date}_{safe}")
        plt.savefig(save_path, dpi=300)
        print(Fore.BLUE + f"Plot saved to {save_path}")
        print("\n")

        if show_plot:
            plt.show()

    def plotNPD(filesA, filesB, temperature):
        if not filesA and not filesB:
            print(f"No NPD files found for temperature: {temperature}")
            return

        plt.figure(figsize=(8, 4), dpi=150)

        # Load optional SpecA
        def load_specA(folder):
            files = search_files(folder, "SpecA")
            if not files:
                return None
            try:
                if not files:
                    return 0
                return (lambda n: n.s_db[:, 1, 0] if len(n.s_db) > 0 else None)(rf.Network(files[0]))
            except:
                return None

        specA_A = load_specA(lmoFolderA)
        specA_B = load_specA(lmoFolderB)

        # To store corrected traces
        corrected_curves = []
        freq_ref = None

        # ---------- Helper function ----------
        def process_file(file, folder, specA_s21, cap_search_func):
            df = pd.read_csv(file)
            num = df.apply(pd.to_numeric, errors="coerce")

            freq_ghz = remove_nan(num.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num.values[:, 1], remove_infinite=True)

            base_loss, bulk_loss = cap_search_func(file, folder)
            cable_s21 = safe_s21_interp(base_loss, freq_ghz)
            bulk_s21 = safe_s21_interp(bulk_loss, freq_ghz)
            spec_s21 = safe_s21_interp(specA_s21, freq_ghz)

            # Smoothing
            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode="valid")
                freq_ghz = freq_ghz[int(n_avg / 2):int(1 - n_avg / 2)]

                if isinstance(cable_s21, np.ndarray):
                    cable_s21 = np.convolve(cable_s21, np.ones(n_avg) / n_avg, mode="valid")
                if isinstance(bulk_s21, np.ndarray):
                    bulk_s21 = np.convolve(bulk_s21, np.ones(n_avg) / n_avg, mode="valid")
                if isinstance(spec_s22, np.ndarray):
                    spec_s21 = np.convolve(spec_s21, np.ones(n_avg) / n_avg, mode="valid")

            noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21
            return freq_ghz, noise_mod

        # ---------- Process Run A ----------
        for file in filesA:
            freq_ghz, noise_mod = process_file(file, lmoFolderA, specA_A, cap_searchA)

            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                noise_mod = np.interp(freq_ref, freq_ghz, noise_mod)

            corrected_curves.append(noise_mod)

            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            c = next(color_cycle)
            plt.plot(freq_ref, noise_mod, color=c, label=f"{serial[-32:-8]} {chain_type} (A)")

        # ---------- Process Run B ----------
        for file in filesB:
            freq_ghz, noise_mod = process_file(file, lmoFolderB, specA_B, cap_searchB)

            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                noise_mod = np.interp(freq_ref, freq_ghz, noise_mod)

            corrected_curves.append(noise_mod)

            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            c = next(color_cycle)
            plt.plot(freq_ref, noise_mod, color=c, label=f"{serial[-32:-8]} {chain_type} (B)")

        # ---------- Per-frequency average ----------
        corrected_curves = np.array(corrected_curves)
        avg_trace = np.mean(corrected_curves, axis=0)
        upper_trace = avg_trace + 2
        lower_trace = avg_trace - 2

        # ---------- Slice band ----------
        mask = (freq_ref >= 2.7) & (freq_ref <= 4.1)

        band_ok = np.all(
            (corrected_curves[:, mask] <= upper_trace[mask]) &
            (corrected_curves[:, mask] >= lower_trace[mask])
        )
        print("PASS" if band_ok else "FAIL")

        # ---------- Plot bounds only in band ----------
        plt.plot(freq_ref[mask], avg_trace[mask], color='red', linestyle='--', label="Average")
        plt.plot(freq_ref[mask], upper_trace[mask], color='red', marker='o', markersize=5, markevery=10,
                 label="Upper bound")
        plt.plot(freq_ref[mask], lower_trace[mask], color='red', marker='x', markersize=5, markevery=10,
                 label="Lower bound")

        # ---------- Formatting ----------
        plt.xlim(freq_ref[0], freq_ref[-1])
        plt.ylim(-130, -90)
        plt.grid(True)

        title = f"{RunA} {RunB} {temperature}: Noise Power"
        plt.title(title)
        plt.xlabel("Frequency (GHz)")
        plt.ylabel("NP (dBm)")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)

        plt.axvline(2.7, color='grey')
        plt.axvline(4.1, color='grey')
        plt.axvspan(2.7, 4.1, color='grey', alpha=0.15)

        plt.subplots_adjust(right=0.7)

        # Save
        date = datetime.now().strftime("%Y%m%d")
        safe = title.replace(" ", "_").replace(":", "") + ".png"
        save_path = os.path.join(folder_path, f"{date}_{safe}")
        plt.savefig(save_path, dpi=300)
        print(Fore.BLUE + f"Plot saved to {save_path}")

        if show_plot:
            plt.show()


    def plotGT(filesA,filesB,temperature,specA_s21,cable_lossA, cable_lossB,gainA,gainB):
        plt.figure(figsize=(8, 4), dpi=150)
        specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
        color_cycle = itertools.cycle(my_colors)
        line_styles_cycle = itertools.cycle(my_line_styles)
        for file in filesA:
            serial = extract_serial(file)
            chain_type=extract_pri_red(file)
            serial_number=extract_serial_number

            last_filename=file[-16:-13]
            last_filename=last_filename
            loss=[s for s in cable_lossA if last_filename in s]
            loss = loss[0] if loss else None



            tile_serial=file[-16:-13]
            gain=[s for s in gainA if tile_serial in s]
            gain = gain[0] if gain else None
            if gain:
                gain_values=np.array(pd.read_csv(gain))
                gain_values=gain_values[:,1]
            else:
                gain_values = 0
            if loss:
                UUT_cable=rf.Network(loss)
                UUT_cable_s21=UUT_cable.s_db[:,1,0]
            else:
                UUT_cable_s21 = 0


            df_all = pd.read_csv(file)# Read CSV with headers automatically detected
            num_df = df_all.apply(pd.to_numeric, errors='coerce')#'raise' 'coerce' 'ignore'
            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            noise_pow_den=remove_nan(num_df.values[:, 2], remove_infinite=True)

            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
                UUT_cable_s21= np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')


            noise_pow_mod=noise_pow_den-specA_s21-UUT_cable_s21


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

            last_filename = file[-16:-13]
            last_filename = last_filename

            loss = [s for s in cable_lossB if last_filename in s]
            loss = loss[0] if loss else None


            tile_serial = file[-16:-13]
            gain = [s for s in gainB if tile_serial in s]
            gain = gain[0] if gain else None
            gain_values = np.array(pd.read_csv(gain))
            gain_values = gain_values[:, 1]
            if loss:
                UUT_cable=rf.Network(loss)
                UUT_cable_s21=UUT_cable.s_db[:,1,0]
            else:
                UUT_cable_s21 = 0

            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            noise_pow_den=remove_nan(num_df.values[:, 2], remove_infinite=True)
            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
                noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
                UUT_cable_s21= np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')

            noise_pow_mod=noise_pow_den-specA_s21-UUT_cable_s21
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

        title = f'{RunA} {RunB} {temperature}: G_T'
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

    def plotS21(filesA, filesB, temperature):
        if not filesA and not filesB:
            print(f"No S21 files found for temperature: {temperature}")
            return

        plt.figure(figsize=(8, 4), dpi=150)

        corrected_curves = []
        freq_ref = None


        # ---------- Process Run A ----------
        for file in filesA:
            if not os.path.exists(file):
                continue

            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            s21 = net.s_db[:, 1, 0]

            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                s21 = np.interp(freq_ref, freq_ghz, s21)

            corrected_curves.append(s21)

            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            c = next(color_cycle)
            plt.plot(freq_ref, s21, color=c, label=f"{serial[-16:-8]} {chain_type} (A)")

        # ---------- Process Run B ----------
        for file in filesB:
            if not os.path.exists(file):
                continue

            net = rf.Network(file)
            freq_ghz = net.f / 1e9
            s21 = net.s_db[:, 1, 0]

            if freq_ref is None:
                freq_ref = freq_ghz
            else:
                s21 = np.interp(freq_ref, freq_ghz, s21)

            corrected_curves.append(s21)

            serial = extract_serial(file)
            chain_type = extract_pri_red(file)
            c = next(color_cycle)
            plt.plot(freq_ref, s21, color=c, label=f"{serial[-16:-8]} {chain_type} (B)")


        # ---------- Per-frequency average ----------
        corrected_curves = np.array(corrected_curves)
        avg_trace = np.mean(corrected_curves, axis=0)
        upper_trace = avg_trace + 4
        lower_trace = avg_trace - 4

        # ---------- Slice to band ----------
        mask = (freq_ref >= 2.7) & (freq_ref <= 4.1)

        band_ok = np.all(
            (corrected_curves[:, mask] <= upper_trace[mask]) &
            (corrected_curves[:, mask] >= lower_trace[mask])
        )
        print("PASS" if band_ok else "FAIL")

        # ---------- Plot bounds only in band ----------
        plt.plot(freq_ref[mask], avg_trace[mask], color='red', linestyle='--', label="Average")
        plt.plot(freq_ref[mask], upper_trace[mask], color='red', marker='o', markersize=5, markevery=max(1, len(freq_ghz)//20),
                 label="Upper bound")
        plt.plot(freq_ref[mask], lower_trace[mask], color='red', marker='x', markersize=5, markevery=max(1, len(freq_ghz)//20),
                 label="Lower bound")

        # ---------- Formatting ----------
        plt.xlim(freq_ref[0], freq_ref[-1])
        plt.ylim(-40, 40)
        plt.grid(True)

        title = f"{RunA} {RunB} {temperature}: Test Hat S21"
        plt.title(title)
        plt.xlabel("Frequency (GHz)")
        plt.ylabel("S21 (dB)")

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)

        plt.axvline(2.7, color='grey')
        plt.axvline(4.1, color='grey')
        plt.axvspan(2.7, 4.1, color='grey', alpha=0.15)

        plt.subplots_adjust(right=0.7)

        # Save
        date = datetime.now().strftime("%Y%m%d")
        safe = title.replace(" ", "_").replace(":", "") + ".png"
        save_path = os.path.join(folder_path, f"{date}_{safe}")
        plt.savefig(save_path, dpi=300)
        print(Fore.BLUE + f"Plot saved to {save_path}")

        if show_plot:
            plt.show()

    # === Generate plots ===
    # if len(filesNPDA)>0 and len(filesNPDB)>0:
    #     temperature='All'
    #     plotGT(filesNPDA,filesNPDB,temperature,specA_s21,cable_lossA,cable_lossB,gainA,gainB)
    # elif len(filesNPDA)==0:
    #     temperature='All'
    #     plotNPD_single(filesNPDB,temperature,specA_s21,cable_lossB)
    # elif len(filesNPDB)==0:
    #     temperature='All'
    #     plotNPD_single(filesNPDA,temperature,specA_s21,cable_lossA)
    #
    # if filesNPDA_25C and filesNPDB_25C:
    #     temperature='25C'
    #     plotGT(filesNPDA_25C,filesNPDB_25C,temperature,specA_s21,cable_lossA,cable_lossB,gainA,gainB)
    #
    # if filesNPDA_64C and filesNPDB_64C:
    #     temperature='64C'
    #     plotGT(filesNPDA_64C,filesNPDB_64C,temperature,specA_s21,cable_lossA,cable_lossB,gainA,gainB)
    #
    # if filesNPDA_n38C and filesNPDB_n38C:
    #     temperature='-38C'
    #     plotGT(filesNPDA_n38C,filesNPDB_n38C,temperature,specA_s21,cable_lossA,cable_lossB,gainA,gainB)

    temperature='All'

    plotNPD_single(filesNPDA,temperature)

    temperature = 'All'
    plotS21(filesSparA, filesSparB, temperature)

    temperature='25C'
    plotS21(filesSparA_25C,filesSparB_25C, temperature)
    plotNPD_single(filesNPDA_25C, temperature)

    temperature='64C'
    plotS21(filesSparA_64C, filesSparB_64C, temperature)
    plotNPD_single(filesNPDA_64C, temperature)

    temperature='-38C'
    plotS21(filesSparA_n38C, filesSparB_n38C, temperature)
    plotNPD_single(filesNPDA_n38C, temperature)

    # if len(filesNPDA)>0 and len(filesNPDB)>0:
    #     temperature='All'
    #     plotNPD(filesNPDA,filesNPDB,temperature)
    # elif len(filesNPDA)==0:
    #     temperature='All'
    #     plotNPD_single(filesNPDB,temperature,specA_s21,cable_lossB)
    # elif len(filesNPDB)==0:
    #     temperature='All'
    #     plotNPD_single(filesNPDA,temperature,specA_s21,cable_lossA)
    # #
    # if filesNPDA_25C and filesNPDB_25C:
    #     temperature='25C'
    #     plotNPD(filesNPDA_25C,filesNPDB_25C,temperature)
    # elif len(filesNPDA_25C)==0:
    #     temperature='25C'
    #     plotNPD_single(filesNPDB_25C,temperature,specA_s21,cable_lossB)
    # elif len(filesNPDB_25C)==0:
    #     temperature='25C'
    #     plotNPD_single(filesNPDA_25C,temperature,specA_s21,cable_lossA)
    # # #
    # if filesNPDA_64C and filesNPDB_64C:
    #     temperature='64C'
    #     plotNPD(filesNPDA_64C,filesNPDB_64C,temperature)
    # elif len(filesNPDA_64C)==0:
    #     temperature='64C'
    #     plotNPD_single(filesNPDB_64C,temperature,specA_s21,cable_lossB)
    # elif len(filesNPDB_64C)==0:
    #     temperature='64C'
    #     plotNPD_single(filesNPDA_64C,temperature,specA_s21,cable_lossA)
    # #
    # if filesNPDA_n38C and filesNPDB_n38C:
    #     temperature='-38C'
    #     plotNPD(filesNPDA_n38C,filesNPDB_n38C,temperature)
    # elif len(filesNPDA_n38C)==0:
    #     temperature='-38C'
    #     plotNPD_single(filesNPDB_n38C,temperature,specA_s21,cable_lossB)
    # elif len(filesNPDB_n38C)==0:
    #     temperature='-38C'
    #     plotNPD_single(filesNPDA_n38C,temperature,specA_s21,cable_lossA)


    #
    # if filesSparA and filesSparB:
    #     temperature='All'
    #     plotS21(filesSparA,filesSparB,temperature)
    # elif len(filesSparA)==0:
    #     temperature='All'
    #     plotS21_single(filesSparB,temperature)
    # elif len(filesSparB)==0:
    #     temperature='All'
    #     plotS21_single(filesSparA,temperature)
    # #
    # if filesSparA_25C and filesSparB_25C:
    #     temperature='25C'
    #     plotS21(filesSparA_25C,filesSparB_25C,temperature)
    # elif len(filesSparA_25C)==0:
    #     temperature='25C'
    #     plotS21_single(filesSparB_25C,temperature)
    # elif len(filesSparB_25C)==0:
    #     temperature='25C'
    #     plotS21_single(filesSparA_25C,temperature)
    # #
    # if filesSparA_64C and filesSparB_64C:
    #     temperature='64C'
    #     plotS21(filesSparA_64C,filesSparB_64C,temperature)
    # elif len(filesSparA_64C)==0:
    #     temperature='64C'
    #     plotS21_single(filesSparB_64C,temperature)
    # elif len(filesSparB_64C)==0:
    #     temperature='64C'
    #     plotS21_single(filesSparA_64C,temperature)
    # if filesSparA_n38C and filesSparB_n38C:
    #     temperature='-38C'
    #     plotS21(filesSparA_n38C,filesSparB_n38C,temperature)
    # elif len(filesSparA_n38C)==0:
    #     temperature='-38C'
    #     plotS21_single(filesSparB_n38C,temperature)
    # elif len(filesSparB_n38C)==0:
    #     temperature='-38C'
    #     plotS21_single(filesSparA_n38C,temperature)
    """
    if filesS11:
        plotS22(filesS11)
    
    if filesSpar:
        #plotS21(filesSpar)
        plotS21smooth(filesSpar)
    
    if filesSpar:
        plotMagRat(filesSpar)
    
    if filesSpar:
        plotPD(filesSpar)
    """

    # Collect all generated PNGs
    png_files = glob(os.path.join(folder_path, '*.png'))
    return png_files

if __name__ == "__main__":
    # For testing, we could pass dummy params here
    pass
