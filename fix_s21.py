content = open('backend/plot_generator.py', 'r').read()

# Remove calibration application from plotS21
old_s21_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_corr = raw_s21 + loss_interp
        else:
            s21_corr = raw_s21"""
new_s21_cal = """        s21_corr = raw_s21"""
content = content.replace(old_s21_cal, new_s21_cal)

# Remove the hardcoded bounds from plotS21
old_s21_bounds = """    plt.grid(True)
    plt.ylim(0, 30)
    title = f'S21 Calibrated {title_suffix}, {status}'"""
new_s21_bounds = """    plt.grid(True)
    title = f'S21 {title_suffix}, {status}'"""
content = content.replace(old_s21_bounds, new_s21_bounds)

open('backend/plot_generator.py', 'w').write(content)
