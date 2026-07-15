content = open('backend/plot_generator.py', 'r').read()

old_plotS21_sig = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=1):"
new_plotS21_sig = "def plotS21(filesA, filesB, title_suffix, freq_min, freq_max, u_bound_s21, l_bound_s21, cal_folder, output_folder, test_type=1, apply_cal=True):"
content = content.replace(old_plotS21_sig, new_plotS21_sig)

open('backend/plot_generator.py', 'w').write(content)
