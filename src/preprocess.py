import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

header = {
    'accept': "application/json",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
    'authorization': "token wQ_DGN5bXlWqkLdlAJQdZQ",
    'content-type': "application/json",
    'dnt': "1",
    'origin': "https://travis-ci.org",
    'referer': "https://travis-ci.org/",
    'sec-fetch-dest': "empty",
    'sec-fetch-mode': "cors",
    'sec-fetch-site': "same-site",
    'travis-api-version': "3",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
}

base_url = "https://api.travis-ci.org/"
version_block = pd.DataFrame(columns=['job_id', 'job_number', 'job_env', 'job_rvm', 'build_id'])

def get_build_by_job(job_id):
    # url='https://api.travis-ci.org/repo/891/builds?repository_id=891&event_type=pull_request&limit=2500&offset=0&skip_count=true&include=build.commit%2Cbuild.branch%2Cbuild.request%2Cbuild.created_by%2Cbuild.repository'

    #base_url = "https://api.travis-ci.org/job/"
    if job_id in version_block['job_id'].values:
        return 0
    
    url = base_url + 'job/' + str(job_id)
    resp = requests.get(url, headers=header)
    # print(resp.text)
    job_block = json.loads(resp.text)
    
    return job_block['build']['id'], job_block['build']['number']


def get_version_by_build(build_id):
    if build_id == 0:
        return
    if build_id in version_block['build_id'].values:
        return
    
    url = 'https://api.travis-ci.org/build/{0}?include=build.jobs%2Cjob.config%2Cbuild.commit%2Cbuild.branch%2Cbuild.request%2Cbuild.created_by%2Cbuild.repository'.format(build_id)
    #print(url)
    resp = requests.get(url, headers=header)
    #print(resp)
    jobs_in_build=json.loads(resp.text)
    
    for job in jobs_in_build['jobs']:
        #print(job['id'], job['number'], job['config']['env'],job['config']['rvm'], build_id)
        size = version_block.index.size
        version_block.loc[size] = [job['id'], job['number'], job['config']['env'],job['config']['rvm'], build_id]        
        
    return

def adjust_rails(filename):
    #read columns header from the header definition on github
    columns = ['test_suite', 'test_suite_start_time', 'test_suite_duration', 'test_suite_runs', 'test_suite_assertions', 'test_suite_failures', 'test_suite_errors', 'test_suite_skips', 'build_number', 'build_pull_request', 'commit_sha', 'build_start_time', 'build_finish_time', 'build_duration', 'job_id', 'job_start_time', 'job_allow_failure']
    
    # read cleaned data from the rail dataset
    df_rail = pd.read_csv(filename, sep=';', header = None, names=columns) 
    
    df_rail['build_status'], df_rail['build_started_at'] = df_rail['build_start_time'].str.split(',', 1).str
    df_rail.drop('build_start_time', axis=1, inplace=True)
    
    return df_rail.head(100000) 

def combine_rail_version(df1, df2, key):
    return pd.merge(df1,df2, how='inner', on=key)
  

if __name__ == "__main__": 
    dataset_rail = 'Datasets/RailsCleanData.out'
    df_rail = adjust_rails(dataset_rail)
    job_id_list = df_rail['job_id'].drop_duplicates()
    
    for job_id in job_id_list:
        if not job_id in version_block['job_id'].values:
            build_id, build_number = get_build_by_job(job_id)
            get_version_by_build(build_id)
    
    rail_ver = combine_rail_version(df_rail, version_block, 'job_id')
    rail_ver.to_csv(path_or_buf='output/cleaned_dataset_rail_100000_new_noindex.csv', sep=';', na_rep='', float_format=None, columns=None, header=True, index=False,
                 index_label=None, mode='w', encoding=None, compression=None, quoting=None, quotechar='"',
                 line_terminator='\n', chunksize=None, date_format=None, doublequote=True)
