import re

content = open('backend/plot_generator.py', 'r').read()

old_loop = """    for file in all_files:
        serial = extract_serial(file)
        freq, noise = load_np_data(file)
        if len(freq) == 0:
            continue
        plt.plot(freq, noise, label=f'{serial[-21:-4:1]}')
        all_freqs.append(freq)
        all_noise.append(noise)
        
        # Window points for Pass/Fail
        start_idx = np.searchsorted(freq, freq_min)
        end_idx = np.searchsorted(freq, freq_max)
        if start_idx == end_idx:
            # If data is out of bounds, use all data just in case
            all_noise_win.append(noise)
        else:
            all_noise_win.append(noise[start_idx:end_idx])
        all_labels.append(serial[-21:-4:1])"""

new_loop = """    ref_freq_full = None
    for file in all_files:
        serial = extract_serial(file)
        freq, noise = load_np_data(file)
        if len(freq) == 0:
            continue
            
        if ref_freq_full is None:
            ref_freq_full = freq
        else:
            if len(freq) != len(ref_freq_full) or not np.allclose(freq, ref_freq_full):
                noise = np.interp(ref_freq_full, freq, noise)
                freq = ref_freq_full

        plt.plot(freq, noise, label=f'{serial[-21:-4:1]}')
        all_freqs.append(freq)
        all_noise.append(noise)
        
        # Window points for Pass/Fail
        start_idx = np.searchsorted(freq, freq_min)
        end_idx = np.searchsorted(freq, freq_max)
        if start_idx == end_idx:
            # If data is out of bounds, use all data just in case
            all_noise_win.append(noise)
        else:
            all_noise_win.append(noise[start_idx:end_idx])
        all_labels.append(serial[-21:-4:1])"""

content = content.replace(old_loop, new_loop)

# There is a line `ref_freq_full = all_freqs[0]` after the loop, we can just leave it or it will be overwritten.
content = content.replace("    ref_freq_full = all_freqs[0]\n", "")

open('backend/plot_generator.py', 'w').write(content)
