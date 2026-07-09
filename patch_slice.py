import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Replace the smoothing block in plotNPD_multi
old_block1 = """            if n_avg > 1:
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                freq_ghz = freq_ghz[int(n_avg/2):-int(n_avg/2)]
                if isinstance(UUT_cable_s21, np.ndarray):
                    UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(specA_s21, np.ndarray):
                    specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
                if isinstance(UUT_bulkhead_s21, np.ndarray):
                    UUT_bulkhead_s21 = np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')"""

new_block1 = """            if n_avg > 1:
                original_len = len(noise_pow)
                noise_pow = np.convolve(noise_pow, np.ones(n_avg) / n_avg, mode='valid')
                diff = len(freq_ghz) - len(noise_pow)
                if diff > 0:
                    start = diff // 2
                    end = diff - start
                    freq_ghz = freq_ghz[start:-end] if end > 0 else freq_ghz[start:]
                
                if isinstance(UUT_cable_s21, np.ndarray) and len(UUT_cable_s21) == original_len:
                    UUT_cable_s21 = np.convolve(UUT_cable_s21, np.ones(n_avg) / n_avg, mode='valid')
                elif isinstance(UUT_cable_s21, np.ndarray):
                    UUT_cable_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(UUT_cable_s21)), UUT_cable_s21)
                    
                if isinstance(specA_s21, np.ndarray) and len(specA_s21) == original_len:
                    specA_s21 = np.convolve(specA_s21, np.ones(n_avg) / n_avg, mode='valid')
                elif isinstance(specA_s21, np.ndarray):
                    specA_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(specA_s21)), specA_s21)
                    
                if isinstance(UUT_bulkhead_s21, np.ndarray) and len(UUT_bulkhead_s21) == original_len:
                    UUT_bulkhead_s21 = np.convolve(UUT_bulkhead_s21, np.ones(n_avg) / n_avg, mode='valid')
                elif isinstance(UUT_bulkhead_s21, np.ndarray):
                    UUT_bulkhead_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(UUT_bulkhead_s21)), UUT_bulkhead_s21)
"""
content = content.replace(old_block1, new_block1)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

