import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace("int(1-n_avg/2):1]", "-int(n_avg/2)]")
content = content.replace("markevery=max(1, len(freq_ghz_out)//10)", "markevery=max(1, len(freq_ghz_out)//15)")

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

