with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_plots = """        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=(test_type == 2))
        if p1: generated_plots.append(p1)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=test_type, apply_cal=(test_type == 2))
        if p2: generated_plots.append(p2)"""

new_plots = """        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=True)
        if p1: generated_plots.append(p1)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=test_type, apply_cal=True)
        if p2: generated_plots.append(p2)"""

content = content.replace(old_plots, new_plots)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
