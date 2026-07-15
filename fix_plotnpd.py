content = open('backend/plot_generator.py', 'r').read()

bad_block = """        if apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            if freq_cal is not None:
                loss_interp = np.interp(freq, freq_cal, total_loss_db)
                noise = noise + loss_interp
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp"""

good_block = """        if apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            if freq_cal is not None:
                loss_interp = np.interp(freq, freq_cal, total_loss_db)
                noise = noise + loss_interp"""

content = content.replace(bad_block, good_block)

open('backend/plot_generator.py', 'w').write(content)
