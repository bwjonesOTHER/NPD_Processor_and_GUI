content = open('backend/plot_generator.py', 'r').read()

old_s21_delta = 'plot_temp_deltas(s21_averages, "S21 Calibrated", "S21 (dB)", output_folder, ax1_ylim=(0, 30), ax2_ylim=(0, 5))'
new_s21_delta = 'plot_temp_deltas(s21_averages, "S21", "S21 (dB)", output_folder, ax1_ylim=(-40, 40), ax2_ylim=(-40, 40))'

content = content.replace(old_s21_delta, new_s21_delta)
open('backend/plot_generator.py', 'w').write(content)
