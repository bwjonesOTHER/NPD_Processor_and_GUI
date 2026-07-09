import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Remove the unconditional freq_ghz_out = freq_ghz lines
content = re.sub(
    r'(freq_ghz = net\.f / 1e9\s+)freq_ghz_out = freq_ghz\n',
    r'\1',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

