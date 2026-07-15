import re

content = open('backend/plot_generator.py', 'r').read()

old_s21_interp = """        if start_idx != end_idx:
            s21_window = s21_corr[start_idx:end_idx]
            if ref_freq_ghz is None:
                ref_freq_ghz = freq_ghz
                ref_freq_win = freq_ghz[start_idx:end_idx]
        else:
            s21_window = s21_corr
            if ref_freq_ghz is None:
                ref_freq_ghz = freq_ghz
                ref_freq_win = freq_ghz
            
        avg_collection.append(s21_window)
        all_s21_full.append(s21_corr)"""

new_s21_interp = """        if ref_freq_ghz is None:
            ref_freq_ghz = freq_ghz
            
            start_idx = np.searchsorted(ref_freq_ghz, freq_min)
            end_idx = np.searchsorted(ref_freq_ghz, freq_max)
            if start_idx != end_idx:
                ref_freq_win = ref_freq_ghz[start_idx:end_idx]
            else:
                ref_freq_win = ref_freq_ghz
        else:
            if len(freq_ghz) != len(ref_freq_ghz) or not np.allclose(freq_ghz, ref_freq_ghz):
                s21_corr = np.interp(ref_freq_ghz, freq_ghz, s21_corr)
                
        start_idx = np.searchsorted(ref_freq_ghz, freq_min)
        end_idx = np.searchsorted(ref_freq_ghz, freq_max)
        if start_idx != end_idx:
            s21_window = s21_corr[start_idx:end_idx]
        else:
            s21_window = s21_corr

        avg_collection.append(s21_window)
        all_s21_full.append(s21_corr)"""

content = content.replace(old_s21_interp, new_s21_interp)
open('backend/plot_generator.py', 'w').write(content)
