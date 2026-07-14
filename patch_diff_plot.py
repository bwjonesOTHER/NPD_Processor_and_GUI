import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Replace the diff math to be safe against empty arrays
new_diff_math = """    # Safely compute differences only if arrays are not empty
    diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1]) if (len(NPD25) > 1 and len(NPD64) > 1 and len(NPD25[1]) > 0 and len(NPD64[1]) > 0) else []
    diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1]) if (len(NPD25) > 1 and len(NPDn38) > 1 and len(NPD25[1]) > 0 and len(NPDn38[1]) > 0) else []
    diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1]) if (len(NPD64) > 1 and len(NPDn38) > 1 and len(NPD64[1]) > 0 and len(NPDn38[1]) > 0) else []"""

content = re.sub(
    r'    diff_npd25_npd64 = np\.abs\(NPD25\[1\] - NPD64\[1\]\)\n    diff_npd25_npdn38 = np\.abs\(NPD25\[1\] - NPDn38\[1\]\)\n    diff_npd64_npdn38 = np\.abs\(NPD64\[1\] - NPDn38\[1\]\)',
    new_diff_math,
    content
)

# Replace the plotting to be safe against empty arrays
new_plotting = """    c = next(color_cycle)
    line = next(line_styles_cycle)
    if len(NPD25) > 1 and len(NPD25[0]) > 0:
        plt.plot(NPD25[0],NPD25[1],label="NP 25",color=c,linestyle=line)
    
    c = next(color_cycle)
    line = next(line_styles_cycle)
    if len(NPD64) > 1 and len(NPD64[0]) > 0:
        plt.plot(NPD64[0], NPD64[1], label="NP 64",color=c,linestyle=line)
    
    c = next(color_cycle)
    line = next(line_styles_cycle)
    if len(NPDn38) > 1 and len(NPDn38[0]) > 0:
        plt.plot(NPDn38[0], NPDn38[1], label="NP n38",color=c,linestyle=line)
    plt.legend(loc='upper left', fontsize='10' )

    ax2=ax1.twinx()
    ax2.set_ylim(0,5)
    plt.ylabel('Diff NP (dB)')  # , fontsize='x-small'
    color_cycle = itertools.cycle(my_colors)
    line_styles_cycle=itertools.cycle(my_line_styles)
    
    if len(diff_npd25_npd64) > 0 and len(NPD25[0]) > 0:
        plt.plot(NPD25[0], diff_npd25_npd64, label="Delta 25/64",color=c,linestyle='--')
        c = next(color_cycle)
        line = next(line_styles_cycle)
    if len(diff_npd25_npdn38) > 0 and len(NPD25[0]) > 0:
        plt.plot(NPD25[0], diff_npd25_npdn38, label="Delta 25/n38",color=c,linestyle='--')
        c = next(color_cycle)
        line = next(line_styles_cycle)
    if len(diff_npd64_npdn38) > 0 and len(NPD64[0]) > 0:
        plt.plot(NPD64[0], diff_npd64_npdn38, label="Delta 64/n38",color=c,linestyle='--')"""

content = re.sub(
    r'    c = next\(color_cycle\)\n    line = next\(line_styles_cycle\)\n    plt\.plot\(NPD25\[0\],NPD25\[1\],label="NP 25",color=c,linestyle=line\).*?plt\.plot\(NPD25\[0\], diff_npd64_npdn38, label="Delta 64/n38",color=c,linestyle=\'--\'\)',
    new_plotting,
    content,
    flags=re.DOTALL
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Patched diff plot")
