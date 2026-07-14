import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Fix assignments
content = re.sub(
    r'([ \t]+)diff_npd25_npd64 = np\.abs\(NPD25\[1\] - NPD64\[1\]\)\n\s+diff_npd25_npdn38 = np\.abs\(NPD25\[1\] - NPDn38\[1\]\)\n\s+diff_npd64_npdn38 = np\.abs\(NPD64\[1\] - NPDn38\[1\]\)',
    r'\1diff_npd25_npd64 = np.abs(NPD25[1] - NPD64[1]) if (len(NPD25) > 1 and len(NPD64) > 1 and len(NPD25[1]) > 0 and len(NPD64[1]) > 0) else []\n'
    r'\1diff_npd25_npdn38 = np.abs(NPD25[1] - NPDn38[1]) if (len(NPD25) > 1 and len(NPDn38) > 1 and len(NPD25[1]) > 0 and len(NPDn38[1]) > 0) else []\n'
    r'\1diff_npd64_npdn38 = np.abs(NPD64[1] - NPDn38[1]) if (len(NPD64) > 1 and len(NPDn38) > 1 and len(NPD64[1]) > 0 and len(NPDn38[1]) > 0) else []',
    content
)

# Fix plots
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD25\[0\],\s*diff_npd25_npd64.*?\))',
    r'\1if len(diff_npd25_npd64) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD25\[0\],\s*diff_npd25_npdn38.*?\))',
    r'\1if len(diff_npd25_npdn38) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD64\[0\],\s*diff_npd64_npdn38.*?\)|plt\.plot\(NPD25\[0\],\s*diff_npd64_npdn38.*?\))',
    r'\1if len(diff_npd64_npdn38) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Patched all diffs")
