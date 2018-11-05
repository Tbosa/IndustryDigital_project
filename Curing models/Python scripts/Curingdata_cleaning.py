import os
import glob
import csv
import json
import pickle
import math
import itertools
import datetime
import numpy as np
import pandas as pd

#%%
# data_dir = "C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data"

os.chdir(data_dir + '/Curing')
os.getcwd()
#%%
# Import des fichiers associés aux tags sélectionnés

tags_del = ['G_GoodPieces', 'M_Extrud_HeadFlow', 'M_Extrud_ScrewFlow', 'M_Extrud_VacuumWellFlow', 'M_Rotocure_CoilLengthCenter'] + ['M_Extrud_Body{}Flow'.format(j) for j in [1,2,3,4]]
txtags_del = ['G_MachineState', 'M_Alarm']

cur_tags_dfs = {}
for file in glob.glob('*.xlsx'):
    # print(file)
    # file = glob.glob('*.xlsx')[3]
    file_name = file[20:].replace('_R.xlsx', '')
    if file_name in tags_del + txtags_del:
        continue
    
    print(file_name)
    df = pd.read_excel('./' + file, header = None, names = ['timestamp', 'value'], skipfooter = 2)
    # print(df.loc[df['value'].apply(lambda x: isinstance(x,str))])
    
    cur_tags_dfs[file_name] = df

#
del file, file_name, df
#%%
# Import et concatenation des tags "splittés"

st_rep = os.getcwd() + '\Splitted Tags'
split_cur_tags_dfs = {}

for file_rep in os.listdir(st_rep):
    
    df = pd.DataFrame()
    
    for file in os.listdir(st_rep + '\{}'.format(file_rep)):
        
        print(file)
        df_temp = pd.read_excel(st_rep + '\{}'.format(file_rep) + '\{}'.format(file), header = None, names = ['timestamp', 'value'],  skipfooter = 2)
        df = df.append(df_temp, ignore_index = True)
        
    split_cur_tags_dfs[file_rep[20:].replace('_R','')] = df.reset_index(drop = True)

#
del file_rep, file, df, df_temp
#%%
os.chdir(os.getcwd()[:-12] + '\Python scripts')
os.getcwd()
from fonctions_script import reformating_dt # fonction de formattage manuel du timestamp

## Import, concatenation et transformation du format timestamp pour les 7 tags composés de 6 fichiers csv (extractions spécifiques)

os.chdir(data_dir + '/Curing')

add_cur_tags = np.array(['M_Extrud_PressureAfterFilter', 'M_Extrud_PressureBeforeFilter', 'M_Extrud_ScrewSpeed', 'M_Rotocure_CylPressureLeft1', 'M_Rotocure_CylPressureRight1',
                'M_Rotocure_LineSpeed', 'M_Rotocure_VulcPressure'])

add_cur_tags_dfs = {}
for folder in os.listdir():
    
    if any([x in folder for x in add_cur_tags]):
        tag_name = str(add_cur_tags[[x in folder for x in add_cur_tags]][0])
        print(tag_name)
        
        subfiles = os.listdir(folder)
        # print(subfiles)
        dict_months = {j.replace('.csv', '') : None for j in subfiles}
         
        for subf in subfiles:
             
             print(subf, '\n')
             
             df = pd.read_csv('./' + folder + '/' + subf, sep = ',', skiprows = 4, usecols = [6,7], 
                              header = None, names = ['value', 'timestamp'])
             
             df['timestamp'] = pd.to_datetime(df['timestamp'], format = '%d/%m/%Y %I:%M:%S')
             df['timestamp'] = reformating_dt(df['timestamp'])
             
             df = df[['timestamp', 'value']]
             
             dict_months[subf.replace('.csv','')] = df
             
        add_cur_tags_dfs[tag_name] =  pd.concat([dict_months[k] for k in sorted(dict_months.keys())], axis = 0, ignore_index = True)
                 
        
del folder, tag_name, subfiles, subf, dict_months, df 
#%%
## Pour chaque tag, mécanisme d'ajout de valeurs pour combler les différents trous provoquant des NaN

tags_list = list(cur_tags_dfs.keys()) + list(split_cur_tags_dfs.keys()) + list(add_cur_tags_dfs.keys())

