import matplotlib
matplotlib.use('Agg')
import os
import glob
from pathlib import Path
import NPD_GT_functions

def generate_plots(params):
    runs = params.get('runs', [])
    folder_path = params.get('folder_path')
    
    if not runs or not folder_path:
        raise ValueError("At least one run and folder_path are required.")

    freq_min = float(params.get('freq_min', 2.7))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Val = float(params.get('reqS11Val', -10))
    reqS21Val = float(params.get('reqS21Val', -14))
    
    n_avg = int(params.get('n_avg', 20))
    show_plot = 0
    
    u_bound_s21 = float(params.get('u_bound_s21', 2))
    l_bound_s21 = float(params.get('l_bound_s21', 2))
    u_bound_npd = float(params.get('u_bound_npd', 2))
    l_bound_npd = float(params.get('l_bound_npd', 2))

    def _collect_files(runs_list, suffix):
        runs_data = []
        for run in runs_list:
            lmo = os.path.join(folder_path, run)
            files = NPD_GT_functions.search_files(lmo, suffix)
            gains = NPD_GT_functions.search_files(lmo, 'Gain')
            if files:
                runs_data.append({'name': run, 'folder': lmo, 'files': files, 'gains': gains})
        return runs_data

    # === Collect Data ===
    
    # NPD Density
    npdd_all = _collect_files(runs, 'NPDOverTempNPD')
    npdd_25C = _collect_files(runs, 'NPDOverTempNPD_ambient')
    npdd_64C = _collect_files(runs, 'NPDOverTempNPD_hot')
    npdd_n38C = _collect_files(runs, 'NPDOverTempNPD_cold')

    # SPars
    spar_all = _collect_files(runs, 'NPDOverTempVSWR')
    spar_25C = _collect_files(runs, 'NPDOverTempVSWR_ambient')
    spar_64C = _collect_files(runs, 'NPDOverTempVSWR_hot')
    spar_n38C = _collect_files(runs, 'NPDOverTempVSWR_cold')
    

    # === Generate plots ===

    # NPD Density
    if npdd_all:
        NPD_GT_functions.plotNPD_density_multi(npdd_all, n_avg, u_bound_npd+1, l_bound_npd+1, 'All', freq_min, freq_max, reqS11Val, folder_path, show_plot)

    nd25 = nd64 = ndn38 = None
    if npdd_25C: nd25 = NPD_GT_functions.plotNPD_density_multi(npdd_25C, n_avg, u_bound_npd, l_bound_npd, '25C', freq_min, freq_max, reqS11Val, folder_path, show_plot)
    if npdd_64C: nd64 = NPD_GT_functions.plotNPD_density_multi(npdd_64C, n_avg, u_bound_npd, l_bound_npd, '64C', freq_min, freq_max, reqS11Val, folder_path, show_plot)
    if npdd_n38C: ndn38 = NPD_GT_functions.plotNPD_density_multi(npdd_n38C, n_avg, u_bound_npd, l_bound_npd, '-38C', freq_min, freq_max, reqS11Val, folder_path, show_plot)

    if nd25 and nd25[0] is not None and nd64 and nd64[0] is not None and ndn38 and ndn38[0] is not None:
        try: NPD_GT_functions.npd_density_temp_diff_plot(nd25, nd64, ndn38, len(runs), freq_min, freq_max, folder_path, show_plot)
        except Exception as e: print("Error in temp diff plot NPD density:", e)

    # NP (Noise Power)
    if npdd_all:
        NPD_GT_functions.plotNPD_multi(npdd_all, n_avg, u_bound_npd+1, l_bound_npd+1, 'All', freq_min, freq_max, reqS11Val, folder_path, show_plot)

    np25 = np64 = npn38 = None
    if npdd_25C: np25 = NPD_GT_functions.plotNPD_multi(npdd_25C, n_avg, u_bound_npd, l_bound_npd, '25C', freq_min, freq_max, reqS11Val, folder_path, show_plot)
    if npdd_64C: np64 = NPD_GT_functions.plotNPD_multi(npdd_64C, n_avg, u_bound_npd, l_bound_npd, '64C', freq_min, freq_max, reqS11Val, folder_path, show_plot)
    if npdd_n38C: npn38 = NPD_GT_functions.plotNPD_multi(npdd_n38C, n_avg, u_bound_npd, l_bound_npd, '-38C', freq_min, freq_max, reqS11Val, folder_path, show_plot)
    
    if np25 and np25[0] is not None and np64 and np64[0] is not None and npn38 and npn38[0] is not None:
        try: NPD_GT_functions.npd_temp_diff_plot(np25, np64, npn38, len(runs), freq_min, freq_max, folder_path, show_plot)
        except Exception as e: print("Error in temp diff plot NP:", e)
        

    # S21 Plots
    if spar_all:
        NPD_GT_functions.plotS21_multi(spar_all, u_bound_s21+3, l_bound_s21+3, 'All', freq_min, freq_max, folder_path, show_plot)

    sp25 = sp64 = spn38 = None
    if spar_25C: sp25 = NPD_GT_functions.plotS21_multi(spar_25C, u_bound_s21, l_bound_s21, '25C', freq_min, freq_max, folder_path, show_plot)
    if spar_64C: sp64 = NPD_GT_functions.plotS21_multi(spar_64C, u_bound_s21, l_bound_s21, '64C', freq_min, freq_max, folder_path, show_plot)
    if spar_n38C: spn38 = NPD_GT_functions.plotS21_multi(spar_n38C, u_bound_s21, l_bound_s21, '-38C', freq_min, freq_max, folder_path, show_plot)

    if sp25 and sp25[0] is not None and sp64 and sp64[0] is not None and spn38 and spn38[0] is not None:
        try: NPD_GT_functions.s21_temp_diff_plot(sp25, sp64, spn38, len(runs), freq_min, freq_max, folder_path, show_plot)
        except Exception as e: print("Error in temp diff plot S21:", e)

    # S11, S22, Group Delay
    if spar_all:
        NPD_GT_functions.plotS11_multi(spar_all, 'All', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotS22_multi(spar_all, 'All', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotGroupDelay_multi(spar_all, 'All', freq_min, freq_max, folder_path, show_plot)
        
    if spar_25C:
        NPD_GT_functions.plotS11_multi(spar_25C, '25C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotS22_multi(spar_25C, '25C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotGroupDelay_multi(spar_25C, '25C', freq_min, freq_max, folder_path, show_plot)

    if spar_64C:
        NPD_GT_functions.plotS11_multi(spar_64C, '64C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotS22_multi(spar_64C, '64C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotGroupDelay_multi(spar_64C, '64C', freq_min, freq_max, folder_path, show_plot)

    if spar_n38C:
        NPD_GT_functions.plotS11_multi(spar_n38C, '-38C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotS22_multi(spar_n38C, '-38C', freq_min, freq_max, folder_path, show_plot)
        NPD_GT_functions.plotGroupDelay_multi(spar_n38C, '-38C', freq_min, freq_max, folder_path, show_plot)

    png_files = glob.glob(os.path.join(folder_path, '*.png'))
    return png_files
