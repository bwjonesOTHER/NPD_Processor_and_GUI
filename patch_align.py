import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# For plotNPD_multi
old_1 = """            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            
            # Interpolate S21 references"""

new_1 = """            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 1], remove_infinite=True)
            min_len = min(len(freq_ghz), len(noise_pow))
            freq_ghz = freq_ghz[:min_len]
            noise_pow = noise_pow[:min_len]
            
            # Interpolate S21 references"""

content = content.replace(old_1, new_1)

# For plotNPD_density_multi
old_2 = """            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True) # Density is index 2
            
            # Interpolate S21 references"""

new_2 = """            freq_ghz = remove_nan(num_df.values[:, 0], remove_infinite=True)
            noise_pow = remove_nan(num_df.values[:, 2], remove_infinite=True) # Density is index 2
            min_len = min(len(freq_ghz), len(noise_pow))
            freq_ghz = freq_ghz[:min_len]
            noise_pow = noise_pow[:min_len]
            
            # Interpolate S21 references"""

content = content.replace(old_2, new_2)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

