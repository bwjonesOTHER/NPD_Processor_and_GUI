import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import itertools
from datetime import datetime

my_colors = ['black', 'blue', 'orange', 'green', 'purple', 'pink', 'brown', 'cyan', 'gold', 'violet']
my_line_styles = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid',
                 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed', 'dashed']

def get_title(temperature, suffix):
    if temperature == 'All':
        return f"All Temps: {suffix}"
    return f"{temperature}: {suffix}"

def get_color_and_style():
    return itertools.cycle(my_colors), itertools.cycle(my_line_styles)

def render_NPD_plot(math_data, u_bound_offset, l_bound_offset, temperature, title_suffix, freq_min, freq_max, req_val, folder_path, show_plot):
    if math_data is None: return None
    
    plt.figure(figsize=(10, 6), dpi=150)
    color_cycle, line_style_cycle = get_color_and_style()
    
    freq_ref = math_data['freq_ref']
    for trace in math_data['traces']:
        c = next(color_cycle)
        line_style = next(line_style_cycle)
        plt.plot(freq_ref, trace['y'], label=trace['label'], color=c, linestyle=line_style)
        
    avg = math_data['avg_trace']
    upper = avg + u_bound_offset
    lower = avg - l_bound_offset
    
    plt.plot(freq_ref, avg, color='red', linestyle='--', label='Average')
    markevery_val = max(1, len(freq_ref) // 15)
    plt.plot(freq_ref, upper, color='red', alpha=1, marker='o', markersize=5, markevery=markevery_val, label='Upper bound')
    plt.plot(freq_ref, lower, color='red', alpha=1, marker='x', markersize=5, markevery=markevery_val, label='Lower bound')
    
    plt.xlim(freq_ref[0], freq_ref[-1])
    plt.ylim(-170, -110) if 'Density' in title_suffix else plt.ylim(-130, -90)
    plt.grid(True)
    
    title = get_title(temperature, title_suffix)
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NPD (dBm/Hz)' if 'Density' in title_suffix else 'NP (dBm)')
    
    if req_val is not None:
        plt.plot([freq_min, freq_max], [req_val, req_val], color='r', label='Req')
        
    plt.axvline(x=freq_min, color='grey', label='Band Edge')
    plt.axvline(x=freq_max, color='grey')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=0.15)
    
    # Legend is rendered last
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.subplots_adjust(right=0.7)
    
    date = datetime.now().strftime("%Y%m%d")
    safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{date}_{safe_title}")
    plt.savefig(save_path, dpi=300)
    if show_plot: plt.show()
    plt.close()
    return save_path

def render_S21_plot(math_data, temperature, title_suffix, freq_min, freq_max, folder_path, show_plot):
    if math_data is None: return None
    
    plt.figure(figsize=(10, 6), dpi=150)
    color_cycle, line_style_cycle = get_color_and_style()
    
    freq_ref = math_data['freq_ref']
    for trace in math_data['traces']:
        c = next(color_cycle)
        line_style = next(line_style_cycle)
        plt.plot(freq_ref, trace['y'], label=trace['label'], color=c, linestyle=line_style)
        
    avg = math_data['avg_trace']
    upper = avg + 4
    lower = avg - 4
    
    plt.plot(freq_ref, avg, color='red', linestyle='--', label='Average')
    markevery_val = max(1, len(freq_ref) // 15)
    plt.plot(freq_ref, upper, color='red', alpha=1, marker='o', markersize=5, markevery=markevery_val, label='Upper bound')
    plt.plot(freq_ref, lower, color='red', alpha=1, marker='x', markersize=5, markevery=markevery_val, label='Lower bound')
    
    plt.xlim(freq_ref[0], freq_ref[-1])
    plt.ylim(-40, 40)
    plt.grid(True)
    
    title = get_title(temperature, title_suffix)
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')
    
    plt.axvline(x=freq_min, color='grey', label='Band Edge')
    plt.axvline(x=freq_max, color='grey')
    plt.axvspan(xmin=freq_min, xmax=freq_max, color='grey', alpha=0.15)
    
    # Legend is rendered last
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.subplots_adjust(right=0.7)
    
    date = datetime.now().strftime("%Y%m%d")
    safe_title = title.replace(" ", "_").replace(":", "") + ".png"
    save_path = os.path.join(folder_path, f"{date}_{safe_title}")
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

