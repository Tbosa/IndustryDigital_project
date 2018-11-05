#%%
scripts_dir = 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Python scripts'
import sys
import os
from math import sqrt
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import pandas as pd

from statsmodels.stats.outliers_influence import variance_inflation_factor

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.linear_model import Ridge, RidgeCV, Lasso, LassoCV, ElasticNet, ElasticNetCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer, mean_absolute_error, mean_squared_error

from sklearn.externals import joblib
import pickle

os.chdir(scripts_dir)
from stepwise_VIF import stepw_VIF_filtering
# %%
data_dir = 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Data/Final tables'
apptest_data_dir = 'C:/Users/barbosaa01/Desktop/Thèse pro - A. Barbosa/Trained models/AppTest data/'
os.chdir(data_dir)
print(os.getcwd())

# %%
df = pd.read_csv('./final_table_new.csv', sep = ';', header = 0, dtype = {'workorder' : str, 'material_cur' : str, 'batch_cur' : str,
'batch_mix' : str, 'box' : str, 'box sequence number' : str, 'maturation_time' : np.float64})

print(df.head(n=3).iloc[:,:5])
df.info() # n = 1260 | p = 143

X = df.iloc[:,6:123] # p = 117
print(X.head(n = 3).iloc[:,[0, X.shape[1] - 1]])

#######################

Y = df.loc[:,['Allgt_avg', 'cont_100_avg', 'cont_rupt_avg', 'durete_avg']]
Y['Allgt_avg'] = Y['Allgt_avg'].astype(np.int64)
Y['durete_avg'] = Y['durete_avg'].astype(np.int64)

print(Y.dtypes.value_counts())
print(Y.head(n = 3))

#######################

Y_corr_mx = Y.corr('pearson')
plt.matshow(Y_corr_mx)
plt.colorbar()
plt.xticks(range(len(list(Y.columns))), list(Y.columns), rotation = 'vertical', fontsize = 8, alpha = 1)
plt.yticks(range(len(list(Y.columns))), list(Y.columns), fontsize = 8.5)
#%%
# Standardisation des variables explicatives tq var(X_i) = 1, pour tout i = 1..p, et isoler la variance intrinsèque de X_i et non-influencé par l'unité de mesure.
# Filtrage des variables exp : suppression des var exp par approche "stepwise VIF"
sc_1 = StandardScaler()
X_scaled = pd.DataFrame(sc_1.fit_transform(X), columns = X.columns)

cols_to_keep = stepw_VIF_filtering(X_exp_df = X_scaled, thresh = 20)
print(len(cols_to_keep)) # p = 69

X = X[cols_to_keep]
D = pd.concat([X, Y], axis = 1)
# X_sub.to_csv('./final_table_newsub.csv', sep = ';', index = False)

#%%
# Etape de stat des sur Y (tableau)
# Représentations graphiques des distributions des DVs par histogramme et estimateur à noyau gaussien de la densité
fig, axs = plt.subplots(nrows = 2, ncols = 2, subplot_kw = {'ylabel' : 'density (g-ker)'})
fig.suptitle('DVs distribution - density functions')
axs = axs.ravel()
specs = {'Allgt_avg' : [245, 480], 'cont_100_avg' : [2.7, 4.7], 'cont_rupt_avg' : [7, 20], 'durete_avg' : [65, 70]}

des_stat_df = Y['Allgt_avg'].describe()
for y in range(len(Y.columns)):
    
    if y < 3:
        des_stat_df = pd.concat([des_stat_df, Y.iloc[:, y+1].describe()], axis = 1)
    unk_values = Y.iloc[:, y].nunique()
    if unk_values > 25:
        nbines = 25
    
    axs[y].set_xlim(specs[Y.columns[y]][0], specs[Y.columns[y]][1])
    sb.distplot(Y.iloc[:, y], bins = nbines, kde = True, hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 4},
                axlabel = f"{Y.columns[y]} values", ax = axs[y])  

