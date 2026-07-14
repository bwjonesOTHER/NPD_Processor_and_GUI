import NPD_GT_functions
import numpy as np

# create dummy data
noise_pow = np.random.rand(100)
freq_ghz = np.linspace(2.7, 4.1, 100)
UUT_cable_s21 = np.random.rand(100)
UUT_bulkhead_s21 = np.random.rand(100)
specA_s21 = np.random.rand(100)
noise_pow_den = np.random.rand(100)

n_avg = 1

if n_avg > 1:
    noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
    noise_pow_den = np.convolve(noise_pow_den, np.ones(n_avg) / n_avg, mode='valid')
    freq_ghz = freq_ghz[int(n_avg/2):int(1-n_avg/2):1]
    UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
    specA_s21=np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
    UUT_bulkhead_s21=np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')

print(len(noise_pow), len(freq_ghz))
