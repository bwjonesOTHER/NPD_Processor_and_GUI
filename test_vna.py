import skrf as rf
import os
import glob

# Find an s2p file
s2p_files = glob.glob('uploads/**/*.s2p', recursive=True)
if s2p_files:
    file = s2p_files[0]
    print(f"File: {file}")
    net = rf.Network(file)
    print(f"net.f[0]: {net.f[0]}")
    print(f"net.f[-1]: {net.f[-1]}")
    print(f"net.f / 1e9: {(net.f / 1e9)[0]} to {(net.f / 1e9)[-1]}")
else:
    print("No s2p files found")
