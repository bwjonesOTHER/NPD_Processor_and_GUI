import numpy as np

file_avg = np.zeros([10000])
try:
    file_avg = np.mean(file_avg[:,[1,(np.array(file_avg)).shape[1]-1]],axis=1)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
