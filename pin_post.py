import os
import re
import csv
import time
import random
import pickle
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from lib import g
from lib import io

project_name = 'martinpellizzer'

with open(f'/home/ubuntu/vault/{project_name}/accounts/pinterest-username.txt') as f: username = f.read().strip()
with open(f'/home/ubuntu/vault/{project_name}/accounts/pinterest-password.txt') as f: password = f.read().strip()

proj_filepath_abs = '/home/ubuntu/proj/terrawhisper-compiler'

random_num = random.randint(-2, 2)
ARTICLES_NUM = 40 - random_num
WAIT_SECONDS = 400
NUM_TINCTURES = 8

# options = Options()
# options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
# driver = webdriver.Firefox(executable_path=r'C:\drivers\geckodriver.exe', options=options)

geckodriver_path = 'geckodriver'
driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)

driver = webdriver.Firefox(service=driver_service)
driver.get('https://www.google.com')
driver.maximize_window()

driver.get("https://www.pinterest.com/login/")
time.sleep(10)

COOKIE_FILEPATH = 'cookies.plk'
if os.path.exists(COOKIE_FILEPATH):
    print(COOKIE_FILEPATH)
    with open(COOKIE_FILEPATH, 'rb') as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            print(cookie)
            if 'sameSite' in cookie:
                del cookie['sameSite']
            try: 
                driver.add_cookie(cookie)
                print(f"**********************************************************")
                print(f"Adding cookie: {cookie.get('name')}")
                print(f"**********************************************************")
            except Exception as e:
                print(f"Skipping cookie: {cookie.get('name')} - {e}")
    # driver.refresh()
    driver.get("https://www.pinterest.com")
    time.sleep(10)
else:
    e = driver.find_element(By.XPATH, '//input[@type="email"]')
    e.send_keys(username) 
    time.sleep(10)
    e = driver.find_element(By.XPATH, '//input[@id="password"]')
    e.send_keys(password) 
    time.sleep(10)
    e = driver.find_element(By.XPATH, '//div[text()="Log in"]')
    e.click()
    time.sleep(60)
    cookies = driver.get_cookies()
    with open(COOKIE_FILEPATH, 'wb') as f:
        pickle.dump(cookies, f)

def pin_post(article_filepath):
    global failed_pins_num
    data = io.json_read(article_filepath)
    title = data['title'].title()
    url = data["url"]
    img_filepath = data['img_filepath']
    description = data['description']
    board_name = data['board_name']
    # LOG
    print('ARTICLE_FILEPATH: ' + article_filepath)
    print('TITLE: ' + title)
    print('URL: ' + url)
    print('IMG_FILEPATH: ' + img_filepath)
    print('DESCRIPTION: ' + description)
    try:
        driver.get("https://www.pinterest.com/pin-creation-tool/")
    except:
        failed_pins_num += 1
        return
    time.sleep(10)
    try:
        e = driver.find_element(By.XPATH, '//input[@id="storyboard-upload-input"]')
    except:
        failed_pins_num += 1
        return
    img_filepath_formatted = img_filepath
    e.send_keys(f'{img_filepath_formatted}') 
    time.sleep(10)
    e = driver.find_element(By.XPATH, '//input[@id="storyboard-selector-title"]')
    e.send_keys(title)
    time.sleep(5) 
    e = driver.find_element(By.XPATH, "//div[@class='notranslate public-DraftEditor-content']")
    for c in description:
        try: e.send_keys(c)
        except: break
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//input[@id="WebsiteField"]')
    e.send_keys(url) 
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//div[@data-test-id="board-dropdown-select-button"]')
    e.click()
    time.sleep(30)
    try:
        e = driver.find_element(By.XPATH, '//input[@id="pickerSearchField"]')
        e.send_keys(board_name) 
    except:
        failed_pins_num += 1
        return
    time.sleep(5)
    e = driver.find_element(By.XPATH, f'//div[@data-test-id="board-row-{board_name}"]')
    e.click()
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//div[@data-test-id="storyboard-creation-nav-done"]/..')
    e.click()
    time.sleep(60)

failed_pins_num = 0
jsons_filenames = os.listdir(f'{g.pinterest_tmp_image_folderpath}/pins')
for i in range(len(jsons_filenames)): 
    # if i < 3: continue
    found = False
    article_filename = ''
    for _json_filename in jsons_filenames:
        json_n = int(_json_filename.split('.')[0])
        if json_n == i:
            found = True
            article_filename = _json_filename
            break
    if found and article_filename != '':
        article_filepath = f'{g.pinterest_tmp_image_folderpath}//pins/{article_filename}'
        print(f'{i}/{len(jsons_filenames)} >> {article_filepath}')
        pin_post(article_filepath)
        ###
        random_time_to_wait = random.randint(-60, 60)
        time_to_wait = WAIT_SECONDS + random_time_to_wait
        time.sleep(time_to_wait)
print(f'FAILED PINS NUM: {failed_pins_num}')
