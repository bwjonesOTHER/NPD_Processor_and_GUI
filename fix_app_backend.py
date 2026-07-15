import re

with open('backend/app.py', 'r') as f:
    content = f.read()

# Fix set_file_info for Test 1
old_test1 = """    if test == 1:
        run_num = data.get('runNumber', '').strip()
        cap_num = data.get('capNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()"""
new_test1 = """    if test == 1:
        run_num = data.get('runNumber', '').strip()
        cap_num = data.get('capNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        base_path = os.path.join(os.getcwd(), 'uploads')"""
content = content.replace(old_test1, new_test1)

# Fix set_file_info for Test 2 upload
old_test2 = """        if upload_mode == 'upload':
            # Create the folder instead of searching for it
            pma_path = os.path.join(base_path, "BenchNPD", pma)
            if not os.path.exists(pma_path) and os.path.exists(os.path.join(base_path, pma)):
                pma_path = os.path.join(base_path, pma)"""
new_test2 = """        if upload_mode == 'upload':
            base_path = os.path.join(os.getcwd(), 'uploads')
            # Create the folder instead of searching for it
            pma_path = os.path.join(base_path, "BenchNPD", pma)
            if not os.path.exists(pma_path) and os.path.exists(os.path.join(base_path, pma)):
                pma_path = os.path.join(base_path, pma)"""
content = content.replace(old_test2, new_test2)

# Fix set_file_info for Test 3 upload
old_test3 = """        upload_mode = data.get('uploadMode', 'access')
        if upload_mode == 'upload':
            run_entry = data.get('runEntry', '').strip()
            if run_entry:
                upload_path = os.path.join(upload_path, run_entry)"""
new_test3 = """        upload_mode = data.get('uploadMode', 'access')
        if upload_mode == 'upload':
            base_path = os.path.join(os.getcwd(), 'uploads')
            upload_path = os.path.join(base_path, sn_folder)
            run_entry = data.get('runEntry', '').strip()
            if run_entry:
                upload_path = os.path.join(upload_path, run_entry)"""
content = content.replace(old_test3, new_test3)

with open('backend/app.py', 'w') as f:
    f.write(content)
