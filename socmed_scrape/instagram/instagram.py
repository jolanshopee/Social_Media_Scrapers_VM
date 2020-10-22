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



def get_page_details(driver,url):
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
    try:
        #go to the ig shop main page
        driver.get(page_details['ig_url'])

        #wait for the element to be present for 5 seconds
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

    #if an error occurred raise an ecception and return the page details    
    except Exception as e:
        print(e)
        return page_details

    return page_details





def get_post_details(driver,url,limit):
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
    try:
        #go to the ig shop main page
        driver.get(url)
        #wait for the element to be present for 5 seconds
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//article/div/div')))
        
        #get the container element for all posts
        container = driver.find_element_by_xpath('//article/div/div[contains(@style, "flex-direction: column")]')
        #get the the number of posts based on the limit
        posts = container.find_elements_by_xpath('.//a')[:limit]
        print("Page posts has been loaded")

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
            except NoSuchElementException:
                publish_date = ""
            try:
                post_content = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('textContent')
            except NoSuchElementException:
                post_content = ""

            details.append({
                'url' : url,
                'publish_date' : datetime.fromisoformat(publish_date[:-1]).strftime('%m/%d/%Y'),
                'post_content' : post_content,
                'likes' : likes,
                'post_link' : link,  
            })
    #if an error occurred raise an ecception and return the details
    except Exception as e:
        print(e)
        return details

    return details