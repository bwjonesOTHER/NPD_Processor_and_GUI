content = open('backend/plot_generator.py', 'r').read()

old_block2 = """        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
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
                    cal_files_to_load.append(os.path.join(root, f))"""

new_block2 = """        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
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
                        cal_files_to_load.append(os.path.join(root, f))"""

content = content.replace(old_block2, new_block2)
open('backend/plot_generator.py', 'w').write(content)
