import sys
sys.path.append('backend')
import skrf as rf
import os
import glob

def check_cables(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.s2p'):
                path = os.path.join(root, file)
                try:
                    net = rf.Network(path)
                    print(f"{file}: {net.s_db[0:2, 1, 0]}")
                except Exception as e:
                    pass

print("Checking uploads directory for cables...")
check_cables('backend/uploads')
