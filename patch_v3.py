import os

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content = f.read()

new_funcs = """    def find_cal_file(folder, cap_num, cal_type):
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
                    import re
                    match = re.search(r'sn0*(\d+)', file.lower())
                    sn_match = False
                    if match:
                        if int(match.group(1)) == cap_num_int:
                            sn_match = True
                            
                    path_lower = os.path.join(root, file).lower()
                    folder_match = False
                    if f"cap_0{cap_num_int}" in path_lower or f"cap_{cap_num_int}" in path_lower:
                        folder_match = True
                        
                    if sn_match or folder_match:
                        return os.path.join(root, file)
                        
        return None

    def cap_searchA(filename, lmoFolderA):
        cap_num = None
        for n in ["01", "02", "03", "04", "05", "06"]:
            if f"Cap_{n}" in filename:
                cap_num = n
                break
                
        if cap_num is None:
            return None, None
            
        loss = find_cal_file(lmoFolderA, cap_num, "Base")
        loss_bulkhead = find_cal_file(lmoFolderA, cap_num, "Bulkhead")
        return loss, loss_bulkhead

    def cap_searchB(filename, lmoFolderB):
        cap_num = None
        for n in ["01", "02", "03", "04", "05", "06"]:
            if f"Cap_{n}" in filename:
                cap_num = n
                break
                
        if cap_num is None:
            return None, None
            
        loss = find_cal_file(lmoFolderB, cap_num, "Base")
        loss_bulkhead = find_cal_file(lmoFolderB, cap_num, "Bulkhead")
        return loss, loss_bulkhead"""

start_idx = content.find("    def cap_searchA(")
end_idx = content.find("    def load_specA_loss(")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_funcs + "\n\n" + content[end_idx:]
    with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
        f.write(content)
    print("V3 patched.")
else:
    print("Could not find the target functions in V3.")
