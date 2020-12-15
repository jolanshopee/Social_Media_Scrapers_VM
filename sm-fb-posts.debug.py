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

from socmed_scrape.facebook import facebook


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


N_DAYS = 8
SHEET_ID = '1npjfZNKLtOZgykcGVvJpKBCzAlD5TX85m_A9jj7W__o'
API_ENDPOINT = 'https://api-handler-u2qce7qlwa-as.a.run.app'

sheet_data = requests.post(
    API_ENDPOINT + '/sheets/read',
    json={
        'sheet_id': SHEET_ID,
        'sheet_name': 'ingestion',
        'sheet_range': 'A1:I10',
    }
).json()['data']

sheet_df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
print(sheet_df)
sheet_df = sheet_df[['shopid', 'FB shop']].fillna('')
sheet_df = (
    sheet_df[sheet_df['FB shop'].str.contains('facebook.com')]
    .iloc[:URL_LIMIT]
)
sheet_df['FB shop'] = sheet_df['FB shop'].apply(clean_link)

scraped_posts = []
for i, row in sheet_df.iterrows():
    url = row['FB shop']
    shop_posts = facebook.get_latest_posts(url, N_DAYS)
    scraped_posts += shop_posts

scrape_df = pd.DataFrame(scraped_posts).rename(columns={'url': 'FB shop'})
sheet_df = (
    sheet_df
    .merge(scrape_df, on='FB shop', how='left')
    .drop_duplicates(['FB shop', 'post_content'])
    .fillna('')
)
sheet_df['timestamp'] = datetime.now().strftime('%m/%d/%Y %H:%M')
output_columns = [
    'shopid',
    'FB shop',
    'comments',
    'likes',
    'post_content',
    'publish_time',
    'timestamp'
]

sheet_df = sheet_df[output_columns]
output_data = sheet_df.values.tolist()
output_data.insert(0, sheet_df.columns.values.tolist())

# res = requests.post(
#     API_ENDPOINT + '/sheets/write',
#     json={
#         'sheet_id': SHEET_ID,
#         'sheet_name': 'fb_scrape',
#         'sheet_range': 'A:H',
#         'data': output_data,
#         'clear_range': 'A:H'
#     }
# )
# print(res.status_code, res.json())

print(output_data)
