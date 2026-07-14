import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Protect specA_cable_loss
    content = re.sub(
        r'specA_s21\s*=\s*specA_cable_loss\.s_db\[:,\s*1,\s*0\]',
        r'specA_s21 = specA_cable_loss.s_db[:, 1, 0] if len(specA_cable_loss.s_db) > 0 else 0',
        content
    )

    # Protect UUT_cable
    content = re.sub(
        r'UUT_cable_s21\s*=\s*UUT_cable\.s_db\[:,\s*1,\s*0\]',
        r'UUT_cable_s21 = UUT_cable.s_db[:, 1, 0] if len(UUT_cable.s_db) > 0 else 0',
        content
    )

    # Protect UUT_bulkhead
    content = re.sub(
        r'UUT_bulkhead_s21\s*=\s*UUT_bulkhead\.s_db\[:,\s*1,\s*0\]',
        r'UUT_bulkhead_s21 = UUT_bulkhead.s_db[:, 1, 0] if len(UUT_bulkhead.s_db) > 0 else 0',
        content
    )

    # Protect gain_values
    content = re.sub(
        r'gain_values\s*=\s*np\.array\(pd\.read_csv\(gain\)\)\n\s+gain_values\s*=\s*gain_values\[:,\s*1\]',
        r'gain_values=np.array(pd.read_csv(gain))\n            gain_values=gain_values[:,1] if len(gain_values) > 0 else 0',
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched zero shapes in {filepath}")

process_file('backend/NPD_GT_functions.py')

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content = f.read()
    
    # Protect cable_s21 and bulk_s21
    content = re.sub(
        r'cable_s21 = rf.Network\(base_loss\)\.s_db\[:, 1, 0\] if base_loss else 0',
        r'cable_s21 = (lambda n: n.s_db[:, 1, 0] if len(n.s_db) > 0 else 0)(rf.Network(base_loss)) if base_loss else 0',
        content
    )
    content = re.sub(
        r'bulk_s21 = rf.Network\(bulk_loss\)\.s_db\[:, 1, 0\] if bulk_loss else 0',
        r'bulk_s21 = (lambda n: n.s_db[:, 1, 0] if len(n.s_db) > 0 else 0)(rf.Network(bulk_loss)) if bulk_loss else 0',
        content
    )
    
    # Protect specA parsing in load_specA
    content = re.sub(
        r'return net.s_db\[:, 1, 0\]',
        r'return net.s_db[:, 1, 0] if len(net.s_db) > 0 else None',
        content
    )
    content = re.sub(
        r'return rf.Network\(files\[0\]\).s_db\[:, 1, 0\]',
        r'return (lambda n: n.s_db[:, 1, 0] if len(n.s_db) > 0 else None)(rf.Network(files[0]))',
        content
    )
    
    # Protect gain_values
    content = re.sub(
        r'gain_values=np.array\(pd.read_csv\(gain\)\)\n\s+gain_values=gain_values\[:, 1\]',
        r'gain_values=np.array(pd.read_csv(gain))\n                gain_values=gain_values[:, 1] if len(gain_values) > 0 else 0',
        content
    )
    
    with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
        f.write(content)
    print("Patched zero shapes in V3")
    
