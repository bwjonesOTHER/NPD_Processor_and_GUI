with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_debug = """            try:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"\\n--- DRILLER DEBUG ---\\n")
                    f_dbg.write(f"pma input: {pma}\\n")
                    f_dbg.write(f"lmo input: {lmo}\\n")
                    f_dbg.write(f"bench root: {bench}\\n")
                    f_dbg.write(f"search_dirB final: {search_dirB}\\n")
            except: pass"""

new_debug = """            try:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"\\n--- DRILLER DEBUG ---\\n")
                    f_dbg.write(f"pma input: {pma}\\n")
                    f_dbg.write(f"lmo input: {lmo}\\n")
                    f_dbg.write(f"bench root: {bench}\\n")
                    f_dbg.write(f"search_dirB final: {search_dirB}\\n")
                    f_dbg.write(f"\\n--- FINAL FILES CHOSEN ---\\n")
                    f_dbg.write(f"Thermal S2P (sparA): {sparA}\\n")
                    f_dbg.write(f"Thermal CSV (npdA): {npdA}\\n")
                    f_dbg.write(f"Benchtop S2P (sparB): {sparB}\\n")
                    f_dbg.write(f"Benchtop CSV (npdB): {npdB}\\n")
            except: pass"""

content = content.replace(old_debug, new_debug)
with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
