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

def run_window_based_test_prioritization(wp_dataset:pd.DataFrame, 
                                         all_tests_history: pd.DataFrame,
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
    existing_tests = set()
    accumulated_runtime = 0
    all_tests_history = pd.DataFrame([])
    
    prioritized_tests = pd.DataFrame([])
    non_prioritized_tests = pd.DataFrame([])
    
    for index, row in tqdm(wp_dataset.iterrows()):
        test_name = row['test_suite']

        test_timestamp = row['job_start_time']

        if test_name in existing_tests:
            is_new = False
            # 第一次执行时判断all_tests_history空
            if len(all_tests_history) == 0:
                break
            test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
            is_test_prioritized = is_prioritized(test_timestamp, test_history, We, Wf, is_new)
        else:
            is_test_prioritized = True
            existing_tests.add(test_name)
        
        if is_test_prioritized:
            build_status = row['build_status']
            exec_time = row['test_suite_duration']
            test_df = pd.DataFrame(index=[test_timestamp],
                                   data={'test_suite': [test_name], 'build_status': [build_status],'exec_time': exec_time})
            test_df.sort_index(inplace=True)

            prioritized_tests = prioritized_tests.append(test_df)
            all_tests_history = all_tests_history.append(test_df)
        else:
            non_prioritized_tests = non_prioritized_tests.append(test_df)
        
    return pd.concat([all_tests_history, non_prioritized_tests], keys=['x','y'])


def split_dataset_into_wp(df:pd.DataFrame,
                          We:Union[int, float], 
                          Wf:Union[int, float],
                          Wp:Union[int, float]):
    
    df['job_start_time'] = pd.to_datetime(df['job_start_time']) #将数据类型转换为日期类型
    df = df.set_index('job_start_time', drop=False)
    df = df.sort_index()
    
    all_tests_history = pd.DataFrame([])
    
    #postqueue_start_time = datetime.strptime(df.iloc[0, :]['job_start_time'], '%Y-%m-%d %H:%M:%S.%f')
    postqueue_start_time = df.iloc[0, :]['job_start_time']
    #postqueue_end_time = datetime.strptime(df.iloc[len(df)-1, :]['job_start_time'], '%Y-%m-%d %H:%M:%S.%f')
    postqueue_end_time = df.iloc[len(df)-1, :]['job_start_time']
    while postqueue_start_time < postqueue_end_time:
        #print("in split")
        postqueue_next_start_time = postqueue_start_time + timedelta(hours=Wp)
        wp_dataset = df[postqueue_start_time:postqueue_next_start_time]  
        #print("wp size: ",wp_dataset.shape[0])
        processed_tests_history = run_window_based_test_prioritization(wp_dataset, all_tests_history, We=24, Wf=48)
        #print("优化后 size: ", processed_tests_history.shape[0], "    type: ", type(processed_tests_history))
        all_tests_history = all_tests_history.append(processed_tests_history)
        #print("所有执行历史 size: ",all_tests_history.shape[0])
        postqueue_start_time = postqueue_next_start_time
    return all_tests_history # 按优先窗口调整的dataframe
    
    
if __name__ == '__main__':
    
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    
    all_tests_history = split_dataset_into_wp(df, We=24, Wf=48, Wp=12)
    print(all_tests_history.shape[0])

    #%%
    from metrics import calc_APFD
    # APFD before prioritization
    failed_tests_before = df.index[df['build_status'] == 'failed'].tolist()
    APFD_before = calc_APFD(list(range(df.shape[0])), failed_tests_before)


    new_df = all_tests_history.reset_index() # change datetime index into integer index
    failed_tests = new_df.index[new_df['build_status'] == 'failed'].tolist()
    print(failed_tests)
    APFD_after = calc_APFD(list(range(new_df.shape[0])), failed_tests)
    print(f'APFD before: {APFD_before}')
    print(f'APFD after:{APFD_after}')
    
