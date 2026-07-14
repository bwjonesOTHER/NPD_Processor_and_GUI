import re

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content = f.read()

debug_code = """
            try:
                noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21
            except Exception as e:
                print(f"DEBUG NOISE MOD V3! noise_pow={getattr(noise_pow, 'shape', noise_pow)}, cable_s21={getattr(cable_s21, 'shape', cable_s21)}, bulk_s21={getattr(bulk_s21, 'shape', bulk_s21)}, spec_s21={getattr(spec_s21, 'shape', spec_s21)}")
                raise e
"""

content = re.sub(r'\n(\s+)noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21', r'\1' + debug_code.strip().replace('\n', '\n' + r'\1'), content)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content)
print("Debug injected V3")
