content = open('backend/plot_generator.py', 'r').read()

old_b_search = """        # Run B is usually pure benchtop, just search by extension and SN
        sparB = search_files(folderB, ".s2p", sn)
        if not sparB and sn: sparB = search_files(folderB, ".s2p", "")
        
        npdB = search_files(folderB, ".csv", sn)
        if not npdB and sn: npdB = search_files(folderB, ".csv", "")"""

new_b_search = """        # Run B is usually pure benchtop, just search by extension and SN
        # IMPORTANT: Since folderB is the same root folder, it will accidentally find the NPDoverTemp files again.
        # We must filter out "NPDoverTemp" files from Run B.
        def filter_benchtop(files):
            return [f for f in files if "npdovertemp" not in f.lower()]
            
        sparB = filter_benchtop(search_files(folderB, ".s2p", sn))
        if not sparB and sn: sparB = filter_benchtop(search_files(folderB, ".s2p", ""))
        
        npdB = filter_benchtop(search_files(folderB, ".csv", sn))
        if not npdB and sn: npdB = filter_benchtop(search_files(folderB, ".csv", ""))"""

content = content.replace(old_b_search, new_b_search)

open('backend/plot_generator.py', 'w').write(content)
