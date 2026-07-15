import numpy as np

try:
    a = np.zeros((5, 5))
    a[:, :] = np.zeros(5)
except Exception as e:
    print("Test 1:", repr(e))

try:
    a = np.zeros((2, 2, 2))
    a[:, :, :] = np.zeros((2, 2))
except Exception as e:
    print("Test 2:", repr(e))

try:
    np.array([np.zeros((2,2)), np.zeros(2)])
except Exception as e:
    print("Test 3:", repr(e))

try:
    a = np.zeros(5)
    a[0] = [1, 2]
except Exception as e:
    print("Test 4:", repr(e))
    
try:
    a = np.zeros((5, 5))
    np.convolve(a, np.ones(5)/5)
except Exception as e:
    print("Test 5:", repr(e))
