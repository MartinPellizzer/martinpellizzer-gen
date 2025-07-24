import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from lib import io
from lib import data
from lib import utils

driver = webdriver.Firefox()
driver.get('https://www.google.com')
driver.maximize_window()
driver.get("https://powo.science.kew.org")
time.sleep(10)

plants = data.plants_wcvp_get()

def taxonomy():
    key = 'taxonomy'
    if key not in json_article: json_article[key] = {}
    # json_article[key] = {}
    if json_article[key] == {}:
        kingdom = ''
        phylum = ''
        _class = ''
        subclass = ''
        order = ''
        family = ''
        genus = ''
        species = ''
        i += 1
        driver.get(f"https://powo.science.kew.org/results?q={plant_name_scientific}")
        time.sleep(5)
        try:
            elements = driver.find_elements(By.XPATH, '//article')
        except:
            json_article[key]['kingdom'] = kingdom
            json_article[key]['phylum'] = phylum
            json_article[key]['class'] = _class
            json_article[key]['subclass'] = subclass
            json_article[key]['order'] = order
            json_article[key]['family'] = family
            json_article[key]['genus'] = genus
            json_article[key]['species'] = species
            io.json_write(json_article_filepath, json_article)
            time.sleep(5)
            continue
        found = False
        for e in elements:
            if plant_name_scientific.lower() in e.text.lower():
                e.click()
                time.sleep(5)
                found = True
                break
        if not found:
            continue
        elements = driver.find_elements(By.XPATH, '//ul[@class="c-classification-list"]//li')
        for e in elements:
            text = e.text
            if 'Kingdom' in text:
                kingdom = text.replace('Kingdom', '').strip()
                continue
            elif 'Phylum' in text:
                phylum = text.replace('Phylum', '').strip()
                continue
            elif 'Class' in text:
                _class = text.replace('Class', '').strip()
                continue
            elif 'Subclass' in text:
                subclass = text.replace('Subclass', '').strip()
                continue
            elif 'Order' in text:
                order = text.replace('Order', '').strip()
                continue
            elif 'Family' in text:
                family = text.replace('Family', '').strip()
                continue
            elif 'Genus' in text:
                genus = text.replace('Genus', '').strip()
                continue
            elif 'Species' in text:
                species = text.replace('Species', '').strip()
                continue
                
        print(f'Kingdom: {kingdom}')
        print(f'Phylum: {phylum}')
        print(f'Class: {_class}')
        print(f'Subclass: {subclass}')
        print(f'Order: {order}')
        print(f'Family: {family}')
        print(f'Genus: {genus}')
        print(f'Species: {species}')
        print()
        
        #######################################################################
        # json
        #######################################################################
        json_article[key]['kingdom'] = kingdom
        json_article[key]['phylum'] = phylum
        json_article[key]['class'] = _class
        json_article[key]['subclass'] = subclass
        json_article[key]['order'] = order
        json_article[key]['family'] = family
        json_article[key]['genus'] = genus
        json_article[key]['species'] = species
        io.json_write(json_article_filepath, json_article)

def browse_plant_page(plant_name_scientific):
    driver.get(f"https://powo.science.kew.org/results?q={plant_name_scientific}")
    time.sleep(5)
    try:
        elements = driver.find_elements(By.XPATH, '//article')
    except:
        time.sleep(5)
        return False
    found = False
    for e in elements:
        if plant_name_scientific.lower() in e.text.lower():
            e.click()
            time.sleep(5)
            found = True
            break
    if not found:
        return False
    return True
    

def distribution_native(plant_name_scientific, regen=False):
    plant_slug = utils.sluggify(plant_name_scientific)
    json_article_filepath = f'{plants_folderpath}/{plant_slug}.json'
    json_article = io.json_read(json_article_filepath, create=True)
    ###
    key = 'distribution_native'
    if key not in json_article: json_article[key] = None
    if regen: json_article[key] = None
    if json_article[key] == None:
        native_to_list = []
        try: 
            e = driver.find_element(By.XPATH, '//h3[text()="Native to:"]/following-sibling::p')
            native_to_list = [x.strip() for x in e.text.split(',')]
        except: 
            pass
        json_article[key] = native_to_list
        io.json_write(json_article_filepath, json_article)

def distribution_introduced(plant_name_scientific, regen=False):
    plant_slug = utils.sluggify(plant_name_scientific)
    json_article_filepath = f'{plants_folderpath}/{plant_slug}.json'
    json_article = io.json_read(json_article_filepath, create=True)
    ###
    key = 'distribution_introduced'
    if key not in json_article: json_article[key] = None
    if regen: json_article[key] = None
    if json_article[key] == None:
        native_to_list = []
        try: 
            e = driver.find_element(By.XPATH, '//h3[text()="Introduced into:"]/following-sibling::p')
            native_to_list = [x.strip() for x in e.text.split(',')]
        except: 
            pass
        json_article[key] = native_to_list
        io.json_write(json_article_filepath, json_article)


start_i = 23894
i = start_i
for plant_i, plant_name_scientific in enumerate(plants[start_i:30000]):
    print(f'{i} - {plant_name_scientific}')
    # if i >= 5: break
    if len(plant_name_scientific.split()) < 2: continue
    first_char = plant_name_scientific.lower().strip()[0]
    if first_char.isalpha():
        plants_folderpath = f'plants-{first_char}'
        
        page_found = browse_plant_page(plant_name_scientific)
        if not page_found: continue

        distribution_native(plant_name_scientific, regen=True)
        distribution_introduced(plant_name_scientific, regen=True)
        json_article_filepath = f'{plants_folderpath}/{plant_slug}.json'
        print(json_article_filepath)

    i += 1
