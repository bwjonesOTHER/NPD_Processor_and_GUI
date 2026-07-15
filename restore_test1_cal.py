import re

content = open('backend/plot_generator.py', 'r').read()

# Remove the old get_calibration_loss
start_idx = content.find("def get_calibration_loss(filepath, cal_folder):")
end_idx = content.find("def plotNPD", start_idx)
content = content[:start_idx] + content[end_idx:]

new_cal_logic = """def find_cal_file(folder, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    try:
        cap_num_int = int(cap_num)
    except (ValueError, TypeError):
        return None
        
    for root, dirs, files in os.walk(folder):
        for file in files:
            if not file.lower().endswith('.s2p'):
                continue
            if cal_type_lower in file.lower():
                # Extract number after SN
                match = re.search(r'sn0*(\d+)', file.lower())
                sn_match = False
                if match:
                    if int(match.group(1)) == cap_num_int:
                        sn_match = True
                        
                # Check path for cap folder
                path_lower = os.path.join(root, file).lower()
                folder_match = False
                if f"cap_0{cap_num_int}" in path_lower or f"cap_{cap_num_int}" in path_lower:
                    folder_match = True
                    
                if sn_match or folder_match:
                    return os.path.join(root, file)
                    
    return None

def get_calibration_loss(filepath, cal_folder):
    if not cal_folder or not os.path.isdir(cal_folder):
        return None, None
        
    cal_files_to_load = []
    
    # 1. Cap_XX Search (for Test 1)
    cap_num = None
    for n in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        if f"Cap_{n}" in filepath:
            cap_num = n
            break
            
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
            
    return freq_ref, total_loss

"""

content = content[:start_idx] + new_cal_logic + content[start_idx:]
open('backend/plot_generator.py', 'w').write(content)
