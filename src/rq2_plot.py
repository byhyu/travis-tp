# -*- coding: utf-8 -*-
#%%
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
#%%
res_file = Path(r'expriment_results/paper2014_fig6_v10/final_results_20201230-005027_df10000_We3_Wf5_Wt0.5_history.csv')
output_dir = res_file.parent
#%%

res_df = pd.read_csv(res_file, header=0)

df = pd.read_csv("../output/cleaned_dataset_rail_100000_new_noindex.csv", sep=';', header=0)
df['test_suite_start time'] = pd.to_datetime(df['test_suite_start time'])  # 将数据类型转换为日期类型
df.sort_values('test_suite_start time', inplace=True)
input_df = df.head(10000)
    #%%
total_exec_time_original = input_df['test_suite_duration'].sum()


# calculate percentage of number of selected tests: [number of selected tests]/[total number of tests]
res_df['percentage_tests_baseline'] = res_df['num_selected_tests_baseline'] / res_df['dataset_length']
res_df['percentage_tests_use_patterns'] = res_df['num_selected_tests_use_patterns'] / res_df['dataset_length']
res_df['percentage_exec_time_baseline'] = res_df['total_exec_time_baseline']/total_exec_time_original
res_df['percentage_exec_time_use_patterns'] = res_df['total_exec_time_use_patterns']/total_exec_time_original

sub_df1 = res_df


# %%
# plot

fig = plt.figure()
plt.plot(sub_df1['Wf'].values, sub_df1['percentage_exec_time_baseline'].values,
             color='k', linestyle='--',marker='+', linewidth=2,
             label='Total execution time -- Baseline model')
plt.plot(sub_df1['Wf'].values, sub_df1['percentage_exec_time_use_patterns'].values,
            color='k', linestyle='-',marker='+', linewidth=2,
            label='Total execution time -- Use patterns')
# axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

plt.plot(sub_df1['Wf'].values, sub_df1['percentage_tests_baseline'].values, color='g', linestyle='dashdot',marker='d',label='Test suites -- Baseline model')
plt.plot(sub_df1['Wf'].values, sub_df1['percentage_tests_use_patterns'].values,color='g',linestyle='-',marker='d',label='Test suites --Use patterns')

plt.plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_baseline'].values, color='r', linestyle='-.',marker='*',
          label='Failed cases -- Baseline model')
plt.plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_use_patterns'].values, color='r', linestyle='-',marker='*',
          label='Failed cases -- Use patterns')
ax = plt.gca()
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.legend()
plt.grid()
plt.xlabel('W_f (Hour)')
plt.ylabel('Percentage compared to original test suites')
plt.title('')
plt.tight_layout()
plt.show()
fig.savefig(output_dir/'rq2_plot.png', dpi=300)
#%%
# fig, axs = plt.subplots(1,1)
# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_exec_time_baseline'].values,
#              color='k', linestyle='--',marker='+', linewidth=2,
#              label='Total execution time -- Baseline model')
# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_exec_time_use_patterns'].values,
#             color='k', linestyle='-',marker='+', linewidth=2,
#             label='Total execution time -- Use patterns')
# # axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_tests_baseline'].values, color='r', linestyle='-',marker='*',label='Test suites -- Baseline model')
# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_tests_use_patterns'].values,color='g',linestyle='-',marker='*',label='Test suites --Use patterns')
# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_baseline'].values, color='r', linestyle='-.',
#           label='Failed cases -- Baseline model')
# axs[0].plot(sub_df1['Wf'].values, sub_df1['percentage_fail_cases_use_patterns'].values, color='g', linestyle='-.',
#           label='Failed cases -- Use patterns')
# # ax = plt.gca()
# axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
# plt.legend()
# plt.grid()
# plt.xlabel('W_f (Hour)')
# plt.ylabel('Percentage compared to original test suites')
# plt.title('')
# plt.tight_layout()
# plt.show()
# fig.savefig(output_dir/'rq2_plot.png', dpi=300)