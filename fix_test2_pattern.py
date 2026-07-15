import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_code = """    else:
        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(folderA, "NPDoverTempVSWR_ambient", sn)"""

new_code = """    else:
        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        search_dirA = folderA
        search_dirB = folderB
        
        if test_type == 2:
            bench_dir = os.path.join(folderB, "BenchNPD")
            temp_dir = os.path.join(folderA, "OverTemp")
            if os.path.exists(bench_dir):
                search_dirB = bench_dir
            if os.path.exists(temp_dir):
                search_dirA = temp_dir
        
        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)"""

content = content.replace(old_code, new_code)

old_code2 = """        if not sparA: sparA = search_files(folderA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS", sn)
        
        # NPD Search with fallbacks for Run A
        npdA = search_files(folderA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN_25C", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN", sn)
        
        # Run B is usually pure benchtop, just search by extension and SN
        # IMPORTANT: Since folderB is the same root folder, it will accidentally find the NPDoverTemp files again.
        # We must filter out "NPDoverTemp" files from Run B.
        def filter_benchtop(files):
            import os
            # Only check the filename and immediate parent directory, not the entire path which might coincidentally contain 'npdovertemp'
            return [f for f in files if "npdovertemp" not in os.path.basename(f).lower()]
            
        sparB = filter_benchtop(search_files(folderB, ".s2p", sn))
        if not sparB and sn: sparB = filter_benchtop(search_files(folderB, ".s2p", ""))
        
        raw_npdB = search_files(folderB, ".csv", sn)
        npdB = filter_benchtop(raw_npdB)
        if not npdB and sn: 
            raw_npdB = search_files(folderB, ".csv", "")
            npdB = filter_benchtop(raw_npdB)"""

new_code2 = """        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
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

content = content.replace(old_code2, new_code2)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
