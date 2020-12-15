import socmed_scrape.facebook.facebook as fb
import socmed_scrape.instagram.instagram as ig
import os
import re
import csv
import json
import requests
import pandas as pd
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta


#initialize and config webdriver
DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(DRIVER_PATH, options=options)

#GET DATA


read_url = 'https://api-handler--dev-u2qce7qlwa-as.a.run.app/sheets/read'
send_url = 'https://api-handler--dev-u2qce7qlwa-as.a.run.app/sendgrid/send-email'
spreadsheet_id = '1npjfZNKLtOZgykcGVvJpKBCzAlD5TX85m_A9jj7W__o'

email = {
    #required
    "auth_key": "Shopeesuki1",
    "from_email": "phbiteam.shp@gmail.com",
    "to_email": "jolan.delacruz@shopee.com",

    #optional
    "cc_email": "deion.menor@shopee.com",
    "bcc_email": "jolan.delacruz@shopee.com",
    "subject": "Execution has been completed",
    "content": "Social media scraper has been executed successfully. Kindly see results ___.",
}

body = {
    "owner": "jolan.delacruz@gmail.com",
    "sheet_id": spreadsheet_id,
    "sheet_name": "ingestion",
    "sheet_range": "A1:H5"
}
response = requests.post(read_url, json=body)

data = response.json()['data']

fb_details = []
for x in data:
    try:
        if 'facebook' in x[7]:
            details = {
                'shop_id' : x[0],
                'url' : x[7]
            }
            fb_details.append(details)
    except IndexError:
        print("Index Error")
#ig_urls = [x for x in data if 'instagram' in x[8]]

print(len(fb_details))


def fb_login():
    #Call the login function
    fb.login(driver, username='karl.kue@shopee.com', password='Shopeesuki1')


def scrape_fb(details):
    page_details = []
    fb_details_filename = 'fb_page_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
    for detail in details:
        page_details.append(fb.get_page_details(driver, detail['url'], detail['shop_id']))
    df_page_details = pd.DataFrame(page_details,  columns=['shop_id','url', 'shop_name', 'likes', 'followers'])
    df_page_details.to_csv(fb_details_filename, index=0)


def scrape_ig(URLs):
    page_details = []
    ig_details_filename = 'ig_page_' + \
        (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
    for url in URLs:
        page_details.append(ig.get_page_details(driver, url[0]))
    df_page_details = pd.DataFrame(page_details, columns=['ig_url', 'shop_name', 'followers'])
    df_page_details.to_csv(ig_details_filename, index=0)


try:
    fb_login()
    scrape_fb(fb_details)
    #scrape_ig(ig_urls)
    response = requests.post(send_url, json=email)
    print(response.content)
except Exception as e:
    email = {
        #required
        "auth_key": "Shopeesuki1",
        "from_email": "phbi-noreply@shopee.com",
        "to_email": "jolan.delacruz@shopee.com",

        #optional
        "cc_email": "jolan.delacruz@shopee.com",
        "bcc_email": "",
        "subject": "An error occurred",
        "content": e
    }
    requests.post(send_url, json=email)
