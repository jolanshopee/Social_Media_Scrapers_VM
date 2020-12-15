import os
import re
import sys
import time
import requests
import traceback
from glob import glob
from datetime import datetime

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from socmed_scrape.instagram import instagram


def init_chromedriver():
    DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3") # silent mode
    options.add_argument('--incognito')
    driver = webdriver.Chrome(DRIVER_PATH,options=options)
    return driver


def clean_link(link):
    if not link:
        return ''

    link = link.split('?')[0]
    if not link.endswith('/'):
        link += '/'

    return link


URL_LIMIT = 5
if 'production' in sys.argv:
    URL_LIMIT = -1


N_POSTS = 30
SHEET_ID = '1npjfZNKLtOZgykcGVvJpKBCzAlD5TX85m_A9jj7W__o'
API_ENDPOINT = 'https://api-handler-u2qce7qlwa-as.a.run.app'

sheet_data = requests.post(
    API_ENDPOINT + '/sheets/read',
    json={
        'sheet_id': SHEET_ID,
        'sheet_name': 'ingestion',
        'sheet_range': 'A1:I20',
    }
).json()['data']

sheet_df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
sheet_df = sheet_df[['shopid', 'IG shop']].fillna('')
sheet_df = (
    sheet_df[sheet_df['IG shop'].str.contains('instagram.com')]
    .iloc[:URL_LIMIT]
)
sheet_df['IG shop'] = sheet_df['IG shop'].apply(clean_link)

scraped_posts = []
driver = init_chromedriver()
for i, row in sheet_df.iterrows():
    url = row['IG shop']
    shop_details = instagram.get_page_details(driver, url)
    scraped_posts.append(shop_details)

scrape_df = pd.DataFrame(scraped_posts).rename(columns={'ig_url': 'IG shop'})
sheet_df = (
    sheet_df
    .merge(scrape_df, on='IG shop', how='left')
    .drop_duplicates(['IG shop'])
    .fillna('')
)
sheet_df['timestamp'] = datetime.now().strftime('%m/%d/%Y %H:%M')
output_columns = [
    'shopid',
    'IG shop',
    'shop_name',
    'about',
    'posts',
    'followers',
    'website'
]

sheet_df = sheet_df[output_columns]
output_data = sheet_df.values.tolist()
output_data.insert(0, sheet_df.columns.values.tolist())

# res = requests.post(
#     API_ENDPOINT + '/sheets/write',
#     json={
#         'sheet_id': SHEET_ID,
#         'sheet_name': 'ig_scrape',
#         'sheet_range': 'A:H',
#         'data': output_data,
#         'clear_range': 'A:H'
#     }
# )
driver.quit()
#print(res.status_code, res.json())
print(output_data)