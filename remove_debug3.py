with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_bad_debug = """        with open("debug.txt", "a") as f_dbg:
            f_dbg.write(f"sparA len: {len(sparA) if sparA else 0}\\n")
            f_dbg.write(f"npdA len: {len(npdA) if npdA else 0}\\n")
            f_dbg.write(f"sparB len: {len(sparB) if sparB else 0}\\n")
            f_dbg.write(f"npdB len: {len(npdB) if npdB else 0}\\n")

        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename"""

new_good = """        # If Thermal files are in a root folder without Area subfolders, filter by PMA Area in the filename"""

content = content.replace(old_bad_debug, new_good)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
