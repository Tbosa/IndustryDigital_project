import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor

# %%

##
def stepw_VIF_filtering(X_exp_df, thresh):
    
    print(X_exp_df.shape[1])
    col_names = list(X_exp_df.columns)
    vif_init_df = pd.DataFrame(np.repeat(0, len(col_names)), columns = ['vif'], index = col_names)
    
    for var in range(len(col_names)):
        vif_var = variance_inflation_factor(np.asarray(X_exp_df), var)
        vif_init_df.loc[col_names[var], ['vif']] = vif_var
        
    vifmax_init = vif_init_df.loc[vif_init_df['vif'] == vif_init_df['vif'].max(),:]
    vifmaxval = vifmax_init['vif'].values[0]
    print(vifmaxval, '\n')
    
    if (vifmaxval < thresh):
        print(f"All initial variables have VIF < {thresh} - VIF max : {vifmax_init.index[0]} -> {vifmaxval}", '\n')
        return col_names
    
    else:
        
        X_exp_df = X_exp_df.drop(columns = vifmax_init.index[0])
        print(f"Initial variable removed : {vifmax_init.index[0]}", '\n')
        
        while (vifmaxval >= thresh):
            print(X_exp_df.shape[1])
            col_names = list(X_exp_df.columns)
            vif_vals_df = pd.DataFrame(np.repeat(0, len(col_names)), columns = ['vif'], index = col_names)
            
            for var in range(len(col_names)):
                vif_var = variance_inflation_factor(np.asarray(X_exp_df), var)
                vif_vals_df.loc[col_names[var], ['vif']] = vif_var
            print(vif_vals_df)
            vifmax_vals = vif_vals_df.loc[vif_vals_df['vif'] == vif_vals_df['vif'].max(),:]
            vifmaxval = vifmax_vals['vif'].values[0]
            
            if (vifmaxval < thresh):
                break
            
            X_exp_df = X_exp_df.drop(columns = vifmax_vals.index[0])
            print(f"Variable removed : {vifmax_vals.index[0]} - VIF = {vifmaxval}", '\n')
            
        
        return(list(X_exp_df.columns))