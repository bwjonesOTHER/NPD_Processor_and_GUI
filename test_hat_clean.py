import os, re

def find_cal_file(folders, cap_num, cal_type):
    cal_type_lower = cal_type.lower()
    cap_num_int = None
    if cap_num is not None:
        try:
            cap_num_int = int(cap_num)
        except (ValueError, TypeError):
            pass

    for folder in folders:
        for root, dirs, files in os.walk(folder):
            files.sort(key=lambda x: (1 if x and x[0].isdigit() else 0, x), reverse=True)
            for file in files:
                if not file.lower().endswith('.s2p'): continue
                name = file.lower()
                name_norm = name.replace(" ", "").replace("_", "")
                cal_norm = cal_type.lower().replace(" ", "")
                
                if cal_type_lower in file.lower():
                    is_excluded_data = any(x in name_norm for x in ["vswr", "ambient", "hot", "cold", "25c", "pri", "nfdirect"])
                    is_excluded_sec = "sec" in name and not ("second" in name or "basecable" in name_norm) and ("_sec" in name or "sec_" in name or name.endswith("sec.s2p") or "sec." in name)
                    is_excluded_red = "red" in name and not ("measured" in name) and ("_red" in name or "red_" in name or name.endswith("red.s2p") or "red." in name)
                    if is_excluded_data or is_excluded_sec or is_excluded_red:
                        continue
                    if cap_num_int is not None:
                        sn_match = False
                        match = re.search(r'cap_(\d+)', os.path.join(root, file).lower())
                        if match and int(match.group(1)) == cap_num_int:
                            sn_match = True
                        path_lower = os.path.join(root, file).lower()
                        folder_match = bool(re.search(rf'(?:cap[_\s]?|sn)0*{cap_num_int}(?!\d)', path_lower))
                        if sn_match or folder_match:
                            return os.path.join(root, file)
                    else:
                        has_cal_norm = cal_norm in name_norm
                        if has_cal_norm:
                            return os.path.join(root, file)
    return None

import json
search_dirs = [
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp\Run 3 LMO965-57",
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp\Run 9 LMO1208-62\Cap_01",
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp\Run 9 LMO1208-62",
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp"
]

# Simulate the user's filesystem
os.makedirs("simulated_fs/NPDoverTemp/Run 1/UUT SMA Cable Path Loss", exist_ok=True)
open("simulated_fs/NPDoverTemp/Run 1/UUT SMA Cable Path Loss/HatSN1Cable_C548-110-84_SN410115210_02272026.s2p", "w").close()

print(find_cal_file(["simulated_fs/NPDoverTemp"], None, "Hat"))
