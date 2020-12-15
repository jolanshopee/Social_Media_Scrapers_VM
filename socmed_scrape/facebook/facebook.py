import os
import time
import json
import sys
import traceback
import re
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
from facebook_scraper import get_posts


#LOGIN
def login(driver, username='', password=''):
    """Log in w/ username and password.

    If the function is executed with username and password kwargs
    then the browser will log in automatically with the provided credentials.
    """
    driver.get('https://www.facebook.com/')
    if not (username and password):
        _ = input('Please log into the browser before continuing')
    else:
        driver.find_element_by_xpath('//input[@id="email"]').send_keys(username)
        driver.find_element_by_xpath('//input[@id="pass"]').send_keys(password)
        driver.find_element_by_xpath('//button[@name="login"]').click()
        time.sleep(10)

    return

#RETURNS FB SEARCH RESULTS
def search_keywords(driver, keyword, limit):
    """Get pages associated with the search keyword.
    Function: search_keywords(driver, keyword, limit)
    Description: Searches using the keywords and gets the page link, name, and username from the search result.
    Arguments: 
    - driver : configured webdriver
    - keyword : string arg used for searching pages
    - limit : int arg used to limit the result to be returned 
    Return Value: a `list` of page search result that contains the following:
        - 'keyword': keyword used in search
        - 'shop_name': facebook page name 
        - 'url': link of the facebook page
        - 'username': username of the page
    """
    print('SEARCHING FOR', keyword)
    search_url = 'https://www.facebook.com/search/pages/?q={}'
    keyword_urls = []
    page_results = []
    driver.get(search_url.format(keyword + ' philippines'))

    # Get scroll height
    worked = False
    for retry in range(5):
        xpaths_to_try = [
            "//div[@aria-label='Preview of a Search Result']",
            "//div[@aria-label='Search Results']",
        ]
        for xpath in xpaths_to_try:
            try:
                search_body = driver.find_element_by_xpath(xpath)
                worked = True
            except:
                pass

        if worked:
            break
        else:
            print('Waiting for page to load')
            time.sleep(5)

    if not worked:
        return []

    end_of_results = False
    while not end_of_results and len(page_results) < limit:
        # Scroll down to bottom and wait to load page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        nested_div_depth = 7
        page_results = search_body.find_elements_by_xpath('/'.join(['div']*nested_div_depth))
        end_of_results = len(search_body.find_elements_by_xpath("//span[text()='End of Results']")) > 0

    print('limit reached - {} shops'.format(len(page_results)))
    for page in page_results:
        # get shop/page details
        try:
            shop_elem = page.find_element_by_css_selector("a[role='link']")
            url = shop_elem.get_attribute('href').split('?')[0]
            if url not in [i['url'] for i in keyword_urls]:
                keyword_urls.append({
                    'keyword': keyword,
                    'shop_name': shop_elem.text,
                    'url': url,
                    'username': url.split('/')[-2]
                })
            print('>>', shop_elem.text)
        except Exception as e:
            pass


    keyword_urls = keyword_urls[:limit]
    print(keyword, len(keyword_urls), 'shops found')
    return keyword_urls

