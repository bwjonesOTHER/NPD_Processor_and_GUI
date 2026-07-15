content = open('backend/plot_generator.py', 'r').read()

old_s21_bounds = """    else:
        plt.ylim(0, 30)
        title = f'S21 {title_suffix}, {status}'"""
new_s21_bounds = """    else:
        plt.ylim(-40, 40)
        title = f'S21 {title_suffix}, {status}'"""
content = content.replace(old_s21_bounds, new_s21_bounds)

old_s21_delta = 'plot_temp_deltas(s21_averages, "S21", "S21 (dB)", output_folder, ax1_ylim=(0, 30), ax2_ylim=(0, 30))'
new_s21_delta = 'plot_temp_deltas(s21_averages, "S21", "S21 (dB)", output_folder, ax1_ylim=(-40, 40), ax2_ylim=(0, 30))'
content = content.replace(old_s21_delta, new_s21_delta)

open('backend/plot_generator.py', 'w').write(content)
