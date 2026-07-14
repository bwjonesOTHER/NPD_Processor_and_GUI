import re

with open("backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py", "r") as f:
    content = f.read()

content = re.sub(r"if not all_freqs:\n\s+continue", "if not all_freqs:\n            return", content)

with open("backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py", "w") as f:
    f.write(content)

