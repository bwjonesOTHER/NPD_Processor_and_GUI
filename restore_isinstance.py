import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Replace the convolve block to add back the isinstance checks I accidentally removed
old_block = """            UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')"""

new_block = """            if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(specA_s21, np.ndarray):
                specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(UUT_bulkhead_s21, np.ndarray):
                UUT_bulkhead_s21 = np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')"""

content = content.replace(old_block, new_block)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content2 = f.read()

old_block2 = """            cable_s21 = np.convolve(cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            bulk_s21 = np.convolve(bulk_s21, np.ones(n_avg) / n_avg, mode='valid')
            spec_s21 = np.convolve(spec_s21, np.ones(n_avg) / n_avg, mode='valid')"""

new_block2 = """            if isinstance(cable_s21, np.ndarray):
                cable_s21 = np.convolve(cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(bulk_s21, np.ndarray):
                bulk_s21 = np.convolve(bulk_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(spec_s21, np.ndarray):
                spec_s21 = np.convolve(spec_s21, np.ones(n_avg) / n_avg, mode='valid')"""

content2 = content2.replace(old_block2, new_block2)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content2)

print("Restored isinstance checks")