tags_dfs = {}
for tag in tags_list:
    
    if tag in cur_tags_dfs.keys():
        temp = cur_tags_dfs[tag]
    elif tag in split_cur_tags_dfs.keys():
        temp = split_cur_tags_dfs[tag]
    elif tag in add_cur_tags_dfs.keys():
        temp = add_cur_tags_dfs[tag]
        
    else:
        print('Error: -tag- not in tags_list')
        break
        
    temp['time_diff'] = temp['timestamp'].diff()
    temp['weekday'] = temp['timestamp'].dt.weekday
    
    rec_index = np.asarray(temp.index.tolist())
    temp_nrow = temp.shape[0]
    
    for row in temp[1:].itertuples():
        
        if ((row.weekday < 5) | ((row.weekday == 5) & (row.timestamp.hour < 2))):
            print(tag + ' - ', row.Index, ' / {}'.format(temp_nrow), '\n')
        
            if (row.time_diff > pd.Timedelta(minutes = 10)) & (not isinstance(temp.iloc[np.where(rec_index == row.Index)[0].item() - 1, 1], str)):
                
                eps = row.time_diff
                val = temp.iloc[np.where(rec_index == row.Index)[0].item() - 1, 1]
                
                while eps > pd.Timedelta(minutes = 10):
                                    
                    new_ts = temp.iloc[np.where(rec_index == row.Index)[0].item() - 1, 0] + pd.Timedelta(minutes = 10)
                    new_timediff = new_ts - temp.iloc[np.where(rec_index == row.Index)[0].item() - 1, 0]
                    new_weekday = new_ts.dayofweek
                    new_rec = pd.DataFrame({'timestamp' : [new_ts], 'value' : [val], 'time_diff' : [new_timediff], 'weekday' : new_weekday})
                                    
                    temp = pd.concat([temp[:(np.where(rec_index == row.Index)[0].item())], new_rec, temp[(np.where(rec_index == row.Index)[0].item()):]])
                    rec_index = np.asarray(temp.index.tolist())
                    
                    eps = row.timestamp - new_rec.loc[0,'timestamp']

    
    temp = temp.reset_index(drop = True).drop(columns = ['time_diff', 'weekday'])
    # temp.to_csv('./Reformated tags/VDR.VDR.LVC3.V62003.{}_R.csv'.format(tag), header = True, index = False)
    tags_dfs[tag] = temp

del tag, row, eps, val, new_ts, new_timediff, new_weekday, new_rec, rec_index, temp
#%%
# with open('tags_dataframes.pkl', 'wb') as handle:
#     pickle.dump(tags_dfs, handle, protocol = pickle.HIGHEST_PROTOCOL)

# with open('tags_dataframes.pkl', 'rb') as f:
#    b = pickle.load(f)  

#%%
## Création d'une fonction pour le formatage spécifique des valeurs process pour les 7 tags du dictionnaire add_cur_tags_dfs:
# valeurs numériques (float) -> garder trois décimales.
# valeurs numériques converties en str lors de l'import [imprécisions sur les extractions massives au format .csv] (str) -> convertir au format float à 3 décimales
# valeurs manquantes 'Null' (str) -> nan.
##
def convert_valtype2(x):
    
    if type(x) != str:
        return round(x, 3)
    
    elif (type(x) == str) and (not x.isalpha()):
        val = round(float(x.strip().replace(' ', '')), 3)
        return val
    
    elif (type(x) == str) and (x.isalpha()):
        val = np.nan
        return val

##
# Formatage des valeurs process des 28 tags du dictionnaire principal tags_dfs.
# Distinguer les deux démarches entre les 7 tags additionnels et les 21 originaux.
tags_name = list(tags_dfs.keys())

