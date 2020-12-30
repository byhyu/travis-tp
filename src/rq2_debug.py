from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
from typing import Union
# from tqdm import tqdm
import pickle
# from tqdm import tqdm
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union
import time
import pandas as pd


def update_unnecessary_patterns(all_tests_history):
    unnecessary_patterns = pd.DataFrame([])
    for name, group in all_tests_history.groupby(['test_suite', 'job_env']):
        if (group['build_status'] == "failed").all():
            pattern_df = pd.DataFrame([[name[0], name[1], 'none']],
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)

    for name, group in all_tests_history.groupby(['test_suite', 'job_rvm']):
        if (group['build_status'] == "failed").all():
            pattern_df = pd.DataFrame([[name[0], 'none', name[1]]],
                                      columns=['test_suite', 'job_env', 'job_rvm'])
            unnecessary_patterns = unnecessary_patterns.append(pattern_df)

    # print("patterns update 之后的size: ", len(unnecessary_patterns))
    return unnecessary_patterns.drop_duplicates()


def is_test_necessary(test_suite, unnecessary_patterns):
    # df = unnecessary_patterns
    if unnecessary_patterns.empty:
        return True

    test_name = test_suite['test_suite']
    job_env = test_suite['job_env']
    job_rvm = test_suite['job_rvm']

    if not unnecessary_patterns[
        (unnecessary_patterns['test_suite'] == test_name) & (unnecessary_patterns['job_env'] == job_env)].empty:
        return False

    if not unnecessary_patterns[
        (unnecessary_patterns['test_suite'] == test_name) & (unnecessary_patterns['job_rvm'] == job_rvm)].empty:
        return False

    return True


def window_based_test_selection(test_timestamp: datetime,
                                test_run_history: pd.DataFrame,
                                We: Union[int, float],
                                Wf: Union[int, float],
                                is_new: bool):
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
    Wf_cond = len(test_run_history[fail_start:test_timestamp].build_status == 'failed') >= 1
    We_cond = test_run_history[exec_start:test_timestamp].shape[0] == 0
    if We_cond or Wf_cond:
        return True
    return False


def run_window_based_test_selection(dataset: pd.DataFrame,
                                    We: Union[int, float],
                                    Wf: Union[int, float],
                                    Wt: Union[int, float],
                                    use_patterns: bool = True):
    """
    Args:
        test_suite_inds: index of test cases, for example [0,1,2,3,4,5,6]
        dataset: test data in pandas.DataFrame
        We: Execution window in hours, refer to 2014 paper for details. The smaller We is, the more test suites are selected.
        Wf: Failure window in hours, refer to 2014 paper for details. The larger Wf is, the more test suites are selected.
    Returns:
    """
    skip_by_baseline_model = set()
    skip_by_patterns = set()

    existing_tests = set()

    unnecessary_patterns = pd.DataFrame([])
    tag_time = dataset.loc[0, 'test_suite_start time']
    # print(f'tag time:{tag_time}')

    all_tests_history = pd.DataFrame([])
    accumulated_runtime = 0
    count = 0
    for index, row in dataset.iterrows():
        test_name = row['test_suite']
        test_timestamp = row['test_suite_start time']

        if (not use_patterns) or is_test_necessary(row, unnecessary_patterns):
            if test_name in existing_tests:
                is_new = False
                test_history = all_tests_history[all_tests_history['test_suite'] == test_name]
                to_run_test = window_based_test_selection(row['test_suite_start time'], test_history, We, Wf, is_new)
            else:
                to_run_test = True
                existing_tests.add(test_name)

            if to_run_test:
                # accumulated_runtime += test_row.build_duration
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
                # test_df.sort_index(inplace=True)
                all_tests_history = all_tests_history.append(test_df)

                # check if we need to tag the dataset based on GEM and ruby version in the Wt window
                if test_timestamp >= tag_time:
                    unnecessary_patterns = update_unnecessary_patterns(all_tests_history)
                    # print(f'new patterns length: {unnecessary_patterns.shape}')
                    tag_time = tag_time + timedelta(hours=Wt)
                    # print(f'new tag time:{tag_time}')
            else:  # to_run_test = False
                skip_by_baseline_model.add(index)

        else:
            skip_by_patterns.add(index)
            # print(f'unnecessary test: {row["test_suite"]}')
            count = count + 1
    print("unnecessary count = ", count)
    # print(unnecessary_patterns['job_rvm'].drop_duplicates())
    # print(f' skip_by_patterns :{len(skip_by_patterns)}')
    # print(f' skip_by_baseline_model :{len(skip_by_baseline_model)}')
    skip_by = {'skip_by_patterns': skip_by_patterns, 'skip_by_baseline_mode': skip_by_baseline_model}
    return all_tests_history, skip_by


