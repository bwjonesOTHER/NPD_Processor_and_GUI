with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Fix bounds in plotNPD
old_npd_bound = """    if plot_density:
        plt.ylim(-170, -110)
    else:
        plt.ylim(-120, -90)"""

new_npd_bound = """    if plot_density:
        plt.ylim(-170, -110)
    else:
        plt.ylim(-130, -90)"""
content = content.replace(old_npd_bound, new_npd_bound)

# Fix bounds in plot_temp_deltas call for Test 1
old_delta_call = 'dp1 = plot_temp_deltas(np_averages, "Noise Power", "NP (dBm)", output_folder, ax1_ylim=(-120, -90), ax2_ylim=(0, 5))'
new_delta_call = 'dp1 = plot_temp_deltas(np_averages, "Noise Power", "NP (dBm)", output_folder, ax1_ylim=(-130, -90), ax2_ylim=(0, 5))'
content = content.replace(old_delta_call, new_delta_call)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
