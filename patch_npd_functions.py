import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

# Fix npdd density
content = re.sub(
    r'(noise_pow_mod = noise_pow_den - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21 - g_t\s+all_files_avg\.append\(noise_pow_mod\))',
    r'noise_pow_mod = noise_pow_den - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21 - g_t\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                noise_pow_mod = np.interp(freq_ghz_out, freq_ghz, noise_pow_mod)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(noise_pow_mod)',
    content
)

# Fix np
content = re.sub(
    r'(noise_pow_mod = noise_pow - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21\s+all_files_avg\.append\(noise_pow_mod\))',
    r'noise_pow_mod = noise_pow - specA_s21 - UUT_cable_s21 - UUT_bulkhead_s21\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                noise_pow_mod = np.interp(freq_ghz_out, freq_ghz, noise_pow_mod)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(noise_pow_mod)',
    content
)

# Fix s21
content = re.sub(
    r'(s21_data = net\.s_db\[:, 1, 0\]\s+all_files_avg\.append\(s21_data\))',
    r's21_data = net.s_db[:, 1, 0]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s21_data = np.interp(freq_ghz_out, freq_ghz, s21_data)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(s21_data)',
    content
)

# Fix s11
content = re.sub(
    r'(s11_data = net\.s_db\[:, 0, 0\]\s+all_files_avg\.append\(s11_data\))',
    r's11_data = net.s_db[:, 0, 0]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s11_data = np.interp(freq_ghz_out, freq_ghz, s11_data)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(s11_data)',
    content
)

# Fix s22
content = re.sub(
    r'(s22_data = net\.s_db\[:, 1, 1\]\s+all_files_avg\.append\(s22_data\))',
    r's22_data = net.s_db[:, 1, 1]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s22_data = np.interp(freq_ghz_out, freq_ghz, s22_data)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(s22_data)',
    content
)

# Fix gd
content = re.sub(
    r'(group_delay_ns = group_delay \* 1e9\s+all_files_avg\.append\(group_delay_ns\))',
    r'group_delay_ns = group_delay * 1e9\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                group_delay_ns = np.interp(freq_ghz_out, freq_ghz, group_delay_ns)\n                freq_ghz = freq_ghz_out\n            all_files_avg.append(group_delay_ns)',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

