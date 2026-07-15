with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_bench = """            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                if pma:
                    pma_folder = get_pma_folder(search_dirB, pma)
                    if pma_folder: search_dirB = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirB, lmo)
                    if lmo_folder: search_dirB = lmo_folder"""

new_bench = """            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                if pma:
                    pma_folder = get_pma_folder(search_dirB, pma)
                    if pma_folder: search_dirB = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirB, lmo)
                    if lmo_folder: search_dirB = lmo_folder
            
            try:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"\\n--- DRILLER DEBUG ---\\n")
                    f_dbg.write(f"pma input: {pma}\\n")
                    f_dbg.write(f"lmo input: {lmo}\\n")
                    f_dbg.write(f"bench root: {bench}\\n")
                    f_dbg.write(f"search_dirB final: {search_dirB}\\n")
            except: pass"""

content = content.replace(old_bench, new_bench)
with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