print(des_stat_df.iloc[1:,])

del specs, nbines, unk_values, y, axs
# %%
apptest_ds_dict = {i:{} for i in Y.columns}
for target in D.columns[-4:]:
    print(target)
    X_train, X_test, y_train, y_test = train_test_split(D.iloc[:,:-4], D[target], test_size = 0.2, random_state = 1) # random_state = 1 => même découpage app/test entre les 4 DVs.
    apptest_ds_dict[target]['train_set'] = pd.concat([X_train, y_train], axis = 1)
    apptest_ds_dict[target]['test_set'] = pd.concat([X_test, y_test], axis = 1)


del target, X_train, X_test, y_train, y_test
# %%
# perfs_df = pd.DataFrame(np.array([np.repeat(0, 4)]*4), index = Y.columns, columns = ['Ridge', 'Lasso', 'EN', 'RF'])
best_rf_models_dict = {i:{} for i in Y.columns}

for target in Y.columns:
    
    print(target, '\n')
    
    D = apptest_ds_dict[target]['train_set']
    X_train = D.drop(columns = [target])
    y_train = D[target]

    # Best RF model selection using grid search 5-fold CV strategy - hyperparameters tuned :
    # nb of decision trees, max nb of candidate features for best split, max nb of splits for a tree (max_depth)
    rf_reg = RandomForestRegressor(criterion = 'mse', bootstrap = True, oob_score = False, n_jobs = -1)
    par_grid = {'n_estimators' : [10, 100, 500, 1000, 5000], 'max_features' : ['auto', 'sqrt', 'log2', 25, 50], 'max_depth' : [5, 10, 15, 25]}

    # mse_scorer = make_scorer(mean_squared_error)
    grid_cv = GridSearchCV(rf_reg, param_grid = par_grid, n_jobs = -1, cv = 5, verbose = 2)
    grid_cv.fit(X_train, y_train)
    print(f"{target} - Best RF config : ", '\n', grid_cv.best_params_, '\n')
    print(f"{target} - Best R² goodness-of-fit : ", grid_cv.best_score_, '\n')  
            
    # Final RF model built with optimal hyperparameter values computed by grid search 5-fold CV :
    rf_reg_model = RandomForestRegressor(n_estimators = grid_cv.best_params_['n_estimators'], criterion = "mse", max_depth = grid_cv.best_params_['max_depth'],
                                         max_features = grid_cv.best_params_['max_features'], bootstrap = True, oob_score = True)
    rf_reg_model.fit(X_train, y_train)
    
    print(f"{target} - best rf model - OOB R² : ", round(rf_reg_model.oob_score_, 3))
    OOB_rmse = round(sqrt(mean_squared_error(y_train, rf_reg_model.oob_prediction_)), 3)
    print(f"{target} - best rf model - OOB RMSE : ", OOB_rmse, '\n')
     
    featImp_df = pd.DataFrame(rf_reg_model.feature_importances_, index = X_train.columns, columns = ['Importance']).sort_values('Importance', ascending = False)
    print(featImp_df)
     
    best_rf_models_dict[target]['final_model'] = rf_reg_model
    best_rf_models_dict[target]['VarImp_df'] = featImp_df
    best_rf_models_dict[target]['Mean 5-fold CV R² - OOB rmse'] = [round(grid_cv.best_score_, 3), OOB_rmse]
    

del  target, D, X_train, y_train, rf_reg, par_grid, grid_cv, rf_reg_model, OOB_rmse

##########
best_rf_submodels_dict = {i:{} for i in Y.columns}

