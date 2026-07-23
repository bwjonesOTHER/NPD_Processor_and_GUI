import os
import re

search_dirs = ["."]
cal_types = ["SpecA"]
cal_files_to_load = ["Base.s2p", "Bulkhead.s2p"]
os.system("mkdir -p dummy_dir")
os.system("touch dummy_dir/SpecA_Cable.s2p")

for cal_type in cal_types:
    f = None
    if not f:
        for sdir in search_dirs:
            if f: break
            for root, dirs, files in os.walk(sdir):
                if f: break
                for file in files:
                    if not file.lower().endswith('.s2p'):
                        continue
                    name = file.lower()
                    if cal_type.lower() == "base" and "speca" in name:
                        continue
                    if cal_type.lower() in name and not any(cal_type.lower() in os.path.basename(p).lower() for p in cal_files_to_load):
                        f = os.path.join(root, file)
                        break
    if f:
        cal_files_to_load.append(f)

print("FOUND:", cal_files_to_load)
