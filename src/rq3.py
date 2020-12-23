from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Union
from tqdm import tqdm

def is_prioritized(test_timestamp:datetime,
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
        Wp: Prioritizaion window in hours, refer to 2014 paper for details
        is_new: Boolean, is the current test suite new?
    Returns:
        Boolean. Test case selected or not.
    """
    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
    Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status=='FAIL')
    We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    if is_new or We_cond or Wf_cond:
        return True
    return False

def run_window_based_test_prioritization(test_suite_inds:List, 
                                         dataset:pd.DataFrame, 
                                         We:Union[int, float], 
                                         Wf:Union[int, float],
                                         Wp:Union[int, float]):
    """
    Args:
        test_suite_inds: index of test cases, for example [0,1,2,3,4,5,6]
        dataset: test data in pandas.DataFrame
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
        Wp: Prioritizaion window in hours, refer to 2014 paper for details
    Returns:
    """

    dataset.sort_values('test_suite_start time', inplace=True)
    existing_tests = set()
    accumulated_runtime = 0
    all_tests_history = pd.DataFrame([])
    
    prioritized_tests = pd.DataFrame([])
    non_prioritized_tests = pd.DataFrame([])
    
    for test_ind in tqdm(test_suite_inds):
        test_row = dataset.iloc[test_ind, :]
        test_name = test_row.test_suite
        # print(f'test name:{test_name}')

        test_time_str = dataset.iloc[test_ind, :]['job_start_time']
        test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')

        if test_name in existing_tests:
            is_new = False
            test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
            is_test_prioritized = is_prioritized(test_timestamp, test_history, We, Wf, Wp)
        else:
            is_test_prioritized = True
            existing_tests.add(test_name)
        
        if is_test_prioritized:
            build_status = test_row.build_status
            exec_time = test_row.test_suite_duration
            test_df = pd.DataFrame(index=[test_timestamp],
                                   data={'test_suite': [test_name], 'build_status': [build_status],
                                         'exec_time': exec_time})
            test_df.sort_index(inplace=True)

            prioritized_tests = prioritized_tests.append(test_df)
            all_tests_history = all_tests_history.append(test_df)
        else:
            non_prioritized_tests = non_prioritized_tests.append(test_df)
        
    return pd.concat([all_tests_history, non_prioritized_tests], keys=['x','y'])


def split_dataset_into_wp(test_suite_inds:List, 
                          df:pd.DataFrame,
                          We:Union[int, float], 
                          Wf:Union[int, float],
                          Wp:Union[int, float]):
    
    df['test_suite_start time'] = pd.to_datetime(df['test_suite_start time']) #将数据类型转换为日期类型
    df = df.set_index('test_suite_start time')
    df = df.sort_index()
    
    all_tests_history = pd.DataFrame([])
    
    postqueue_start_time = datetime.strptime(df.iloc[0, :]['job_start_time'], '%Y-%m-%d %H:%M:%S.%f')
    postqueue_end_time = datetime.strptime(df.iloc[len(df)-1, :]['job_start_time'], '%Y-%m-%d %H:%M:%S.%f')
    while postqueue_start_time < postqueue_end_time:
        print(postqueue_start_time)
        postqueue_next_start_time = postqueue_start_time + timedelta(hours=Wp)
        wp_dataset = df[postqueue_start_time:postqueue_next_start_time]  
        prioritized_tests_history = run_window_based_test_prioritization(list(range(10)), wp_dataset, We=24, Wf=48, Wp=12)
        all_tests_history.append(prioritized_tests_history)
        postqueue_start_time = postqueue_next_start_time
    return all_tests_history
    
    
if __name__ == '__main__':
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    
    all_tests_history = split_dataset_into_wp(list(range(10)), df, We=24, Wf=48, Wp=12)
    print(all_tests_history.shape[0])
    