# best_rf_models_dict
for target in Y.columns:

    print(target)
    
    Dapp = apptest_ds_dict[target]['train_set']
    Dtest = apptest_ds_dict[target]['test_set']
    X_train = Dapp.drop(columns = [target])
    X_test = Dtest.drop(columns = [target])
    y_train = Dapp[target]
    y_test = Dtest[target]
    
    R_squared_max = float('-inf')
    perf_by_q_df = pd.DataFrame(np.ones((4,2)), index = [5, 10, 15, 20], columns = ['R-squared', 'OOB_RMSE'])
    
    for q in [5, 10, 15, 20]:

        print(q, '\n')
        
        selected_features = list(best_rf_models_dict[target]['VarImp_df'].index[:q])
        X_train_sub = X_train[selected_features]
        
        print(X_train_sub.head(n = 3), '\n')
        
        rf_reg = RandomForestRegressor(criterion = 'mse', bootstrap = True, oob_score = True, n_jobs = -1)
        
        par_grid = {'n_estimators' : [10, 100, 500, 1000], 'max_features' : ['auto', 'sqrt'], 'max_depth' : [5, 10]}
        grid_cv = GridSearchCV(rf_reg, param_grid = par_grid, n_jobs = -1, cv = 5, verbose = 2)
        grid_cv.fit(X_train_sub, y_train)
        
        print(f"{target} - First {q} important variables - best rf sub-model config : {grid_cv.best_params_}", '\n')
        print(f"{target} - First {q} important variables - best rf sub-model R-squared score : {grid_cv.best_score_}", '\n')
        
        OOB_RMSE = round(sqrt(mean_squared_error(y_train, grid_cv.best_estimator_.oob_prediction_)), 3)
        
        print(f"{target} - First {q} important variables - best rf sub-model OOB_RMSE : {OOB_RMSE}", '\n')
        
        perf_by_q_df.loc[q, ['R-squared']] = round(grid_cv.best_score_, 3)
        perf_by_q_df.loc[q, ['OOB_RMSE']] = OOB_RMSE
        
        print(perf_by_q_df, '\n')
        
        if (grid_cv.best_score_ > R_squared_max):
            R_squared_max = grid_cv.best_score_
            best_submodel_est = grid_cv.best_estimator_
            best_feat_nb = q
            best_features = selected_features
            print('True', '\n')          
    
    # test performance - RMSE
    y_pred = best_submodel_est.predict(X_test[best_features])
    RMSE = np.sqrt(mean_squared_error(np.asarray(y_test), y_pred))
    
    # Features importance list
    # featImp_df = pd.DataFrame(best_submodel_est.feature_importances_, index = X_train[best_features].columns,
    #                          columns = ['Importance']).sort_values('Importance', ascending = False)

    best_rf_submodels_dict[target]['best_model'] = best_submodel_est
    best_rf_submodels_dict[target]['features_nb'] = [best_feat_nb, best_features]
    best_rf_submodels_dict[target]['CV R-squared mean / features_nb'] = RMSE
    

del Dapp, Dtest, X_train, X_train_sub, X_test, y_train, y_test, R_squared_max, selected_features, par_grid, y_pred, RMSE, q, target, best_feat_nb
#%%
# Saving 4 best submodels
os.chdir('C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Curing model/Global py objects/')
os.getcwd()

pickle.dump(best_rf_models_dict, open("best_rf_models.pkl", 'wb'), pickle.HIGHEST_PROTOCOL)
pickle.dump(best_rf_submodels_dict, open("best_rf_submodels.pkl", 'wb'), pickle.HIGHEST_PROTOCOL)

#%%
# Diagrammes en barres illustrant l'importance des variables explicatives dans la construction des 4 modèles RF réduits.
# -> Critère de mesure : décroissance moyenne du MSE sur l'ensemble des splits. Capacité globale de la variable à engendrer des noeuds pures au sens du MSE, et
# à influer sur les chemins de prédictions des arbres de décision. 

VI_1 = pd.DataFrame(best_rf_submodels_dict['Allgt_avg']['best_model'].feature_importances_, index = best_rf_submodels_dict['Allgt_avg']['features_nb'][1],
                    columns = ['Importance']).sort_values(by = 'Importance', ascending = False)
