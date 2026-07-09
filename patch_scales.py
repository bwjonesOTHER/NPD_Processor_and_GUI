with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

import re
old_func_pattern = re.compile(r'    def render_temp_diff\(.*?except Exception as e:\n                print\(f"Error in {title}:", e\)', re.DOTALL)

new_func = """    def render_temp_diff(d25, d64, dn38, title):
        if d25 and d64 and dn38:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                freq = d25['freq_ref']
                # Interpolate to ensure same shapes
                trace_64 = np.interp(freq, d64['freq_ref'], d64['avg_trace'])
                trace_n38 = np.interp(freq, dn38['freq_ref'], dn38['avg_trace'])
                
                diff1 = np.abs(d25['avg_trace'] - trace_64)
                diff2 = np.abs(d25['avg_trace'] - trace_n38)
                diff3 = np.abs(trace_64 - trace_n38)

                fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
                
                # Plot original traces on primary y-axis
                l1 = ax1.plot(freq, d25['avg_trace'], label='25C Original', color='blue')
                l2 = ax1.plot(freq, trace_64, label='64C Original', color='red')
                l3 = ax1.plot(freq, trace_n38, label='-38C Original', color='cyan')
                
                ax1.set_xlabel('Frequency (GHz)')
                ax1.set_ylabel('Original Value')
                ax1.grid(True)
                
                # Plot deltas on secondary y-axis
                ax2 = ax1.twinx()
                l4 = ax2.plot(freq, diff1, label='|25C - 64C| Delta', color='orange', linestyle='--')
                l5 = ax2.plot(freq, diff2, label='|25C - (-38C)| Delta', color='purple', linestyle='--')
                l6 = ax2.plot(freq, diff3, label='|64C - (-38C)| Delta', color='green', linestyle='--')
                
                ax2.set_ylabel('Delta')
                
                # Separate scales for minimum overlap
                # Put originals on bottom half, deltas on top half
                all_orig = np.concatenate([d25['avg_trace'], trace_64, trace_n38])
                min_orig, max_orig = np.nanmin(all_orig), np.nanmax(all_orig)
                orig_range = max_orig - min_orig if max_orig != min_orig else 1
                
                all_diffs = np.concatenate([diff1, diff2, diff3])
                max_delta = np.nanmax(all_diffs)
                if max_delta == 0: max_delta = 1
                
                # Ax1 takes bottom half: expand top limit by 150% of range
                ax1.set_ylim(min_orig - orig_range * 0.1, max_orig + orig_range * 1.5)
                
                # Ax2 takes top half: expand bottom limit to 0 minus 150% of max_delta
                ax2.set_ylim(-max_delta * 1.5, max_delta * 1.2)
                
                # Combine legends and put outside the plot entirely
                lines = l1 + l2 + l3 + l4 + l5 + l6
                labels = [l.get_label() for l in lines]
                ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.1, 1), fontsize='small')
                
                plt.title(title)
                plt.xlim(freq[0], freq[-1])
                
                safe_title = title.replace(" ", "_").replace(":", "") + ".png"
                # bbox_inches='tight' ensures the outside legend isn't cut off
                plt.savefig(os.path.join(folder_path, safe_title), dpi=300, bbox_inches='tight')
                plt.close()
            except Exception as e:
                print(f"Error in {title}:", e)"""

content = old_func_pattern.sub(new_func, content)
with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
