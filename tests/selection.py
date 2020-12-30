from src.rq2_debug import window_based_test_selection
import pandas as pd

def load_data():
    df = pd.read_csv("output\cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
    df['test_suite_start time'] = pd.to_datetime(df['test_suite_start time'])  # 将数据类型转换为日期类型
    df.sort_values('test_suite_start time', inplace=True)
    return df

#%%
df = load_data()
#%%
df1 = df.iloc[0:500,:]
fail_df = df1[df1['build_status'] == 'FAIL']
any(fail_df)
#%%
def test_window_based_test_selection():
    df = load_data()
    pass

    # window_based_test_selection(test_timestamp: datetime,
    # test_run_history: pd.DataFrame,
    # We: Union[int, float],
    # Wf: Union[int, float],
    # is_new: bool):
    #
