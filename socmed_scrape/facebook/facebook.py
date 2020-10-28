import os
import time
import json
import sys
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
from selenium.common.exceptions import NoSuchElementException

DRIVER_PATH = os.path.join(os.getcwd(), glob('*chromedriver*')[0])
options = Options()
driver = webdriver.Chrome(DRIVER_PATH, options=options)

#LOGIN
def login(self):
    """Log in w/ username and password.

    If the script is executed with 2 positional arguments
    (i.e. python fb_scrape.py username@shopee.com mypassword)
    then the browser will log in automatically with the provided credentials.
    """
    driver.get('https://www.facebook.com/')
    if len(sys.argv) < 3:
        _ = input('Please log into the browser before continuing')
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        driver.find_element_by_xpath('//input[@id="email"]').send_keys(username)
        driver.find_element_by_xpath('//input[@id="pass"]').send_keys(password)
        driver.find_element_by_xpath('//button[@name="login"]').click()
        time.sleep(10)

    return

#RETURNS FB SEARCH RESULTS
def search_keywords( keyword, limit):
    keyword_urls = []
    search_url = 'https://www.facebook.com/search/pages/?q={}'
    driver.get(search_url.format(keyword + ' philippines'))
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(0.5)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    #Get search results
    results = driver.find_elements_by_css_selector("div[class='nc684nl6']")
    for r in results:
        # get shop/page details
        shop_elem = r.find_element_by_css_selector("a")
        url = shop_elem.get_attribute('href').split('?')[0]
        if url not in [i['url'] for i in keyword_urls]:
            keyword_urls.append({
                'keyword': keyword,
                'shop_name': shop_elem.text,
                'url': url,
                'username': url.split('/')[-2]
            })

    keyword_urls = keyword_urls[:limit]
    print(keyword, len(keyword_urls), 'shops found')
    return keyword_urls

#RETURNS LATEST POST DATE
def chk_latest_post(shop_url):
    page_url = {'url': shop_url}
    post_dates = []
    try:
        driver.get(page_url['url'].replace("https://www.", "https://m."))
        for scroll in range(0,5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
        posts = driver.find_elements_by_xpath('//article[@class="_55wo _5rgr _5gh8 _3drq async_like"]')
        for post in posts:
            post_data = json.loads(post.get_attribute('data-ft'))
            get_timestamp = post_data['page_insights'][post_data['page_id']]['post_context']['publish_time']
            post_dates.append(datetime.fromtimestamp(get_timestamp).strftime('%m/%d/%Y')).sort()
    except Exception as e:
        print(e)

    return post_dates[0]

#RETURNS SHOP DETAILS
def get_page_details(shop_url):
    """Get shop/page details"""
    page_details = {'url': shop_url}
    try:
        # shop main page
        driver.get(page_details['url'])
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@id="entity_sidebar"]')))
            print("Page details has been loaded")
            page_details['shop_name'] = driver.find_element_by_xpath('//div[@id="entity_sidebar"]/div[2]/div[1]/div/div/div/span/div/span[1]/a').get_attribute('textContent')  
        except NoSuchElementException:
            page_details['shop_name'] = "Page not found/link error"

        try:
            page_details['username'] = driver.find_element_by_xpath('//div[@id="entity_sidebar"]/div[2]/div[2]/div/div/a').get_attribute('textContent')
        except NoSuchElementException:
            page_details['username'] = ''
            
        try:
            page_details['category'] = driver.find_element_by_xpath('//a[contains(@href,"category")]').get_attribute('textContent')
        except NoSuchElementException:
            page_details['category'] = ''

        try:
            page_details['likes'] = driver.find_element_by_xpath('//div[contains(text(),"people like this")]').get_attribute('textContent').split(' ')[0]
        except NoSuchElementException:
            page_details['likes'] = ''
        #Check if Shop Exists
        try:
            driver.find_element_by_xpath('//button[contains(text(),"Shop")]')
            page_details['has_shop'] = '1'
        except NoSuchElementException:
            print('Shop Not Found')
            page_details['has_shop'] = '0'

    except Exception as e:
        print(e)
    pass

    return page_details

#RETURNS LATEST POST DETAILS
def get_latest_posts(shop_url,limit,details = []):
    post_details = {'url': shop_url}
    try:
        driver.get(post_details['url'].replace("https://www.", "https://m."))

        posts = {}
        
        for scroll in range(0,(limit+1)):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        posts = driver.find_elements_by_xpath('//article[@class="_55wo _5rgr _5gh8 _3drq async_like"]')[:limit]
        
        for post in posts:
            post_data = json.loads(post.get_attribute('data-ft'))
            get_timestamp = post_data['page_insights'][post_data['page_id']]['post_context']['publish_time']
            #post_details['publish_time'] = datetime.fromtimestamp(get_timestamp).strftime('%m/%d/%Y')
            try:
                post_content = post.find_element_by_xpath('.//div[@class="story_body_container"]/div/span').get_attribute('textContent')
            except NoSuchElementException:
                print('Content cannot be extracted')
                post_content = 'n/a' 
            try:
                reactions = post.find_element_by_xpath('.//span[contains(text(), "Likes")]').get_attribute('textContent')
            except NoSuchElementException:
                print('Reactions Not Found')
                reactions = '0'
            try:
                comments = post.find_element_by_xpath('.//span[contains(text(), "Likes")]').get_attribute('textContent').split(' ')[0]
            except NoSuchElementException:
                print('Comments Not Found')
                comments = '0'
            #Share Data is Unavailable 
            # try:
            #     post_details['shares'] = post.find_element_by_xpath('.//div[@data-sigil="reactions-bling-bar"]/div[2]/span[2]').get_attribute('textContent').split(' ')[0]
            # except NoSuchElementException:
            #     print('Shares Not Found')
            #     post_details['shares'] = '0'
            details.append({
                'url' : shop_url,
                'publish_time' : datetime.fromtimestamp(get_timestamp).strftime('%m/%d/%Y'),
                'post_content' : post_content,
                'reactions' : reactions,
                'comments' : comments     
            })

    except Exception as e:
        print(e)

    return details
    
