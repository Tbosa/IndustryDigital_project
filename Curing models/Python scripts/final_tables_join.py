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
data_dir = "C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data"
# os.chdir(data_dir + "/rheo")
os.chdir(data_dir)
os.getcwd()

#%%
MES_prod_df = pd.read_csv('./final_MESprod.csv', sep = ';', header = 0, dtype = 'category')
print(MES_prod_df.dtypes)

rheo_df = pd.read_csv('./final_rheo.csv', sep = ';', header = 0, dtype = {'batch_mix' : 'category'})
print(rheo_df.dtypes)

maturation_df = pd.read_csv('./final_mat.csv', sep = ';', header = 0, usecols = [0,3], dtype = {'wo-b_mx' : 'category'})
print(maturation_df.dtypes)

cur_tags_df = pd.read_csv('./final_cur_tags.csv', sep = ';', decimal = ',', header = 0, dtype = {'box' : 'category'})
print(cur_tags_df.dtypes)

idos_df = pd.read_csv('./final_idos.csv', sep = ';', decimal =',', header = 0, dtype = {'lot-box_nb' : 'category'})
print(idos_df.dtypes)

#%%
final0 = pd.merge(MES_prod_df, maturation_df, how = 'left', on = 'wo-b_mx', validate = 'many_to_one')
final1 = pd.merge(final0, rheo_df, how = 'left', on = 'batch_mix', validate = 'many_to_one')
final2 = pd.merge(final1, cur_tags_df, how = 'left', on = 'box', validate ='one_to_one')

final = (pd.merge(final2, idos_df, how = 'left', on = 'lot-box_nb', validate = 'one_to_one')).drop(columns = ['wo-b_mx', 'lot-box_nb'])

for col in final.columns[~final.dtypes.isin([np.dtype(np.int64), np.dtype(np.float64)])]:
    final[col] = final[col].astype('category')
final.dtypes

final.info()

del final0, final1, final2
#%%
# liste des bobines à supprimer : 
# => produites le 05/01/2017 entre 12h et 14h, période de panne MES connectivity avec génération de données aberrantes : 11043002104127-28-29, 11043002104095-96-98
# => Invalidées / non-contrôlées et intraçables sur idos : 12057810-1, 12438950-1, 12438960-[2, 4, 8], 13303190-[6, 7, 8].

idos_col = final.columns[final.columns.slice_indexer(start = 'Allgt_avg', end = 'durete_min')]
box_del = ['11043002104127', '11043002104128', '11043002104129', '11043002104095', '11043002104096', '11043002104098']
for index, row in final.iterrows():
    if row[idos_col].isnull().all():
        box_del = box_del + [row['box']]
print(box_del) # check - 14 bobines à enlever

final = final.loc[~(final['box'].isin(box_del)),:] # (n = 1698, p = 155)

# 3 bobines aux données de duretés inconnues sur idos : 11043002108866-67-68
# Ajouter les valeurs de moyenne, min, max récupérées à partir des dossiers de lot

# final.loc[final.isnull().any(axis = 1),['workorder', 'batch_cur', 'batch_mix', 'box']]
final.loc[final.isnull().any(axis = 1), ['durete_avg']] = pd.Series([68,68,68], index = final.loc[final.isnull().any(axis = 1), ['durete_avg']].index)
final.loc[final.isnull().any(axis = 1), ['durete_min']] = pd.Series([65]*3, index = final.loc[final.isnull().any(axis = 1), ['durete_min']].index)
final.loc[final.isnull().any(axis = 1), ['durete_max']] = pd.Series([70]*3, index = final.loc[final.isnull().any(axis = 1), ['durete_max']].index)


print(final.columns[np.where(final.isnull().sum() != 0)])
#%%
os.getcwd()
final.to_csv('./Final tables/final.csv', sep = ';', decimal = ',', index = False, na_rep = 'NA', quoting = csv.QUOTE_NONE)


