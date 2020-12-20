from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pathlib import Path


def window_based_test_selection(test_timestamp, test_run_history, We, Wf, is_new):
    """

    Args:
        test_timestamp: test timestamp from test dataset DataFrame, df['job_start_time']
        test_run_history:
        We: Execution window in hours, refer to 2014 paper for details
        Wf: Failure window in hours, refer to 2014 paper for details
        is_new: Boolean, is the current test suite new?

    Returns:
        Boolean. Test case selected or not.

    """

    exec_start = test_timestamp - timedelta(hours=We)
    fail_start = test_timestamp - timedelta(hours=Wf)
    We_cond = any(test_run_history[exec_start:test_timestamp].build_status=='FAIL')
    Wf_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    if is_new or We_cond or Wf_cond:
        # print('test True')
        return True
    return False


def run_window_based_test_selection(test_suite_inds, dataset, We, Wf):
    """
    :param test_suite_inds:
    :param dataset:
    :param We:
    :param Wf:
    :return:
    """
    existing_tests = set()
    test_selection = []
    accumulated_runtime = 0
    all_tests_history = pd.DataFrame([])
    for test_ind in test_suite_inds:
        test_row = dataset.iloc[test_ind, :]
        test_name = test_row.test_suite
        print(f'test name:{test_name}')

        test_time_str = dataset.iloc[test_ind, :]['job_start_time']
        test_timestamp = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M:%S.%f')


        if test_name in existing_tests:
            is_new = False
            test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
            to_run_test = window_based_test_selection(test_timestamp, test_history, We, Wf, is_new)
            print(f'test selected: {to_run_test}')
        else:
            to_run_test = True


        if to_run_test:
            # accumulated_runtime += test_row.build_duration
            build_status = test_row.build_status
            exec_time = test_row.build_duration
            test_df = pd.DataFrame(index=[test_timestamp],
                                   data={'test_suite': [test_name], 'build_status': [build_status],
                                         'exec_time': exec_time})

            all_tests_history = all_tests_history.append(test_df)

    return all_tests_history


    #     test_name = dataset.test_suite[test_ind]
    #     print(test_timestamp)
    #
    #     if test not in existing_tests:
    #         is_new = True
    #         print('new test')
    #         existing_tests.add(test)
    #     else:
    #         print('old test')
    # return test_selection


if __name__ == '__main__':
    data_dir = Path(r'C:\Users\hyu\Documents\Nutstore\Abroad2020\LOG6703')
    rails_data_file = 'cleaned_dataset_rail_100000_new_noindex.csv'
    df = pd.read_csv(data_dir / rails_data_file, sep=';')
    # all_tests_history = run_window_based_test_selection(list(range(df.shape[0])), df, We=24, Wf=48)
    all_tests_history = run_window_based_test_selection(list(range(5000)), df, We=24, Wf=48)

    print(all_tests_history)
