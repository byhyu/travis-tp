from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Union
from tqdm import tqdm

def update_unnecessary_patterns(all_tests_history):
    unnecessary_patterns = pd.DataFrame([])
    for name, group in all_tests_history.groupby(['test_suite','job_env']):
        if (group['build_status'] == "passed").all():
            pattern_df = pd.DataFrame([[name[0],name[1],'none']], 
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)
            
    for name, group in all_tests_history.groupby(['test_suite','job_rvm']):
        if (group['build_status'] == "failed").all():
            pattern_df = pd.DataFrame([[name[0],'none', name[1]]], 
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)
    
    #print("patterns update 之后的size: ", len(unnecessary_patterns))
    return unnecessary_patterns.drop_duplicates()

def is_test_necessary(test_suite, unnecessary_patterns):
    #df = unnecessary_patterns
    if unnecessary_patterns.empty:
        return True
    
    test_name = test_suite['test_suite']
    job_env = test_suite['job_env']
    job_rvm = test_suite['job_rvm']
    
    if not unnecessary_patterns[(unnecessary_patterns['test_suite'] == test_name) & (unnecessary_patterns['job_env'] == job_env)].empty:
        return False
    
    if not unnecessary_patterns[(unnecessary_patterns['test_suite'] == test_name) & (unnecessary_patterns['job_rvm'] == job_rvm)].empty:
        return False
   
    return True


def window_based_test_selection(test_timestamp:datetime,
                                test_run_history:pd.DataFrame,
                                We:Union[int, float],
                                Wf:Union[int, float],
                                is_new:bool):
    """
    Implementation of test selection algorithm reported in 2014 paper.
    Args:
        test_timestamp: test timestamp from test dataset DataFrame, df['job_start_time']
        test_run_history:
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
        is_new: Boolean, is the current test suite new?
    Returns:
        Boolean. Test case selected or not.
    """
    
    if is_new:
        return True
    
    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
    Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status=='FAIL')
    We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    if We_cond or Wf_cond:
        return True
    return False


def run_window_based_test_selection(dataset:pd.DataFrame, 
                                    We:Union[int, float], 
                                    Wf:Union[int, float],
                                    Wt:Union[int, float]):
    """
    Args:
        test_suite_inds: index of test cases, for example [0,1,2,3,4,5,6]
        dataset: test data in pandas.DataFrame
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
    Returns:
    """
    count = 0
    existing_tests = set()
    unnecessary_patterns = pd.DataFrame([])
    
    test_selection = []
    accumulated_runtime = 0
    all_tests_history = pd.DataFrame([])
    tag_time = dataset.loc[0, 'test_suite_start time']
    #print("tag_time:    ",  tag_time)
    
    for index, row in dataset.iterrows():
        test_name = row['test_suite']
        test_timestamp = row['test_suite_start time']
        #print("test_timestamp: ",test_timestamp)
        is_nece = is_test_necessary(row, unnecessary_patterns)
        #is_nece = True
        if is_nece:
            if test_name in existing_tests:
                is_new = False
                test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
                to_run_test = window_based_test_selection(row['test_suite_start time'], test_history, We, Wf, is_new)
            else:
                to_run_test = True
                existing_tests.add(test_name)
            
            if to_run_test:
                #accumulated_runtime += test_row.build_duration
                test_name = row['test_suite']
                build_status = row.build_status
                exec_time = row.test_suite_duration
                job_env = row.job_env
                job_rvm = row.job_rvm
                
                test_df = pd.DataFrame(index=[test_timestamp],
                                       data={'test_suite': [test_name], 
                                             'job_env': [job_env],
                                             'job_rvm': [job_rvm],
                                             'build_status': [build_status],
                                             'exec_time': exec_time
                                             })
                test_df.sort_index(inplace=True)
                all_tests_history = all_tests_history.append(test_df) 
                #print("=========================================================")
                #print(all_tests_history.head(1))
                
                # check if we need to tag the dataset based on GEM and ruby version in the Wt window
                if test_timestamp >= tag_time:
                    
                    unnecessary_patterns = update_unnecessary_patterns(all_tests_history)
                    tag_time = tag_time + timedelta(hours=Wt)
                    #print("new tag_time  : ", tag_time)
        else:
            count = count + 1
    print("count = ", count)
    return all_tests_history


if __name__ == '__main__':
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    df['test_suite_start time'] = pd.to_datetime(df['test_suite_start time']) #将数据类型转换为日期类型
    df.sort_values('test_suite_start time', inplace=True)
    #df = df.head(1000) # 112
    #df = df.head(10000) # 791
    #df = df.head(1000)
    df = df.head(2000) # 645
    df = df.head(1000) # 645
    
    all_tests_history = run_window_based_test_selection(df, We=24, Wf=48, Wt=0)
    print(all_tests_history.shape)
