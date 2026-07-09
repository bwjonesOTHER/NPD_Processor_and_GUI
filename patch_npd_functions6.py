import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Fix markevery
content = re.sub(
    r'markevery=100',
    r'markevery=max(1, len(freq_ghz_out)//10)',
    content
)

# Fix legend ordering for plotNPD_density_multi (around line 160)
# We need to move `plt.legend` to after the `plt.plot` calls.
# Let's just find plt.legend in all multi-plot functions and move it below.
# The easiest way is to remove plt.legend(...) and put it right before plt.subplots_adjust or plt.savefig

content = re.sub(r'(\s+)plt\.legend\(loc=\'center left\', bbox_to_anchor=\(1, 0\.5\), fontsize=\'8\'\)\n', r'', content)
content = re.sub(r'(\s+)(plt\.subplots_adjust\(right=0\.7\))', r'\1plt.legend(loc=\'center left\', bbox_to_anchor=(1, 0.5), fontsize=\'8\')\1\2', content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

