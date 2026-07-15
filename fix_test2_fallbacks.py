content = open('backend/plot_generator.py', 'r').read()

old_test2_calls = """        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        npdA = search_files(folderA, "NPD", sn)
        npdB = search_files(folderB, "NPD", sn)
        sparA = search_files(folderA, ".s2p", sn)
        sparB = search_files(folderB, ".s2p", sn)"""

new_test2_calls = """        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(folderA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS", sn)
        if not sparA: sparA = search_files(folderA, ".s2p", sn)
        
        # NPD Search with fallbacks for Run A
        npdA = search_files(folderA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN_25C", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN", sn)
        if not npdA: npdA = search_files(folderA, "NPD", sn)
        
        # Run B is usually pure benchtop, just search by extension and SN
        sparB = search_files(folderB, ".s2p", sn)
        if not sparB and sn: sparB = search_files(folderB, ".s2p", "")
        
        npdB = search_files(folderB, ".csv", sn)
        if not npdB and sn: npdB = search_files(folderB, ".csv", "")"""

content = content.replace(old_test2_calls, new_test2_calls)

open('backend/plot_generator.py', 'w').write(content)
