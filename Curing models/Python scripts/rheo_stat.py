import sys
import os
import csv
import pandas as pd
import datetime
import time
import numpy as np

from pandas import Categorical
#%%
data_dir = "C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data"
os.chdir(data_dir + '/rheo')
os.getcwd()

#%%
##################
# Import data - Delete empty (NaNs) columns
rheo_df = pd.read_excel('./Rheo_novembre_2016_Juillet_2017.xlsx', header = 0,
                        dtype = {'N° de Charge' : str, 'Mélange' : str, 'N° de lot' : str})
print(rheo_df.isnull().all()) # Only NaN columns : 'Instrument SN'
rheo_df = rheo_df.loc[:,~(rheo_df.isnull().all())]
rheo_df.info() # -> (n = 10 552, p = 10)

# Convert 'object' variables into pd.Categorical
for col in rheo_df.columns[rheo_df.dtypes == object]:
    rheo_df[col] = rheo_df[col].astype('category')
rheo_df.dtypes

# Rename 'TS2 lb-in' column
rheo_df = rheo_df.rename(columns = {'TS2 lb-in' : 'TS2'}) 

# Check for NaNs
rheo_df.isnull().sum()

rheo_df = rheo_df.dropna(axis = 0) # -> n = 10 533
rheo_df = rheo_df.loc[~rheo_df['Mélange'].isin(['ETALONNAGE', 'ESSAI']),:] # --> n = 10 328
rheo_df = rheo_df.loc[rheo_df['Date/Time'].sort_values(ascending = True).index,:]

rheo_stat_df = pd.DataFrame()
rheo_stat_colnames = ['batch_mix', 'ML_mean', 'ML_std', 'ML_min', 'ML_max', 'MH_mean', 'MH_std', 'MH_min', 'MH_max',
 'TS2_mean', 'TS2_std', 'TS2_min', 'TS2_max', 'T90_mean', 'T90_std', 'T90_min', 'T90_max']

for i in ['ML','MH','TS2','T90']:
    if i == 'ML':
        mean_col = rheo_df.groupby(by = 'N° de lot', as_index = False, observed = True)[i].mean()
    else:
        mean_col = rheo_df.groupby(by = 'N° de lot', as_index = False, observed = True)[i].mean().drop(axis = 1, columns = 'N° de lot')
    # stdev = facteur de normalisation à 0, tq stdev = (1/n[- 1])*sum((x-mean(x))²) --> argument ddof = 0.
    stdev_col = rheo_df.groupby(by = 'N° de lot', as_index = False, observed = True)[i].agg(np.std, ddof=0).drop(axis = 1, columns = 'N° de lot')
    min_col = rheo_df.groupby(by = 'N° de lot', as_index = False, observed = True)[i].min().drop(axis = 1, columns = 'N° de lot')
    max_col = rheo_df.groupby(by = 'N° de lot', as_index = False, observed = True)[i].max().drop(axis = 1, columns = 'N° de lot')
        
    rheo_stat_df = pd.concat([rheo_stat_df, mean_col, stdev_col, min_col, max_col], axis = 1, ignore_index = True)

rheo_stat_df.columns = rheo_stat_colnames
rheo_stat_df.info() # --> (n = 218, p = 17)
rheo_stat_df['batch_mix'].apply(lambda x: isinstance(x, str)).sum() # OK

len(rheo_stat_df['batch_mix'].unique()) # PK : N° de lot mélange

# rheo_stat_df --> (n = 218, p = 17)

###
del col, mean_col, stdev_col, min_col, max_col, i
###

rheo_stat_df.to_csv(data_dir + './final_rheo.csv', sep = ';', index = False)


