import re

content = open('backend/plot_generator.py', 'r').read()

# Update definition
old_def = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder):"
new_def = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=1):"
content = content.replace(old_def, new_def)

# Restore calibration for test_type != 1
old_s21_cal = "        s21_corr = raw_s21"
new_s21_cal = """        if test_type != 1:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            if freq_cal is not None:
                loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
                s21_corr = raw_s21 + loss_interp
            else:
                s21_corr = raw_s21
        else:
            s21_corr = raw_s21"""
content = content.replace(old_s21_cal, new_s21_cal)

# Restore bounds for test_type != 1
old_s21_bounds = """    plt.grid(True)
    title = f'S21 {title_suffix}, {status}'"""
new_s21_bounds = """    plt.grid(True)
    if test_type != 1:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'
    else:
        title = f'S21 {title_suffix}, {status}'"""
content = content.replace(old_s21_bounds, new_s21_bounds)

# Update the call in generate_plots
old_call = "plotS21(run_a_files, run_b_files, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder)"
new_call = "plotS21(run_a_files, run_b_files, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type)"
content = content.replace(old_call, new_call)

open('backend/plot_generator.py', 'w').write(content)
