import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import itertools
from datetime import datetime

def render_NPD_plot(math_data, u_bound_offset, l_bound_offset, temperature, title_suffix, freq_min, freq_max, req_val, folder_path, show_plot):
    if math_data is None: return None
    
    plt.figure(figsize=(8, 4), dpi=150)
    
    freq_ref = math_data['freq_ref']
    traces = math_data['traces']
    avg = math_data['avg_trace']
    upper = avg + u_bound_offset
    lower = avg - l_bound_offset
    
    # Calculate pass/fail inside the freq_min, freq_max window
    mask = (freq_ref >= freq_min) & (freq_ref <= freq_max)
    
    failed_labels = []
    for trace in traces:
        y = trace['y']
        plt.plot(freq_ref, y, label=trace['label'])
        
        # Check fail within window
        if np.any(y[mask] > upper[mask]) or np.any(y[mask] < lower[mask]):
            failed_labels.append(trace['label'])
            
    if failed_labels:
        status = "Failed"
        print(f"[{temperature}] Failed units ({title_suffix}):", failed_labels)
    else:
        status = "Passed"
        
    plt.plot(freq_ref[mask], lower[mask], color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
    plt.plot(freq_ref[mask], upper[mask], color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')
    
    plt.xlim(freq_ref[0], freq_ref[-1])
    plt.ylim(-130, -90)
    plt.grid(True)
    
    title = f"{temperature}: {title_suffix}, {status}"
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NP (dBm)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    
    plt.axvline(x=freq_min, color='g')
    plt.axvline(x=freq_max, color='g')
    if req_val is not None:
        plt.plot([freq_min, freq_max], [req_val, req_val], 'r', label='Req')
        
    plt.subplots_adjust(right=0.7)
    
    date = datetime.now().strftime("%Y%m%d")
    safe_title = title.replace(" ", "_").replace(":", "").replace(",", "") + ".png"
    save_path = os.path.join(folder_path, f"{date}_{safe_title}")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    if show_plot: plt.show()
    plt.close()
    return save_path

def render_S21_plot(math_data, temperature, title_suffix, freq_min, freq_max, folder_path, show_plot):
    if math_data is None: return None
    
    plt.figure(figsize=(7, 4), dpi=150)
    
    freq_ref = math_data['freq_ref']
    traces = math_data['traces']
    avg = math_data['avg_trace']
    upper = avg + 2
    lower = avg - 2
    
    # Calculate pass/fail inside the freq_min, freq_max window
    mask = (freq_ref >= freq_min) & (freq_ref <= freq_max)
    
    failed_labels = []
    for trace in traces:
        y = trace['y']
        plt.plot(freq_ref, y, label=trace['label'])
        
        # Check fail within window
        if np.any(y[mask] > upper[mask]) or np.any(y[mask] < lower[mask]):
            failed_labels.append(trace['label'])
            
    if failed_labels:
        status = "Failed"
        print(f"[{temperature}] Failed units ({title_suffix}):", failed_labels)
    else:
        status = "Passed"
        
    plt.plot(freq_ref[mask], lower[mask], color='red', alpha=1, marker='o', markersize=5, markevery=100, label='Lower bound')
    plt.plot(freq_ref[mask], upper[mask], color='red', alpha=1, marker='x', markersize=5, markevery=100, label='Upper bound')
    
    plt.xlim(freq_ref[0], freq_ref[-1])
    plt.ylim(-40, 40)
    plt.grid(True)
    
    title = f"{temperature}: {title_suffix}, {status}"
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')
    plt.axvline(x=freq_min, color='g', label='axvline - full height')
    plt.axvline(x=freq_max, color='g', label='axvline - full height')
    
    plt.subplots_adjust(right=0.8)
    
    date = datetime.now().strftime("%Y%m%d")
    safe_title = title.replace(" ", "_").replace(":", "").replace(",", "") + ".png"
    save_path = os.path.join(folder_path, f"{date}_{safe_title}")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    if show_plot: plt.show()
    plt.close()
    return save_path

def s21_temp_diff_plot(diff_y, freq_ref, title, folder_path, show_plot):
    plt.figure(figsize=(10, 6), dpi=150)
    plt.plot(freq_ref, diff_y, color='black')
    plt.xlim(freq_ref[0], freq_ref[-1])
    plt.ylim(-2, 2)
    plt.grid(True)
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Delta S21 (dB)')
    
    date = datetime.now().strftime("%Y%m%d")
    safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{date}_{safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot: plt.show()
    plt.close()
    return save_path

# To preserve API compatibility if anything else imports it
def search_files(root_dir, pattern):
    from math_v3 import search_files as sf
    return sf(root_dir, pattern)

