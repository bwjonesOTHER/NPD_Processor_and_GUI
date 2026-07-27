with open("backend/plot_generator.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if i == 1418: # 0-indexed, so line 1419
        skip = True
        new_lines.append("        pma = None\n")
        new_lines.append("        lmo = None\n")
        new_lines.append("        if test_type == 2:\n")
        new_lines.append("            pma = params.get('pmaArea')\n")
        new_lines.append("            search_dirA = params.get('benchPath', search_dirA)\n")
        new_lines.append("            search_dirB = params.get('tempPath', search_dirB)\n")
    if i == 1499: # 0-indexed, so line 1500 `def filter_benchtop(files):`
        skip = False
    
    if not skip:
        new_lines.append(line)

with open("backend/plot_generator.py", "w") as f:
    f.writelines(new_lines)
