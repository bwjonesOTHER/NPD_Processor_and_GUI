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
import NPD_GT_functions

"""Input Params"""
RunA = #Point to a directory in the gui and fill in here
RunB = #Point to a directory in the gui and fill in here


freq_min = 2.7 #operational freq range
freq_max = 4.1 #operational freq range
reqS11Ns = [700,2100]
reqS11Val = -10
reqS21Val = -14

n_avg = 20 #use even numbers
show_plot = 1

u_bound_s21=2
l_bound_s21=2

u_bound_npd=2
l_bound_npd=2
"""Collect and categorize files"""
folder_path= #Point to a directory in the gui and fill in here

lmoFolderA = folder_path+'\\'+RunA

filesSparA = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR')
filesSparA_25C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_ambient')
filesSparA_64C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_hot')
filesSparA_n38C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempVSWR_cold')


filesNPDA = NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD')
filesNPDA_25C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_ambient')
filesNPDA_64C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_hot')
filesNPDA_n38C=NPD_GT_functions.search_files(lmoFolderA, 'NPDOverTempNPD_cold')

lmoFolderB = folder_path+'\\'+RunB

filesSparB = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR')
filesSparB_25C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_ambient')
filesSparB_64C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_hot')
filesSparB_n38C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempVSWR_cold')

filesNPDB = NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD')
filesNPDB_25C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_ambient')
filesNPDB_64C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_hot')
filesNPDB_n38C=NPD_GT_functions.search_files(lmoFolderB, 'NPDOverTempNPD_cold')



# === Generate plots ===


'NPD'

