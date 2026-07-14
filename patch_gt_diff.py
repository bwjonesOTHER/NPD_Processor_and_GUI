import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Fix assignments
content = re.sub(
    r'([ \t]+)diff_GT25_GT64 = np\.abs\(GT25\[1\] - GT64\[1\]\)\n\s+diff_GT25_GTn38 = np\.abs\(GT25\[1\] - GTn38\[1\]\)\n\s+diff_GT64_GTn38 = np\.abs\(GT64\[1\] - GTn38\[1\]\)',
    r'\1diff_GT25_GT64 = np.abs(GT25[1] - GT64[1]) if (len(GT25) > 1 and len(GT64) > 1 and len(GT25[1]) > 0 and len(GT64[1]) > 0) else []\n'
    r'\1diff_GT25_GTn38 = np.abs(GT25[1] - GTn38[1]) if (len(GT25) > 1 and len(GTn38) > 1 and len(GT25[1]) > 0 and len(GTn38[1]) > 0) else []\n'
    r'\1diff_GT64_GTn38 = np.abs(GT64[1] - GTn38[1]) if (len(GT64) > 1 and len(GTn38) > 1 and len(GT64[1]) > 0 and len(GTn38[1]) > 0) else []',
    content
)

# Fix plots
# 1. Delta 25/64
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD25\[0\],\s*diff_GT25_GT64.*?\))',
    r'\1if len(diff_GT25_GT64) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)
# 2. Delta 25/n38
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD25\[0\],\s*diff_GT25_GTn38.*?\))',
    r'\1if len(diff_GT25_GTn38) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)
# 3. Delta 64/n38
content = re.sub(
    r'([ \t]+)(plt\.plot\(NPD25\[0\],\s*diff_GT64_GTn38.*?\))',
    r'\1if len(diff_GT64_GTn38) > 0 and len(NPD25) > 0 and len(NPD25[0]) > 0:\n\1    \2',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Patched GT diff plots")
