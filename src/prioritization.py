import numpy as np
from collections import deque
import pandas as pd
from datetime import datetime, timedelta

#%%


def assign_priority(test_timestamp, test_run_history, We, Wf, is_new):
    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
    Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status == 'FAIL')
    We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    if is_new or We_cond or Wf_cond:
        # print('test True')
        return 1
    return 2
    
def window_based_prioritization(post_queue, test_run_history,existing_tests, We, Wf, is_new):
    priority = []
    for test_suite in post_queue.test_suite:
        
        if test_suite in  existing_tests:
            is_new = Fasle
            priority
            
        else:
            is_new = True
            priority.append(1)
            
    pass


def run_window_based_prioritization(test_timestamp,
                                dataset,
                                test_run_history: pd.DataFrame,
                                We,
                                Wf,
                                Wp,
                                is_new):
    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
    Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status == 'FAIL')
    We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0


    # start time stamp
    test_time_str = dataset.iloc[0, :]['job_start_time']
    test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')
    post_queue_timestamp = test_timestamp
    
    # accumulated_timestamp = 
    existing_tests = set()
    test_run_history = pd.DataFrame([])

    for test_ind in range(dataset.shape[0]):
        test_row = dataset.iloc[test_ind, :]
        test_name = test_row.test_suite
        test_timestamp = test_row.index
        # print(f'test name:{test_name}')

        test_time_str = dataset.iloc[test_ind, :]['job_start_time']
        test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')

        if test_timestamp >= post_queue_timestamp: # trigger condition
            post_queue_timestamp = test_timestamp+timedelta(hours=Wp)
            post_queue = dataset.loc[test_timestamp:post_queue_timestamp]
            sorted_test_suites = window_based_prioritization(post_queue, test_run_history,existing_tests, We, Wf, is_new)
            
            test_run_history = test_run_history.append(sorted_test_suites)
        
            
            
        
            
            


        post_queue_timestamp = current_timestamp + timedelta(hours=Wp)
        post_queue =

    return 1

#%%
data_dir = Path(r'C:\Users\hyu\Documents\Nutstore\Abroad2020\LOG6703')
rails_data_file = 'cleaned_dataset_rail_100000_new_noindex.csv'
df = pd.read_csv(data_dir / rails_data_file, sep=';')
df1 = df.set_index('job_start_time')
df1.index = pd.DatetimeIndex(df1.index)
