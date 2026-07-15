content = open('backend/plot_generator.py', 'r').read()

# Fix plotNPD signature
old_plotNPD_sig = "def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False):"
new_plotNPD_sig = "def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True):"
content = content.replace(old_plotNPD_sig, new_plotNPD_sig)

# Fix plotNPD body
old_plotNPD_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:"""
new_plotNPD_cal = """        if apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            if freq_cal is not None:
                loss_interp = np.interp(freq, freq_cal, total_loss_db)
                noise = noise + loss_interp"""
content = content.replace(old_plotNPD_cal, new_plotNPD_cal)

old_plotNPD_cal2 = """        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp
            
        if n_avg > 1:"""
new_plotNPD_cal2 = """        if n_avg > 1:"""
content = content.replace(old_plotNPD_cal2, new_plotNPD_cal2)


# Fix plotS21 signature
old_plotS21_sig = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder):"
new_plotS21_sig = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, apply_cal=True):"
content = content.replace(old_plotS21_sig, new_plotS21_sig)

# Fix plotS21 body
old_plotS21_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_data = s21_data + loss_interp"""
new_plotS21_cal = """        if apply_cal:
            freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
            if freq_cal is not None:
                loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
                s21_data = s21_data + loss_interp"""
content = content.replace(old_plotS21_cal, new_plotS21_cal)

# Fix Test 2/3 calls
old_call1 = "p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, \"\", output_folder, plot_density=False)"
new_call1 = "p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, \"\", output_folder, plot_density=False, apply_cal=False)"
content = content.replace(old_call1, new_call1)

old_call2 = "p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, \"\", output_folder, plot_density=True)"
new_call2 = "p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, \"\", output_folder, plot_density=True, apply_cal=False)"
content = content.replace(old_call2, new_call2)

old_call3 = "p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, \"\", output_folder)"
new_call3 = "p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, \"\", output_folder, apply_cal=False)"
content = content.replace(old_call3, new_call3)

open('backend/plot_generator.py', 'w').write(content)
