with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Remove the broken debug block from the wrong location
bad_debug = """            try:
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

good_driller_only = """            try:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"\\n--- DRILLER DEBUG ---\\n")
                    f_dbg.write(f"pma input: {pma}\\n")
                    f_dbg.write(f"lmo input: {lmo}\\n")
                    f_dbg.write(f"bench root: {bench}\\n")
                    f_dbg.write(f"search_dirB final: {search_dirB}\\n")
            except: pass"""

content = content.replace(bad_debug, good_driller_only)

# Insert the files debug block in the right location
anchor = """        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)"""

new_files_debug = """        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)
        
        try:
            with open("debug_log.txt", "a") as f_dbg:
                f_dbg.write(f"\\n--- FINAL FILES CHOSEN ---\\n")
                f_dbg.write(f"Thermal S2P (sparA): {sparA}\\n")
                f_dbg.write(f"Thermal CSV (npdA): {npdA}\\n")
                f_dbg.write(f"Benchtop S2P (sparB): {sparB}\\n")
                f_dbg.write(f"Benchtop CSV (npdB): {npdB}\\n")
        except: pass"""

content = content.replace(anchor, new_files_debug)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

