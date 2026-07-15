with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Restore calibration variables and arguments for Test 1
old_p1 = 'p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, "", output_folder, plot_density=False, apply_cal=False)'
new_p1 = 'p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True)'
content = content.replace(old_p1, new_p1)

old_p1_den = 'p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, "", output_folder, plot_density=True, apply_cal=False)'
new_p1_den = 'p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True, apply_cal=True)'
content = content.replace(old_p1_den, new_p1_den)

old_p2 = 'p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, "", output_folder, apply_cal=False)'
new_p2 = 'p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, apply_cal=True)'
content = content.replace(old_p2, new_p2)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
