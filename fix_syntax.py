import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace('noise_pow_mod==', 'noise_pow_mod=')

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Syntax fixed")