def run_parametric_study(df, We_list, Wf_list, Wt_list, save_to_file=True, output_dir=None):
    if output_dir is None:
        output_dir = Path('expriment_results')

    output_dir.mkdir(parents=True, exist_ok=True)



    experiment_id = 0
    # res = pd.DataFrame([])
    res = []
    dataset_length = df.shape[0]

    num_fail_cases_all = df[df['build_status'] == 'failed'].shape[0]

    for We in We_list:
        for Wf in Wf_list:
            for Wt in Wt_list:
                time_start = time.time()
                experiment_id += 1
                experiment_name = f'df{dataset_length}_We{We}_Wf{Wf}_Wt{Wt}_history'
                experiment_file = output_dir / f'{experiment_name}.csv'

                if experiment_file.exists():
                    print('experiment file already exists. Skip.')
                    continue

                print('**' * 10)
                print(f'running experiment {experiment_id}, dataset length: {dataset_length}, We={We}, Wf={Wf},Wt={Wt}')

                all_tests_history, skip_by = run_window_based_test_selection(df, We=We, Wf=Wf, Wt=Wt,
                                                                             use_patterns=False)
                all_tests_history_use_patterns, skip_by_use_patterns = run_window_based_test_selection(df, We=We, Wf=Wf,
                                                                                                       Wt=Wt,
                                                                                                       use_patterns=True)
                # accum_exec_time = all_tests_history['exec_time'].sum()
                num_selected_tests_baseline = len(all_tests_history)
                num_selected_tests_use_patterns = len(all_tests_history_use_patterns)
                num_skipped_by_baseline_model = len(skip_by_use_patterns['skip_by_baseline_mode'])
                num_skipped_by_patterns = len(skip_by_use_patterns['skip_by_patterns'])

                total_exec_time_baseline = all_tests_history['exec_time'].sum()
                total_exec_time_use_patterns = all_tests_history_use_patterns['exec_time'].sum()
                num_fail_cases_baseline = all_tests_history[all_tests_history['build_status']=='failed'].shape[0]
                num_fail_cases_use_patterns = all_tests_history_use_patterns[all_tests_history_use_patterns['build_status']=='failed'].shape[0]

                percentage_fail_cases_baseline = num_fail_cases_baseline / num_fail_cases_all
                percentage_fail_cases_use_patterns = num_fail_cases_use_patterns / num_fail_cases_all
                # append current results to res
                res.append([experiment_id, dataset_length,
                            We, Wf, Wt,
                            num_fail_cases_all,
                            num_selected_tests_baseline, num_selected_tests_use_patterns,
                            total_exec_time_baseline, total_exec_time_use_patterns,
                            num_fail_cases_baseline, num_fail_cases_use_patterns,
                            percentage_fail_cases_baseline, percentage_fail_cases_use_patterns])
                time_end = time.time()

                print('--' * 10)
                print(f'finished experiment {experiment_id}, dataset length: {dataset_length}, We={We}, Wf={Wf},Wt={Wt}')
                print(f'results: \n'
                      f'num_selected_tests_baseline: {num_selected_tests_baseline}, \n'
                      f'num_selected_tests_use_patterns: {num_selected_tests_use_patterns},\n'
                      f'num_skipped_by_baseline_model:{num_skipped_by_baseline_model},\n'
                      f'num_skipped_by_patterns:{num_skipped_by_patterns}\n'
                      )
                print(f'run time on local computer:{time_end - time_start} seconds \n')
                print('--' * 10)

                if save_to_file:
                    # save results to file
                    experiment_name = f'df{dataset_length}_We{We}_Wf{Wf}_Wt{Wt}_history'
                    all_tests_history.to_csv(output_dir / f'{experiment_name}.csv')
                    all_tests_history_use_patterns.to_csv(output_dir / f'{experiment_name}_use_patterns.csv')

                    # # write skip_by to file
                    # with open(output_dir / f'{experiment_name}_skipby.pickle', 'wb') as f:
                    #     pickle.dump(skip_by, f)
                    #
                    # with open(output_dir / f'{experiment_name}_skipby_use_patterns.pickle', 'wb') as f:
                    #     pickle.dump(skip_by_use_patterns, f)
                    

    res_col_names = ['experiment_id', 'dataset_length',
                     'We', 'Wf', 'Wt',
                     'num_fail_cases_all',
                     'num_selected_tests_baseline', 'num_selected_tests_use_patterns',
                     'total_exec_time_baseline', 'total_exec_time_use_patterns',
                     'num_fail_cases_baseline', 'num_fail_cases_use_patterns',
                     'percentage_fail_cases_baseline', 'percentage_fail_cases_use_patterns'
                     ]

    res_df = pd.DataFrame(res,
                          columns=res_col_names)

    datetime_now = datetime.now().strftime('%Y%m%d-%H%M%S')
    res_df.to_csv(output_dir / f'final_results_{datetime_now}_{experiment_name}.csv')

    print('==' * 10)
    print(f'final results:'
          f'{res_df}')
    print('==' * 10)
    return res_df


