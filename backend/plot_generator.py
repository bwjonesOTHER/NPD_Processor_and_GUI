import os
import re
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pandas as pd
import itertools
from pathlib import Path
import math
import glob
import NPD_GT_functions

def resolve_run_dir(run_dir):
    if not run_dir or not os.path.isdir(run_dir):
        return run_dir
    items = os.listdir(run_dir)
    dirs = [d for d in items if os.path.isdir(os.path.join(run_dir, d))]
    if len(dirs) == 1:
        return os.path.join(run_dir, dirs[0])
    return run_dir

def generate_plots(params):
    runs = params.get('runs', [])
    lmoFolderA = resolve_run_dir(runs[0]) if len(runs) > 0 else ""
    lmoFolderB = resolve_run_dir(runs[1]) if len(runs) > 1 else ""

    RunA = params.get('RunA', os.path.basename(lmoFolderA.rstrip('/\\')) if lmoFolderA else "")
    RunB = params.get('RunB', os.path.basename(lmoFolderB.rstrip('/\\')) if lmoFolderB else "")
    
    freq_min = float(params.get('freq_min', 2.7))
    freq_max = float(params.get('freq_max', 4.1))
    reqS11Ns = [700,2100]
    reqS11Val = -10
    reqS21Val = -14
    
    n_avg = int(params.get('n_avg', 20))
    show_plot = 0
    
    u_bound_s21 = float(params.get('u_bound_s21', 2))
    l_bound_s21 = float(params.get('l_bound_s21', 2))
    u_bound_npd = float(params.get('u_bound_npd', 2))
    l_bound_npd = float(params.get('l_bound_npd', 2))
    
    folder_path = params.get('folder_path', '')
    if not folder_path and lmoFolderA:
        folder_path = os.path.dirname(lmoFolderA)

    old_pngs = glob.glob(os.path.join(folder_path, '*.png'))
    for png in old_pngs:
        try:
            os.remove(png)
        except Exception:
            pass
            
    filesSparA = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR') if lmoFolderA else []
    filesSparA_25C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_ambient') if lmoFolderA else []
    filesSparA_64C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_hot') if lmoFolderA else []
    filesSparA_n38C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_cold') if lmoFolderA else []
    
    filesNPDA = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD') if lmoFolderA else []
    filesNPDA_25C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_ambient') if lmoFolderA else []
    filesNPDA_64C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_hot') if lmoFolderA else []
    filesNPDA_n38C = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_cold') if lmoFolderA else []
    
    filesSparB = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR') if lmoFolderB else []
    filesSparB_25C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_ambient') if lmoFolderB else []
    filesSparB_64C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_hot') if lmoFolderB else []
    filesSparB_n38C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_cold') if lmoFolderB else []
    
    filesNPDB = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD') if lmoFolderB else []
    filesNPDB_25C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_ambient') if lmoFolderB else []
    filesNPDB_64C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_hot') if lmoFolderB else []
    filesNPDB_n38C = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_cold') if lmoFolderB else []

    NPD_density_25 = ([], [])
    NPD_density_64 = ([], [])
    NPD_density_n38 = ([], [])
    NPD25 = ([], [])
    NPD64 = ([], [])
    NPDn38 = ([], [])
    Spar_25 = ([], [])
    Spar_64 = ([], [])
    Spar_n38 = ([], [])

    if len(filesNPDA)>0 and len(filesNPDB)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD_density(filesNPDA,lmoFolderA,n_avg,filesNPDB,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA)==0 and len(filesNPDB)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD_density_single(filesNPDB,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB)==0 and len(filesNPDA)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD_density_single(filesNPDA,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_25C)>0 and len(filesNPDB_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD_density_25 = NPD_GT_functions.plotNPD_density(filesNPDA_25C,lmoFolderA,n_avg,filesNPDB_25C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_25C)==0 and len(filesNPDB_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD_density_25 = NPD_GT_functions.plotNPD_density_single(filesNPDB_25C,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_25C)==0 and len(filesNPDA_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD_density_25 = NPD_GT_functions.plotNPD_density_single(filesNPDA_25C,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_64C)>0 and len(filesNPDB_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_64=NPD_GT_functions.plotNPD_density(filesNPDA_64C,lmoFolderA,n_avg,filesNPDB_64C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_64C)==0 and len(filesNPDB_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_64=NPD_GT_functions.plotNPD_density_single(filesNPDB_64C,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_64C)==0 and len(filesNPDA_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_64=NPD_GT_functions.plotNPD_density_single(filesNPDA_64C,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_n38C)>0 and len(filesNPDB_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_n38=NPD_GT_functions.plotNPD_density(filesNPDA_n38C,lmoFolderA,n_avg,filesNPDB_n38C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_n38C)==0 and len(filesNPDB_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_n38=NPD_GT_functions.plotNPD_density_single(filesNPDB_n38C,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_n38C)==0 and len(filesNPDA_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD_density_n38=NPD_GT_functions.plotNPD_density_single(filesNPDA_n38C,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if NPD_density_25 and len(NPD_density_25)>0 and any([len(NPD_density_25[0]), len(NPD_density_64[0]), len(NPD_density_n38[0])]):
        NPD_GT_functions.npd_density_temp_diff_plot(NPD_density_25,NPD_density_64,NPD_density_n38,folder_path,show_plot)

    if len(filesNPDA)>0 and len(filesNPDB)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD(filesNPDA,lmoFolderA,n_avg,filesNPDB,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA)==0 and len(filesNPDB)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD_single(filesNPDB,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB)==0 and len(filesNPDA)>0:
        temperature='All'
        u_bound_npd_temp=u_bound_npd+1
        l_bound_npd_temp=l_bound_npd+1
        NPD_GT_functions.plotNPD_single(filesNPDA,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_25C)>0 and len(filesNPDB_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD25=NPD_GT_functions.plotNPD(filesNPDA_25C,lmoFolderA,n_avg,filesNPDB_25C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_25C)==0 and len(filesNPDB_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD25=NPD_GT_functions.plotNPD_single(filesNPDB_25C,lmoFolderB,n_avg,u_bound_npd_temp, l_bound_npd_temp, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_25C)==0 and len(filesNPDA_25C)>0:
        temperature='25C'
        u_bound_npd_temp=u_bound_npd-1
        l_bound_npd_temp=l_bound_npd-1
        NPD25=NPD_GT_functions.plotNPD_single(filesNPDA_25C,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_64C)>0 and len(filesNPDB_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD64=NPD_GT_functions.plotNPD(filesNPDA_64C,lmoFolderA,n_avg,filesNPDB_64C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_64C)==0 and len(filesNPDB_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD64=NPD_GT_functions.plotNPD_single(filesNPDB_64C,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_64C)==0 and len(filesNPDA_64C)>0:
        temperature='64C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPD64=NPD_GT_functions.plotNPD_single(filesNPDA_64C,lmoFolderA,n_avg,u_bound_npd_temp, l_bound_npd_temp, RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if len(filesNPDA_n38C)>0 and len(filesNPDB_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPDn38=NPD_GT_functions.plotNPD(filesNPDA_n38C,lmoFolderA,n_avg,filesNPDB_n38C,lmoFolderB,u_bound_npd_temp, l_bound_npd_temp,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDA_n38C)==0 and len(filesNPDB_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPDn38=NPD_GT_functions.plotNPD_single(filesNPDB_n38C,lmoFolderB,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
    elif len(filesNPDB_n38C)==0 and len(filesNPDA_n38C)>0:
        temperature='-38C'
        u_bound_npd_temp=u_bound_npd
        l_bound_npd_temp=l_bound_npd
        NPDn38=NPD_GT_functions.plotNPD_single(filesNPDA_n38C,lmoFolderA,n_avg, u_bound_npd_temp, l_bound_npd_temp,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

    if NPD25 and len(NPD25)>0 and any([len(NPD25[0]), len(NPD64[0]), len(NPDn38[0])]):
        NPD_GT_functions.npd_temp_diff_plot(NPD25,NPD64,NPDn38,folder_path,show_plot)

    if len(filesSparA)>0 and len(filesSparB)>0:
        temperature='All'
        u_bound_s21_temp=u_bound_s21+3
        l_bound_s21_temp=l_bound_s21+3
        NPD_GT_functions.plotS21(filesSparA,filesSparB,u_bound_s21_temp,l_bound_s21_temp,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparA)==0 and len(filesSparB)>0:
        temperature='All'
        u_bound_s21_temp=u_bound_s21+3
        l_bound_s21_temp=l_bound_s21+3
        NPD_GT_functions.plotS21_single(filesSparB,u_bound_s21_temp,l_bound_s21_temp, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparB)==0 and len(filesSparA)>0:
        temperature='All'
        u_bound_s21_temp=u_bound_s21+3
        l_bound_s21_temp=l_bound_s21+3
        NPD_GT_functions.plotS21_single(filesSparA,u_bound_s21_temp,l_bound_s21_temp,RunA,temperature,freq_min,freq_max,folder_path,show_plot)

    if len(filesSparA_25C)>0 and len(filesSparB_25C)>0:
        temperature='25C'
        u_bound_s21_temp=u_bound_s21-3
        l_bound_s21_temp=l_bound_s21-3
        Spar_25=NPD_GT_functions.plotS21(filesSparA_25C,filesSparB_25C,u_bound_s21_temp,l_bound_s21_temp,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparA_25C)==0 and len(filesSparB_25C)>0:
        temperature='25C'
        u_bound_s21_temp=u_bound_s21-3
        l_bound_s21_temp=l_bound_s21-3
        Spar_25=NPD_GT_functions.plotS21_single(filesSparB_25C,u_bound_s21_temp,l_bound_s21_temp,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparB_25C)==0 and len(filesSparA_25C)>0:
        temperature='25C'
        u_bound_s21_temp=u_bound_s21-3
        l_bound_s21_temp=l_bound_s21-3
        Spar_25=NPD_GT_functions.plotS21_single(filesSparA_25C,u_bound_s21_temp,l_bound_s21_temp,RunA,temperature,freq_min,freq_max,folder_path,show_plot)

    if len(filesSparA_64C)>0 and len(filesSparB_64C)>0:
        temperature='64C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_64=NPD_GT_functions.plotS21(filesSparA_64C,filesSparB_64C,u_bound_s21_temp,l_bound_s21_temp,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparA_64C)==0 and len(filesSparB_64C)>0:
        temperature='64C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_64=NPD_GT_functions.plotS21_single(filesSparB_64C,u_bound_s21_temp,l_bound_s21_temp,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparB_64C)==0 and len(filesSparA_64C)>0:
        temperature='64C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_64=NPD_GT_functions.plotS21_single(filesSparA_64C,u_bound_s21_temp,l_bound_s21_temp,RunA,temperature,freq_min,freq_max,folder_path,show_plot)

    if len(filesSparA_n38C)>0 and len(filesSparB_n38C)>0:
        temperature='-38C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_n38=NPD_GT_functions.plotS21(filesSparA_n38C,filesSparB_n38C,u_bound_s21_temp,l_bound_s21_temp,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparA_n38C)==0 and len(filesSparB_n38C)>0:
        temperature='-38C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_n38=NPD_GT_functions.plotS21_single(filesSparB_n38C,u_bound_s21_temp,l_bound_s21_temp,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
    elif len(filesSparB_n38C)==0 and len(filesSparA_n38C)>0:
        temperature='-38C'
        u_bound_s21_temp=u_bound_s21
        l_bound_s21_temp=l_bound_s21
        Spar_n38=NPD_GT_functions.plotS21_single(filesSparA_n38C,u_bound_s21_temp,l_bound_s21_temp,RunA,temperature,freq_min,freq_max,folder_path,show_plot)

    if Spar_25 and len(Spar_25)>0 and any([len(Spar_25[0]), len(Spar_64[0]), len(Spar_n38[0])]):
        NPD_GT_functions.s21_temp_diff_plot(Spar_25,Spar_64,Spar_n38, folder_path, show_plot)

    plt.close('all')
    return glob.glob(os.path.join(folder_path, '*.png'))
