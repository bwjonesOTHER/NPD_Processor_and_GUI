import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

anchor = """        # NPD Search with fallbacks for Run A
        npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD_25C", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)"""

new_anchor = """        # NPD Search with fallbacks for Run A
        npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD_25C", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
        
        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename
        if pma and search_dirA == temp_dir: # only filter if we didn't successfully drill down into a PMA folder
            import os, re
            pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma).lower()
            
            def file_has_pma(f):
                fname = re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(f)).lower()
                if pma_norm in fname: return True
                # In case of typos in filename (e.g. L11072E instead of L110172E), match last character if the file has E or C
                last_char = pma_norm[-1]
                if last_char.isalpha():
                    # look for AreaE or AreaC in name
                    if f"area{last_char}" in fname: return True
                    # look for L11...E pattern
                    if re.search(rf'l11\d+{last_char}', fname): return True
                return False
                
            sparA = [f for f in sparA if file_has_pma(f)]
            npdA = [f for f in npdA if file_has_pma(f)]"""

content = content.replace(anchor, new_anchor)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
