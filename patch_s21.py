import os

with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'r') as f:
    content = f.read()

target_s21_a = """            idx_min = (np.abs(freq_ghz - freq_min)).argmin()
            idx_max = (np.abs(freq_ghz - freq_max)).argmin()
            if idx_min > idx_max: idx_min, idx_max = idx_max, idx_min
            
            s21_values = net.s_db[idx_min:idx_max, 1, 0]
            avg_collection.append(s21_values)
            file_coll.append(serial[-21:-4:1])"""

replace_s21 = """            from scipy.interpolate import interp1d
            common_freq = np.linspace(freq_min, freq_max, 1000)
            f_interp = interp1d(freq_ghz, net.s_db[:, 1, 0], bounds_error=False, fill_value=np.nan)
            avg_collection.append(f_interp(common_freq))
            file_coll.append(serial[-21:-4:1])"""

content = content.replace(target_s21_a, replace_s21)

target_s21_bounds = """        s21_avg = np.array(avg_collection)
        files_collected = np.array(file_coll)
        avg = np.mean(s21_avg, axis=0)"""

replace_s21_bounds = """        s21_avg = np.array(avg_collection)
        files_collected = np.array(file_coll)
        avg = np.nanmean(s21_avg, axis=0)
        ref_freq_ghz = np.linspace(freq_min, freq_max, 1000)"""

content = content.replace(target_s21_bounds, replace_s21_bounds)

target_s21_plot = """        idx_min = (np.abs(ref_freq_ghz - freq_min)).argmin()
        idx_max = (np.abs(ref_freq_ghz - freq_max)).argmin()
        if idx_min > idx_max: idx_min, idx_max = idx_max, idx_min
        
        plt.plot(ref_freq_ghz[idx_min:idx_max], lb, color='red', alpha=1,
                 marker='o', markersize=5, markevery=100, label='Lower bound')

        plt.plot(ref_freq_ghz[idx_min:idx_max], ub, color='red', alpha=1,
                 marker='x', markersize=5, markevery=100, label='Upper bound')"""

replace_s21_plot = """        plt.plot(ref_freq_ghz, lb, color='red', alpha=1,
                 marker='o', markersize=5, markevery=100, label='Lower bound')

        plt.plot(ref_freq_ghz, ub, color='red', alpha=1,
                 marker='x', markersize=5, markevery=100, label='Upper bound')"""

content = content.replace(target_s21_plot, replace_s21_plot)

with open('backend/Macallan_PMA_BenchtopNPD_PlotData_v2.py', 'w') as f:
    f.write(content)
