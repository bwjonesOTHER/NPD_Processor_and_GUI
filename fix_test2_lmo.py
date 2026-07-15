import re

with open('backend/app.py', 'r') as f:
    content = f.read()

old_app = """        params['serial_number'] = read_txt("serialNumber.txt")
        params['pma'] = read_txt("PMA_Area.txt")"""

new_app = """        params['serial_number'] = read_txt("serialNumber.txt")
        params['pma'] = read_txt("PMA_Area.txt")
        params['lmo'] = read_txt("LMO_Number.txt")
        if not params['lmo']:
            params['lmo'] = read_txt("lmoNumber.txt")"""

content = content.replace(old_app, new_app)

with open('backend/app.py', 'w') as f:
    f.write(content)

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_logic = """            bench = get_subfolder(folderB, "bench")
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

new_logic = """            lmo = params.get('lmo')
            
            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                if pma:
                    pma_folder = get_pma_folder(search_dirB, pma)
                    if pma_folder: search_dirB = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirB, lmo)
                    if lmo_folder: search_dirB = lmo_folder
                
            temp = get_subfolder(folderA, "overtemp")
            if not temp: temp = get_subfolder(folderA, "temp")
            if temp:
                search_dirA = temp
                if pma:
                    pma_folder = get_pma_folder(search_dirA, pma)
                    if pma_folder: search_dirA = pma_folder
                if lmo:
                    lmo_folder = get_pma_folder(search_dirA, lmo)
                    if lmo_folder: search_dirA = lmo_folder"""

content = content.replace(old_logic, new_logic)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

