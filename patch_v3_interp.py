import re

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content = f.read()

helper_func = """    def safe_s21_interp(file_path, target_freq):
        import skrf as rf
        import numpy as np
        if not file_path: return 0
        try:
            net = rf.Network(file_path)
            if len(net.s_db) == 0: return 0
            s21 = net.s_db[:, 1, 0]
            if len(s21) != len(target_freq) and len(s21) > 1:
                return np.interp(target_freq, net.f / 1e9, s21)
            return s21
        except:
            return 0
"""

# Insert helper function at the top of generate_plots
content = content.replace("    def extract_pri_red(filename):", helper_func + "\n    def extract_pri_red(filename):")

# Replace lambdas with helper function call
# For cable_s21
content = re.sub(
    r'cable_s21 = \(lambda n: n\.s_db\[:, 1, 0\] if len\(n\.s_db\) > 0 else 0\)\(rf\.Network\(base_loss\)\) if base_loss else 0',
    r'cable_s21 = safe_s21_interp(base_loss, freq_ghz)',
    content
)

# For bulk_s21
content = re.sub(
    r'bulk_s21 = \(lambda n: n\.s_db\[:, 1, 0\] if len\(n\.s_db\) > 0 else 0\)\(rf\.Network\(bulk_loss\)\) if bulk_loss else 0',
    r'bulk_s21 = safe_s21_interp(bulk_loss, freq_ghz)',
    content
)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content)
print("Patched V3")
