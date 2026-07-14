import os
import re

with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'r') as f:
    content = f.read()

# Replace plotNPD
# We need to find the loop in plotNPD and replace the average logic
target_npd = """        if not all_freqs:
            return
        ref_freq_full = all_freqs[0]
        
        idx_min = (np.abs(ref_freq_full - freq_min)).argmin()
        idx_max = (np.abs(ref_freq_full - freq_max)).argmin()
        if idx_min > idx_max:
            idx_min, idx_max = idx_max, idx_min
            
        all_noise_win = np.array([noise[idx_min:idx_max] for noise in all_noise])
        ref_freq_win = ref_freq_full[idx_min:idx_max]

        # ---- compute average + bounds ---- #
        avg = np.mean(all_noise_win, axis=0)"""

replacement_npd = """        if not all_freqs:
            return
        
        from scipy.interpolate import interp1d
        common_freq = np.linspace(freq_min, freq_max, 1000)
        all_noise_win = []
        for i in range(len(all_freqs)):
            f_interp = interp1d(all_freqs[i], all_noise[i], bounds_error=False, fill_value=np.nan)
            all_noise_win.append(f_interp(common_freq))
            
        all_noise_win = np.array(all_noise_win)
        ref_freq_win = common_freq

        # ---- compute average + bounds ---- #
        avg = np.nanmean(all_noise_win, axis=0)"""

content = content.replace(target_npd, replacement_npd)

with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'w') as f:
    f.write(content)
