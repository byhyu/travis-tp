import numpy as np

def calc_APFD(all_test_index_list, failed_index_list):
    """
    Calculate Average Percentage of Faults Detected (APFD).
    APFD is defined as follows:
    Denote the set of all failed test cases in T as T_f = [tf1, tf2, ... tfl],
    where l is the number of failed test cases and the index of test case tfi in T is fi.
    The APFD target function is formulated as:
        APFD = 1 - sum(fi)/(nl) + 1/(2n)

    Args:
        ranks:
        failed_ids:

    Returns:

    """
    num_failed = len(failed_index_list) # l in equation
    num_tests = len(all_test_index_list) # n in equation
    sum_fi = sum(failed_index_list)
    APFD = 100*(1 - sum_fi/(num_failed*num_tests) + 1/(2*num_tests))
    #
    # sum = 0
    # for f in failed_ids:
    #     ind = np.where(ranks == f)
    #     assert(np.size(ind) == 1)
    #     sum += (ind[0]+1)
    #
    # m = np.size(failed_ids)
    # n = np.size(ranks)
    # APFD = 100*(1 - sum/(m*n) + 1/(2*n))
    return APFD

def calc_first_fail_time(dataset):
    """
    Calculate first fail time for specific test suite. Will be used to generate Fig6 and Fig7 in 2014 paper.
    Args:
        dataset: input dataset. Should have at least these columns: ['test_suite', 'job_start_time' (or other time), 'build_status']

    Returns:
        dataframe with columns: ['test_suite','first_fail_time']

    """
    #TODO
    failed_tests = dataset[dataset.build_status == 'failed']
    # unique_failed_tests =


if __name__ == '__main__':
    import pandas as pd
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    failed_tests = df.index[df['build_status'] == 'failed'].tolist()
    print(failed_tests)
    APFD = calc_APFD(list(range(df.shape[0])), failed_tests)
    print(f'APFD:{APFD}')


    # all_tests_history = split_dataset_into_wp(list(range(10)), df, We=24, Wf=48, Wp=12)
    # print(all_tests_history.shape[0])
