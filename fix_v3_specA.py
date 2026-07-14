import re

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'r') as f:
    content = f.read()

# Fix load_specA_loss to return filepath
new_load_specA = """    def load_specA_loss(folder):
        spec_files = search_files(folder, "SpecA")
        if not spec_files:
            print(f"No SpecA cable loss file found in: {folder}")
            return None
        return spec_files[0]"""

content = re.sub(
    r'    def load_specA_loss\(folder\):.*?return net\.s_db\[:, 1, 0\].*?except Exception as e:.*?return None',
    new_load_specA,
    content,
    flags=re.DOTALL
)

# Replace spec_s21 assignment in process_file
content = re.sub(
    r'spec_s21 = specA_s21 if isinstance\(specA_s21, np\.ndarray\) else 0',
    r'spec_s21 = safe_s21_interp(specA_s21, freq_ghz)',
    content
)

with open('backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py', 'w') as f:
    f.write(content)

print("Fixed SpecA parsing in V3")
