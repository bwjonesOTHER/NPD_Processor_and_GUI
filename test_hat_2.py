import os

def find_hat(search_dirs):
    for sdir in search_dirs:
        print(f"Searching {sdir}")
        for root, dirs, files in os.walk(sdir):
            for file in files:
                if not file.lower().endswith('.s2p'): continue
                if 'hat' in file.lower():
                    name = file.lower()
                    name_norm = name.replace(" ", "").replace("_", "")
                    cal_norm = "hat"
                    
                    is_excluded_data = any(x in name_norm for x in ["vswr", "ambient", "hot", "cold", "25c", "pri", "nfdirect"])
                    is_excluded_sec = "sec" in name and not ("second" in name or "basecable" in name_norm) and ("_sec" in name or "sec_" in name or name.endswith("sec.s2p") or "sec." in name)
                    is_excluded_red = "red" in name and not ("measured" in name) and ("_red" in name or "red_" in name or name.endswith("red.s2p") or "red." in name)
                    is_base_speca_exclude = False
                    
                    has_cal_norm = cal_norm in name_norm
                    print(f"Found {file}: exc_data={is_excluded_data}, exc_sec={is_excluded_sec}, exc_red={is_excluded_red}, has_cal_norm={has_cal_norm}")
                    if not is_excluded_data and not is_excluded_sec and not is_excluded_red and has_cal_norm:
                        return os.path.join(root, file)
    return None

search_dirs = [
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp"
]
print(find_hat(search_dirs))
