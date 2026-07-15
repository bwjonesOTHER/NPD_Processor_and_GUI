import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_logic = """        if test_type == 2:
            pma = params.get('pma')
            bench_dir = os.path.join(folderB, "BenchNPD")
            temp_dir = os.path.join(folderA, "OverTemp")
            if pma:
                if os.path.exists(os.path.join(bench_dir, pma)): bench_dir = os.path.join(bench_dir, pma)
                if os.path.exists(os.path.join(temp_dir, pma)): temp_dir = os.path.join(temp_dir, pma)
            if os.path.exists(bench_dir):
                search_dirB = bench_dir
            if os.path.exists(temp_dir):
                search_dirA = temp_dir"""

new_logic = """        if test_type == 2:
            pma = params.get('pma')
            
            def get_subfolder(base_d, target_name):
                if not os.path.exists(base_d): return None
                for d in os.listdir(base_d):
                    if os.path.isdir(os.path.join(base_d, d)) and target_name.lower() in d.lower().replace("_", ""):
                        return os.path.join(base_d, d)
                return None
                
            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                for d in os.listdir(base_d):
                    if os.path.isdir(os.path.join(base_d, d)) and pma_area.lower() in d.lower():
                        return os.path.join(base_d, d)
                return None
            
            bench = get_subfolder(folderB, "bench")
            if bench:
                search_dirB = bench
                pma_folder = get_pma_folder(search_dirB, pma)
                if pma_folder: search_dirB = pma_folder
                
            temp = get_subfolder(folderA, "overtemp")
            if not temp: temp = get_subfolder(folderA, "temp")
            if temp:
                search_dirA = temp
                pma_folder = get_pma_folder(search_dirA, pma)
                if pma_folder: search_dirA = pma_folder"""

content = content.replace(old_logic, new_logic)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
