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
os.chdir('C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data/MES Prod/')
os.getcwd()

#%%
colnames = ['timestamp', 'atr_name', 'subtype', 'workorder', 'material', 'description', 'batch new', 'box',
                             'box sequence number', 'quality new', 'reason']

df1 = pd.read_excel('./20170825_VDR_Transaction_History_B61002_new.xlsx', header = None, skiprows = 1,
                    usecols = [x for x in np.arange(0,9)] + [11,23], names = colnames,
                    converters = {0 : pd.to_datetime})

df1[[x for x in df1.columns if x not in ['timestamp', 'quality new']]] = df1[[x for x in df1.columns if x not in ['timestamp', 'quality new']]].astype('category')

df1.info()
df1.isnull().sum()
for col in df1.columns:
    print(len(df1[col].unique()))


# df1.dim : 81 890 x 11

##################################

df2 = df1.loc[df1['reason'] == 'production',:] # n = 9 924
# df2.isnull().sum() - 84 initial NaNs removed
df2 = df2.loc[df1['box sequence number'] == 1,:] # n = 294

# for col in df2.columns:
#    print(col + ' : ', len(df2[col].unique()))
# mixing batch is key of df2 - 294 batches produced

df2 = df2[['timestamp', 'workorder', 'batch new']].rename(columns = {'timestamp' : 'TS_1stbox_prod', 'batch new' : 'batch_new'})
df2.info()

#%%
df_sec1 = pd.read_excel('./20170825_VDR_Transaction_History_cleaned.xlsx', header = 0,
                        usecols = [0,3,4,6,7,8,23], converters = {'timestamp' : pd.to_datetime, 'batch new' : int})

df_sec1[[y for y in df_sec1.columns if y != 'timestamp']] = df_sec1[[y for y in df_sec1.columns if y != 'timestamp']].astype('category')
df_sec1 = df_sec1[['timestamp', 'workorder', 'batch new', 'reason']].loc[df_sec1['reason'] == 'consumption']

df_sec1 = df_sec1.rename(columns = {'timestamp' : 'TS_conso', 'batch new' : 'batch_new'}).drop(columns = ['reason'])

df_sec2 = df_sec1.sort_values('TS_conso', axis = 0).drop_duplicates(subset = ['workorder', 'batch_new'], keep = 'first')

# for col in df_sec2.columns:
#    print(col + ' : ', len(df_sec2[col].unique())) # workorder : PK - n = 53

#%%
final = pd.merge(df_sec2, df2.drop(columns = ['workorder']), how = 'left', on = 'batch_new')
final[['workorder', 'batch_new']] = final[['workorder', 'batch_new']].astype('category')
final['maturation_time'] = (final['TS_conso'] - final['TS_1stbox_prod']).dt.days

final.info()
for col in final.columns:
    print(col + ' : ', len(final[col].unique()))
final.isnull().sum()

print(final['maturation_time'].min(), final['maturation_time'].max())

final['wo-b_mx'] = (final['workorder'].astype(str) + '-' + final['batch_new'].astype(str)).astype('category')
final = final[['wo-b_mx', 'TS_conso', 'TS_1stbox_prod', 'maturation_time']]
# final : (53 x 6)
#%%
final.to_csv('final_mat.csv', sep = ';', index = False)
