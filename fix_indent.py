import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = re.sub(r'gain_values=np\.array\(pd\.read_csv\(gain\)\)\n\s+gain_values=gain_values\[:,1\] if len\(gain_values\) > 0 else 0',
                 r'gain_values=np.array(pd.read_csv(gain))\n        gain_values=gain_values[:,1] if len(gain_values) > 0 else 0',
                 content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

