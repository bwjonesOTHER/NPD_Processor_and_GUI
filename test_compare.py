import sys
import os

# We will run the original Test 3 script and see what files it finds and what plots it saves
# We need to set up the environment variables or input files for Test 3
import shutil

# Read SN
sn = ""
if os.path.exists("serialNumber.txt"):
    with open("serialNumber.txt", "r") as f:
        sn = f.read().strip()
        
# Read paths
runA = ""
runB = ""
if os.path.exists("RunA_Path.txt"):
    with open("RunA_Path.txt", "r") as f:
        runA = f.read().strip()
if os.path.exists("RunB_Path.txt"):
    with open("RunB_Path.txt", "r") as f:
        runB = f.read().strip()

print(f"SN: {sn}")
print(f"RunA: {runA}")
print(f"RunB: {runB}")
