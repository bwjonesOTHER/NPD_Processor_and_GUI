import re

# 1. Update app.py
content_app = open('backend/app.py', 'r').read()
old_app_test2 = """    elif test == 2:
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        params['runs'] = [path] if path else []"""
new_app_test2 = """    elif test == 2:
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        params['runs'] = [path] if path else []
        params['serial_number'] = read_txt("serialNumber.txt")"""
content_app = content_app.replace(old_app_test2, new_app_test2)

old_app_test3 = """    elif test == 3:
        path1 = read_txt("path.txt")
        path2 = read_txt("upload_path.txt")
        params['runs'] = [p for p in [path1, path2] if p]"""
new_app_test3 = """    elif test == 3:
        path1 = read_txt("path.txt")
        path2 = read_txt("upload_path.txt")
        params['runs'] = [p for p in [path1, path2] if p]
        params['serial_number'] = read_txt("serialNumber.txt")"""
content_app = content_app.replace(old_app_test3, new_app_test3)
open('backend/app.py', 'w').write(content_app)

# 2. Update plot_generator.py
content_plot = open('backend/plot_generator.py', 'r').read()
old_search_files = """def search_files(root_dir, filename_part):
    matches = []
    if not root_dir or not os.path.isdir(root_dir):
        return matches
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if filename_part.lower() in file.lower():
                matches.append(os.path.join(dirpath, file))
    return matches"""
new_search_files = """def search_files(root_dir, filename_part, serial_number=None):
    matches = []
    if not root_dir or not os.path.isdir(root_dir):
        return matches
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if filename_part.lower() in file.lower():
                if serial_number:
                    if serial_number.lower() not in file.lower():
                        continue
                matches.append(os.path.join(dirpath, file))
    return matches"""
content_plot = content_plot.replace(old_search_files, new_search_files)

old_test2_calls = """        # Benchtop (Test 2 & 3)
        npdA = search_files(folderA, "NPD")
        npdB = search_files(folderB, "NPD")
        sparA = search_files(folderA, ".s2p")
        sparB = search_files(folderB, ".s2p")"""
new_test2_calls = """        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        npdA = search_files(folderA, "NPD", sn)
        npdB = search_files(folderB, "NPD", sn)
        sparA = search_files(folderA, ".s2p", sn)
        sparB = search_files(folderB, ".s2p", sn)"""
content_plot = content_plot.replace(old_test2_calls, new_test2_calls)

open('backend/plot_generator.py', 'w').write(content_plot)
