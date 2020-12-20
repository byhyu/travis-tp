import pandas as pd

dataset_rail_complete = '../output/cleaned_dataset_rail_100000_new_noindex.csv'
columns = ['test_suite', 'test_suite_start time', 'test_suite_duration',
           'test_suite_runs', 'test_suite_assertions', 'test_suite_failures',
           'test_suite_errors', 'test_suite_skips', 'build_number',
           'build_pull_request', 'commit_sha', 'build_finish_time',
           'build_duration', 'job_id', 'job_start_time', 'job_allow_failure',
           'build_status', 'build_started_at', 'job_number', 'job_env', 'job_rvm',
           'build_id']

df_rail_complete = pd.read_csv(dataset_rail_complete, sep=';', header=1, names=columns)  # df.columns = columns
df_rail_truncated = df_rail_complete[
    ['test_suite', 'test_suite_start time', 'test_suite_duration', 'test_suite_failures', 'test_suite_errors',
     'job_id', 'job_number', 'job_start_time', 'job_env', 'job_rvm',
     'build_id', 'build_number', 'build_status']]

df_rail_clean_onets = df_rail_complete.loc[
    df_rail_complete['test_suite'] == 'railties/test/application/asset_debugging_test.rb']
# print(df_rail_clean_onets[['test_suite','job_env', 'job_rvm', 'job_number', 'build_number']].head(400))
# print(df_rail_truncated.loc[df_rail_truncated['test_suite_failures']!=0])
df_rail_truncated = df_rail_complete[['test_suite',
                                      'job_env', 'job_rvm', 'build_status'
                                      ]].drop_duplicates()

pd_sorted = df_rail_truncated.sort_values("test_suite", inplace=False)
# print(pd_sorted)

#%%
# a TS fails for any Ruby version for a specific GEM configuration
df1 = df_rail_complete[['test_suite', 'job_env', 'job_rvm', 'build_status']].drop_duplicates()
group1 = df1.groupby(['test_suite', 'job_env'])  # ['build_status'].unique()
count = 1
total = 1
for x in group1:
    total = total + 1
    if (x[1]['build_status'] == 'failed').all():
        # print(x[0])
        count = count + 1

print(count, ' / ', total)

# a TS fails for any GEM configuration for a specific Ruby version
df1 = df_rail_complete[['test_suite', 'job_env', 'job_rvm', 'build_status']].drop_duplicates()
group1 = df1.groupby(['test_suite', 'job_rvm'])  # ['build_status'].unique()
count = 1
total = 1
for x in group1:
    total = total + 1
    if (x[1]['build_status'] == 'failed').all():
        # print(x[0])
        count = count + 1

print(count, ' / ', total)
#%%
# a tS fails for any GEM configuration for any Ruby version
df1 = df_rail_complete[['test_suite', 'build_status']].drop_duplicates()
group1 = df1.groupby(['test_suite'])  # ['build_status'].unique()
count = 1
total = 1
for x in group1:
    total = total + 1
    if (x[1]['build_status'] == 'failed').all():
        # print(x[0])
        count = count + 1
print(count, ' / ', total)

#%%

