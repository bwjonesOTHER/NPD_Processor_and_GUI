import re

# 1. Patch NPD_GT_functions.py missed SpecA with lmoFolderB
with open("backend/NPD_GT_functions.py", "r") as f:
    content = f.read()

spec_a_b_replacement = """specA_cable_loss = search_files(lmoFolderB, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0"""
content = re.sub(r"specA_cable_loss\s*=\s*search_files\(lmoFolderB, 'SpecA'\)\n\s+specA_cable_loss\s*=\s*rf\.Network\(specA_cable_loss\[0\]\)\n\s+specA_s21\s*=\s*specA_cable_loss\.s_db\[:,\s*1,\s*0\]", spec_a_b_replacement, content)

with open("backend/NPD_GT_functions.py", "w") as f:
    f.write(content)

# 2. Patch V2 to fallback if _ambient is missing
with open("backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py", "r") as f:
    v2_content = f.read()

v2_content = re.sub(r"filesSparA = search_files\(lmoFolderA, 'NPDoverTempVSWR_ambient',f\"\{serial_number\}\"\)",
                    r"filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR_ambient',f\"{serial_number}\")\n    if not filesSparA:\n        filesSparA = search_files(lmoFolderA, 'NPDoverTempVSWR',f\"{serial_number}\")", v2_content)

v2_content = re.sub(r"filesNPDA = search_files\(lmoFolderA, 'NPDoverTempNPD_ambient',f\"\{serial_number\}\"\)",
                    r"filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD_ambient',f\"{serial_number}\")\n    if not filesNPDA:\n        filesNPDA = search_files(lmoFolderA, 'NPDoverTempNPD',f\"{serial_number}\")", v2_content)

v2_content = re.sub(r"filesSparB = search_files\(lmoFolderB, 'NPDoverTempVSWR_ambient',f\"\{serial_number\}\"\)",
                    r"filesSparB = search_files(lmoFolderB, 'NPDoverTempVSWR_ambient',f\"{serial_number}\")\n    if not filesSparB and lmoFolderB:\n        filesSparB = search_files(lmoFolderB, 'NPDoverTempVSWR',f\"{serial_number}\")", v2_content)

v2_content = re.sub(r"filesNPDB = search_files\(lmoFolderB, 'NPDoverTempNPD_ambient',f\"\{serial_number\}\"\)",
                    r"filesNPDB = search_files(lmoFolderB, 'NPDoverTempNPD_ambient',f\"{serial_number}\")\n    if not filesNPDB and lmoFolderB:\n        filesNPDB = search_files(lmoFolderB, 'NPDoverTempNPD',f\"{serial_number}\")", v2_content)

v2_content = re.sub(r"ref_freq_full = all_freqs\[0\]",
                    r"if not all_freqs:\n            continue\n        ref_freq_full = all_freqs[0]", v2_content)

with open("backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py", "w") as f:
    f.write(v2_content)

# 3. Patch V3 to fix missing files throwing IndexError
with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "r") as f:
    v3_content = f.read()

v3_content = re.sub(r"net = rf\.Network\(spec_files\[0\]\)",
                    r"if not spec_files:\n                continue\n            net = rf.Network(spec_files[0])", v3_content)

v3_content = re.sub(r"return rf\.Network\(files\[0\]\)\.s_db\[:, 1, 0\]",
                    r"if not files:\n                    return 0\n                return rf.Network(files[0]).s_db[:, 1, 0]", v3_content)

v3_content = re.sub(r"loss=loss\[0\]", r"loss = loss[0] if loss else None", v3_content)
v3_content = re.sub(r"gain=gain\[0\]", r"gain = gain[0] if gain else None", v3_content)
v3_content = re.sub(r"loss = loss\[0\]", r"loss = loss[0] if loss else None", v3_content)
v3_content = re.sub(r"gain = gain\[0\]", r"gain = gain[0] if gain else None", v3_content)

with open("backend/Macallan_PMA_NPDxoverTemp_GT_MPedits_V3.py", "w") as f:
    f.write(v3_content)

