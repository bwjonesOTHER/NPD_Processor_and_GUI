with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'r') as f:
    content = f.read()

target = """    lmoFolderA = os.path.join(folder_path, RunA)
    filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR_ambient',f"{serial_number}")"""

replace = """    lmoFolderA = os.path.join(folder_path, RunA)
    if not os.path.exists(lmoFolderA) and os.path.exists(folder_path):
        area_type = pma_area[-1].upper() if pma_area else 'C'
        found_alt = False
        for d in os.listdir(folder_path):
            if d.startswith("Run") and os.path.isdir(os.path.join(folder_path, d)):
                run_dir = os.path.join(folder_path, d)
                for sub in os.listdir(run_dir):
                    if sub.startswith(area_type + "_SN") and f"{serial_number}" in sub and str(lmo_number) in sub:
                        lmoFolderA = os.path.join(run_dir, sub)
                        RunA = d # Update RunA name for the plot titles
                        found_alt = True
                        break
            if found_alt:
                break
                
    try:
        filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR_ambient',f"{serial_number}")
    except FileNotFoundError:
        filesSparA = []"""

content = content.replace(target, replace)

target2 = """    if not filesSparA:
        filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR',f"{serial_number}")
    filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD_ambient',f"{serial_number}")
    if not filesNPDA:
        filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD',f"{serial_number}")"""

replace2 = """    if not filesSparA:
        try:
            filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR',f"{serial_number}")
        except FileNotFoundError:
            filesSparA = []
    
    try:
        filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD_ambient',f"{serial_number}")
    except FileNotFoundError:
        filesNPDA = []
        
    if not filesNPDA:
        try:
            filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD',f"{serial_number}")
        except FileNotFoundError:
            filesNPDA = []"""
            
content = content.replace(target2, replace2)

with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'w') as f:
    f.write(content)
