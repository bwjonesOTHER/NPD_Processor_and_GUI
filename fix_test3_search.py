import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Replace the npdA and sparA search block
old_search_block = """
        sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR", sn)
        if not sparA: sparA = search_files(search_dirA, "NPDoverTempS", sn)
        
        npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD", sn)
        if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
"""

new_search_block = """
        if test_type == 2:
            sparA = search_files(search_dirA, "NPDoverTempVSWR_ambient", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempS_25C", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempVSWR", sn)
            if not sparA: sparA = search_files(search_dirA, "NPDoverTempS", sn)
            
            npdA = search_files(search_dirA, "NPDoverTempNPD_ambient", sn)
            if not npdA: npdA = search_files(search_dirA, "NPDoverTempNPD", sn)
            if not npdA: npdA = search_files(search_dirA, "NPDoverTempN_25C", sn)
        else:
            sparA = search_files(search_dirA, ".s2p", sn)
            if not sparA and sn: sparA = search_files(search_dirA, ".s2p", "")
            
            npdA = search_files(search_dirA, ".csv", sn)
            if not npdA and sn: npdA = search_files(search_dirA, ".csv", "")
"""

content = content.replace(old_search_block.strip('\n'), new_search_block.strip('\n'))

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
