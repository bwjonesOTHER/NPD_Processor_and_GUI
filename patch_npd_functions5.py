import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace('            \n            serial', '            serial')
content = content.replace('                        serial', '            serial')

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

