import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

debug_code = """
        try:
            noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21
        except Exception as e:
            print(f"DEBUG NOISE POW MOD! noise_pow={getattr(noise_pow, 'shape', noise_pow)}, specA_s21={getattr(specA_s21, 'shape', specA_s21)}, UUT_cable_s21={getattr(UUT_cable_s21, 'shape', UUT_cable_s21)}, UUT_bulk_s21={getattr(UUT_bulkhead_s21, 'shape', UUT_bulkhead_s21)}")
            raise e
"""

content = re.sub(r'\n(\s+)noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21', r'\1' + debug_code.strip().replace('\n', '\n' + r'\1'), content)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)
print("Debug injected")
