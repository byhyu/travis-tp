import numpy as np
from collections import deque
import pandas as pd
from datetime import datetime, timedelta

#%%


# def assign_priority(test_timestamp, test_run_history, We, Wf, is_new):
#     exec_start = test_timestamp - timedelta(hours=We)
#     fail_start = test_timestamp - timedelta(hours=Wf)
#     Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status == 'FAIL')
#     We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
#     if is_new or We_cond or Wf_cond:
#         # print('test True')
#         return 1
#     return 2
    
# def window_based_prioritization(post_queue, test_run_history,existing_tests, We, Wf, is_new):
#     priority = []
#     for test_suite in post_queue.test_suite:
#
#         if test_suite in  existing_tests:
#             is_new = Fasle
#             priority
#
#         else:
#             is_new = True
#             priority.append(1)
#
#     pass

# def is_prioritized():
#     pass

def calculate_priority(test_timestamp, this_test_history, We, Wf, is_new):
    if (this_test_history is None) or (len(this_test_history) == 0):
        Wf_cond = False
        We_cond = True
    else:
        exec_start = test_timestamp - timedelta(hours=We)
        fail_start = test_timestamp - timedelta(hours=Wf)
        Wf_cond = any(this_test_history[fail_start:test_timestamp].build_status == 'FAIL')
        We_cond = this_test_history[exec_start:test_timestamp].shape[0] == 0
    if is_new or We_cond or Wf_cond:
        # print('test True')
        return 1
    return 2


def _helper(post_queue_df, We, Wf, test_run_history):
    test_timestamp = post_queue_df.index[0]
    # exec_start = test_timestamp - timedelta(hours=We)
    # fail_start = test_timestamp - timedelta(hours=Wf)

    if (test_run_history is None) or (len(test_run_history) == 0) or ('test_suites' not in test_run_history.columns):
        existing_tests = set()
    else:
        existing_tests = set(test_run_history['test_suite'].values)

    high_priority_tests = pd.DataFrame([])
    low_priorty_tests = pd.DataFrame([])

    for i,test_name in enumerate(post_queue_df['test_suite'].values):
        is_new = (test_name in existing_tests)
        if (test_run_history is None) or (len(test_run_history) == 0) or ('test_suites' not in test_run_history.columns):
            test_run_history = None

        if (test_run_history is None ) or (len(test_run_history) == 0):
            this_test_history = None
        else:
            this_test_history = test_run_history[test_run_history['test_suites'] == test_name]

        priority = calculate_priority(test_timestamp, this_test_history, We, Wf, is_new)
        if priority == 1:
            high_priority_tests = high_priority_tests.append(post_queue_df.iloc[i,:])
        else:
            low_priorty_tests= low_priorty_tests.append(post_queue_df.iloc[i,:])
    return high_priority_tests.append(low_priorty_tests)


def run_window_based_prioritization(
                                dataset,
                                # test_run_history: pd.DataFrame,
                                We,
                                Wf,
                                Wp):

    # sort dataset by job start time
    dataset.set_index('job_start_time')
    dataset.index = pd.DatetimeIndex(dataset.index)
    dataset.sort_index(inplace=True)

    end_time = dataset.index[-1]
    test_time = dataset.index[0]
    post_queue_time = test_time + timedelta(hours=Wp)

    test_run_history = pd.DataFrame([])
    existing_tests = set()

    while test_time <= end_time:
        post_queue_time = test_time + timedelta(hours=Wp)
        post_queue_df = dataset.loc[test_time:post_queue_time,:]

        sorted_test_suites = _helper(post_queue_df, We, Wf, test_run_history)
        test_run_history = test_run_history.append(sorted_test_suites)
        test_time = post_queue_time

    return test_run_history
    #
    #
    #
    # exec_start = test_timestamp - timedelta(hours=We)
    # fail_start = test_timestamp - timedelta(hours=Wf)
    # Wf_cond = any(test_run_history[fail_start:test_timestamp].build_status == 'FAIL')
    # We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    #
    #
    #
    #
    # # start time stamp
    # test_time_str = dataset.iloc[0, :]['job_start_time']
    # test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')
    # post_queue_timestamp = test_timestamp
    #
    # # accumulated_timestamp =
    # existing_tests = set()
    # test_run_history = pd.DataFrame([])
    #
    # for test_ind in range(dataset.shape[0]):
    #     test_row = dataset.iloc[test_ind, :]
    #     test_name = test_row.test_suite
    #     test_timestamp = test_row.index
    #     # print(f'test name:{test_name}')
    #
    #     test_time_str = dataset.iloc[test_ind, :]['job_start_time']
    #     test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')
    #     end_timestamp =
    #     while test_timestamp <= end_timestamp
    #
    #     if test_timestamp >= post_queue_timestamp: # trigger condition
    #         post_queue_timestamp = test_timestamp+timedelta(hours=Wp)
    #         post_queue = dataset.loc[test_timestamp:post_queue_timestamp]
    #         sorted_test_suites = window_based_prioritization(post_queue, test_run_history,existing_tests, We, Wf, is_new)
    #
    #         test_run_history = test_run_history.append(sorted_test_suites)
    #
    #     post_queue_timestamp = current_timestamp + timedelta(hours=Wp)
    #     post_queue =
    #
    # return 1

#%%
if __name__ == '__main__':
    from pathlib import Path
    data_dir = Path(r'C:\Users\hyu\Documents\Nutstore\Abroad2020\LOG6703')
    rails_data_file = 'cleaned_dataset_rail_100000_new_noindex.csv'
    df = pd.read_csv(data_dir / rails_data_file, sep=';')

    test_run_history = run_window_based_prioritization(dataset=df,
                                    We=24,
                                    Wf=48,
                                    Wp=12)
# test_run_history
# df1 = df.set_index('job_start_time')
# df1.index = pd.DatetimeIndex(df1.index)
