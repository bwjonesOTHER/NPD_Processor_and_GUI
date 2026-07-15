import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Fix search_files exact SN matching
old_search = """                if serial_number:
                    if serial_number.lower() not in file.lower():
                        continue
                matches.append(os.path.join(dirpath, file))"""

new_search = """                if serial_number:
                    import re
                    sn_clean = re.sub(r'^[SsnN0]+', '', serial_number)
                    if not sn_clean: sn_clean = serial_number
                    pattern = r'(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
                    if not re.search(pattern, file, re.IGNORECASE):
                        continue
                matches.append(os.path.join(dirpath, file))"""

content = content.replace(old_search, new_search)

# Fix Test 2 Fallbacks
old_fallbacks = """        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS", sn)
        
        # NPD Search with fallbacks for Run A
        npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN", sn)
        
        # Run B is usually pure benchtop, just search by extension and SN
        # IMPORTANT: Since folderB is the same root folder, it will accidentally find the NPDoverTemp files again.
        # We must filter out "NPDoverTemp" files from Run B.
        def filter_benchtop(files):
            import os
            # Only check the filename and immediate parent directory, not the entire path which might coincidentally contain 'npdovertemp'
            return [f for f in files if "npdovertemp" not in os.path.basename(f).lower()]
            
        sparB = filter_benchtop(search_files(search_dirB, ".s2p", sn))
        if not sparB and sn: sparB = filter_benchtop(search_files(search_dirB, ".s2p", ""))
        
        raw_npdB = search_files(search_dirB, ".csv", sn)
        npdB = filter_benchtop(raw_npdB)
        if not npdB and sn: 
            raw_npdB = search_files(search_dirB, ".csv", "")
            npdB = filter_benchtop(raw_npdB)"""

new_fallbacks = """        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR_25C", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
        
        # NPD Search with fallbacks for Run A
        npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD_25C", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
        
        # Run B is usually pure benchtop, just search by extension and SN
        # IMPORTANT: Since folderB is the same root folder, it will accidentally find the NPDoverTemp files again.
        # We must filter out "NPDoverTemp" files from Run B.
        def filter_benchtop(files):
            import os
            # Only check the filename and immediate parent directory, not the entire path which might coincidentally contain 'npdovertemp'
            return [f for f in files if "npdovertemp" not in os.path.basename(f).lower()]
            
        raw_sparB = search_files(search_dirB, ".s2p", sn)
        if not raw_sparB and sn: raw_sparB = search_files(search_dirB, ".s2p", "")
        sparB_filt = [f for f in raw_sparB if "vswr" in os.path.basename(f).lower()]
        sparB = filter_benchtop(sparB_filt if sparB_filt else raw_sparB)
        
        raw_npdB = search_files(search_dirB, ".csv", sn)
        if not raw_npdB and sn: raw_npdB = search_files(search_dirB, ".csv", "")
        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)"""

content = content.replace(old_fallbacks, new_fallbacks)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
