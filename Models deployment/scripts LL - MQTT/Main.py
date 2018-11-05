# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 11:32:10 2018

@author: Barbosa.A
"""

import os

import sklearn

path_wdir = 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Curing model'

os.chdir(path_wdir)
os.getcwd()
#%%

# Import 4 trained models

trained_models_dict = {}
for model in os.listdir('Models/random forests/'):

    trained_models_dict[model.split('_')[0]] = sklearn.externals.joblib.load(f"Models/random forests/{model}")

trained_models_dict['Allgt'].get_params()
