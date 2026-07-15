content = open('backend/plot_generator.py', 'r').read()

old_npdA = """        # NPD Search with fallbacks for Run A
        npdA = search_files(folderA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN_25C", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN", sn)
        if not npdA: npdA = search_files(folderA, "NPD", sn)"""

new_npdA = """        # NPD Search with fallbacks for Run A
        npdA = search_files(folderA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN_25C", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(folderA, "NPDoverTempN", sn)"""

content = content.replace(old_npdA, new_npdA)

old_sparA = """        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(folderA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS", sn)
        if not sparA: sparA = search_files(folderA, ".s2p", sn)"""

new_sparA = """        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(folderA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(folderA, "NPDoverTempS", sn)"""

content = content.replace(old_sparA, new_sparA)

open('backend/plot_generator.py', 'w').write(content)
