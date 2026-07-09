import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = re.sub(r'(plt\.ylabel\([^)]+\))\s+(plt\.)', r'\1\n    \2', content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

