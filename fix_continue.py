import re

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "r") as f:
    content = f.read()

content = re.sub(r"if not spec_files:\n\s+continue", "if not spec_files:\n                return 0", content)

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "w") as f:
    f.write(content)

