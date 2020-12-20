#%%
from pathlib import Path
import pandas as pd
from csv import reader
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

#%%
#%%

data_dir = Path(r'C:\Users\hyu\Documents\Nutstore\Abroad2020\LOG6703')
rails_data_file = 'cleaned_dataset_rail_100000_new_noindex.csv'
df = pd.read_csv(data_dir/rails_data_file, sep=';')
#%%
sub = df[['test_suite','test_suite_start time','test_suite_duration','job_env','job_rvm','build_status']]
res = sub.groupby(['test_suite','job_env','job_rvm'])['build_status'].unique()
#%%
ind =[set(r)==set(['failed']) for r in res]
any(ind)

#%% heatmap
res1 = res[ind]

def get_rule1(df):
    pass


#%%
# len(res) = 3751

## find test and <env, rvm> that always fails
# sub1 = sub.iloc[0:5000]

#%%

