import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Fix markevery
    if "markevery=100" in line:
        line = line.replace("markevery=100", "markevery=max(1, len(freq_ghz_out)//10)")
    
    if "plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')" in line:
        continue # skip the original legend
        
    if "plt.subplots_adjust(right=0.7)" in line:
        # Insert the legend before this
        indent = line.split("plt.subplots_adjust")[0]
        new_lines.append(indent + "plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='8')\n")
        new_lines.append(line)
        continue

    # Fix the missing newline between ylabel and plot
    if ")    plt.plot([" in line:
        parts = line.split("    plt.plot([")
        new_lines.append(parts[0] + "\n" + parts[0].split("plt.ylabel")[0] + "plt.plot([" + parts[1])
        continue
        
    if ")    plt.axvline(" in line:
        parts = line.split("    plt.axvline(")
        new_lines.append(parts[0] + "\n" + parts[0].split("plt.ylabel")[0] + "plt.axvline(" + parts[1])
        continue

    new_lines.append(line)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.writelines(new_lines)

