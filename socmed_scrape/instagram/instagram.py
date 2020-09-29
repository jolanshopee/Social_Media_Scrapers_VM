import os
import time
import json
from datetime import datetime, timedelta
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidArgumentException

DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
options = Options()
driver = webdriver.Chrome(DRIVER_PATH, options=options)


#RETURNS SHOP DETAILS
def get_page_details(url):
    """Get shop/page details"""
    page_details = {'ig_url': url}
    try:
        # shop main page
        driver.get(page_details['ig_url'])

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//main[@role="main"]/div/header')))
        print("Page details has been loaded")
        try:
            page_details['shop_name'] = driver.find_element_by_xpath('//header/section/div/h1').get_attribute('textContent')  
        except NoSuchElementException:
            page_details['shop_name'] = "Page not found/link error"
        try:
            page_details['posts'] = driver.find_element_by_xpath('//header/section/ul/li[1]/a/span').get_attribute('textContent')
        except NoSuchElementException:
            page_details['posts'] = ''
            
        try:
            page_details['followers'] = driver.find_element_by_xpath('//header/section/ul/li[2]/a/span').get_attribute('title')
        except NoSuchElementException:
            page_details['followers'] = ''

        try:
            page_details['website'] = driver.find_element_by_xpath('//a[@page_id="profilePage"]').get_attribute('textContent')
        except NoSuchElementException:
            page_details['website'] = ''
        
    except Exception as e:
        print(e)
        #return page_details

    return page_details


