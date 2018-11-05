import sys
import os
import csv
import pickle
import datetime
import time
import pandas as pd
import numpy as np

from pandas import Categorical
#%%
data_dir = "C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data"
# os.chdir(data_dir + "/rheo")
os.chdir(data_dir)
os.getcwd()

#%%
MESprod_df = pd.read_excel("./MES Prod/20170825_VDR_Transaction_History.xlsx", header=0,
                           dtype = {'id' : str, 'workorder' : str, 'material' : str, 'box' : str, 'batch new' : str})
print(sys.getsizeof(MESprod_df)/10**6, "MB") # alloue +700 MB d'espace mémoire
MESprod_df.info(memory_usage = 'deep') # p = 26
###############################################################################
# 1st cleaning
print((MESprod_df.duplicated().sum()/MESprod_df.shape[0])*100) # 83.5% de doublons
MESprod_df = MESprod_df.drop_duplicates(keep = 'first') # (n = 105 603 ; p = 26)
print(MESprod_df.isnull().sum()) # champs vides : 'pallet', 'cust reg', 'equipment', 'silo', 'mateirial movement'
MESprod_df = MESprod_df.loc[:,~(MESprod_df.isnull().sum() == MESprod_df.shape[0])] # (p = 21)

MESprod_df = MESprod_df.rename(columns = {'equipment.1' : 'equipment'})

# 2nd cleaning
MESprod_df = MESprod_df[['atr_name','timestamp', 'workorder', 'material', 'description', 'batch new',
                         'box', 'box sequence number', 'quality new', 'equipment', 'reason']] # (n = 105 603, p = 11)

MESprod_df.isnull().sum()
###############################################################################
for col_name in MESprod_df.columns:
    if col_name == 'timestamp':
        MESprod_df[col_name] = pd.to_datetime(MESprod_df[col_name], format = '%Y-%m-%d %H:%M:%S', origin = 'unix')
    elif col_name == 'quality new':
        MESprod_df[col_name] = MESprod_df[col_name].str.strip() # Enlever les vides aux extrêmes gauche et droite des objets string
        MESprod_df['quantity'], MESprod_df['unit'] = MESprod_df[col_name].str.split().str 
        MESprod_df = MESprod_df.drop(columns = 'quality new')
        MESprod_df['quantity'] = MESprod_df['quantity'].astype(np.float64)
    else:
        MESprod_df[col_name] = MESprod_df[col_name].astype('category')

MESprod_df.dtypes # OK
# p = 12

# l43 : Enlever les vides aux extrêmes gauche et droite des objets string
# l44: Décomposer l'objet string en une liste de deux éléments, avec séparation par défaut (chaine max de vides)
###############################################################################
MESprod_403E_df = MESprod_df.loc[MESprod_df['equipment'] == 'V62003',:] # (n = 10 310)
MESprod_403E_df = MESprod_403E_df.loc[MESprod_403E_df['reason'].isin(['production', 'consumption']),:] # (n = 6 458)
# np.unique(MESprod_403E_df['description'].values)
MESprod_403E_df.isnull().sum() # 0

MESprod_403E_df = MESprod_403E_df.loc[MESprod_403E_df['description'].str.contains('403E'),:] # (n = 2538)
# MESprod_403E_df['description'].value_counts(dropna = False)

MESprod_403E_df = MESprod_403E_df.loc[MESprod_403E_df['timestamp'].sort_values(ascending = True).index, :]
# MESprod_403E_df['timestamp'].max()

sub1 = MESprod_403E_df[['timestamp', 'workorder']]
sub1 = sub1.loc[(sub1['timestamp'] >= '2017-01-01 00:00:00') & (sub1['timestamp'] <= '2017-07-01 00:00:00'),]

first_OF = sub1.iloc[0,:] # 100797734
last_OF = sub1.iloc[-1,:] # 100914402

sub2 = MESprod_403E_df.loc[MESprod_403E_df['workorder'].isin([first_OF['workorder'], last_OF['workorder']]), 'timestamp']
MESprod_403E_df = MESprod_403E_df.loc[(MESprod_403E_df['timestamp'] >= sub2.iloc[0]) & (MESprod_403E_df['timestamp'] <= sub2.iloc[-1]),:] # n = 2266

len(MESprod_403E_df.loc[MESprod_403E_df['reason'] == 'production','box'].unique()) # 1712 bobines de 403E produites
len(MESprod_403E_df['workorder'].unique()) # 46 OF lancés

MESprod_403E_df = MESprod_403E_df.drop(columns = ['equipment']) # p = 11
###############################################################################
# Vérifier la validité des OFs - Cohérence au niveau des quantités consommées et produites -> suffisantes pour cloture d'un OF ?
OF_failed = []    
for of in MESprod_403E_df['workorder'].unique():
    print(of)
    MES_sub = MESprod_403E_df.loc[MESprod_403E_df['workorder'] == of, 'reason']
    print('mixing boxes consumed: ', (MES_sub == 'consumption').sum())
    print('curing boxes produced: ', (MES_sub == 'production').sum())
    if not (MES_sub.isin(['consumption']).any() & MES_sub.isin(['production']).any()):
        OF_failed.append(of)
        print('OF failed: ', OF_failed)
        
print(OF_failed) # OF 'cassés' : 100810120        
MESprod_403E_df = MESprod_403E_df.loc[~MESprod_403E_df['workorder'].isin(OF_failed),:] # n = 2265
len(MESprod_403E_df['workorder'].unique()) # nb d'OF valides : 45

