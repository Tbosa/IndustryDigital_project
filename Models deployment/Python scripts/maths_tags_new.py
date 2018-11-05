# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 16:43:58 2018

@author: BarbosaA
"""
import os
import pickle

import math
import numpy as np

data_dir = 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Curing model'
os.chdir(data_dir)
os.getcwd()

with open('./Global py objects/best_rf_models.pkl', 'rb') as dict_:
    rf_models_dict_ = pickle.load(dict_)

select_feat_idx = list(rf_models_dict_['Allgt_avg']['VarImp_df'].index[:20])
Dapp = apptest_ds_dict['Allgt_avg']['train_set'].drop(columns = ['Allgt_avg'])
X_app = Dapp[select_feat_idx]

###############################################################################
###############################################################################
###############################################################################

def RHEO_Stags(TS2_list, T90_list, ML_list, MH_list):
    
    TS2_n = len(TS2_list)
    T90_n = len(T90_list)
    ML_n = len(ML_list)
    MH_n = len(MH_list)
    
    TS2_mean = (sum(TS2_list))/TS2_n
    TS2_dev = [x - TS2_mean for x in TS2_list]
    TS2_std = math.sqrt((sum([i**2 for i in TS2_dev]))/(TS1_n - 1))
    
    T90_min = min(T90_list)
    
    ML_min = min(ML_list)
    ML_mean_temp = (sum(ML_list))/ML_n
    ML_dev = [x - ML_mean_temp for x in ML_list]
    ML_std = math.sqrt((sum([i**2 for i in ML_dev]))/(ML_n - 1))
    
    MH_min = min(MH_list)
    MH_max = max(MH_list)
    MH_mean_temp = (sum(MH_list))/MH_n
    MH_dev = [y - MH_mean_temp for y in MH_list]
    MH_std = math.sqrt((sum([j**2 for j in MH_dev]))/(MH_n - 1))        
    
    Stags_output = {"TS2_mean" : TS2_mean, "TS2_std" : TS2_std, "T90_min" : T90_min, "ML_min" : ML_min, "ML_mean_temp" : ML_mean_temp,
                    "ML_std": ML_std, "MH_min" : MH_min, "MH_max" : MH_max, "MH_mean": MH_mean_temp, "MH_std": MH_std}
    
    return Stags_output


###############################################################################
###############################################################################
###############################################################################

def Allgt_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    tags_name = ['Rotocure_RotoCylinderTemp', 'Rotocure_CylinderTempUpper', 'Extrud_ScrewSpeed', 'Extrud_MixtureTemperature', 
                 'Extrud_PressureAfterFilter', 'Caland_OpeningLevelRight', 'CylinderSpeedUpper', 'CylinderSpeedLower','Extrud_PressureBeforeFilter']
    
    if not Stags_output:
        Stags_output[f"{tags_name[1]}_min"], Stags_output[f"{tags_name[2]}_min"] = (math.inf,)*2
        Stags_output[f"{tags_name[3]}_max"], Stags_output[f"{tags_name[4]}_max"], Stags_output[f"{tags_name[6]}_max"] = (-math.inf,)*3
        Stags_output[f"{tags_name[0]}_mean"], Stags_output[f"{tags_name[5]}_mean"], Stags_output[f"{tags_name[8]}_mean"] = (0,)*3
        Stags_output[f"{tags_name[7]}_mean_temp"], Stags_output[f"{tags_name[6]}_mean_temp"], Stags_output[f"{tags_name[2]}_mean"] = (0,)*3
        Stags_output[f"{tags_name[7]}_stdev"], Stags_output[f"{tags_name[6]}_stdev"], Stags_output[f"{tags_name[2]}_stdev"] = (0,)*3
           
    mesco_tags = {k : MESCO_tags[k] for k in tags_name}
        
    R_CTU_min = min(Stags_output[f"{tags_name[1]}_min"], mesco_tags[tags_name[1]])
    E_MT_max = max(Stags_output[f"{tags_name[3]}_max"], mesco_tags[tags_name[3]])
    E_PAF_max = max(Stags_output[f"{tags_name[4]}_max"], mesco_tags[tags_name[4]])
    R_RCT_mean = (n/(n+1))*Stags_output[f"{tags_name[0]}_mean"] + (1/(n+1))*mesco_tags[tags_name[0]]
    C_OLR_mean = (n/(n+1))*Stags_output[f"{tags_name[5]}_mean"] + (1/(n+1))*mesco_tags[tags_name[5]]
    E_PBF_mean = (n/(n+1))*Stags_output[f"{tags_name[8]}_mean"] + (1/(n+1))*mesco_tags[tags_name[8]]
    
    CSL_var = (n/(n+1))*(Stags_output[f"{tags_name[7]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[7]] - Stags_output[f"{tags_name[7]}_mean_temp"])**2)
    CSL_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[7]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[7]]
    
    CSU_max = max(Stags_output[f"{tags_name[6]}_max"], mesco_tags[tags_name[6]])
    CSU_var = (n/(n+1))*(Stags_output[f"{tags_name[6]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[6]] - Stags_output[f"{tags_name[6]}_mean_temp"])**2)
    CSU_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[6]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[6]]
    
    E_SS_min = min(Stags_output[f"{tags_name[2]}_min"], mesco_tags[tags_name[2]])
    E_SS_var = (n/(n+1))*(Stags_output[f"{tags_name[2]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[2]] - Stags_output[f"{tags_name[2]}_mean"])**2)
    E_SS_mean = (n/(n+1))*Stags_output[f"{tags_name[2]}_mean"] + (1/(n+1))*mesco_tags[tags_name[2]]
    
    Stags_output_new = {f"{tags_name[0]}_mean" : R_RCT_mean, f"{tags_name[1]}_min" : R_CTU_min, f"{tags_name[2]}_mean" : E_SS_mean, f"{tags_name[2]}_min" : E_SS_min,
                        f"{tags_name[3]}_max" : E_MT_max, f"{tags_name[4]}_max" : E_PAF_max, f"{tags_name[5]}_mean" : C_OLR_mean, f"{tags_name[6]}_stdev" : math.sqrt(CSU_var),
                        f"{tags_name[6]}_mean_temp" : CSU_mean_temp, f"{tags_name[2]}_stdev" : math.sqrt(E_SS_var), f"{tags_name[6]}_max" : CSU_max, f"{tags_name[8]}_mean" : E_PBF_mean,
                        f"{tags_name[7]}_stdev" : math.sqrt(CSL_var), f"{tags_name[7]}_mean_temp" : CSL_mean_temp}
                       
    
    return Stags_output_new


###############################################################################
###############################################################################
###############################################################################


def Cont100_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    tags_name = ['Extrud_MixtureTemperature', 'Extrud_ScrewSpeed', 'Rotocure_RotoCylinderTemp', 
                 'Extrud_PressureAfterFilter', 'Extrud_PressureBeforeFilter', 'Rotocure_CylinderTempUpper']
    
    if not Stags_output:
        Stags_output[f"{tags_name[5]}_min"], Stags_output[f"{tags_name[1]}_min"] = (math.inf,)*2
        Stags_output[f"{tags_name[0]}_max"], Stags_output[f"{tags_name[3]}_max"] = (-math.inf,)*2
        Stags_output[f"{tags_name[1]}_mean"], Stags_output[f"{tags_name[2]}_mean"], Stags_output[f"{tags_name[4]}_mean"] = (0,)*3

    mesco_tags = {k : MESCO_tags[k] for k in tags_name}
    
    R_CTU_min = min(Stags_output[f"{tags_name[5]}_min"], mesco_tags[tags_name[5]])
    E_SS_min = min(Stags_output[f"{tags_name[1]}_min"], mesco_tags[tags_name[1]])
    E_MT_max = max(Stags_output[f"{tags_name[0]}_max"], mesco_tags[tags_name[0]])
    E_PAF_max = max(Stags_output[f"{tags_name[3]}_max"], mesco_tags[tags_name[3]])
    E_SS_mean = (n/(n+1))*Stags_output[f"{tags_name[1]}_mean"] + (1/(n+1))*mesco_tags[tags_name[1]]
    R_RCT_mean = (n/(n+1))*Stags_output[f"{tags_name[2]}_mean"] + (1/(n+1))*mesco_tags[tags_name[2]]
    E_PBF_mean = (n/(n+1))*Stags_output[f"{tags_name[4]}_mean"] + (1/(n+1))*mesco_tags[tags_name[4]]
    
    Stags_output_new = {f"{tags_name[0]}_max" : E_MT_max, f"{tags_name[1]}_mean" : E_SS_mean, f"{tags_name[2]}_mean" : R_RCT_mean, f"{tags_name[3]}_max" : E_PAF_max,
                        f"{tags_name[1]}_min" : E_SS_min, f"{tags_name[4]}_mean" : E_PBF_mean, f"{tags_name[5]}_min" : R_CTU_min}
    
    return Stags_output_new


###############################################################################
###############################################################################
###############################################################################



def Contrupt_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    tags_name = ['Caland_OpeningLevelRight', 'CylinderSpeedUpper', 'Caland_OpeningLevelLeft', 'CylinderSpeedLower', 'Extrud_HeadTemperature',
                 'Rotocure_VulcPressure', 'Extrud_ScrewSpeed', 'Rotocure_CylPressureRight1', 'Rotocure_CylPressureLeft1', 'Rotocure_LineSpeed',
                 'Rotocure_RotoCylinderTemp']
    
    if not Stags_output:
        Stags_output[f"{tags_name[1]}_min"], Stags_output[f"{tags_name[4]}_min"] = (math.inf,)*2
        Stags_output[f"{tags_name[1]}_max"], Stags_output[f"{tags_name[2]}_max"], Stags_output[f"{tags_name[8]}_max"] = (-math.inf,)*3
        Stags_output[f"{tags_name[0]}_mean"], Stags_output[f"{tags_name[4]}_mean"], Stags_output[f"{tags_name[8]}_mean"], Stags_output[f"{tags_name[10]}_mean"], Stags_output[f"{tags_name[6]}_mean"] = (0,)*5
        Stags_output[f"{tags_name[3]}_mean_temp"], Stags_output[f"{tags_name[2]}_mean_temp"], Stags_output[f"{tags_name[5]}_mean_temp"], Stags_output[f"{tags_name[7]}_mean_temp"], Stags_output[f"{tags_name[9]}_mean_temp"] = (0,)*5
        Stags_output["{tags_name[3]}_stdev"], Stags_output[f"{tags_name[2]}_stdev"], Stags_output[f"{tags_name[5]}_stdev"], Stags_output[f"{tags_name[7]}_stdev"], Stags_output[f"{tags_name[9]}_stdev"] = (0,)*5
        
    
    mesco_tags = {k : MESCO_tags[k] for k in tags_name}
    
    CSU_min = min(Stags_output[f"{tags_name[1]}_min"], mesco_tags[tags_name[1]])
    E_HT_min = min(Stags_output[f"{tags_name[4]}_min"], mesco_tags[tags_name[4]])
    CSU_max = max(Stags_output[f"{tags_name[1]}_max"], mesco_tags[tags_name[1]])
    C_OLL_max = max(Stags_output[f"{tags_name[2]}_max"], mesco_tags[tags_name[2]])
    R_CPL1_max = max(Stags_output[f"{tags_name[8]}_max"], mesco_tags[tags_name[8]])
    C_OLR_mean = (n/(n+1))*Stags_output[f"{tags_name[0]}_mean"] + (1/(n+1))*mesco_tags[tags_name[0]]
    E_HT_mean = (n/(n+1))*Stags_output[f"{tags_name[4]}_mean"] + (1/(n+1))*mesco_tags[tags_name[4]]
    R_CPL1_mean = (n/(n+1))*Stags_output[f"{tags_name[8]}_mean"] + (1/(n+1))*mesco_tags[tags_name[8]]
    R_RCT_mean = (n/(n+1))*Stags_output[f"{tags_name[10]}_mean"] + (1/(n+1))*mesco_tags[tags_name[10]]
    
    E_SS_var = (n/(n+1))*(Stags_output[f"{tags_name[6]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[6]] - Stags_output[f"{tags_name[6]}_mean"])**2)
    E_SS_mean = (n/(n+1))*Stags_output[f"{tags_name[6]}_mean"] + (1/(n+1))*mesco_tags[tags_name[6]]
    
    CSL_var = (n/(n+1))*(Stags_output["{tags_name[3]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[3]] - Stags_output[f"{tags_name[3]}_mean_temp"])**2)
    CSL_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[3]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[3]]
    C_OLL_var = (n/(n+1))*(Stags_output[f"{tags_name[2]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[2]] - Stags_output[f"{tags_name[2]}_mean_temp"])**2)
    C_OLL_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[2]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[2]]
    R_VP_var = (n/(n+1))*(Stags_output[f"{tags_name[5]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[5]] - Stags_output[f"{tags_name[5]}_mean_temp"])**2)
    R_VP_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[5]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[5]]
    R_CPR1_var = (n/(n+1))*(Stags_output[f"{tags_name[7]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[7]] - Stags_output[f"{tags_name[7]}_mean_temp"])**2)
    R_CPR1_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[7]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[7]]
    R_LS_var = (n/(n+1))*(Stags_output[f"{tags_name[9]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[9]] - Stags_output[f"{tags_name[9]}_mean_temp"])**2)
    R_LS_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[9]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[9]]
    
    Stags_output_new = {f"{tags_name[0]}_mean" : C_OLR_mean, f"{tags_name[1]}_max" : CSU_max, f"{tags_name[1]}_min" : CSU_min, f"{tags_name[8]}_max" : R_CPL1_max,
                        f"{tags_name[3]}_stdev" : math.sqrt(CSL_var), f"{tags_name[3]}_mean_temp" : CSL_mean_temp, f"{tags_name[2]}_stdev" : math.sqrt(C_OLL_var),
                        f"{tags_name[2]}_mean_temp" : C_OLL_mean_temp, f"{tags_name[4]}_mean" : E_HT_mean, f"{tags_name[5]}_stdev" : math.sqrt(R_VP_var),
                        f"{tags_name[5]}_mean_temp" : R_VP_mean_temp, f"{tags_name[6]}_mean" : E_SS_mean, f"{tags_name[7]}_stdev" : math.sqrt(R_CPR1_var),
                        f"{tags_name[4]}_min" : E_HT_min, f"{tags_name[6]}_stdev" : math.sqrt(E_SS_var), f"{tags_name[8]}_mean" : R_CPL1_mean, f"{tags_name[9]}_stdev" : math.sqrt(R_LS_var),
                        f"{tags_name[9]}_mean_temp" : R_LS_mean_temp, f"{tags_name[8]}_max" : R_CPL1_max, f"{tags_name[10]}_mean" : R_RCT_mean}
    
    return Stags_output_new
    

###############################################################################
###############################################################################
###############################################################################


def Durete_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    tags_name = ['Rotocure_RotoCylinderTemp', 'Rotocure_CylinderTempUpper', 'Extrud_ScrewSpeed', 'Extrud_MixtureTemperature', 'Caland_OpeningLevelRight',
                 'Extrud_PressureBeforeFilter','Rotocure_CylPressureLeft1', 'CylinderSpeedUpper', 'Caland_OpeningLevelLeft', 'Rotocure_LineSpeed',
                 'Rotocure_CylPressureRight1', 'Extrud_PressureAfterFilter']
    
    if not Stags_output:
        Stags_output[f"{tags_name[1]}_min"], Stags_output[f"{tags_name[2]}_min"] = (math.inf,)*2
        Stags_output[f"{tags_name[3]}_max"], Stags_output[f"{tags_name[7]}_max"] = (-math.inf,)*2
        Stags_output[f"{tags_name[0]}_mean"], Stags_output[f"{tags_name[4]}_mean"], Stags_output[f"{tags_name[5]}_mean"], Stags_output[f"{tags_name[6]}_mean"], Stags_output[f"{tags_name[2]}_mean"], Stags_output[f"{tags_name[9]}_mean"] = (0,)*6
        Stags_output[f"{tags_name[7]}_mean_temp"], Stags_output[f"{tags_name[8]}_mean_temp"], Stags_output[f"{tags_name[10]}_mean_temp"], Stags_output[f"{tags_name[11]}_mean_temp"] = (0,)*4
        Stags_output[f"{tags_name[2]}_stdev"], Stags_output[f"{tags_name[7]}_stdev"], Stags_output[f"{tags_name[9]}_stdev"], Stags_output[f"{tags_name[8]}_stdev"], Stags_output[f"{tags_name[10]}_stdev"], Stags_output[f"{tags_name[11]}_stdev"] = (0,)*6
        
    
    mesco_tags = {k : MESCO_tags[k] for k in tags_name}
    
    R_CTU_min = min(Stags_output[f"{tags_name[1]}_min"], mesco_tags[tags_name[1]])
    E_MT_max = max(Stags_output[f"{tags_name[3]}_max"], mesco_tags[tags_name[3]])
    R_RCT_mean = (n/(n+1))*Stags_output[f"{tags_name[0]}_mean"] + (1/(n+1))*mesco_tags[tags_name[0]]
    C_OLR_mean = (n/(n+1))*Stags_output[f"{tags_name[4]}_mean"] + (1/(n+1))*mesco_tags[tags_name[4]]
    E_PBF_mean = (n/(n+1))*Stags_output[f"{tags_name[5]}_mean"] + (1/(n+1))*mesco_tags[tags_name[5]]
    R_CPL1_mean = (n/(n+1))*Stags_output[f"{tags_name[6]}_mean"] + (1/(n+1))*mesco_tags[tags_name[6]]
    
    E_SS_min = min(Stags_output[f"{tags_name[2]}_min"], mesco_tags[tags_name[2]])
    E_SS_var = (n/(n+1))*(Stags_output[f"{tags_name[2]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[2]] - Stags_output[f"{tags_name[2]}_mean"])**2)
    E_SS_mean = (n/(n+1))*Stags_output[f"{tags_name[2]}_mean"] + (1/(n+1))*mesco_tags[tags_name[2]]
    CSU_max = max(Stags_output[f"{tags_name[7]}_max"], mesco_tags[tags_name[7]])
    CSU_var = (n/(n+1))*(Stags_output[f"{tags_name[7]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[7]] - Stags_output[f"{tags_name[7]}_mean_temp"])**2)
    CSU_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[7]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[7]]
    R_LS_var = (n/(n+1))*(Stags_output[f"{tags_name[9]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[9]] - Stags_output[f"{tags_name[9]}_mean"])**2)
    R_LS_mean = (n/(n+1))*Stags_output[f"{tags_name[9]}_mean"] + (1/(n+1))*mesco_tags[tags_name[9]]
    
    C_OLL_var = (n/(n+1))*(Stags_output[f"{tags_name[8]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[8]] - Stags_output[f"{tags_name[8]}_mean_temp"])**2)
    C_OLL_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[8]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[8]]
    R_CPR1_var = (n/(n+1))*(Stags_output[f"{tags_name[10]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[10]] - Stags_output[f"{tags_name[10]}_mean_temp"])**2)
    R_CPR1_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[10]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[10]]
    E_PAF_var = (n/(n+1))*(Stags_output[f"{tags_name[11]}_stdev"]**2) + (n/((n+1)**2))*((mesco_tags[tags_name[11]] - Stags_output[f"{tags_name[11]}_mean_temp"])**2)
    E_PAF_mean_temp = (n/(n+1))*Stags_output[f"{tags_name[11]}_mean_temp"] + (1/(n+1))*mesco_tags[tags_name[11]]
    
    Stags_output_new = {f"{tags_name[0]}_mean" : R_RCT_mean, f"{tags_name[1]}_min" : R_CTU_min, f"{tags_name[2]}_mean" : E_SS_mean, f"{tags_name[3]}_max" : E_MT_max,
                        f"{tags_name[2]}_min" : E_SS_min, f"{tags_name[2]}_stdev" : math.sqrt(E_SS_var), f"{tags_name[4]}_mean" : C_OLR_mean,
                        f"{tags_name[5]}_mean" : E_PBF_mean, f"{tags_name[6]}_mean" : R_CPL1_mean, f"{tags_name[7]}_stdev" : math.sqrt(CSU_var),
                        f"{tags_name[7]}_mean_temp" : CSU_mean_temp, f"{tags_name[8]}_stdev" : math.sqrt(C_OLL_var), f"{tags_name[8]}_mean_temp" : C_OLL_mean_temp,
                        f"{tags_name[9]}_stdev" : math.sqrt(R_LS_var), f"{tags_name[10]}_stdev" : math.sqrt(R_CPR1_var), f"{tags_name[10]}_mean_temp" : R_CPR1_mean_temp,
                        f"{tags_name[7]}_max" : CSU_max, f"{tags_name[11]}_stdev" : math.sqrt(E_PAF_var), f"{tags_name[11]}_mean_temp" : E_PAF_mean_temp, f"{tags_name[9]}_mean" : R_LS_mean}
    

    return Stags_output_new
    
    
    

    
    
    
        
        
        
    
    

