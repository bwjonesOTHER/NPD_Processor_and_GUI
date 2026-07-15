with open('backend/app.py', 'r') as f:
    content = f.read()

old_app = """    elif test == 2:
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        params['runs'] = [path] if path else []
        params['serial_number'] = read_txt("serialNumber.txt")"""

new_app = """    elif test == 2:
        path = params.get('dataSource')
        if not path:
            path = read_txt("path.txt")
        params['runs'] = [path] if path else []
        params['serial_number'] = read_txt("serialNumber.txt")
        params['pma'] = read_txt("PMA_Area.txt")"""

content = content.replace(old_app, new_app)
with open('backend/app.py', 'w') as f:
    f.write(content)

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_plot = """        if test_type == 2:
            bench_dir = os.path.join(folderB, "BenchNPD")
            temp_dir = os.path.join(folderA, "OverTemp")
            if os.path.exists(bench_dir):
                search_dirB = bench_dir
            if os.path.exists(temp_dir):
                search_dirA = temp_dir"""

new_plot = """        if test_type == 2:
            pma = params.get('pma')
            bench_dir = os.path.join(folderB, "BenchNPD")
            temp_dir = os.path.join(folderA, "OverTemp")
            if pma:
                if os.path.exists(os.path.join(bench_dir, pma)): bench_dir = os.path.join(bench_dir, pma)
                if os.path.exists(os.path.join(temp_dir, pma)): temp_dir = os.path.join(temp_dir, pma)
            if os.path.exists(bench_dir):
                search_dirB = bench_dir
            if os.path.exists(temp_dir):
                search_dirA = temp_dir"""

content = content.replace(old_plot, new_plot)

old_plot_call1 = """        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False)
        if p1: generated_plots.append(p1)
        p1_den = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True)
        if p1_den: generated_plots.append(p1_den)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder)"""

new_plot_call1 = """        p1 = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=False, apply_cal=(test_type!=2))
        if p1: generated_plots.append(p1)
        p1_den = plotNPD(npdA, npdB, "Benchtop", freq_min, freq_max, u_bound_npd, l_bound_npd, reqS11Val, n_avg, cal_folder, output_folder, plot_density=True, apply_cal=(test_type!=2))
        if p1_den: generated_plots.append(p1_den)
        
        p2 = plotS21(sparA, sparB, "Benchtop", freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=test_type, apply_cal=(test_type!=2))"""

content = content.replace(old_plot_call1, new_plot_call1)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

