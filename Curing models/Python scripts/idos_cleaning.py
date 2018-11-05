import sys
import os
import glob
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
os.chdir(data_dir + '/Idos/')
os.getcwd()

#%%
# Table 'Idos_Points_controles_403E_2016-11.2017.xlsx' - Dim : (10 047 x 25)
# Métadonnées sur les points de contrôle ('inspection point') de chaque lot entre 01/2016 et 11/2017.
# Point de contrôle : série de mesures effectuées en même temps à une fréquence prédéfinie.
# Niveau de précision (granularité de la table) : jusqu'aux opérations effectuées sur les bobines vulcanisées, identifiées par leur n° unique par lot de contrôle (int)
# Une opération est une liste de caractéristiques à mesurer et contrôler, selon un plan de contrôle définie par le lot de contrôle.

ctrl_check_df = pd.read_excel('./Idos_Points_controles_403E_2016-11.2017.xlsx', header = 0, usecols = [0,1,2,3,4,16],
                              converters = {'Lot ctrle' : str, 'Opé.' : str, 'Echant' : str, 'Code' : str, 'ZoneUtilis' : int, 'ZoneUtilis.1' : str})
ctrl_check_df = ctrl_check_df.rename(columns = {'Lot ctrle' : 'lot_ctrl', 'Opé.' : 'Op', 'Echant' : 'Ech', 'ZoneUtilis' : 'ZoneUser', 'ZoneUtilis.1' : 'ZoneLVC'})
ctrl_check_df.dtypes
ctrl_check_df.isnull().sum() # colonne 'ZoneLVC' : 43 NaN

ctrl_check_df.applymap(lambda x: isinstance(x, str)).sum(axis = 0)

# Concaténation des colonnes lot de contrôle / Opération / Echantillon
ctrl_check_df['lot_ctrl-Op-Ech'] = (ctrl_check_df['lot_ctrl'] + '-' + ctrl_check_df['Op'] + '-' + ctrl_check_df['Ech']).astype('category')
ctrl_check_df = ctrl_check_df[['lot_ctrl-Op-Ech', 'Code', 'ZoneLVC', 'ZoneUser']]

ctrl_check_df['ZoneUser'] = ctrl_check_df['ZoneUser'].astype(str)


print('lot_ctrl-Op-Ech column = Primary Key ? ->', len(ctrl_check_df['lot_ctrl-Op-Ech'].unique()) == ctrl_check_df.shape[0]) # OK : colonne lot_ctrl-Op-Ech ==> Primary key
ctrl_check_df.info()

# ctrl_check_df : (10 628 x 4)
#%%
# Table 'Idos_Caractéristiques_403E_2016-11.2017.xlsx' - Dim : (61 977) x 103

ctrl_char_df = pd.read_excel('./Idos_Caractéristiques_403E_2016-11.2017.xlsx', header = 0, usecols = [0,1,2,3,5,6,7,8,12,13],
                             converters = {'Opé.' : str, 'Car.' : str, 'Désignation' : str, 'Lot' : str, 'Echant' : str, 'Lot ctrle' : str}) # (n = 61 977, p = 10)
ctrl_char_df = ctrl_char_df.rename(columns = {'Lot ctrle' : 'lot_ctrl', 'Opé.' : 'Op', 'Car.' : 'Car', 'Echant' : 'Ech',
                                                'Désignation' : 'Des', 'Lot' : 'lot' , 'Val.moy.' : 'avg', 'Ecart-type' : 'stdev', 'Maximum' : 'max', 'Minimum' : 'min'})

ctrl_char_df.applymap(lambda x: isinstance(x, str)).sum()
ctrl_char_df.isnull().sum()

ctrl_char_df['lot_ctrl-Op-Ech'] = (ctrl_char_df['lot_ctrl'] + '-' + ctrl_char_df['Op'] + '-' + ctrl_char_df['Ech']).astype('category') # (p = 11)
ctrl_char_df = ctrl_char_df[['lot', 'lot_ctrl-Op-Ech', 'Car', 'Des', 'avg', 'stdev', 'max', 'min', 'lot_ctrl', 'Op', 'Ech']]

len(ctrl_char_df['lot_ctrl-Op-Ech'].unique())
ctrl_char_df.info()
# ctrl_char_df : (61 977 x 11)
#%%
# Jointure externe pour garder les mesures qualités observées (left table : ctrl_char_df) sur les bobines de chaque lot et importer la colonne 'ZoneUser'.

final1 = pd.merge(ctrl_char_df, ctrl_check_df, how ='left', on = 'lot_ctrl-Op-Ech', validate = 'many_to_one') # (61 977 x 14)
final1.isnull().sum() # présence de NaN dans les colonnes (avg, stdev, max, min, Code, zoneLVC, ZoneUser)

