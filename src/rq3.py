from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Union
#from tqdm import tqdm

def update_unnecessary_patterns(all_tests_history):
    unnecessary_patterns = pd.DataFrame([])
    for name, group in all_tests_history.groupby(['test_suite','job_env']):
        if (group['build_status'] == "failed").all():
            pattern_df = pd.DataFrame([[name[0],name[1],'none']], 
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)
            
    for name, group in all_tests_history.groupby(['test_suite','job_rvm']):
        if (group['build_status'] == "failed").all():
            pattern_df = pd.DataFrame([[name[0],'none', name[1]]], 
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)
    
    return unnecessary_patterns#.drop_duplicates()


def prioritize_test(test_row:pd.Series,
                   test_run_history:pd.DataFrame, 
                   existing_tests: set,
                   unnecessary_patterns:pd.DataFrame,
                   We:Union[int, float],
                   Wf:Union[int, float]):
    """
    Implementation of test selection algorithm reported in 2014 paper.
    Args:
        test_timestamp: test timestamp from test dataset DataFrame, df['job_start_time']
        test_run_history:
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
        Wp: Prioritizaion window in hours, refer to 2014 paper for details
        is_new: Boolean, is the current test suite new?
    Returns:
        Boolean. Test case selected or not.
    """
    
    test_name = test_row['test_suite']
    test_timestamp = test_row['test_suite_start_time']
    job_env = test_row['job_env']
    job_rvm = test_row['job_rvm']
    build_status = test_row.build_status
    exec_time = test_row.test_suite_duration
    test_df = pd.DataFrame(index=[test_timestamp],
                           data={'test_suite': [test_name], 
                                 'job_env': [job_env],
                                 'job_rvm': [job_rvm],
                                 'build_status': [build_status],
                                 'exec_time': exec_time,
                                 'priority': [0]
                                })
    
     # check if the test suite follows a certain pattern based on <GEM, rvm>
    if unnecessary_patterns.empty:
        return test_df
    
    job_env = test_row['job_env']
    job_rvm = test_row['job_rvm']
    
    is_pattern1 = not unnecessary_patterns[
        unnecessary_patterns['test_suite'] == test_name].empty #& (unnecessary_patterns['job_env'] == job_env)].empty
    is_pattern2 = not unnecessary_patterns[
        (unnecessary_patterns['test_suite'] == test_name)].empty #& (unnecessary_patterns['job_rvm'] == job_rvm)].empty
    if is_pattern1 or is_pattern2: 
        test_df['priority'] = 1
        return test_df
    
    
    # check if the current test suite is a new comer
    if test_name not in existing_tests:
        test_df['priority'] = 2
        existing_tests.add(test_name)
        return test_df
    
    
    # check the We window and Wf window
    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
     
    if not test_run_history.empty: 
        test_run_history = test_run_history.sort_index()
        
        is_faulty = any(test_run_history[fail_start:test_timestamp].build_status=='failed')
        is_idle = (test_run_history[exec_start:test_timestamp].shape[0] == 0)
        if is_faulty or is_idle: 
            test_df['priority'] = 2
            return test_df
    
    return test_df

def run_window_based_test_prioritization(wp_dataset:pd.DataFrame, 
                                         all_tests_history: pd.DataFrame,
                                         existing_tests: set,
                                         unnecessary_patterns:pd.DataFrame,
                                         We:Union[int, float], 
                                         Wf:Union[int, float]):
    """
    Args:
        test_suite_inds: index of test cases, for example [0,1,2,3,4,5,6]
        dataset: test data in pandas.DataFrame
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
        Wp: Prioritizaion window in hours, refer to 2014 paper for details
    Returns:
    """
    
    #wp_dataset.sort_values('job_start_time', inplace=True)
    
    waiting_queue = pd.DataFrame(columns = ['test_suite', 'job_env','job_rvm','build_status','exec_time','priority'])
    accumulated_runtime = 0
    
    for index, row in wp_dataset.iterrows(): #tqdm(wp_dataset.iterrows()):
        test_name = row['test_suite']
        if(all_tests_history.empty):
            test_history = pd.DataFrame([])
        else:
            test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
        test_df = prioritize_test(row, test_history, existing_tests, unnecessary_patterns, We, Wf)
        test_df.sort_index(inplace=True)
        waiting_queue = waiting_queue.append(test_df)
    
    waiting_queue.sort_values(by='priority', ascending=False, inplace=True) #by priority decending
    return waiting_queue

def split_dataset_into_wp(df:pd.DataFrame,
                          We:Union[int, float], 
                          Wf:Union[int, float],
                          Wp:Union[int, float]):
    
    existing_tests = set()
    all_tests_history = pd.DataFrame([])
    unnecessary_patterns = pd.DataFrame([])
    
    postqueue_start_time = df.iloc[0, :]['test_suite_start_time']
    postqueue_end_time = df.iloc[len(df)-1, :]['test_suite_start_time']
    while postqueue_start_time < postqueue_end_time:
        postqueue_next_start_time = postqueue_start_time + timedelta(hours=Wp)
        wp_dataset = df[postqueue_start_time:postqueue_next_start_time]  
        window_df = run_window_based_test_prioritization(wp_dataset, all_tests_history, existing_tests, unnecessary_patterns, We, Wf)        
        all_tests_history = all_tests_history.append(window_df, ignore_index=False)
        unnecessary_patterns = update_unnecessary_patterns(all_tests_history)
        
        postqueue_start_time = postqueue_next_start_time
    
    return all_tests_history
    
    
if __name__ == '__main__':
    #%%
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    df['test_suite_start_time'] = pd.to_datetime(df['test_suite_start time']) #将数据类型转换为日期类型
    df = df.set_index('test_suite_start_time', drop=False)
    df = df.sort_index()
    df = df.head(10000)
    #%%
    all_tests_history = split_dataset_into_wp(df, We=12, Wf=24, Wp=2)
    
    print(all_tests_history.shape)
    
    print("priority 1: ", all_tests_history.loc[all_tests_history['priority'] == 1])
    
    #%%
    from metrics import calc_APFD
    # APFD before prioritization
    df1 = df.reset_index(drop=True) # calc_APFD 要求 int index， 不是 datetime index
    failed_tests_before = df1.index[df1['build_status'] == 'failed'].tolist()
    APFD_before = calc_APFD(list(range(df1.shape[0])), failed_tests_before)

    new_df = all_tests_history.reset_index() # change datetime index into integer index
    failed_tests = new_df.index[new_df['build_status'] == 'failed'].tolist()
    print(failed_tests)
    APFD_after = calc_APFD(list(range(new_df.shape[0])), failed_tests)
    print(f'APFD before: {APFD_before}')
    print(f'APFD after:{APFD_after}')
