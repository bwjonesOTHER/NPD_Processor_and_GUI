import re

content = open('backend/plot_generator.py', 'r').read()

# Add debug prints to get_calibration_loss
old_get_cal = """    for f in cal_files_to_load:
        try:
            net = rf.Network(f)
            freq_ghz = net.f / 1e9
            loss_db = -net.s_db[:, 1, 0]
            
            if freq_ref is None:
                freq_ref = freq_ghz
                total_loss = np.zeros_like(freq_ref)
                
            ls_interp = np.interp(freq_ref, freq_ghz, loss_db)
            total_loss += ls_interp
        except Exception:
            pass
            
    return freq_ref, total_loss"""

new_get_cal = """    print(f"\\nDEBUG get_cal: Processing file {filepath}")
    print(f"DEBUG get_cal: Found cal files: {cal_files_to_load}")
    
    for f in cal_files_to_load:
        try:
            net = rf.Network(f)
            freq_ghz = net.f / 1e9
            loss_db = -net.s_db[:, 1, 0]
            print(f"DEBUG get_cal: Loaded {f} (loss={loss_db[0]:.2f}dB to {loss_db[-1]:.2f}dB)")
            
            if freq_ref is None:
                freq_ref = freq_ghz
                total_loss = np.zeros_like(freq_ref)
                
            ls_interp = np.interp(freq_ref, freq_ghz, loss_db)
            total_loss += ls_interp
        except Exception as e:
            print(f"DEBUG get_cal: Failed to load {f}: {e}")
            pass
            
    if total_loss is not None:
        print(f"DEBUG get_cal: TOTAL LOSS to apply = {total_loss[0]:.2f}dB to {total_loss[-1]:.2f}dB")
    return freq_ref, total_loss"""
content = content.replace(old_get_cal, new_get_cal)

# Also debug the plotNPD calibration application
old_plot_npd_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp"""
new_plot_npd_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            print(f"DEBUG plotNPD: raw noise={noise[0]:.2f}, loss_interp={loss_interp[0]:.2f}, new noise={noise[0]+loss_interp[0]:.2f}")
            noise = noise + loss_interp"""
content = content.replace(old_plot_npd_cal, new_plot_npd_cal)

open('backend/plot_generator.py', 'w').write(content)
