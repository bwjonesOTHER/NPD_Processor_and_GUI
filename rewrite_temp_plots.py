import re

content = open('backend/plot_generator.py', 'r').read()

# 1. Fix S21 Calibration Math
content = content.replace("s21_corr = raw_s21 - loss_interp", "s21_corr = raw_s21 + loss_interp")

# 2. Add return for average traces in plotNPD and plotS21
# plotNPD return
content = content.replace(
    'return {"path": save_path, "status": status.lower()}',
    'return {"path": save_path, "status": status.lower(), "freq": ref_freq_win if len(all_noise_win)>0 else None, "avg": avg if len(all_noise_win)>0 else None}'
)

# 3. Add Temp Delta Plot functions
temp_plot_funcs = """

def plot_temp_deltas(data_dict, title, ylabel, output_folder):
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
    
    ax2 = ax1.twinx()
    ax2.plot(a_f, np.abs(a_v - h_v), label='|Amb - Hot|', color='orange', linestyle='dashed')
    ax2.plot(a_f, np.abs(a_v - c_v), label='|Amb - Cold|', color='cyan', linestyle='dashed')
    ax2.plot(a_f, np.abs(h_v - c_v), label='|Hot - Cold|', color='purple', linestyle='dashed')
    ax2.set_ylabel('Delta (dB)')
    
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
"""

# Insert temp_plot_funcs before def generate_plots
content = content.replace("def generate_plots(params):", temp_plot_funcs + "\ndef generate_plots(params):")

# 4. In Test 1 loop, collect averages and plot deltas
old_test1_loop = """        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)
            if p1: generated_plots.append(p1)
                
            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder)
            if p2: generated_plots.append(p2)"""

new_test1_loop = """        npd_averages = {}
        s21_averages = {}
        for name, tag in temp_tags:
            npdA = search_files(folderA, f"NPD{tag}") if tag else search_files(folderA, "NPD")
            npdB = search_files(folderB, f"NPD{tag}") if tag else search_files(folderB, "NPD")
            
            sparA = search_files(folderA, f"VSWR{tag}") if tag else search_files(folderA, "VSWR")
            sparB = search_files(folderB, f"VSWR{tag}") if tag else search_files(folderB, "VSWR")
                
            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)
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

content = content.replace(old_test1_loop, new_test1_loop)

open('backend/plot_generator.py', 'w').write(content)
