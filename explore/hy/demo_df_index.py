# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 18:14:08 2020

@author: hyu
"""
#%%
from pathlib import Path
import pandas as pd


data_dir = Path(r'C:\Users\hyu\Documents\Nutstore\Abroad2020\LOG6703')
rails_data_file = 'cleaned_dataset_rail_100000_new_noindex.csv'
df = pd.read_csv(data_dir / rails_data_file, sep=';')

#%%
df.set_index('job_start_time',inplace=True)
#%%
df.reset_index(inplace=True)

#%%
test_row = df.iloc[0, :]
#%%
test_timestamp_str = test_row['job_start_time']
test_name = test_row['test_suite']
build_status = test_row['build_status']
exec_time = test_row['build_duration']
#%%
test_df = pd.DataFrame([[test_timestamp_str, test_name,build_status,exec_time]])
#%%
test_df  = pd.DataFrame(index=[test_timestamp_str],
                                   data={'test_suite': [test_name], 'build_status': [build_status],
                                         'exec_time': exec_time})

#%%
test_names = df.test_suite.values[0:5]
build_status_list = df.build_status.values[0:5]
exec_times = df.build_duration.values[0:5]

from datetime import datetime
ts1 = datetime(2020,1,1,1,0,0)
ts2 = datetime(2020,1,1,1,1,0)
ts3 = datetime(2020,1,1,1,2,0)
ts4 = datetime(2020,1,1,1,3,0)
ts5 = datetime(2020,1,1,1,4,0)

#%%
df1 = pd.DataFrame(data={'test_suite': test_names, 'build_status': build_status_list,
                                         'exec_time': exec_times},
                   index=[ts1,ts2,ts3,ts4,ts5])

#%%
# df.sort_values('job_start_time', inplace=True)
# all_tests_history = run_window_based_test_selection(list(range(df.shape[0])), df, We=24, Wf=48)
# all_tests_history = run_window_based_test_selection(list(range(5000)), df, We=24, Wf=48)
# print(all_tests_history.shape)
