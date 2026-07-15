content = open('backend/plot_generator.py', 'r').read()

old_test2_plot1 = """            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False)"""
new_test2_plot1 = """            p1 = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, "", output_folder, plot_density=False)"""
content = content.replace(old_test2_plot1, new_test2_plot1)

old_test2_plot2 = """            p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True)"""
new_test2_plot2 = """            p1_den = plotNPD(npdA, npdB, name, freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, "", output_folder, plot_density=True)"""
content = content.replace(old_test2_plot2, new_test2_plot2)

old_test2_plot3 = """            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder)"""
new_test2_plot3 = """            p2 = plotS21(sparA, sparB, name, freq_min, freq_max, u_bound_s21, l_bound_s21, "", output_folder)"""
content = content.replace(old_test2_plot3, new_test2_plot3)

open('backend/plot_generator.py', 'w').write(content)
