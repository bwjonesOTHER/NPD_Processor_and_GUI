import re

content = open('backend/plot_generator.py', 'r').read()

new_get_cal = """def get_calibration_loss(filepath, cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        print(f"DEBUG: No cal folder provided or not a dir: {cal_folder}")
        return None, None
        
    cal_files_to_load = []
    
    # 1. Cap_XX Search (for Test 1)
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        if f"Cap_{n}" in filepath:
            cap_num = n
            break
            
    print(f"DEBUG: Processing file: {filepath}")
    print(f"DEBUG: Found Cap_num: {cap_num}")
    
    if cap_num is not None:
        base_file = find_cal_file(cal_folder, cap_num, "Base")
        if base_file: cal_files_to_load.append(base_file)
        
        bulkhead_file = find_cal_file(cal_folder, cap_num, "Bulkhead")
        if bulkhead_file: cal_files_to_load.append(bulkhead_file)
        
        # SpecA
        for root, _, files in os.walk(cal_folder):
            for file in files:
                if 'speca' in file.lower() and file.lower().endswith('.s2p'):
                    cal_files_to_load.append(os.path.join(root, file))
                    break
            else:
                continue
            break
            
    else:
        # 2. Benchtop Search (Fallback)
        filepath_upper = filepath.upper()
        chain_type = "Pri" if "PRI" in filepath_upper else "Red" if "RED" in filepath_upper else None
        print(f"DEBUG: Fallback chain_type: {chain_type}")
        
        for root, _, files in os.walk(cal_folder):
            for f in files:
                name = f.lower()
                if not name.endswith(".s2p"): continue
                
                if chain_type == "Pri" and "pathloss_base" in name:
                    cal_files_to_load.append(os.path.join(root, f))
                elif chain_type == "Red" and "pathloss_cap" in name:
                    cal_files_to_load.append(os.path.join(root, f))
                elif chain_type is None and "pathloss_base" in name:
                    cal_files_to_load.append(os.path.join(root, f))
                    
                if "speca" in name:  # Matches specan or speca
                    cal_files_to_load.append(os.path.join(root, f))
                    
                if chain_type == "Pri" and name.startswith("pri") and "bulkhead" not in name:
                    cal_files_to_load.append(os.path.join(root, f))
                elif chain_type == "Red" and name.startswith("red") and "bulkhead" not in name:
                    cal_files_to_load.append(os.path.join(root, f))

    if not cal_files_to_load:
        print(f"DEBUG: Failed to find ANY calibration files for {filepath}")
        return None, None
        
    freq_ref = None
    total_loss = None
    
    print(f"DEBUG: Found calibration files to load: {cal_files_to_load}")
    for f in cal_files_to_load:
        try:
            net = rf.Network(f)
            freq_ghz = net.f / 1e9
            loss_db = -net.s_db[:, 1, 0]
            
            print(f"DEBUG: Loaded {f} (loss: {loss_db[0]:.2f} dB to {loss_db[-1]:.2f} dB)")
            
            if freq_ref is None:
                freq_ref = freq_ghz
                total_loss = np.zeros_like(freq_ref)
                
            ls_interp = np.interp(freq_ref, freq_ghz, loss_db)
            total_loss += ls_interp
        except Exception as e:
            print(f"DEBUG: Failed to load {f}: {e}")
            pass
            
    print(f"DEBUG: TOTAL LOSS = {total_loss[0]:.2f} dB to {total_loss[-1]:.2f} dB")
    return freq_ref, total_loss"""

start = content.find("def get_calibration_loss")
end = content.find("def plotNPD", start)
content = content[:start] + new_get_cal + "\n\n" + content[end:]

open('backend/plot_generator.py', 'w').write(content)
