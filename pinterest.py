import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from oliark_io import json_read

username = 'martinpellizzer1990@gmail.com'
password = 'Newoliark1'

vault = '/home/ubuntu/vault'

proj_filepath_abs = '/home/ubuntu/proj/martinpellizzer-gen'

WAIT_SECONDS = 400

# options = Options()
# options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
# driver = webdriver.Firefox(executable_path=r'C:\drivers\geckodriver.exe', options=options)

driver = webdriver.Firefox()
driver.get('https://www.google.com')
driver.maximize_window()
driver.get("https://www.pinterest.com/login/")
time.sleep(10)
e = driver.find_element(By.XPATH, '//input[@id="email"]')
e.send_keys(username) 
time.sleep(10)
e = driver.find_element(By.XPATH, '//input[@id="password"]')
e.send_keys(password) 
time.sleep(10)
e = driver.find_element(By.XPATH, '//div[text()="Log in"]')
e.click()
time.sleep(30)

def pin_post(article_filepath):
    website_url = 'https://martinpellizzer.com'
    data = json_read(article_filepath)
    title = data['title'].title()
    url = data["url"]
    image_slug = data['url'].replace('/', '-')
    img_filepath = f'pinterest/images/{image_slug}.jpg'
    description = data['description']
    board_name = data['board_name']
    url = f'{website_url}/{data["url"]}.html'
    # LOG
    print('ARTICLE_FILEPATH: ' + article_filepath)
    print('TITLE: ' + title)
    print('URL: ' + url)
    print('IMG_FILEPATH: ' + img_filepath)
    print('DESCRIPTION: ' + description)
    driver.get("https://www.pinterest.com/pin-creation-tool/")
    time.sleep(10)
    e = driver.find_element(By.XPATH, '//input[@id="storyboard-upload-input"]')
    img_filepath_formatted = img_filepath
    e.send_keys(f'{proj_filepath_abs}/{img_filepath_formatted}') 
    time.sleep(10)
    e = driver.find_element(By.XPATH, '//input[@id="storyboard-selector-title"]')
    e.send_keys(title)
    time.sleep(5) 
    e = driver.find_element(By.XPATH, "//div[@class='notranslate public-DraftEditor-content']")
    for c in description:
        e.send_keys(c)
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//input[@id="WebsiteField"]')
    e.send_keys(url) 
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//div[@data-test-id="board-dropdown-select-button"]')
    e.click()
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//input[@id="pickerSearchField"]')
    e.send_keys(board_name) 
    time.sleep(5)
    e = driver.find_element(By.XPATH, f'//div[@data-test-id="board-row-{board_name}"]')
    e.click()
    time.sleep(5)
    e = driver.find_element(By.XPATH, '//div[@data-test-id="storyboard-creation-nav-done"]/..')
    e.click()
    time.sleep(60)
    random_time_to_wait = random.randint(-60, 60)
    time_to_wait = WAIT_SECONDS + random_time_to_wait
    time.sleep(time_to_wait)



jsons_filenames = os.listdir(f'pinterest/pins')
jsons_filenames = sorted(jsons_filenames)
i = 0
for json_filename in jsons_filenames:
    json_filepath = f'pinterest/pins/{json_filename}'
    print(f'{i}/{len(jsons_filenames)} >> {json_filepath}')
    i += 1
    pin_post(json_filepath)