if __name__ == '__main__':
    #%%
    df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    df['test_suite_start time'] = pd.to_datetime(df['test_suite_start time'])  # 将数据类型转换为日期类型
    df.sort_values('test_suite_start time', inplace=True)
    # df = df.head(1000) # 加是否necessary前：112
    # df = df.head(2000) # 加是否necessary前：416
    # df = df.head(3000) # 加是否necessary前：489
    # df = df.head(4000) # 加是否necessary前：677
    # df = df.head(5000)  # 加是否necessary前：684
    # df = df.head(10000) # 加是否necessary前：799
    # all_tests_history, skip_by = run_window_based_test_selection(df, We=4, Wf=12, Wt=1, use_patterns=False)
    # all_tests_history_use_patterns, skip_by1 = run_window_based_test_selection(df, We=4, Wf=12, Wt=1, use_patterns=True)
    # print(all_tests_history.shape)
    # print(all_tests_history_use_patterns.shape)
    #
    # We_list = [1,2,4,8,12,24]
    # Wf_list = [1,2,4,8,12,24]
    # Wt_list = [1,4,8,12,24]
    # 
    # We_list = [1]
    # Wf_list = [1,2,4,6 8,10, 12]
    # Wt_list = [1, 4]
    # 
    # res_df = run_parametric_study(df=df.head(100000),
    #                               We_list=We_list,
    #                               Wf_list=Wf_list,
    #                               Wt_list=Wt_list,
    #                               save_to_file=True)
    # print(res_df)
    #%%
    # fig 6 in 2014 paper
    Wf_list = [0.25, 0.5,1,2,4,8]
    # Wf_list = [0.25, 0.5]
    We_list = [0.5]
    Wt_list = [1]
    output_dir = Path(r'expriment_results') / 'paper2014_fig6_v4'
    #%%
    res_df = run_parametric_study(df=df.head(20000),
                                  We_list=We_list,
                                  Wf_list=Wf_list,
                                  Wt_list=Wt_list,
                                  save_to_file=True,
                                  output_dir=output_dir)

    #%%
    # calculate percentage of number of selected tests: [number of selected tests]/[total number of tests]
    res_df['percentage_tests_baseline'] = res_df['num_selected_tests_baseline'] / res_df['dataset_length']
    res_df['percentage_tests_use_patterns'] = res_df['num_selected_tests_use_patterns'] / res_df['dataset_length']
    # %%
    # choose We = 1, as in Figure 6 from 2014 paper. Also fix Wt = 1
    # sub_df1 = res_df[(res_df['Wf'] == 2) & (res_df['Wt'] == 1)]
    sub_df1 = res_df
    # %%
    # plot
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.plot(sub_df1['Wf'].values, sub_df1['percentage_tests_baseline'].values, color='r', linestyle='-',marker='*',label='Test suites -- Baseline model')
    plt.plot(sub_df1['Wf'].values, sub_df1['percentage_tests_use_patterns'].values,color='g',linestyle='-',marker='*',label='Test suites --Use patterns')
    plt.plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_baseline'].values, color='r', linestyle='-.',
             label='Failed cases -- Baseline model')
    plt.plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_use_patterns'].values, color='g', linestyle='-.',
             label='Failed cases -- Use patterns')
    plt.legend()
    plt.grid()
    plt.xlabel('W_f (Hour)')
    plt.ylabel('Percentage compared to original test suites')
    plt.tight_layout()
    plt.show()
    fig.savefig(output_dir/'rq2_plot.png', dpi=300)

#%%
    # plt.figure()
    # plt.plot(sub_df1['We'].values, sub_df1['percentage_fail_cases_baseline'].values, color='r',linestyle='-.', label='Failed cases -- Baseline model')
    # plt.plot(sub_df1['We'].values, sub_df1['percentage_fail_cases_use_patterns'].values,color='g',linestyle='-.',label='Failed cases -- Use patterns')
    # plt.legend()
    # plt.grid()
    # plt.tight_layout()
    # plt.show()
    # #%%
    #to load a pickle file:
    # filename = Path(r'C:\Users\hyu\github-repos\travis-tp\src\expriment_results\df1000_We4_Wf6_Wt1_history_skipby.pickle')
    # with open(filename,'rb') as f:
    #     skipby_res = pickle.load(f)