for tag_name in tags_name:
    print(tag_name)
    print(tags_dfs[tag_name]['value'].dtype, '\n')
    
    if tag_name in list(add_cur_tags_dfs.keys()):
        
        tags_dfs[tag_name]['value'] = tags_dfs[tag_name]['value'].apply(convert_valtype2)
        print('new "value" column dtype : ', tags_dfs[tag_name]['value'].dtype)
        print('NaN nb : ', tags_dfs[tag_name]['value'].isnull().sum())
    
    else:
        
        tags_dfs[tag_name]['value'] = tags_dfs[tag_name]['value'].apply(pd.to_numeric, errors = 'coerce').astype('float64')
        print('new "value" column dtype : ', tags_dfs[tag_name]['value'].dtype)
        print('NaN nb : ', tags_dfs[tag_name]['value'].isnull().sum())
    
        
#%%     
# os.getcwd()
#with open('tags_dataframes_cleaned.pkl', 'wb') as f:
#    pickle.dump(tags_dfs, f, protocol = pickle.HIGHEST_PROTOCOL)
#
with open('tags_dataframes_cleaned.pkl', 'rb') as obj:
    tags_dfs = pickle.load(obj)

#%%
# Réutilisation de l'algo pour les tags initiaux (xlsx) pour homogénéiser le volume de données entre tous les tags
    
tags_name = ['M_Caland_Biasing','M_Caland_CylinderTemperatureUpper', 'M_Caland_CylinderTemperatureLower', 'M_Extrud_HeadTemperature', 'M_Rotocure_CylinderTempUpper',
             'M_Extrud_PressureAfterFilter', 'M_Extrud_PressureBeforeFilter', 'M_Extrud_ScrewSpeed', 'M_Rotocure_CylPressureLeft1', 'M_Rotocure_CylPressureRight1',
             'M_Rotocure_LineSpeed', 'M_Rotocure_VulcPressure', 'M_Extrud_BodyTemperature1', 'M_Extrud_VaccumWellTemperature']

for tag in tags_name:
    
    # tag = tags_name[0]
    # print(tag)
    tags_dfs[tag]['time_diff'] = tags_dfs[tag]['timestamp'].diff()
    tags_dfs[tag]['weekday'] = tags_dfs[tag]['timestamp'].dt.weekday
    
    rec_index = np.asarray(tags_dfs[tag].index.tolist())
    tag_df_nrow = tags_dfs[tag].shape[0]
    
    for row in tags_dfs[tag][1:].itertuples():
        
        if row.weekday < 6:
            print(tag + ' - ', row.Index, f' / {tag_df_nrow}', '\n')
        
            if (row.time_diff > pd.Timedelta(minutes = 10)) and (not math.isnan(tags_dfs[tag].iloc[np.where(rec_index == row.Index)[0].item() - 1, 1])):
                
                eps = row.time_diff
                val = tags_dfs[tag].iloc[np.where(rec_index == row.Index)[0].item() - 1, 1]
                
                while eps > pd.Timedelta(minutes = 10):
                                    
                    new_ts = tags_dfs[tag].iloc[np.where(rec_index == row.Index)[0].item() - 1, 0] + pd.Timedelta(minutes = 10)
                    new_timediff = new_ts - tags_dfs[tag].iloc[np.where(rec_index == row.Index)[0].item() - 1, 0]
                    new_weekday = new_ts.dayofweek
                    new_rec = pd.DataFrame({'timestamp' : [new_ts], 'value' : [val], 'time_diff' : [new_timediff], 'weekday' : new_weekday})
                                    
                    tags_dfs[tag] = pd.concat([tags_dfs[tag][:(np.where(rec_index == row.Index)[0].item())], new_rec, tags_dfs[tag][(np.where(rec_index == row.Index)[0].item()):]])
                    rec_index = np.asarray(tags_dfs[tag].index.tolist())
                    
                    eps = row.timestamp - new_rec.loc[0,'timestamp']

    
    tags_dfs[tag] = tags_dfs[tag].reset_index(drop = True).drop(columns = ['time_diff', 'weekday'])
    # temp.to_csv('./Reformated tags/VDR.VDR.LVC3.V62003.{}_R.csv'.format(tag), header = True, index = False)
    

del tag, rec_index, tag_df_nrow, row, eps, val, new_ts, new_timediff, new_weekday, new_rec 
    
#%%
#with open('./Curing/tags_dataframes_cleaned_1.pkl', 'wb') as f:
#    pickle.dump(tags_dfs, f, protocol = pickle.HIGHEST_PROTOCOL)


