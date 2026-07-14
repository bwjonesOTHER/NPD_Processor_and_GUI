import re

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "r") as f:
    content = f.read()

replacement = """            if loss:
                UUT_cable=rf.Network(loss)
                UUT_cable_s21=UUT_cable.s_db[:,1,0]
            else:
                UUT_cable_s21 = 0"""

content = re.sub(r"\s+UUT_cable=rf\.Network\(loss\)\n\s+UUT_cable_s21=UUT_cable\.s_db\[:,1,0\]", replacement, content)

replacement_conv = """            if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21=np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')"""
content = re.sub(r"\s+UUT_cable_s21=np\.convolve\(UUT_cable_s21, np\.ones\(n_avg\) / n_avg, mode='valid'\)", replacement_conv, content)

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "w") as f:
    f.write(content)

