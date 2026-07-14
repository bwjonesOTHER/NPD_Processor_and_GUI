import re

with open("backend/NPD_GT_functions.py", "r") as f:
    content = f.read()

replacement_A = """        gain = search_files(lmoFolderA, 'SystemGain')
        gain = gain[0] if gain else None
        
        if gain:
            sys_gain=pd.read_csv(gain)
            sys_gain = sys_gain.apply(pd.to_numeric, errors='coerce')
            sys_gain_freq=remove_nan(sys_gain.values[:, 0], remove_infinite=True)
            sys_gain_val=remove_nan(sys_gain.values[:, 1], remove_infinite=True)
        else:
            sys_gain_freq = np.zeros(0)
            sys_gain_val = np.zeros(0)"""
content = re.sub(r"gain\s*=\s*search_files\(lmoFolderA, 'SystemGain'\)\n\s+gain\s*=\s*gain\[0\] if gain else None\n\s+sys_gain=pd\.read_csv\(gain\)\n\s+sys_gain\s*=\s*sys_gain\.apply\(pd\.to_numeric,\s*errors='coerce'\)\n\s+sys_gain_freq=remove_nan\(sys_gain\.values\[:, 0\], remove_infinite=True\)\n\s+sys_gain_val=remove_nan\(sys_gain\.values\[:, 1\], remove_infinite=True\)", replacement_A, content)

replacement_B = """        gain = search_files(lmoFolderB, 'SystemGain')
        gain = gain[0] if gain else None
        
        if gain:
            sys_gain=pd.read_csv(gain)
            sys_gain = sys_gain.apply(pd.to_numeric, errors='coerce')
            sys_gain_freq=remove_nan(sys_gain.values[:, 0], remove_infinite=True)
            sys_gain_val=remove_nan(sys_gain.values[:, 1], remove_infinite=True)
        else:
            sys_gain_freq = np.zeros(0)
            sys_gain_val = np.zeros(0)"""
content = re.sub(r"gain\s*=\s*search_files\(lmoFolderB, 'SystemGain'\)\n\s+gain\s*=\s*gain\[0\] if gain else None\n\s+sys_gain=pd\.read_csv\(gain\)\n\s+sys_gain\s*=\s*sys_gain\.apply\(pd\.to_numeric,\s*errors='coerce'\)\n\s+sys_gain_freq=remove_nan\(sys_gain\.values\[:, 0\], remove_infinite=True\)\n\s+sys_gain_val=remove_nan\(sys_gain\.values\[:, 1\], remove_infinite=True\)", replacement_B, content)

with open("backend/NPD_GT_functions.py", "w") as f:
    f.write(content)

