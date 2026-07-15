import re

content = open('backend/plot_generator.py', 'r').read()

# 1. Replace load_calibration_loss with get_calibration_loss
old_load_cal = """def load_calibration_loss(cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        return None, None
    cal_files = []
    for root, _, files in os.walk(cal_folder):
        for f in files:
            name = f.lower()
            if ("pathloss_base" in name or "pathloss_cap" in name or "specan_none" in name or "specanbase" in name or "specan_base" in name) and name.endswith(".s2p"):
                cal_files.append(os.path.join(root, f))
    if not cal_files:
        return None, None

    freq_list = []
    loss_list = []
    for f in cal_files:
        net = rf.Network(f)
        freq_ghz = net.f / 1e9
        loss_db = -net.s_db[:, 1, 0]
        freq_list.append(freq_ghz)
        loss_list.append(loss_db)
    
    freq_ref = freq_list[0]
    total_loss = np.zeros_like(freq_ref)
    for fr, ls in zip(freq_list, loss_list):
        ls_interp = np.interp(freq_ref, fr, ls)
        total_loss += ls_interp
    return freq_ref, total_loss"""

new_get_cal = """def get_calibration_loss(filepath, cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        return None, None
        
    filepath_upper = filepath.upper()
    chain_type = "Pri" if "PRI" in filepath_upper else "Red" if "RED" in filepath_upper else None
    
    cal_files_to_load = []
    
    for root, _, files in os.walk(cal_folder):
        for f in files:
            name = f.lower()
            if not name.endswith(".s2p"): continue
            
            # Base/Pathloss
            if chain_type == "Pri" and "pathloss_base" in name:
                cal_files_to_load.append(os.path.join(root, f))
            elif chain_type == "Red" and "pathloss_cap" in name:
                cal_files_to_load.append(os.path.join(root, f))
            # Fallback
            elif chain_type is None and "pathloss_base" in name:
                cal_files_to_load.append(os.path.join(root, f))
                
            # SpecAn
            if "specan" in name:
                cal_files_to_load.append(os.path.join(root, f))
                
            # Bulkhead
            if chain_type == "Pri" and name.startswith("pri") and "bulkhead" not in name:
                cal_files_to_load.append(os.path.join(root, f))
            elif chain_type == "Red" and name.startswith("red") and "bulkhead" not in name:
                cal_files_to_load.append(os.path.join(root, f))

    if not cal_files_to_load:
        return None, None
        
    freq_ref = None
    total_loss = None
    
    for f in cal_files_to_load:
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
content = content.replace(old_load_cal, new_get_cal)

# 2. Update plotNPD signature and logic
content = content.replace(
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder, plot_density=False):',
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False):'
)
old_np_cal = """        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp"""
new_np_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp"""
content = content.replace(old_np_cal, new_np_cal)

# 3. Update plotS21 signature and logic
content = content.replace(
    'def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, freq_cal, total_loss_db, output_folder):',
    'def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder):'
)
old_s21_cal = """        if freq_cal is not None:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_corr = raw_s21 + loss_interp"""
new_s21_cal = """        freq_cal, total_loss_db = get_calibration_loss(file, cal_folder)
        if freq_cal is not None:
            loss_interp = np.interp(freq_ghz, freq_cal, total_loss_db)
            s21_corr = raw_s21 + loss_interp"""
content = content.replace(old_s21_cal, new_s21_cal)

# 4. Remove freq_cal, total_loss_db = load_calibration_loss(cal_folder)
content = re.sub(r'    freq_cal, total_loss_db = load_calibration_loss\(cal_folder\)\n', '', content)

# 5. Update generate_plots calls
content = content.replace('freq_cal, total_loss_db, output_folder, plot_density=False)', 'cal_folder, output_folder, plot_density=False)')
content = content.replace('freq_cal, total_loss_db, output_folder, plot_density=True)', 'cal_folder, output_folder, plot_density=True)')
content = content.replace('freq_cal, total_loss_db, output_folder)', 'cal_folder, output_folder)')

open('backend/plot_generator.py', 'w').write(content)
