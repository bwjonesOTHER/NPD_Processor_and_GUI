with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# I will add logging into the search section for Test 3
# Test 3 uses the same Benchtop block as Test 2.
old_block = """        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR_25C", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)"""

new_block = """        with open("debug.txt", "a") as f_dbg:
            f_dbg.write(f"\\n--- TEST 3 DEBUG ---\\n")
            f_dbg.write(f"search_dirA: {search_dirA}\\n")
            f_dbg.write(f"search_dirB: {search_dirB}\\n")
            f_dbg.write(f"sn: {sn}\\n")
            f_dbg.write(f"test_type: {test_type}\\n")

        # S2P Search with fallbacks for Run A to ensure we only get ambient if pointed to a Temp folder
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR_25C", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)"""

content = content.replace(old_block, new_block)

old_block2 = """        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename
        if pma and search_dirA == temp: # only filter if we didn't successfully drill down into a PMA folder"""

new_block2 = """        with open("debug.txt", "a") as f_dbg:
            f_dbg.write(f"sparA len: {len(sparA) if sparA else 0}\\n")
            f_dbg.write(f"npdA len: {len(npdA) if npdA else 0}\\n")
            f_dbg.write(f"sparB len: {len(sparB) if sparB else 0}\\n")
            f_dbg.write(f"npdB len: {len(npdB) if npdB else 0}\\n")

        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename
        if pma and search_dirA == temp: # only filter if we didn't successfully drill down into a PMA folder"""

content = content.replace(old_block2, new_block2)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