###############################################################################
## Identification de(s) clé(s) primaire(s)
for col_name in MESprod_403E_df.columns:
    unk_val = len(MESprod_403E_df[col_name].unique())    
    if unk_val == MESprod_403E_df.shape[0]:
        print(col_name, ': PRIMARY KEY')
        
###############################################################################
# MESprod_403E_df: (n = 2265, p = 11)

###
del sub1, sub2, MES_sub, of, col_name, unk_val
###

#%%
# * Partir du n° de bobine comme clé primaire de la table finale
# * Garder l'OF/n° de lot vulc associés pour jointure avec lots de mélanges consommés.
df1 = MESprod_403E_df.loc[MESprod_403E_df['reason'] == 'production', ['workorder', 'material', 'batch new', 'box', 'box sequence number']]
df2 = MESprod_403E_df.loc[MESprod_403E_df['reason'] == 'consumption', ['workorder', 'material', 'batch new']] 

df1 = df1.rename(columns = {'material' : 'material_cur', 'batch new' : 'batch_cur'})
df2 = df2.rename(columns = {'material' : 'material_mix', 'batch new' : 'batch_mix'})

df2 = df2.drop_duplicates(keep = 'first') # n = 45 OK

final = pd.merge(df1, df2, how = 'left', on = 'workorder', validate = 'many_to_one')
final = final[['workorder', 'material_cur', 'batch_cur', 'batch_mix', 'box', 'box sequence number']]
final.info()
final.isnull().sum() # Ok

final['wo-b_mx'] = (final['workorder'].astype(str) + '-' + final['batch_mix'].astype(str)).astype('category')
final['lot-box_nb'] = (final['batch_cur'].astype(str) + '-' + final['box sequence number'].astype(str)).astype('category')

# final : (n = 1712, p = 8)

###
del df1, df2
###

# final.to_csv('./final_MESprod.csv', sep = ';', index = False)
#%%
# Création d'une table annexe à MESprod_403E_df spécifiant les timestamp de lancement/fin de prod d'une bobine
# Import de la table Cadences_403E_LVC3 spécifiant la cadence (m/h) fixe de production d'une bobine par CA de 403E.
os.chdir(data_dir)

CA_cad = pd.read_excel("./MES Prod/Cadences_403E_LVC3.xlsx", header = 0, dtype = {'material' : str})
CA_cad.info()
for i in CA_cad.columns[:2]:
    CA_cad[i] = CA_cad[i].astype('category')

MES_sub1 = (MESprod_403E_df.loc[MESprod_403E_df['reason'] == 'production',:]).drop(columns = 'reason') # p = 10
MES_sub1 = MES_sub1.rename(columns = {'timestamp' : 'TS.end_time (s)'})
MES_sub1 = pd.merge(MES_sub1, CA_cad.drop(columns = 'désignation'), how = 'left', on = 'material', validate = 'many_to_one') # p = 11

MES_sub1['prod time (s)'] = ((MES_sub1['quantity']/MES_sub1['cadence m/heure'])*3600).astype(np.int64)
MES_sub1['TS.start_time (s)'] = MES_sub1['TS.end_time (s)'] - pd.to_timedelta(MES_sub1['prod time (s)'], unit = 's')

MES_sub1 = MES_sub1[['atr_name', 'TS.start_time (s)', 'TS.end_time (s)', 'workorder', 'material', 'description',
                     'batch new', 'box', 'box sequence number']]

# MES_sub1 : (n = 1712,  p = 9)

###
del CA_cad, i
###
#%%
with open('./Curing/tags_dataframes_cleaned_1.pkl', 'rb') as obj:
    d = pickle.load(obj)

stat_tags_names = []
for x in d.keys():   
    stat_tags_names = stat_tags_names + [x+'_mean', x+'_stdev', x+'_min', x+'_max']

D = pd.concat([MES_sub1['box'], pd.DataFrame(data = np.empty((MES_sub1.shape[0], len(d)*4)), columns = stat_tags_names)], axis = 1)
print(len(D['box'].unique()) == D.shape[0])

i = 1
for bx in D['box'].unique():
    
    intval_ts = [MES_sub1.loc[MES_sub1.box == bx, 'TS.start_time (s)'].iloc[0], MES_sub1.loc[MES_sub1.box == bx, 'TS.end_time (s)'].iloc[0]]
    stat_values = []
        
    for tag in d.keys():
        values = d[tag].loc[(d[tag]['timestamp'] >= intval_ts[0]) & (d[tag]['timestamp'] <= intval_ts[1]), 'value']
               
        mean_t = values.mean()
        stdev_t = values.std(ddof = 0)
        min_t = values.min()
        max_t = values.max()
        
        stat_values = stat_values + [mean_t, stdev_t, min_t, max_t]
    
    D.loc[(D['box'] == bx), stat_tags_names] = stat_values
    print(f"boxes done : {i}/{len(D['box'])}")
    
    i = i + 1

# D_nans_nb = D.iloc[:,1:].isnull().sum()
# ==> D : shape(1712, 1 + 113) - mix of NaN and float values
    
###
del stat_tags_names, x, bx, intval_ts, stat_values, mean_t, stdev_t, min_t, max_t
###

D.to_csv(data_dir + './Curing/final_cur_tags.csv', sep = ';', decimal = ',', index = False, na_rep = 'NA', quoting = csv.QUOTE_NONE)