VI_2 = pd.DataFrame(best_rf_submodels_dict['cont_100_avg']['best_model'].feature_importances_, index = best_rf_submodels_dict['cont_100_avg']['features_nb'][1],
                   columns = ['Importance']).sort_values(by = 'Importance', ascending = False)
VI_3 = pd.DataFrame(best_rf_submodels_dict['cont_rupt_avg']['best_model'].feature_importances_, index = best_rf_submodels_dict['cont_rupt_avg']['features_nb'][1],
                    columns = ['Importance']).sort_values(by = 'Importance', ascending = False)
VI_4 = pd.DataFrame(best_rf_submodels_dict['durete_avg']['best_model'].feature_importances_, index = best_rf_submodels_dict['durete_avg']['features_nb'][1],
                    columns = ['Importance']).sort_values(by = 'Importance', ascending = False)

fig, ax = plt.subplots(subplot_kw = {'ylabel' : 'Mean MSE decrease'})
ax.bar(range(len(VI_1.index)), VI_1['Importance'].values)
plt.xticks(range(len(VI_1.index)), VI_1.index, rotation = 90)
plt.tick_params(axis = 'x', labelsize = 8)
plt.title('Variable importance - Allg_avg')

plt.bar(range(len(VI_2.index)), VI_2['Importance'].values)
plt.xticks(range(len(VI_2.index)), VI_2.index, rotation = 90)
plt.tick_params(axis = 'x', labelsize = 8)
plt.title('Variable importance - Cont_100_avg')

plt.bar(range(len(VI_3.index)), VI_3['Importance'].values)
plt.xticks(range(len(VI_3.index)), VI_3.index, rotation = 90)
plt.tick_params(axis = 'x', labelsize = 8)
plt.title('Variable importance - Cont_rupt_avg')

plt.bar(range(len(VI_4.index)), VI_4['Importance'].values)
plt.xticks(range(len(VI_4.index)), VI_4.index, rotation = 90)
plt.tick_params(axis = 'x', labelsize = 8)
plt.title('Variable importance - durete_avg')  

#%%

######  RIDGE / LASSO / ELASTIC NET  ######
best_lasso_models = {i:{} for i in Y.columns}
best_ridge_models = {i:{} for i in Y.columns}

ridge_alphas = np.array([1e-6, 1e-4, 0.001, 0.01, 0.1] +  list(np.arange(0.1, 1, 0.05)) + list(np.arange(1,50)) + list([100, 1000]))

