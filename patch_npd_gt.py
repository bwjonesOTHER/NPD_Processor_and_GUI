import re

with open("backend/NPD_GT_functions.py", "r") as f:
    content = f.read()

# 1. Fix cap_searchA and cap_searchB to not index [0] unsafely
content = re.sub(r"loss\s*=\s*search_files\((.*?)\)\n\s+loss\s*=\s*loss\[0\]", 
                 r"loss = search_files(\1)\n        loss = loss[0] if loss else None", content)

content = re.sub(r"loss_bulkhead\s*=\s*search_files\((.*?)\)\n\s+loss_bulkhead\s*=\s*loss_bulkhead\[0\]", 
                 r"loss_bulkhead = search_files(\1)\n        loss_bulkhead = loss_bulkhead[0] if loss_bulkhead else None", content)

content = re.sub(r"gain\s*=\s*search_files\((.*?)\)\n\s+gain\s*=\s*gain\[0\]", 
                 r"gain = search_files(\1)\n        gain = gain[0] if gain else None", content)

# 2. Fix the plotting functions that consume `loss` and `loss_bulkhead`
# They do:
# loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
# UUT_cable=rf.Network(loss)
# UUT_cable_s21=UUT_cable.s_db[:,1,0]
# UUT_bulkhead=rf.Network(loss_bulkhead)
# UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]

replacement = """        loss,loss_bulkhead=cap_searchA(file,lmoFolderA)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0"""
content = re.sub(r"loss,loss_bulkhead=cap_searchA\(file,lmoFolderA\)\n\s+UUT_cable=rf\.Network\(loss\)\n\s+UUT_cable_s21=UUT_cable\.s_db\[:,1,0\]\n\s+UUT_bulkhead=rf\.Network\(loss_bulkhead\)\n\s+UUT_bulkhead_s21=UUT_bulkhead\.s_db\[:,1,0\]", replacement, content)

replacementB = """        loss,loss_bulkhead=cap_searchB(file,lmoFolderB)
        if loss:
            UUT_cable=rf.Network(loss)
            UUT_cable_s21=UUT_cable.s_db[:,1,0]
        else:
            UUT_cable_s21 = 0
        if loss_bulkhead:
            UUT_bulkhead=rf.Network(loss_bulkhead)
            UUT_bulkhead_s21=UUT_bulkhead.s_db[:,1,0]
        else:
            UUT_bulkhead_s21 = 0"""
content = re.sub(r"loss,loss_bulkhead=cap_searchB\(file,lmoFolderB\)\n\s+UUT_cable=rf\.Network\(loss\)\n\s+UUT_cable_s21=UUT_cable\.s_db\[:,1,0\]\n\s+UUT_bulkhead=rf\.Network\(loss_bulkhead\)\n\s+UUT_bulkhead_s21=UUT_bulkhead\.s_db\[:,1,0\]", replacementB, content)

# 3. Fix SpecA cable loss
spec_a_replacement = """specA_cable_loss = search_files(lmoFolderA, 'SpecA')
        if specA_cable_loss:
            specA_cable_loss = rf.Network(specA_cable_loss[0])
            specA_s21 = specA_cable_loss.s_db[:, 1, 0]
        else:
            specA_s21 = 0"""
content = re.sub(r"specA_cable_loss\s*=\s*search_files\(lmoFolderA, 'SpecA'\)\n\s+specA_cable_loss\s*=\s*rf\.Network\(specA_cable_loss\[0\]\)\n\s+specA_s21\s*=\s*specA_cable_loss\.s_db\[:,\s*1,\s*0\]", spec_a_replacement, content)

spec_b_replacement = """specB_cable_loss = search_files(lmoFolderB, 'SpecB')
        if specB_cable_loss:
            specB_cable_loss = rf.Network(specB_cable_loss[0])
            specB_s21 = specB_cable_loss.s_db[:, 1, 0]
        else:
            specB_s21 = 0"""
content = re.sub(r"specB_cable_loss\s*=\s*search_files\(lmoFolderB, 'SpecB'\)\n\s+specB_cable_loss\s*=\s*rf\.Network\(specB_cable_loss\[0\]\)\n\s+specB_s21\s*=\s*specB_cable_loss\.s_db\[:,\s*1,\s*0\]", spec_b_replacement, content)


# 4. Fix np.convolve to handle 0
convolve_repl_A = """if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(UUT_bulkhead_s21, np.ndarray):
                UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(specA_s21, np.ndarray):
                specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')"""
content = re.sub(r"UUT_cable_s21\s*=\s*np\.convolve\(UUT_cable_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)\n\s+UUT_bulkhead_s21=np\.convolve\(UUT_bulkhead_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)\n\s+specA_s21=np\.convolve\(specA_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)", convolve_repl_A, content)

convolve_repl_B = """if isinstance(UUT_cable_s21, np.ndarray):
                UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(UUT_bulkhead_s21, np.ndarray):
                UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
            if isinstance(specB_s21, np.ndarray):
                specB_s21=np.convolve(specB_s21, np.ones(n_avg) / n_avg, mode='valid')"""
content = re.sub(r"UUT_cable_s21\s*=\s*np\.convolve\(UUT_cable_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)\n\s+UUT_bulkhead_s21=np\.convolve\(UUT_bulkhead_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)\n\s+specB_s21=np\.convolve\(specB_s21,\s*np\.ones\(n_avg\)\s*/\s*n_avg,\s*mode='valid'\)", convolve_repl_B, content)


with open("backend/NPD_GT_functions_patched.py", "w") as f:
    f.write(content)

