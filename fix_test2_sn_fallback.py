with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_fallback = """        raw_sparB = search_files(search_dirB, ".s2p", sn)
        if not raw_sparB and sn: raw_sparB = search_files(search_dirB, ".s2p", "")
        sparB_filt = [f for f in raw_sparB if "vswr" in os.path.basename(f).lower()]
        sparB = filter_benchtop(sparB_filt if sparB_filt else raw_sparB)
        
        raw_npdB = search_files(search_dirB, ".csv", sn)
        if not raw_npdB and sn: raw_npdB = search_files(search_dirB, ".csv", "")
        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)"""

new_fallback = """        raw_sparB = search_files(search_dirB, ".s2p", sn)
        sparB_filt = [f for f in raw_sparB if "vswr" in os.path.basename(f).lower()]
        sparB = filter_benchtop(sparB_filt if sparB_filt else raw_sparB)
        
        raw_npdB = search_files(search_dirB, ".csv", sn)
        npdB_filt = [f for f in raw_npdB if "nfdirect" in os.path.basename(f).lower() or "npd" in os.path.basename(f).lower()]
        npdB = filter_benchtop(npdB_filt if npdB_filt else raw_npdB)"""

content = content.replace(old_fallback, new_fallback)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
