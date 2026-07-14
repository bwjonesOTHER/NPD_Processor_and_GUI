import NPD_GT_functions
import os
os.makedirs("test_run", exist_ok=True)
with open("test_run/file_NPDoverTempNPD.csv", "w") as f: f.write("test")
files = NPD_GT_functions.search_files("test_run", "NPDOverTempNPD")
print("Files:", files)