final1.info()
#%%
## Filtrage sur les données qualités des 4 PMC : allongement, contrainte à 100%, contrainte à la rupture, dureté.

#
final1[['lot_ctrl-Op-Ech', 'Car', 'Des', 'lot_ctrl', 'Op', 'Ech', 'Code', 'ZoneLVC']] = final1[['lot_ctrl-Op-Ech', 'Car', 'Des', 'lot_ctrl', 'Op', 'Ech', 'Code', 'ZoneLVC']].astype('category')
# final1['Op'].value_counts(dropna = False)
# final1['Op'].apply(lambda x: isinstance(x, str)).sum()

#
final1['lot'] = final1['lot'].str.slice(2,)
final1['lot'].head(5)

#
final1 = final1.loc[final1['Op'].isin(['0040', '0045']),:] # (59 119 x 14)
final1['Op'].value_counts()
final1.isnull().sum() # présence de NaN dans les colonnes (avg, stdev, max, min, zoneLVC)

#
final1 = final1.loc[final1['Des'].isin(['Allongement', 'Dureté', 'Contrainte à 100%', 'Contrainte à la rupture']), :]  # (19 691 x 14)
final1['Des'].value_counts(dropna = False)
final1['Car'].value_counts(dropna = False)

abv = ['durete', 'Allgt', 'cont_rupt', 'cont_100']
idos_sub = {}
j = 0

for i in final1['Des'].unique().categories:
    
    # i = 'Dureté'
    print(i)
    
    A = final1.loc[final1['Des'] == i, ['lot', 'ZoneUser', 'Des', 'avg', 'stdev', 'max', 'min', 'Code']]
    print((A['Des'] == i).all(skipna = False))
    
    A = A.rename(columns = {'Code' : f"Code_{abv[j]}", 'avg' : abv[j] + '_avg', 'stdev' : abv[j] + '_stdev', 'max' : abv[j] + '_max', 'min' : abv[j] + '_min'}).drop(columns = 'Des')
    A['lot-box_nb'] = A['lot'] + '-' + A['ZoneUser']
        
    if A.duplicated(subset = 'lot-box_nb', keep = False).any():
        
        print(A.loc[A.duplicated(subset = 'lot-box_nb', keep = False),:])
        A = A.loc[A[f"Code_{abv[j]}"] != 'I',:]
        # --> Erreurs de saisies sur les n° de bobine 'ZoneUser': 12622640-19 = .-18 (lot ctrle : 030000607637) | 12647210-61 = .-81 (" : 030000608814)
        
        if i == 'Dureté':
            
            A.loc[A.loc[(A['lot-box_nb'] == '12622640-19'), 'lot-box_nb'].index[0],'lot-box_nb'] = (A.loc[(A['lot-box_nb'] == '12622640-19'), 'lot-box_nb']).iloc[0].replace('19', '18')
            A.loc[A.loc[(A['lot-box_nb'] == '12647210-61'), 'lot-box_nb'].index[1], 'lot-box_nb'] = (A.loc[(A['lot-box_nb'] == '12647210-61'), 'lot-box_nb']).iloc[1].replace('61', '81')
        
        #if (A['Code'] == 'A').all():
             # ...   
     
    print(A.shape)
    print(len(A['lot-box_nb'].unique()))
    
    idos_sub[abv[j]] = A.drop(columns = ['lot', 'ZoneUser'] ) 
    
    
    j = j + 1


###
idos_sub1 = idos_sub['Allgt']
for k in sorted(idos_sub.keys())[1:]:
    idos_sub1 = idos_sub1.merge(idos_sub[k], how = 'outer', on = 'lot-box_nb') # (4911 x 21)

cols = idos_sub1.columns.tolist()
codes_cols = ['Code_Allgt', 'Code_cont_rupt', 'Code_cont_100', 'Code_durete']
idos_sub1 = idos_sub1[['lot-box_nb'] + [x for x in cols if x not in ['lot-box_nb'] + codes_cols] + codes_cols]

#
del j, i, A, cols, k
#%%

for k in idos_sub1.columns.drop(['lot-box_nb'] + codes_cols):
    # k = idos_sub1.columns[1]
    if ('Allgt' in k) | ('durete' in k):
        idos_sub1[k] = pd.to_numeric(idos_sub1[k], errors = 'coerce') 
        # présence de nan dans une colonne Series composés de int --> conversion obligatoire en float64 pour faciliter stockage en mémoire
    else:
        idos_sub1[k] = pd.to_numeric(idos_sub1[k].str.replace(',', '.'), errors = 'coerce')
    
    print(idos_sub1[k].apply(type).value_counts())

############
idos_sub1.to_csv('final_idos.csv', sep = ';', decimal = ',', index = False, na_rep = 'NA', quoting = csv.QUOTE_NONE)



