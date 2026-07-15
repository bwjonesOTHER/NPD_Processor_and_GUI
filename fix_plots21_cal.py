with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_s21 = """        if test_type != 1:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)"""

new_s21 = """        if test_type != 1 and apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)"""

content = content.replace(old_s21, new_s21)

old_title = """    if test_type != 1:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'"""

new_title = """    if test_type != 1 and apply_cal:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'"""

content = content.replace(old_title, new_title)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

