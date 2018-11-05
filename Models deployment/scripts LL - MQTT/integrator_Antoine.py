# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 12:37:10 2018

@author: s-legrandl
"""

import numpy as np
import math 

#%%
# - Function ModContRupt_SDtags() for the iterative calculcation of the 5 descriptive statistics used as inputs of the contrainte à la rupture model.
# - Statistics not meaningful for the model are indicated by "_temp" mark. 
# - Parameters : a dict of MES Connectivity tag values (1 by tag), the iteration index, and an output list of the updated statistical tags

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
     
     for j in range(len(ST_outputs_new) - 1):
         print("\n{} = {}\n".format([*ST_outputs_new.keys()][j], ST_outputs_new[[*ST_outputs_new.keys()][j]]))
     
     return ST_outputs_new
 
     
#%%

# - Test block code for the iterative application of the ModContRupt_SDtags function

# - Distribution data informations  :
# M_Caland_OpeningLevelRight_R : [mean = 0.8590949, sd = 0.1989093]
# M_Cooler_Speed2_R : [mean = 1.769098, sd = 0.666532]
# M_Rotocure_CylinderTempLower_R : [161, 176]
# M_Rotocure_CylinderTempUpper_R : [30 : 201]
# M_Rotocure_RotoCylinderTemp_R : [mean = 193.9002, sd = 32.87846]

j = 0
n = 0
FST = {}
while j <= 3:
    
    print(n)
    CUR_tags = {"M_Caland_OpeningLevelRight_R": round(np.random.normal(0.8590949, 0.1989093), 7),
            "M_Cooler_Speed2_R": round(np.random.normal(1.769098, 0.666532),6),
            "M_Rotocure_CylinderTempLower_R": round(np.random.uniform(161, 176), 0),
            "M_Rotocure_CylinderTempUpper_R": round(np.random.uniform(30, 201), 0),
            "M_Rotocure_RotoCylinderTemp_R": round(np.random.normal(193.9002, 32.87846),0)}
 
    print(CUR_tags, sep = "\n")
    
    if n == 0:
        FST = ModContRupt_SDtags(CUR_tags, n, ST_outputs = {})
    
    else:
        FST = ModContRupt_SDtags(CUR_tags, n, ST_outputs = FST)
    
    n = n + 1
    j = j + 1
        
     
 
