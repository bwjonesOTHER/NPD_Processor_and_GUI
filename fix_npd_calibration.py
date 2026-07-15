import re

content = open('backend/plot_generator.py', 'r').read()

# 1. Update plotNPD signature
content = content.replace(
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder):',
    'def plotNPD(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder):'
)

# 2. Update load_np_data to apply calibration
old_load_np = """        if len(noise) == 0 or len(freq) == 0:
            return np.array([]), np.array([])
        if n_avg > 1:
            noise = np.convolve(noise, np.ones(n_avg) / n_avg, mode='valid')
            freq = freq[int(n_avg / 2):int(1 - n_avg / 2):1]
        return freq, noise"""

new_load_np = """        if len(noise) == 0 or len(freq) == 0:
            return np.array([]), np.array([])
            
        if freq_cal is not None:
            loss_interp = np.interp(freq, freq_cal, total_loss_db)
            noise = noise + loss_interp
            
        if n_avg > 1:
            noise = np.convolve(noise, np.ones(n_avg) / n_avg, mode='valid')
            freq = freq[int(n_avg / 2):int(1 - n_avg / 2):1]
        return freq, noise"""

content = content.replace(old_load_np, new_load_np)

# 3. Update calls to plotNPD
content = content.replace(
    'p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)',
    'p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder)'
)
content = content.replace(
    'p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, output_folder)',
    'p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, freq_cal, total_loss_db, output_folder)'
)

open('backend/plot_generator.py', 'w').write(content)
