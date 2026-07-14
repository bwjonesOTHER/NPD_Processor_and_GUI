import re

with open("backend/NPD_GT_functions.py", "r") as f:
    content = f.read()

replacement = """        if len(sys_gain_val) == 0:
            continue
        elif len(sys_gain_val) == 1:"""
content = re.sub(r"if len\(sys_gain_val\) == 1:", replacement, content)

with open("backend/NPD_GT_functions.py", "w") as f:
    f.write(content)

