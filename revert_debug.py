import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Remove the try/except block around noise_pow_mod
content = re.sub(
    r'\s+try:\s+noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21\s+except Exception as e:\s+print\(.*?\)\s+raise Exception\(.*?\)',
    r'\n        noise_pow_mod=noise_pow-specA_s21-UUT_cable_s21-UUT_bulkhead_s21',
    content,
    flags=re.DOTALL
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content2 = f.read()

content2 = re.sub(
    r'\s+try:\s+noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21\s+except Exception as e:\s+print\(.*?\)\s+raise Exception\(.*?\)',
    r'\n            noise_mod = noise_pow - cable_s21 - bulk_s21 - spec_s21',
    content2,
    flags=re.DOTALL
)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content2)

print("Reverted debug blocks")
