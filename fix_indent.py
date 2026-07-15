content = open('backend/plot_generator.py', 'r').read()

old_block = """    for folder in folders:
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
                    return os.path.join(root, file)"""

new_block = """    for folder in folders:
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
                        return os.path.join(root, file)"""

content = content.replace(old_block, new_block)
open('backend/plot_generator.py', 'w').write(content)