for target in Y.columns:
    print(target, '\n')

    ###### LASSO model ######
    print('Lasso model', '\n')
    Dapp = apptest_ds_dict[target]['train_set']
    Dtest = apptest_ds_dict[target]['test_set']
    feature_names = list(Dapp.columns[:-1])
    
    Dapp_sc = StandardScaler(with_mean = True, with_std = True).fit(Dapp)
    
    Dapp = Dapp_sc.transform(Dapp)
    X_train = Dapp[:,:-1]
    y_train = Dapp[:,-1:].ravel()
    
    Dtest = Dapp_sc.transform(Dtest)
    X_test = Dtest[:,:-1]
    y_test = Dtest[:,-1:].ravel()
    
    lasso_cv_obj = LassoCV(eps = 1e-3, n_alphas = 100, fit_intercept = False, cv = 5, n_jobs = -1) # standardized data => beta0 = E[Y] = 0
    lasso_cv_obj.fit(X_train, y_train)
    
    lasso_coef_df = pd.DataFrame(lasso_cv_obj.coef_, index = feature_names, columns = ['coef_value']).sort_values(by = 'coef_value', ascending = False)
    lasso_coef_df = lasso_coef_df.loc[(lasso_coef_df['coef_value'] != 0), :]
    
    print(f'Best alpha : {lasso_cv_obj.alpha_}')
    print(f'Nb of non-zero coefficients : {lasso_coef_df.shape[0]} / {X_train.shape[1]}', '\n')
    
    y_pred = lasso_cv_obj.predict(X_test)
    RMSE_test = sqrt(mean_squared_error(y_test, y_pred))
    print(f'Eval - RMSE on test set : {RMSE_test}', '\n')
    
    best_lasso_models[target]['best_model'] = lasso_cv_obj
    best_lasso_models[target]['alpha'] = lasso_cv_obj.alpha_
    best_lasso_models[target]['coef_values'] = lasso_coef_df
    best_lasso_models[target]['RMSE - test_set'] = round(RMSE_test, 3)
    
    ###### Ridge model ######
    print('Ridge model', '\n')
    
    X_train, X_test, y_train, y_test = train_test_split(X, Y[target], test_size = 0.2, random_state = 1)
    Dapp = pd.concat([X_train, y_train], axis = 1)
    Dtest = pd.concat([X_test, y_test], axis = 1)    
    
    Dapp_sc = StandardScaler(with_mean = True, with_std = True).fit(Dapp)
    
    Dapp = Dapp_sc.transform(Dapp)
    X_train = Dapp[:,:-1]
    y_train = Dapp[:,-1:].ravel()
    
    Dtest = Dapp_sc.transform(Dtest)
    X_test = Dtest[:,:-1]
    y_test = Dtest[:,-1:].ravel()
    
    ridge_cv_obj = RidgeCV(alphas = ridge_alphas, fit_intercept = False, gcv_mode = 'svd', store_cv_values = True)
    ridge_cv_obj.fit(X_train, y_train)
    
    print(f'Best alpha : {ridge_cv_obj.alpha_}')
    y_pred = ridge_cv_obj.predict(X_test)
    RMSE_test = sqrt(mean_squared_error(y_test, y_pred))
    print(f'Eval - RMSE on test set : {RMSE_test}', '\n')
    
    best_ridge_models[target]['best_model'] = ridge_cv_obj
    best_ridge_models[target]['alpha'] = ridge_cv_obj.alpha_
    best_ridge_models[target]['RMSE - test_set'] = round(RMSE_test, 3)
    
     
del target, Dapp, Dtest, feature_names, Dapp_sc, X_train, X_test, y_train, y_test, lasso_cv_obj, ridge_cv_obj, y_pred, RMSE_test
# %%
# Dapp / Dtest for MMR
Dapp = pd.concat([apptest_ds_dict['Allgt_avg']['train_set'], apptest_ds_dict['cont_100_avg']['train_set'].loc[:,['cont_100_avg']],
                 apptest_ds_dict['cont_rupt_avg']['train_set'].loc[:,['cont_rupt_avg']], apptest_ds_dict['durete_avg']['train_set'].loc[:,['durete_avg']]], axis = 1)
Dtest = pd.concat([apptest_ds_dict['Allgt_avg']['test_set'], apptest_ds_dict['cont_100_avg']['test_set'].loc[:,['cont_100_avg']],
                 apptest_ds_dict['cont_rupt_avg']['test_set'].loc[:,['cont_rupt_avg']], apptest_ds_dict['durete_avg']['test_set'].loc[:,['durete_avg']]], axis = 1)

Dapp.to_csv('./App-Test datasets/Dapp.csv', sep = ';', index = False)
Dtest.to_csv('./App-Test datasets/Dtest.csv', sep =';', index = False)

#%%
models_path = 'C:/Users/barbosaa01/Documents/Juin 2018/Thesis project/Curing model/Models/random forests'

joblib.dump(best_rf_submodels_dict['Allgt_avg']['best_model'], f"{models_path}/Allgt_final.joblib")
joblib.dump(best_rf_submodels_dict['cont_100_avg']['best_model'], f"{models_path}/Cont100_final.joblib")
joblib.dump(best_rf_submodels_dict['cont_rupt_avg']['best_model'], f"{models_path}/Contrupt_final.joblib")
joblib.dump(best_rf_submodels_dict['durete_avg']['best_model'], f"{models_path}/Durete_final.joblib")