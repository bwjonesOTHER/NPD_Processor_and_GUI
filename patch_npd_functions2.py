import sys
import re

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = re.sub(
    r'(s21_data = net\.s_db\[:, 1, 0\]\s+plt\.plot\(freq_ghz, s21_data, label=label, color=c, linestyle=line_style\)\s+all_files_avg\.append\(s21_data\))',
    r's21_data = net.s_db[:, 1, 0]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s21_data = np.interp(freq_ghz_out, freq_ghz, s21_data)\n                freq_ghz = freq_ghz_out\n            plt.plot(freq_ghz, s21_data, label=label, color=c, linestyle=line_style)\n            all_files_avg.append(s21_data)',
    content
)

content = re.sub(
    r'(s11_data = net\.s_db\[:, 0, 0\]\s+plt\.plot\(freq_ghz, s11_data, label=label, color=c, linestyle=line_style\)\s+all_files_avg\.append\(s11_data\))',
    r's11_data = net.s_db[:, 0, 0]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s11_data = np.interp(freq_ghz_out, freq_ghz, s11_data)\n                freq_ghz = freq_ghz_out\n            plt.plot(freq_ghz, s11_data, label=label, color=c, linestyle=line_style)\n            all_files_avg.append(s11_data)',
    content
)

content = re.sub(
    r'(s22_data = net\.s_db\[:, 1, 1\]\s+plt\.plot\(freq_ghz, s22_data, label=label, color=c, linestyle=line_style\)\s+all_files_avg\.append\(s22_data\))',
    r's22_data = net.s_db[:, 1, 1]\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                s22_data = np.interp(freq_ghz_out, freq_ghz, s22_data)\n                freq_ghz = freq_ghz_out\n            plt.plot(freq_ghz, s22_data, label=label, color=c, linestyle=line_style)\n            all_files_avg.append(s22_data)',
    content
)

content = re.sub(
    r'(group_delay_ns = group_delay \* 1e9\s+plt\.plot\(freq_ghz, group_delay_ns, label=label, color=c, linestyle=line_style\)\s+all_files_avg\.append\(group_delay_ns\))',
    r'group_delay_ns = group_delay * 1e9\n            if freq_ghz_out is None:\n                freq_ghz_out = freq_ghz\n            else:\n                group_delay_ns = np.interp(freq_ghz_out, freq_ghz, group_delay_ns)\n                freq_ghz = freq_ghz_out\n            plt.plot(freq_ghz, group_delay_ns, label=label, color=c, linestyle=line_style)\n            all_files_avg.append(group_delay_ns)',
    content
)

with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

