with open('backend/app.py', 'r') as f:
    content = f.read()

old_test3 = """    elif test == 3:
        path1 = read_txt("path.txt")
        path2 = read_txt("upload_path.txt")
        params['runs'] = [p for p in [path1, path2] if p]
        params['serial_number'] = read_txt("serialNumber.txt")"""

new_test3 = """    elif test == 3:
        run_a = read_txt("RunA_Path.txt")
        run_b = read_txt("RunB_Path.txt")
        params['runs'] = [run for run in [run_a, run_b] if run]
        params['serial_number'] = read_txt("serialNumber.txt")"""

content = content.replace(old_test3, new_test3)

with open('backend/app.py', 'w') as f:
    f.write(content)
