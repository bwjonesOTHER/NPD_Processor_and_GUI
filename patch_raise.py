import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace("raise e", "raise Exception(f'DEBUG: noise_pow={getattr(noise_pow, \"shape\", noise_pow)}, spec={getattr(specA_s21, \"shape\", specA_s21)}, cable={getattr(UUT_cable_s21, \"shape\", UUT_cable_s21)}, bulk={getattr(UUT_bulkhead_s21, \"shape\", UUT_bulkhead_s21)} | Error: {e}')")

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content2 = f.read()

content2 = content2.replace("raise e", "raise Exception(f'DEBUG V3: noise={getattr(noise_pow, \"shape\", noise_pow)}, cable={getattr(cable_s21, \"shape\", cable_s21)}, bulk={getattr(bulk_s21, \"shape\", bulk_s21)}, spec={getattr(spec_s21, \"shape\", spec_s21)} | Error: {e}')")

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content2)
print("Updated exceptions to raise debug info")
