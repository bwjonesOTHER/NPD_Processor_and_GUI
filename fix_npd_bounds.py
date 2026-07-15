import re

content = open('backend/plot_generator.py', 'r').read()

# 1. Update plotNPD signature and load_np_data
content = content.replace(
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder):',
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder, plot_density=False):'
)

old_load_np_data = """        freq = remove_nan(num_df.values[:, 0], remove_infinite=True)
        noise = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if len(noise) == 0 or len(freq) == 0:"""

new_load_np_data = """        freq = remove_nan(num_df.values[:, 0], remove_infinite=True)
        if plot_density:
            try:
                noise = remove_nan(num_df.values[:, 2], remove_infinite=True)
            except IndexError:
                noise = np.array([])
        else:
            noise = remove_nan(num_df.values[:, 1], remove_infinite=True)
        if len(noise) == 0 or len(freq) == 0:"""
content = content.replace(old_load_np_data, new_load_np_data)

# Update plotNPD title and labels
content = content.replace(
    "title = f'Noise Power {title_suffix}, {status}'",
    "title = f'Noise Power Density {title_suffix}, {status}' if plot_density else f'Noise Power {title_suffix}, {status}'"
)
content = content.replace(
    "plt.ylabel('NP (dBm)')",
    "plt.ylabel('NPD (dBm/Hz)') if plot_density else plt.ylabel('NP (dBm)')"
)

# 2. Update plot_temp_deltas signature and set ylims
content = content.replace(
    "def plot_temp_deltas(data_dict, title, ylabel, output_folder):",
    "def plot_temp_deltas(data_dict, title, ylabel, output_folder, ax1_ylim=None, ax2_ylim=None):"
)
content = content.replace(
    "ax1.grid(True)",
    "ax1.grid(True)\n    if ax1_ylim: ax1.set_ylim(ax1_ylim)"
)
content = content.replace(
    "ax2.set_ylabel('Delta (dB)')",
    "ax2.set_ylabel('Delta (dB)')\n    if ax2_ylim: ax2.set_ylim(ax2_ylim)"
)

# 3. Update the Test 1 loop to call plot_density=True and pass ylims
old_test1_loop = """        npd_averages = {}
        s21_averages = {}
        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder)
            if p1: 
                generated_plots.append(p1)
                npd_averages[name] = (p1.get("freq"), p1.get("avg"))
                
            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder)
            if p2: 
                generated_plots.append(p2)
                s21_averages[name] = (p2.get("freq"), p2.get("avg"))
                
        dp1 = plot_temp_deltas(npd_averages, "Noise Power", "NP (dBm)", output_folder)
        if dp1: generated_plots.append(dp1)
        dp2 = plot_temp_deltas(s21_averages, "S21 Calibrated", "S21 (dB)", output_folder)
        if dp2: generated_plots.append(dp2)"""

new_test1_loop = """        np_averages = {}
        npd_averages = {}
        s21_averages = {}
        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder, plot_density=False)
            if p1: 
                generated_plots.append(p1)
                np_averages[name] = (p1.get("freq"), p1.get("avg"))
                
            p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder, plot_density=True)
            if p1_den and p1_den.get("freq") is not None:
                generated_plots.append(p1_den)
                npd_averages[name] = (p1_den.get("freq"), p1_den.get("avg"))
                
            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder)
            if p2: 
                generated_plots.append(p2)
                s21_averages[name] = (p2.get("freq"), p2.get("avg"))
                
        dp1 = plot_temp_deltas(np_averages, "Noise Power", "NP (dBm)", output_folder, ax1_ylim=(-120, -90), ax2_ylim=(0, 5))
        if dp1: generated_plots.append(dp1)
        dp1_den = plot_temp_deltas(npd_averages, "Noise Power Density", "NPD (dBm/Hz)", output_folder, ax1_ylim=(-170, -110), ax2_ylim=(0, 5))
        if dp1_den: generated_plots.append(dp1_den)
        dp2 = plot_temp_deltas(s21_averages, "S21 Calibrated", "S21 (dB)", output_folder, ax1_ylim=(0, 30), ax2_ylim=(0, 2))
        if dp2: generated_plots.append(dp2)"""

content = content.replace(old_test1_loop, new_test1_loop)

# 4. Update the benchtop loop to explicitly pass plot_density=False
content = content.replace(
    'p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder)',
    'p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder, plot_density=False)'
)

open('backend/plot_generator.py', 'w').write(content)
