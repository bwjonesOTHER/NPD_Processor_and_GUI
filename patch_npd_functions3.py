import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = re.sub(
    r'(group_delay_ns = group_delay \* 1e9\s+plt\.plot\(freq_ghz, group_delay_ns, label=label, color=c, linestyle=line_style\)\s+all_files_avg\.append\(group_delay_ns\))',
    r'group_delay_ns = group_delay * 1e9\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                group_delay_ns = np.interp(freq_ghz_out, freq_ghz, group_delay_ns)\n                freq_ghz = freq_ghz_out\n            plt.plot(freq_ghz, group_delay_ns, label=label, color=c, linestyle=line_style)\n            all_files_avg.append(group_delay_ns)',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

