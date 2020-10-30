#BELOW ARE THE SAMPLE SCRIPTS FOR THE INSTAGRAM PACKAGE FUNCTIONS
import instagram as ig
import os
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import csv
from datetime import datetime, timedelta

def page_details_sample():
    """
    Sample function to get the instagram page details.
    This will get the input from a csv and output the result in csv.
    """

    #initialize and config webdriver
    DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
    options = Options()
    driver = webdriver.Chrome(DRIVER_PATH, options=options)
    
    #get shop from the csv file
    URLs = pd.read_csv('socmed_scrape/instagram/shop_urls.csv')['url'].drop_duplicates().values.tolist()[:5] #update or remove limit, used only for testing

    
    page_details = []
    page_details_filename = 'page_details_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
    df_page_details = pd.DataFrame()
    #execute the get_page_details function for each url
    for url in URLs:
        try:
            #append the result to the list
            page_details.append(ig.get_page_details(driver,url))
        except Exception as e:
            print(e)
    df_page_details = df_page_details.append(page_details) 
    df_page_details.to_csv(page_details_filename, index=0)



def post_details_sample():
    """
    Sample function to get the instagram post details.
    This will get the input from a csv and output the result in csv.
    """

    #initialize and config webdriver
    DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
    options = Options()
    driver = webdriver.Chrome(DRIVER_PATH, options=options)
    
    #get shop from the csv file
    URLs = pd.read_csv('socmed_scrape/instagram/shop_urls.csv')['url'].drop_duplicates().values.tolist()[:2] #update or remove limit, used only for testing

    post_details = []
    post_details_filename = 'ig_post_details_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
    df_post_details = pd.DataFrame()
    #execute the get_page_details function for each url
    for url in URLs:
        try:
            post_details = ig.get_latest_posts(driver,url,5)
        except Exception as e:
            print(e)
        df_post_details = df_post_details.append(post_details)
    df_post_details.to_csv(post_details_filename, index=0)


#execute the functions
page_details_sample()
post_details_sample()
