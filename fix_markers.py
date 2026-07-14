import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# We need to replace markevery=100 with dynamic markevery.
# Instead of doing it inline which is messy, we can insert a variable calculation before plt.plot
# Actually, replacing `markevery=100` with `markevery=max(1, len(freq_ghz)//20)` is easiest!

content = re.sub(r'markevery=100', r'markevery=max(1, len(freq_ghz)//20)', content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content2 = f.read()

content2 = re.sub(r'markevery=100', r'markevery=max(1, len(freq_ghz)//20)', content2)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content2)

print("Fixed markevery")
