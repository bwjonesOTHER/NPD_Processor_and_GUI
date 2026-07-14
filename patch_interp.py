import numpy as np
from scipy.interpolate import interp1d

# Mock data
freq1 = np.linspace(0, 4, 4001)
data1 = np.sin(freq1)

freq2 = np.linspace(0, 4.5, 4001)
data2 = np.sin(freq2)

common_freq = np.linspace(0.7, 4.1, 1000)

f1 = interp1d(freq1, data1, bounds_error=False, fill_value=np.nan)
f2 = interp1d(freq2, data2, bounds_error=False, fill_value=np.nan)

d1 = f1(common_freq)
d2 = f2(common_freq)

avg = np.nanmean([d1, d2], axis=0)
print(avg.shape)
