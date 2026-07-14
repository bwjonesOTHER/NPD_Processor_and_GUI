import re

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "r") as f:
    content = f.read()

# Fix UUT_cable
replacement_uut = """            if loss:
                UUT_cable=rf.Network(loss)
                UUT_cable_s21=UUT_cable.s_db[:,1,0]
                if isinstance(UUT_cable_s21, np.ndarray):
                    UUT_cable_s21=np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            else:
                UUT_cable_s21 = 0"""
content = re.sub(r"\s+UUT_cable=rf\.Network\(loss\)\n\s+UUT_cable_s21=UUT_cable\.s_db\[:,1,0\]\n\s+UUT_cable_s21=np\.convolve\(UUT_cable_s21, np\.ones\(n_avg\) / n_avg, mode='valid'\)", replacement_uut, content)

# Fix gain reading
replacement_gain = """            if gain:
                gain_values=np.array(pd.read_csv(gain))
                gain_values=gain_values[:,1]
            else:
                gain_values = 0"""
content = re.sub(r"\s+gain_values=np\.array\(pd\.read_csv\(gain\)\)\n\s+gain_values=gain_values\[:,1\]", replacement_gain, content)

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "w") as f:
    f.write(content)

