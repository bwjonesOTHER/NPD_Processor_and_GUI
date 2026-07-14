import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

interp_code = """        if isinstance(specA_s21, np.ndarray) and len(specA_s21) > 1 and len(specA_s21) != len(freq_ghz):
            specA_s21 = np.interp(freq_ghz, specA_cable_loss.f / 1e9, specA_s21)
        if isinstance(UUT_cable_s21, np.ndarray) and len(UUT_cable_s21) > 1 and len(UUT_cable_s21) != len(freq_ghz):
            UUT_cable_s21 = np.interp(freq_ghz, UUT_cable.f / 1e9, UUT_cable_s21)
        if isinstance(UUT_bulkhead_s21, np.ndarray) and len(UUT_bulkhead_s21) > 1 and len(UUT_bulkhead_s21) != len(freq_ghz):
            UUT_bulkhead_s21 = np.interp(freq_ghz, UUT_bulkhead.f / 1e9, UUT_bulkhead_s21)
"""

# Remove the incorrectly placed interp code
content = content.replace(interp_code, "")

# Insert it before if n_avg > 1:
content = re.sub(r'\n(\s+)if n_avg > 1:', r'\n' + interp_code + r'\1if n_avg > 1:', content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Patched NPD_GT_functions.py")