#RETURNS LATEST POST DATE
def chk_latest_post(driver, shop_url):
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
def get_page_details(driver, shop_url, shopid):
    """Get shop/page details
    Function: get_page_details(driver, shop_url)
    Description: Gets the details of a facebook page.
    Arguments: 
        - driver : configured webdriver
        - shop_url : facebook page url
    Return Value: a `dict` which contains the page details:
        - 'url' : facebook page url
        - 'username' : page username
        - 'category' : facebook page category
        - 'likes' : number of page likes
        - 'has_shop' : if page has a shop button
    """
    shop_result = {'url': shop_url}
    shop_result['shop_id'] = shopid

    # match only alphanumeric after facebook.com, 
    pattern = 'facebook\.com\/([A-Za-z0-9-_.]*)'
    try:
        username = re.search(pattern, shop_url).group(1)
    except:
        print('username not found')
        username = 'n/a'
    shop_result['username'] = username

    about_suffix = 'about'
    if not shop_url.endswith('/'):
        about_suffix = '/' + about_suffix

    try:
        # shop main page
        driver.get(shop_url + about_suffix)
        about_body = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div/div')))
        print("Page has been loaded")
        time.sleep(1.5)
        try:
            shop_result['shop_name'] = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div[2]/div/div/div[1]/h2').get_attribute('textContent')  
        except NoSuchElementException:
            shop_result['shop_name'] = ''
            print('Cannot get shop name')

        try:
            likes_xpath = "//div[@role='main']/div[4]/div/div/div/div/div[contains(.//span, 'like this')]"
            shop_result['likes'] = driver.find_element_by_xpath(likes_xpath).text.split(' ')[0].replace(',','')
        except Exception as e:
            shop_result['likes'] = ''
            print('Cannot get likes')
        
        try:
            followers_xpath = "//div[@role='main']/div[4]/div/div/div/div/div[contains(.//span, 'follow this')]"
            shop_result['followers'] = driver.find_element_by_xpath(followers_xpath).text.split(' ')[0].replace(',','')
        except Exception as e:
            shop_result['followers'] = ''
            print('Cannot get followers')

        try:
            shop_result['about'] = about_body.find_element_by_xpath('.//span[contains(text(),"About")]/ancestor::div[2]').get_attribute('textContent').split('About',1)[1]
        except Exception as e:
            shop_result['about'] = ''
            print('Cannot get about')

        try:
            shop_result['website'] = about_body.find_element_by_xpath('.//i[contains(@class, "sx_0c66b8")]/ancestor::div[2]').get_attribute('textContent')
        except Exception as e:
            shop_result['website'] = ''
            print('Cannot get website')

        try:
            shop_result['mobile'] = about_body.find_element_by_xpath('.//i[contains(@class, "sx_5af472")]/ancestor::div[2]').get_attribute('textContent')
        except Exception as e:
            shop_result['mobile'] = ''
            print('Cannot get mobile')

        try:
            ig_base_url = "https://www.instagram.com/"
            ig = driver.find_element_by_xpath('//i[contains(@class, "sx_1acfe2")]/ancestor::div[2]/div[2]/div/div/span/span/a').get_attribute('textContent')
            shop_result['ig link'] = ig_base_url + ig
        except Exception as e:
            shop_result['ig link'] = ''
            print('Cannot get ig link')

        try:
            shop_result['page_type'] = driver.find_element_by_xpath(
                "//div[@role='main']/div/div/div/div/div/div/div/div/div[2]"
            ).text.strip().split('\n')[-1]
            pass
        except Exception as e:
            shop_result['page_type'] = ''
            print('Cannot get page type')

        try:
            base_path = '//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[4]/div'
            shop_loc = driver.find_element_by_xpath(
                base_path + '//a[contains(@href, "maps")]'
            )
            shop_result['location_text'] = shop_loc.text
            shop_result['location_url'] = shop_loc.get_attribute('href')

        except Exception as e:
            print('Cannot get location info')
            shop_result['location_text'] = ''
            shop_result['location_url'] = ''

        # latest post
        post_timestamps = []
        for ts in get_posts(shop_result['username'], pages=2):
            post_timestamps.append(ts['time'])

        latest_post = sorted(post_timestamps, reverse=True)[0]
        shop_result['last_post_date'] = latest_post.strftime('%m/%d/%Y')

    except Exception as e:
        print(traceback.format_exc())

    return shop_result

#RETURNS LATEST POST DETAILS
def get_latest_posts(shop_url,days=7):
    """
    Function: get_latest_posts(shop_url, days=)
    Description: Gets the latest posts of the facebook page.
    Arguments: 
        - shop_url : facebook page url
        - days: int arg to set the number days (optional, default is 7)
    Return Value: a `dict` which contains the page details:
        - 'url' : facebook page url
        - 'publish_time' : post publish time
        - 'post_content' : post text content
        - 'likes' : number of post likes
        - 'comments' : number of post comments
    """
    post_details = {'url': shop_url}
    print(post_details['url'])
    # match only alphanumeric after facebook.com, 
    pattern = 'facebook\.com\/([A-Za-z0-9-_.]*)'
    try:
        username = re.search(pattern, shop_url).group(1)
    except:
        print('username not found')
        username = 'n/a'
    details = []
    chk_post = 0
    try:
        for post in get_posts(username):
            
            if (datetime.now() - post['time']).days <= days:
                details.append({
                'url' : shop_url,
                'publish_time' : post['time'].strftime('%m/%d/%Y'),
                'post_content' : post['text'],
                'likes' : post['likes'],
                'comments' : post['comments']     
                })
            elif chk_post > 2:
                break
            else:
                chk_post += 1
            

    except Exception as e:
        print(e)

    return details
    
