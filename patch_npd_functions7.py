import sys

with open('backend/NPD_GT_functions.py', 'r') as f:
    content = f.read()

content = content.replace(r"\'", "'")
content = content.replace("plt.ylabel('NP (dBm)')    plt.plot([freq_min, freq_max]", "plt.ylabel('NP (dBm)')\n    plt.plot([freq_min, freq_max]")
content = content.replace("plt.ylabel('S11 (dB)')    plt.axvline(x=freq_min", "plt.ylabel('S11 (dB)')\n    plt.axvline(x=freq_min")
content = content.replace("plt.ylabel('S22 (dB)')    plt.axvline(x=freq_min", "plt.ylabel('S22 (dB)')\n    plt.axvline(x=freq_min")
content = content.replace("plt.ylabel('Group Delay (ns)')    plt.axvline(x=freq_min", "plt.ylabel('Group Delay (ns)')\n    plt.axvline(x=freq_min")
content = content.replace("plt.ylabel('S21 (dB)')    plt.axvline(x=freq_min", "plt.ylabel('S21 (dB)')\n    plt.axvline(x=freq_min")
with open('backend/NPD_GT_functions.py', 'w') as f:
    f.write(content)

