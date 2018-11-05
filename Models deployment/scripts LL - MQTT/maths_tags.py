# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 08:29:35 2018

@author: s-legrandl
"""

import math
import numpy as np

def RHEO_Stags(MH_list, ML_list):
    
    ML_n = len(ML_list)
    MH_n = len(MH_list)
        
    ML_mean_temp = (sum(ML_list))/ML_n
    MH_mean_temp = (sum(MH_list))/MH_n
    ML_dev = [x - ML_mean_temp for x in ML_list]
    MH_dev = [y - MH_mean_temp for y in MH_list]
    
    ML_std = math.sqrt((sum([i**2 for i in ML_dev]))/(ML_n - 1))
    MH_std = math.sqrt((sum([j**2 for j in MH_dev]))/(MH_n - 1))        
    
    Stags_output = {"MH_std": MH_std,
                    "ML_std": ML_std,
                    "MH_mean": MH_mean_temp}
    
    return Stags_output


def Allgt_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    if not Stags_output:
        Stags_output["M_Cooler_Speed2_R_mean_temp"], Stags_output["M_Cooler_Speed2_R_std"], Stags_output["M_Caland_OpeningLevelLeft_SP_mean"], Stags_output["M_Caland_OpeningLevelRight_R_mean"], = (0,)*4
    
    cur_tags = {k : MESCO_tags[k] for k in ("M_Caland_OpeningLevelLeft_SP", "M_Caland_OpeningLevelRight_R", "M_Cooler_Speed2_R")}
        
    var_C_S2_R = (n/(n+1))*(Stags_output["M_Cooler_Speed2_R_std"]**2) + (n/((n+1)**2))*((cur_tags["M_Cooler_Speed2_R"] - Stags_output["M_Cooler_Speed2_R_mean_temp"])**2)
    mean_C_S2_R_temp = (n/(n+1))*Stags_output["M_Cooler_Speed2_R_mean_temp"] + (1/(n+1))*cur_tags["M_Cooler_Speed2_R"]
    
    mean_C_OLL_SP = (n/(n+1))*Stags_output["M_Caland_OpeningLevelLeft_SP_mean"] + (1/(n+1))*cur_tags["M_Caland_OpeningLevelLeft_SP"]
    mean_C_OLR_R = (n/(n+1))*Stags_output["M_Caland_OpeningLevelRight_R_mean"] + (1/(n+1))*cur_tags["M_Caland_OpeningLevelRight_R"]
    
    Stags_output_new = {"M_Caland_OpeningLevelLeft_SP_mean": mean_C_OLL_SP,
                       "M_Caland_OpeningLevelRight_R_mean": mean_C_OLR_R,
                       "M_Cooler_Speed2_R_std" : math.sqrt(var_C_S2_R),
                       "M_Cooler_Speed2_R_mean_temp": mean_C_S2_R_temp}
    
    return Stags_output_new

def ModContRupt_SDtags(MESCO_tags, n, ST_outputs = {}):
     
     FTags = {k : MESCO_tags[k] for k in ("M_Caland_OpeningLevelRight_R", "M_Cooler_Speed2_R", "M_Rotocure_CylinderTempLower_R",
              "M_Rotocure_CylinderTempUpper_R", "M_Rotocure_RotoCylinderTemp_R" )}
     
     if not ST_outputs :
         ST_outputs["M_Cooler_Speed2_R_max"] = -math.inf
         ST_outputs["M_Caland_OpeningLevelRight_R_mean_temp"], ST_outputs["M_Rotocure_CylinderTempLower_R_mean"], ST_outputs["M_Rotocure_CylinderTempUpper_R_mean"], ST_outputs["M_Rotocure_RotoCylinderTemp_R_mean"], ST_outputs["M_Caland_OpeningLevelRight_R_std"] =  np.repeat(0,5)
     
     maxi_CS2_R = max(ST_outputs["M_Cooler_Speed2_R_max"], FTags["M_Cooler_Speed2_R"])
 
     var_COLR_R = (n/(n+1))*(ST_outputs["M_Caland_OpeningLevelRight_R_std"]**2) + (n/((n+1)**2))*((FTags["M_Caland_OpeningLevelRight_R"] -  ST_outputs["M_Caland_OpeningLevelRight_R_mean_temp"])**2) 
     mean_COLR_R_temp = (n/(n+1))*ST_outputs["M_Caland_OpeningLevelRight_R_mean_temp"] + (1/(n+1))*FTags["M_Caland_OpeningLevelRight_R"]
     
     mean_RCTL_R = (n/(n+1))*ST_outputs["M_Rotocure_CylinderTempLower_R_mean"] + (1/(n+1))*FTags["M_Rotocure_CylinderTempLower_R"]
     mean_RCTU_R = (n/(n+1))*ST_outputs["M_Rotocure_CylinderTempUpper_R_mean"] + (1/(n+1))*FTags["M_Rotocure_CylinderTempUpper_R"]
     mean_R_RCT_R = (n/(n+1))*ST_outputs["M_Rotocure_RotoCylinderTemp_R_mean"] + (1/(n+1))*FTags["M_Rotocure_RotoCylinderTemp_R"]
     
     
     ST_outputs_new = {"M_Caland_OpeningLevelRight_R_std" : round(math.sqrt(var_COLR_R), 7), 
                       "M_Cooler_Speed2_R_max" : maxi_CS2_R,
                       "M_Rotocure_CylinderTempLower_R_mean" : round(mean_RCTL_R, 1),
                       "M_Rotocure_CylinderTempUpper_R_mean" : round(mean_RCTU_R, 1),
                       "M_Rotocure_RotoCylinderTemp_R_mean" : round(mean_R_RCT_R, 1),
                       "M_Caland_OpeningLevelRight_R_mean_temp" : round(mean_COLR_R_temp, 7)}

     return ST_outputs_new


def ModCont100_Stags(MESCO_tags, n, Stags_output = {}):
    
    if not Stags_output:
        Stags_output["M_Caland_OpeningLevelLeft_R_mean"], Stags_output["M_Caland_OpeningLevelLeft_SP_mean"], Stags_output["M_Extrud_HeadFlow_R_mean_temp"], Stags_output["M_Extrud_MixtureTemperature_R_mean"], Stags_output["M_Extrud_ScrewSpeed_SP_mean"], Stags_output["M_Extrud_HeadFlow_R_std"] = (0,)*6
    
    cur_tags = {k : MESCO_tags[k] for k in ("M_Caland_OpeningLevelLeft_R", "M_Caland_OpeningLevelLeft_SP",
                "M_Extrud_HeadFlow_R", "M_Extrud_MixtureTemperature_R", "M_Extrud_ScrewSpeed_SP")}
        
    var_E_HF_R = (n/(n+1))*(Stags_output["M_Extrud_HeadFlow_R_std"]**2) + (n/((n+1)**2))*((cur_tags["M_Extrud_HeadFlow_R"] - Stags_output["M_Extrud_HeadFlow_R_mean_temp"])**2)
    mean_E_HF_R_temp = (n/(n+1))*Stags_output["M_Extrud_HeadFlow_R_mean_temp"] + (1/(n+1))*cur_tags["M_Extrud_HeadFlow_R"]
    
    mean_C_OLL_R = (n/(n+1))*Stags_output["M_Caland_OpeningLevelLeft_R_mean"] + (1/(n+1))*cur_tags["M_Caland_OpeningLevelLeft_R"]
    mean_C_OLL_SP = (n/(n+1))*Stags_output["M_Caland_OpeningLevelLeft_SP_mean"] + (1/(n+1))*cur_tags["M_Caland_OpeningLevelLeft_SP"]
    mean_E_MT_R = (n/(n+1))*Stags_output["M_Extrud_MixtureTemperature_R_mean"] + (1/(n+1))*cur_tags["M_Extrud_MixtureTemperature_R"]
    mean_SS_SP = (n/(n+1))*Stags_output["M_Extrud_ScrewSpeed_SP_mean"] + (1/(n+1))*cur_tags["M_Extrud_ScrewSpeed_SP"]
    
    Stags_output_new = {"M_Caland_OpeningLevelLeft_R_mean": mean_C_OLL_R,
                        "M_Caland_OpeningLevelLeft_SP_mean": mean_C_OLL_SP,
                        "M_Extrud_HeadFlow_R_std": math.sqrt(var_E_HF_R),
                        "M_Extrud_MixtureTemperature_R_mean": mean_E_MT_R,
                        "M_Extrud_ScrewSpeed_SP_mean": mean_SS_SP,
                        "M_Extrud_HeadFlow_R_mean_temp": mean_E_HF_R_temp}  
    return Stags_output_new

def Durete_MESCO_Stags(MESCO_tags, n, Stags_output = {}):
    
    if not Stags_output:
           Stags_output["M_Caland_CylinderTemperatureLower_R_min"], Stags_output["M_Caland_OpeningLevelLeft_R_min"], Stags_output["M_Extrud_ScrewTemperature_R_mean"] = (math.inf,)*2 + (0,)
    
    cur_tags = {j : MESCO_tags[j] for j in ("M_Caland_CylinderTemperatureLower_R", "M_Caland_OpeningLevelLeft_R", "M_Extrud_ScrewTemperature_R")}
    
    mini_C_CTL_R = min(Stags_output["M_Caland_CylinderTemperatureLower_R_min"], cur_tags["M_Caland_CylinderTemperatureLower_R"])
    mini_C_OLL_R = min(Stags_output["M_Caland_OpeningLevelLeft_R_min"], cur_tags["M_Caland_OpeningLevelLeft_R"])
    mean_E_ST_R = (n/(n+1))*Stags_output["M_Extrud_ScrewTemperature_R_mean"] + (1/(n+1))*cur_tags["M_Extrud_ScrewTemperature_R"]
    
    Stags_outputs = {"M_Caland_CylinderTemperatureLower_R_min": mini_C_CTL_R,
                       "M_Caland_OpeningLevelLeft_R_min": mini_C_OLL_R,
                       "M_Extrud_ScrewTemperature_R_mean": mean_E_ST_R}
    
    return Stags_outputs




#%%
    
dict_ = {}
bool(dict_)
not dict_
