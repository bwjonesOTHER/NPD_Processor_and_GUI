import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "plt.ylabel" in line and "    plt." in line and not line.strip().startswith("#"):
        parts = line.split("    plt.", 1)
        new_lines.append(parts[0] + "\n    plt." + parts[1])
    else:
        new_lines.append(line)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.writelines(new_lines)

