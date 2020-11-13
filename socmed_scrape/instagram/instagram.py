import time
from datetime import datetime, timedelta
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


search_url = 'https://www.instagram.com/explore/tags/{}/'


def login(driver, username='', password=''):
    """Log in w/ username and password.

    If the script is executed with 2 positional arguments
    (i.e. python fb_scrape.py username@shopee.com mypassword)
    then the browser will log in automatically with the provided credentials.
    """
    driver.get('https://www.instagram.com/')
    if not (username and password):
        _ = input('Please log into the browser before continuing')
    else:
        time.sleep(1)
        driver.find_element_by_css_selector("input[name='username']").send_keys(username)
        driver.find_element_by_css_selector("input[type='password']").send_keys(password)
        driver.find_element_by_css_selector("button[type='submit']").click()
        time.sleep(10)


def search_keywords(driver, keyword, limit=10):
    time.sleep(3)
    keyword_urls = []
    if keyword.endswith('ph'):
        keyword = keyword[:-2]

    driver.get(search_url.format(keyword.replace(' ','') + 'ph'))
    retry = 0
    prev_len = 0
    while len(keyword_urls) < limit and retry <= 5:
        if prev_len == len(keyword_urls):
            retry += 1
            time.sleep(3)

        prev_len = len(keyword_urls)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results_groups = driver.find_elements_by_css_selector("div[style*='flex-direction']")
        results = []
        for group in results_groups:
            post_links = group.find_elements_by_tag_name("a")
            for link in post_links:
                try:
                    post_url = link.get_attribute('href')
                except Exception as e:
                    print(e)
                    continue
                if post_url not in [i['post_url'] for i in keyword_urls]:
                    keyword_urls.append({
                        'keyword': keyword,
                        'post_url': post_url
                    })

    keyword_urls = keyword_urls[:limit]
    print(keyword, len(keyword_urls), 'posts found')
    return keyword_urls

def get_page_details(driver, url, from_post=False, ignore=[]):
    """
    GET INSTAGRAM PAGE DETAILS
    Function: get_page_details(driver,url)
    Description: Gets the details of an instagram page.
    Arguments: 
        - driver : configured webdriver
        - shop_url : instagram page url
    Return Value: a `dict` which contains the page details:
        - 'ig_url' : instagram page url
        - 'shop_name' : instagram page username
        - 'posts' : number of posts
        - 'followers' : number of instagram page followers
        - 'website' : page has website link
    """
    page_details = {'ig_url': url}
    if from_post:
        driver.get(url)
        shop_url = driver.find_element_by_tag_name('header').find_element_by_tag_name('a').get_attribute('href')
        username = shop_url.split('/')[-2]
        page_details.update({
            'ig_url': shop_url,
            'username': username,
            'post_url': url
        })

    try:
        if page_details['ig_url'] in ignore:
            return {}

        #go to the ig shop main page
        driver.get(page_details['ig_url'])

        #wait for the element to be present for 5 seconds
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//main[@role="main"]/div/header')))
        print("Page details has been loaded")
        try:
            page_details['shop_name'] = driver.find_element_by_xpath('//header/section/div/h1').get_attribute('textContent')  
        except NoSuchElementException:
            page_details['shop_name'] = ''
        try:
            page_details['about'] = driver.find_element_by_xpath('//header/section/div/span').get_attribute('textContent')
        except NoSuchElementException:
            page_details['about'] = ''
        try:
            page_details['posts'] = driver.find_element_by_xpath('//header/section//li').get_attribute('textContent').split(' ')[0]
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

    #if an error occurred raise an ecception and return the page details    
    except Exception as e:
        print(e)
        return page_details

    return page_details


def get_latest_posts(driver, url, days=7, limit=30):
    """
    GET INSTAGRAM POST DETAILS
    Function: get_post_details(driver,url, limit)
    Description: Gets the latest posts of the facebook page.
    Arguments: 
        - driver : configured webdriver
        - url : instagram page url
        - limit: int arg to set the max limit posts to get per page
    Return Value: a `list` which contains the post details:
        - 'url' : instagram page url
        - 'publish_date' : page username
        - 'post_content' : text content of the post
        - 'likes' : number of post likes
        - 'post_link' : instagram post link
    """
    details = []
    driver.get(url)
    #go to the ig shop main page
    try:
        #wait for the element to be present for 5 seconds
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//article/div/div'))
            )
            num_posts_text = driver.find_element_by_xpath('//main//header//section//ul').text
            num_posts = float(num_posts_text.split(' posts')[0])
            post_container = driver.find_element_by_xpath(
                '//article/div/div[contains(@style, "flex-direction: column")]'
            )
        except:
            print('no posts found')
            return []

        limit_reached = False
        retry = 0
        max_retry = 10
        while not limit_reached:
            retry += 1
            posts = post_container.find_elements_by_xpath('.//a')
            if retry >= max_retry or len(posts) >= max(limit, num_posts):
                print('posts from last {} days loaded'.format(days))
                limit_reached = True
                break
            else:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

        print("Page posts has been loaded")

    except Exception as e:
        print('Could not load posts -', e)
        return []

    #get post links
    post_links = []
    for post in posts:
        try:
            post_links.append(post.get_attribute('href'))
        except NoSuchElementException:
            print("post link not found")

    #for each post link get go to the post page, then get the details
    for link in post_links:
        driver.get(link)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//article[@role="presentation"]')))
        try:
            likes = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/button/span').get_attribute('textContent')
        except NoSuchElementException:
            likes = ""
        try:
            publish_date = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[2]/a/time').get_attribute('datetime')
            publish_date = datetime.fromisoformat(publish_date[:-1])
            publish_date_str = publish_date.strftime('%m/%d/%Y')
        except NoSuchElementException:
            publish_date = ""
        try:
            post_content = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('textContent')
        except NoSuchElementException:
            post_content = ""

        details.append({
            'url' : url,
            'publish_date' : publish_date_str,
            'post_content' : post_content,
            'likes' : likes,
            'post_link' : link,
        })
        if (datetime.now() - publish_date).days > days:
            print('date limit reached')
            break

    return details
