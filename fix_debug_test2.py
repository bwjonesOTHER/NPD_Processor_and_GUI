content = open('backend/plot_generator.py', 'r').read()

old_debug = """        with open(os.path.join(output_folder, "DEBUG_TEST2.txt"), "w") as f:
            f.write(f"Folder B: {folderB}\\n")
            f.write(f"SN: {sn}\\n")
            f.write(f"Raw CSV found: {raw_npdB}\\n")
            f.write(f"Filtered npdB: {npdB}\\n")
            f.write(f"Filtered sparB: {sparB}\\n")
            f.write(f"npdA: {npdA}\\n")"""

new_debug = """        with open("debug_test2_output.txt", "w") as f:
            f.write(f"Folder B: {folderB}\\n")
            f.write(f"SN: {sn}\\n")
            f.write(f"Raw CSV found: {raw_npdB}\\n")
            f.write(f"Filtered npdB: {npdB}\\n")
            f.write(f"Filtered sparB: {sparB}\\n")
            f.write(f"npdA: {npdA}\\n")"""

content = content.replace(old_debug, new_debug)
open('backend/plot_generator.py', 'w').write(content)
