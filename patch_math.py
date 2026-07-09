with open('backend/math_v3.py', 'r') as f:
    content = f.read()

content = content.replace('search_files(loss_path, "Base")', 'search_files(loss_path, "*Base*")')
content = content.replace('search_files(loss_path, "Bulkhead")', 'search_files(loss_path, "*Bulkhead*")')
content = content.replace('search_files(folder, "SpecA")', 'search_files(folder, "*SpecA*")')

with open('backend/math_v3.py', 'w') as f:
    f.write(content)
