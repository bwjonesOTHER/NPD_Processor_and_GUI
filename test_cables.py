import skrf as rf
import numpy as np
import sys
import os

def get_loss(f):
    try:
        net = rf.Network(f)
        idx = np.abs(net.f - 3e9).argmin()
        print(f"{f.split('/')[-1]}: {np.abs(net.s_db[idx, 1, 0]):.2f} dB at {net.f[idx]/1e9} GHz")
    except Exception as e:
        print(f"Error reading {f}: {e}")

try:
    # Need to find the temp_uploads dir
    base_dir = "backend/temp_uploads"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if "BaseSN5Cable" in file or "Bulkhead_SN05" in file or "BaseBulkSN6" in file:
                get_loss(os.path.join(root, file).replace("\\", "/"))
except Exception as e:
    print(e)
