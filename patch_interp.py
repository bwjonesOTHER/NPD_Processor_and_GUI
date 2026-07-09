import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

old_block = """            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            
            if n_avg > 1:"""

new_block = """            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            
            # Interpolate S21 references to match the noise_pow frequency grid before any smoothing
            if isinstance(UUT_cable_s21, np.ndarray) and len(UUT_cable_s21) != len(noise_pow):
                UUT_cable_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(UUT_cable_s21)), UUT_cable_s21)
            if isinstance(specA_s21, np.ndarray) and len(specA_s21) != len(noise_pow):
                specA_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(specA_s21)), specA_s21)
            if isinstance(UUT_bulkhead_s21, np.ndarray) and len(UUT_bulkhead_s21) != len(noise_pow):
                UUT_bulkhead_s21 = np.interp(freq_ghz, np.linspace(freq_ghz[0], freq_ghz[-1], len(UUT_bulkhead_s21)), UUT_bulkhead_s21)

            if n_avg > 1:"""

content = content.replace(old_block, new_block)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

