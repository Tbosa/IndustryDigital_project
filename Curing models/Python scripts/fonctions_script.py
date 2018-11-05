import sys
import os
import pandas as pd
import datetime
import time
import numpy as np
import matplotlib.style
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv

from pandas import Categorical
#%%

def deal_strings(x):
    x = x.replace(' ','')
    x = x.isalpha()
    return x

def reformating_dt(ds):
    
    print(ds.dt.day.unique())
    TS = pd.Series()
    
    for i in ds.dt.day.unique():
        temp = ds.loc[ds.dt.day == i]
        temp_twelve = temp.dt.hour == 0
        temp_twelve_blockmask = temp_twelve[temp_twelve.shift() != temp_twelve]
        print(i)
        # print(temp_twelve_blockmask, '\n')
        
        if temp_twelve_blockmask.size == 2: #  midnight = T | noon = F
            noon_date = temp_twelve[temp.dt.hour.diff() < 0]
            noon_date.iloc[0] = True
            
            temp_twelve_blockmask = temp_twelve_blockmask.append(noon_date)
            print(temp_twelve_blockmask)
            
        elif temp_twelve_blockmask.size == 3: # midnight = F | noon = T
            temp_twelve_blockmask.iloc[0] = True
            print(temp_twelve_blockmask)
        
        elif temp_twelve_blockmask.size == 1:
            temp_twelve_blockmask.iloc[0] = True
            
            noon_date = temp_twelve[temp.dt.hour.diff() < 0]
            noon_date.iloc[0] = True
            
            temp_twelve_blockmask = temp_twelve_blockmask.append(noon_date)
            print(temp_twelve_blockmask) # 
            
            
        midnight = temp_twelve.replace(True, False)
        midnight.loc[min(temp_twelve_blockmask[temp_twelve_blockmask].index)] = True
    
        noon = temp_twelve.replace(True, False)
        noon.loc[max(temp_twelve_blockmask[temp_twelve_blockmask].index)] = True
    
      
        offset = pd.Series(np.nan, index = temp.index, dtype ='timedelta64[ns]')
        offset[midnight] = pd.Timedelta(0)
        offset[noon] = pd.Timedelta(12, 'h')
        offset.fillna(method = 'ffill', inplace = True)
    
        temp += offset
        TS = pd.concat([TS,temp])
    
    return TS

