import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_func = """            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                for d in os.listdir(base_d):
                    if os.path.isdir(os.path.join(base_d, d)) and pma_area.lower() in d.lower():
                        return os.path.join(base_d, d)
                return None"""

new_func = """            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                import re
                pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma_area).lower()
                for d in os.listdir(base_d):
                    d_norm = re.sub(r'[^a-zA-Z0-9]', '', d).lower()
                    if os.path.isdir(os.path.join(base_d, d)) and pma_norm in d_norm:
                        return os.path.join(base_d, d)
                # If a specific PMA Area was requested but we couldn't find its folder, 
                # return a dummy path so we don't accidentally scan ALL areas in the root folder!
                return os.path.join(base_d, "NON_EXISTENT_PMA_AREA_FALLBACK")"""

content = content.replace(old_func, new_func)

old_bench = """            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                pma_folder = get_pma_folder(search_dirB, pma)
                if pma_folder: search_dirB = pma_folder
                
            temp = get_subfolder(folderA, "overtemp")
            if not temp: temp = get_subfolder(folderA, "temp")
            if temp:
                search_dirA = temp
                pma_folder = get_pma_folder(search_dirA, pma)
                if pma_folder: search_dirA = pma_folder"""

new_bench = """            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                if pma:
                    pma_folder = get_pma_folder(search_dirB, pma)
                    if pma_folder: search_dirB = pma_folder
                
            temp = get_subfolder(folderA, "overtemp")
            if not temp: temp = get_subfolder(folderA, "temp")
            if temp:
                search_dirA = temp
                if pma:
                    pma_folder = get_pma_folder(search_dirA, pma)
                    if pma_folder: search_dirA = pma_folder"""

content = content.replace(old_bench, new_bench)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
