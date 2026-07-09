import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace(")    plt.plot", ")\n    plt.plot")
content = content.replace(")    plt.axvline", ")\n    plt.axvline")

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

