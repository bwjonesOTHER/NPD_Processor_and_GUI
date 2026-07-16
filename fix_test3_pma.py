with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_code = """    else:
        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        search_dirA = folderA
        search_dirB = folderB
        
        if test_type == 2:
            pma = params.get('pma')"""

new_code = """    else:
        # Benchtop (Test 2 & 3)
        sn = params.get('serial_number')
        
        search_dirA = folderA
        search_dirB = folderB
        
        pma = None
        lmo = None
        if test_type == 2:
            pma = params.get('pma')"""

content = content.replace(old_code, new_code)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
