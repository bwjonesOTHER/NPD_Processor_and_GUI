import re

content = open('backend/plot_generator.py', 'r').read()

# 1. plotNPD
# Replace return line to use full averages
npd_replacement = """    
    full_avg = None
    if len(all_noise) > 0:
        min_len = min(len(x) for x in all_noise)
        full_avg = np.mean([x[:min_len] for x in all_noise], axis=0)
        ref_freq_full = ref_freq_full[:min_len]
        
    return {"path": save_path, "status": status.lower(), "freq": ref_freq_full if full_avg is not None else None, "avg": full_avg}
"""
content = content.replace('    return {"path": save_path, "status": status.lower(), "freq": ref_freq_win if len(all_noise_win)>0 else None, "avg": avg if len(all_noise_win)>0 else None}', npd_replacement)


# 2. plotS21
# Need to track all_s21_full
content = content.replace('    avg_collection = []\n    file_coll = []', '    avg_collection = []\n    all_s21_full = []\n    file_coll = []')

# Inside the loop, save s21_corr
content = content.replace('        avg_collection.append(s21_window)\n        file_coll.append(serial[-21:-4:1])', '        avg_collection.append(s21_window)\n        all_s21_full.append(s21_corr)\n        file_coll.append(serial[-21:-4:1])')

# Replace return line
s21_replacement = """    
    full_avg = None
    if len(all_s21_full) > 0:
        min_len = min(len(x) for x in all_s21_full)
        full_avg = np.mean([x[:min_len] for x in all_s21_full], axis=0)
        ref_freq_ghz = ref_freq_ghz[:min_len]
        
    return {"path": save_path, "status": status.lower(), "freq": ref_freq_ghz if full_avg is not None else None, "avg": full_avg}
"""
content = content.replace('    return {"path": save_path, "status": status.lower(), "freq": ref_freq_win if len(s21_avg)>0 else None, "avg": avg if len(s21_avg)>0 else None}', s21_replacement)


open('backend/plot_generator.py', 'w').write(content)
