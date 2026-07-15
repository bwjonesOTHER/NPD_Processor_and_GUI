content = open('backend/plot_generator.py', 'r').read()

old_b = """        npdB = filter_benchtop(search_files(folderB, ".csv", sn))
        if not npdB and sn: npdB = filter_benchtop(search_files(folderB, ".csv", ""))"""

new_b = """        raw_npdB = search_files(folderB, ".csv", sn)
        npdB = filter_benchtop(raw_npdB)
        if not npdB and sn: 
            raw_npdB = search_files(folderB, ".csv", "")
            npdB = filter_benchtop(raw_npdB)
        
        with open(os.path.join(output_folder, "DEBUG_TEST2.txt"), "w") as f:
            f.write(f"Folder B: {folderB}\\n")
            f.write(f"SN: {sn}\\n")
            f.write(f"Raw CSV found: {raw_npdB}\\n")
            f.write(f"Filtered npdB: {npdB}\\n")
            f.write(f"Filtered sparB: {sparB}\\n")
            f.write(f"npdA: {npdA}\\n")
"""

content = content.replace(old_b, new_b)
open('backend/plot_generator.py', 'w').write(content)
