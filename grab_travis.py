# from bs4 import BeautifulSoup
# soup = BeautifulSoup('<p>Hello</p>', 'html.parser')
# print(soup.p.string)

#%%
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
#%%
driver = webdriver.Chrome(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--enable-javascript")
url = 'https://travis-ci.org/github/rails/rails/builds/517573851'
url = 'https://travis-ci.org/github/rails/rails/jobs/517573852'
# driver = webdriver.Chrome()

driver.get(url)

html = driver.page_source
soup = BeautifulSoup(html)
#%% another way


url = 'https://api.travis-ci.org/build/517573851?include=build.jobs%2Cjob.config%2Cbuild.commit%2Cbuild.branch%2Cbuild.request%2Cbuild.created_by%2Cbuild.repository'

url = 'https://api.travis-ci.org/build/517573851?include=build.jobs%2Cjob.config%2Cbuild.commit%2Cbuild.branch%2Cbuild.request%2Cbuild.created_by%2Cbuild.repository'

resp = requests.get(url, headers=header)

def get_page_from_job_id(job_id):
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
    url = f'https://api.travis-ci.org/build/{job_id}?include=build.jobs%2Cjob.config%2Cbuild.commit%2Cbuild.branch%2Cbuild.request%2Cbuild.created_by%2Cbuild.repository'
    resp = requests.get(url, headers=header)
    return resp

#%%
import json
import pandas as pd

def parse_page(resp):
    data_block = json.loads(resp.text)
    res  = {}
    ids = []
    langs = []
    gems = []
    for job in data_block['jobs']:
        job_id =  job['id']
        job_rvm =  job['config']['env']
        job_lang = job['config']['rvm']
        ids.append(job_id)
        langs.append(job_lang)
        gems.append(job_rvm)
    df = pd.DataFrame(data={'job_id':ids,
                            'lang':langs,
                            'gem':gems})
    df.to_csv(f'{job_id}_lang_gem.csv')
#%%
parse_page(resp)

#%%
from pathlib import Path
data_dir = Path(r'C:\Users\hyu\Desktop\RailsCleanData.out')
dataset_rail = data_dir/'RailsCleanData.out'
df = pd.read_csv(dataset_rail,sep=';')#%%, sep=';', header = None, names=columns)
#%%
df = pd.read_csv(C:\Users\hyu\Desktop\RailsCleanData.out)


#%%
with open("build_jobs.html",'w') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
    f.write(resp.text)
#%%
soup = BeautifulSoup(resp.text,'lxml') # 'html.parser')
#%%
pprint(soup)
#%%
job_lang = soup.select(div,'.detail-job-lang')
#%%
jobs = soup.select('.jobs-item')
#%%
job_lang_list = []
for job in jobs:
    job_lang = job.select('.job-lang')[0]
    job_lang_list.append(job_lang)
    print(job_lang.text)
# header = {
#     'accept': "application/json",
#     'accept-encoding': "gzip, deflate, br",
#     'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
#     'authorization': "token wQ_DGN5bXlWqkLdlAJQdZQ",
#     'content-type': "application/json",
#     'dnt': "1",
#     'origin': "https://travis-ci.org",
#     'referer': "https://travis-ci.org/",
#     'sec-fetch-dest': "empty",
#     'sec-fetch-mode': "cors",
#     'sec-fetch-site': "same-site",
#     'travis-api-version': "3",
#     'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
# }

# url="https://api.travis-ci.org/build/517555895"

#url="https://api.travis-ci.org/job/517357183"
# url="https://api.travis-ci.org/job/517555896/log"

# resp = requests.get(url, headers=header)
# soup = BeautifulSoup(resp.text,'lxml') # 'html.parser')
#%%
# with open("job_log.txt",'w') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
#     f.write(str(soup))