if len(filesNPDA)>0 and len(filesNPDB)>0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD_density(filesNPDA,lmoFolderA,n_avg,filesNPDB,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA)==0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD_density_single(filesNPDB,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB)==0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD_density_single(filesNPDA,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

if len(filesNPDA_25C)>0 and len(filesNPDB_25C)>0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD_density_25 = NPD_GT_functions.plotNPD_density(filesNPDA_25C,lmoFolderA,n_avg,filesNPDB_25C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_25C)==0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD_density_25 = NPD_GT_functions.plotNPD_density_single(filesNPDB_25C,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_25C)==0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD_density_25 = NPD_GT_functions.plotNPD_density_single(filesNPDA_25C,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

if len(filesNPDA_64C)>0 and len(filesNPDB_64C)>0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_64=NPD_GT_functions.plotNPD_density(filesNPDA_64C,lmoFolderA,n_avg,filesNPDB_64C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_64C)==0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_64=NPD_GT_functions.plotNPD_density_single(filesNPDB_64C,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_64C)==0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_64=NPD_GT_functions.plotNPD_density_single(filesNPDA_64C,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

if len(filesNPDA_n38C)>0 and len(filesNPDB_n38C)>0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_n38=NPD_GT_functions.plotNPD_density(filesNPDA_n38C,lmoFolderA,n_avg,filesNPDB_n38C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_n38C)==0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_n38=NPD_GT_functions.plotNPD_density_single(filesNPDB_n38C,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_n38C)==0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD_density_n38=NPD_GT_functions.plotNPD_density_single(filesNPDA_n38C,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

NPD_GT_functions.npd_density_temp_diff_plot(NPD_density_25,NPD_density_64,NPD_density_n38,folder_path,show_plot)
#
#
#
#
# 'NP'
#
if len(filesNPDA)>0 and len(filesNPDB)>0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD(filesNPDA,lmoFolderA,n_avg,filesNPDB,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA)==0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD_single(filesNPDB,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB)==0:
    temperature='All'
    u_bound_npd=u_bound_npd+1
    l_bound_npd=l_bound_npd+1
    NPD_GT_functions.plotNPD_single(filesNPDA,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
# #

if len(filesNPDA_25C)>0 and len(filesNPDB_25C)>0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD25=NPD_GT_functions.plotNPD(filesNPDA_25C,lmoFolderA,n_avg,filesNPDB_25C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_25C)==0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD25=NPD_GT_functions.plotNPD_single(filesNPDB_25C,lmoFolderB,n_avg,u_bound_npd, l_bound_npd, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_25C)==0:
    temperature='25C'
    u_bound_npd=u_bound_npd-1
    l_bound_npd=l_bound_npd-1
    NPD25=NPD_GT_functions.plotNPD_single(filesNPDA_25C,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
# # #
if len(filesNPDA_64C)>0 and len(filesNPDB_64C)>0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD64=NPD_GT_functions.plotNPD(filesNPDA_64C,lmoFolderA,n_avg,filesNPDB_64C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_64C)==0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD64=NPD_GT_functions.plotNPD_single(filesNPDB_64C,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_64C)==0:
    temperature='64C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPD64=NPD_GT_functions.plotNPD_single(filesNPDA_64C,lmoFolderA,n_avg,u_bound_npd, l_bound_npd, RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)

if len(filesNPDA_n38C)>0 and len(filesNPDB_n38C)>0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPDn38=NPD_GT_functions.plotNPD(filesNPDA_n38C,lmoFolderA,n_avg,filesNPDB_n38C,lmoFolderB,u_bound_npd, l_bound_npd,RunA, RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDA_n38C)==0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPDn38=NPD_GT_functions.plotNPD_single(filesNPDB_n38C,lmoFolderB,n_avg, u_bound_npd, l_bound_npd,RunB,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)
elif len(filesNPDB_n38C)==0:
    temperature='-38C'
    u_bound_npd=u_bound_npd
    l_bound_npd=l_bound_npd
    NPDn38=NPD_GT_functions.plotNPD_single(filesNPDA_n38C,lmoFolderA,n_avg, u_bound_npd, l_bound_npd,RunA,temperature,freq_min,freq_max,reqS11Val,folder_path,show_plot)


NPD_GT_functions.npd_temp_diff_plot(NPD25,NPD64,NPDn38,folder_path,show_plot)
#
#




'S par plots'
# #
if len(filesSparA)>0 and len(filesSparB)>0:
    temperature='All'
    u_bound_s21=u_bound_s21+3
    l_bound_s21 = l_bound_s21 + 3
    NPD_GT_functions.plotS21(filesSparA,filesSparB,u_bound_s21,l_bound_s21,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparA)==0:
    temperature='All'
    u_bound_s21=u_bound_s21+3
    l_bound_s21=l_bound_s21+3
    NPD_GT_functions.plotS21_single(filesSparB,u_bound_s21,l_bound_s21, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparB)==0:
    temperature='All'
    u_bound_s21=u_bound_s21+3
    l_bound_s21=l_bound_s21+3
    NPD_GT_functions.plotS21_single(filesSparA,u_bound_s21,l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot)
# #
if len(filesSparA_25C)>0 and len(filesSparB_25C)>0:
    temperature='25C'
    u_bound_s21=u_bound_s21-3
    l_bound_s21=l_bound_s21-3
    Spar_25=NPD_GT_functions.plotS21(filesSparA_25C,filesSparB_25C,u_bound_s21,l_bound_s21,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparA_25C)==0:
    temperature='25C'
    u_bound_s21=u_bound_s21-3
    l_bound_s21=l_bound_s21-3
    Spar_25=NPD_GT_functions.plotS21_single(filesSparB_25C,u_bound_s21,l_bound_s21,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparB_25C)==0:
    temperature='25C'
    u_bound_s21=u_bound_s21-3
    l_bound_s21=l_bound_s21-3
    Spar_25=NPD_GT_functions.plotS21_single(filesSparA_25C,u_bound_s21,l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot)
# #
if len(filesSparA_64C)>0 and len(filesSparB_64C)>0:
    temperature='64C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_64=NPD_GT_functions.plotS21(filesSparA_64C,filesSparB_64C,u_bound_s21,l_bound_s21,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparA_64C)==0:
    temperature='64C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_64=NPD_GT_functions.plotS21_single(filesSparB_64C,u_bound_s21,l_bound_s21,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparB_64C)==0:
    temperature='64C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_64=NPD_GT_functions.plotS21_single(filesSparA_64C,u_bound_s21,l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot)
# #
if len(filesSparA_n38C)>0 and len(filesSparB_n38C)>0:
    temperature='-38C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_n38=NPD_GT_functions.plotS21(filesSparA_n38C,filesSparB_n38C,u_bound_s21,l_bound_s21,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparA_n38C)==0:
    temperature='-38C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_n38=NPD_GT_functions.plotS21_single(filesSparB_n38C,u_bound_s21,l_bound_s21,RunB,temperature,freq_min,freq_max,folder_path,show_plot)
elif len(filesSparB_n38C)==0:
    temperature='-38C'
    u_bound_s21=u_bound_s21
    l_bound_s21=l_bound_s21
    Spar_n38=NPD_GT_functions.plotS21_single(filesSparA_n38C,u_bound_s21,l_bound_s21,RunA,temperature,freq_min,freq_max,folder_path,show_plot)
#
NPD_GT_functions.s21_temp_diff_plot(Spar_25,Spar_64,Spar_n38, folder_path, show_plot)

"G/T plots"
# if len(filesNPDA)>0 and len(filesNPDB)>0:
#     temperature='All'
#     plotGT(filesNPDA,lmoFolderA,gainA,n_avg,filesNPDB,lmoFolderB,gainB,RunA, RunB,temperature,freq_min,freq_max,folder_path,show_plot)
# elif len(filesNPDA)==0:
#     temperature='All'
#     plotNPD_single(filesNPDB,temperature,specA_s21)
# elif len(filesNPDB)==0:
#     temperature='All'
#     plotNPD_single(filesNPDA,temperature,specA_s21)
#
# if filesNPDA_25C and filesNPDB_25C:
#     temperature='25C'
#     plotGT(filesNPDA_25C,filesNPDB_25C,temperature,specA_s21,gainA,gainB)
#
# if filesNPDA_64C and filesNPDB_64C:
#     temperature='64C'
#     plotGT(filesNPDA_64C,filesNPDB_64C,temperature,specA_s21,gainA,gainB)
#
# if filesNPDA_n38C and filesNPDB_n38C:
#     temperature='-38C'
#     plotGT(filesNPDA_n38C,filesNPDB_n38C,temperature,specA_s21,gainA,gainB)



# if filesNPDA and filesNPDB:
#     temperature='All'
     #gainA=search_files(lmoFolderA,'Gain')
     #gainB=search_files(lmoFolderB,'Gain')
#     plotGT(filesNPDA,filesNPDB,temperature,specA_s21,gainA,gainB)
#
# if filesNPDA_25C and filesNPDB_25C:
#     temperature='25C'
# gainA=search_files(lmoFolderA,'Gain')
# gainB=search_files(lmoFolderB,'Gain')
#     GT25=plotGT(filesNPDA_25C,filesNPDB_25C,temperature,specA_s21,gainA,gainB)
#
# if filesNPDA_64C and filesNPDB_64C:
#     temperature='64C'
# gainA=search_files(lmoFolderA,'Gain')
# gainB=search_files(lmoFolderB,'Gain')
#     GT64=plotGT(filesNPDA_64C,filesNPDB_64C,temperature,specA_s21,gainA,gainB)
#
# if filesNPDA_n38C and filesNPDB_n38C:
#     temperature='-38C'
# gainA=search_files(lmoFolderA,'Gain')
# gainB=search_files(lmoFolderB,'Gain')
#     GTn38=plotGT(filesNPDA_n38C,filesNPDB_n38C,temperature,specA_s21,gainA,gainB)
#
# gt_temp_diff_plot(GT25,GT64,GTn38)
