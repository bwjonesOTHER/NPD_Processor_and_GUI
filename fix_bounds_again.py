import re

content = open('backend/plot_generator.py', 'r').read()

# 1. Update plotNPD to set ylim for the main plots
old_npd_plot = """    plt.grid(True)
    title = f'Noise Power Density {title_suffix}, {status}' if plot_density else f'Noise Power {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NPD (dBm/Hz)') if plot_density else plt.ylabel('NP (dBm)')"""

new_npd_plot = """    plt.grid(True)
    if plot_density:
        plt.ylim(-170, -110)
    else:
        plt.ylim(-120, -90)
    
    title = f'Noise Power Density {title_suffix}, {status}' if plot_density else f'Noise Power {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('NPD (dBm/Hz)') if plot_density else plt.ylabel('NP (dBm)')"""
content = content.replace(old_npd_plot, new_npd_plot)

# 2. Update plotS21 to set ylim for the main plots
old_s21_plot = """    plt.grid(True)
    title = f'S21 Calibrated {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')"""

new_s21_plot = """    plt.grid(True)
    plt.ylim(0, 30)
    title = f'S21 Calibrated {title_suffix}, {status}'
    plt.title(title)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('S21 (dB)')"""
content = content.replace(old_s21_plot, new_s21_plot)

# 3. Update the delta plots bounds
# For S21 delta, change ax2_ylim from (0, 2) to (0, 5)
content = content.replace(
    'dp2 = plot_temp_deltas(s21_averages, "S21 Calibrated", "S21 (dB)", output_folder, ax1_ylim=(0, 30), ax2_ylim=(0, 2))',
    'dp2 = plot_temp_deltas(s21_averages, "S21 Calibrated", "S21 (dB)", output_folder, ax1_ylim=(0, 30), ax2_ylim=(0, 5))'
)

open('backend/plot_generator.py', 'w').write(content)
