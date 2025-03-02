import os
import json
import random
import shutil
import datetime

from nltk import tokenize
from PIL import Image, ImageFont, ImageDraw

from oliark_llm import llm_reply
from oliark_io import json_read, json_write

from art_plant_benefit import gen_art_plant_benefits
from art_plant import gen_art_plant

from art_ailments import gen_art_ailments

import g
import components
import utils

vault = f'/home/ubuntu/vault'
g.WEBSITE_FOLDERPATH = 'website'

model_8b = f'/home/ubuntu/vault-tmp/llms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'
model_validator_filepath = f'llms/Llama-3-Partonus-Lynx-8B-Instruct-Q4_K_M.gguf'
model = model_8b

checkpoint_filepath = f'{vault}/stable-diffusion/checkpoints/juggernautXL_juggXIByRundiffusion.safetensors'

'''
vertices = json_read('vertices.json')
vertices_herbs = json_read('vertices-herbs.json')
vertices_preparations = json_read('vertices-preparations.json')
vertices_ailments = json_read('vertices-ailments.json')

edges = json_read('edges.json')
edges_ai = json_read('edges.json')

edges_families_orders_filepath = f'/home/ubuntu/vault/herbalism/edges-families-orders.json'
edges_families_orders = json_read(edges_families_orders_filepath)
edges_orders_subclasses_filepath = f'/home/ubuntu/vault/herbalism/edges-orders-subclasses.json'
edges_orders_subclasses = json_read(edges_orders_subclasses_filepath)
edges_subclasses_classes_filepath = f'/home/ubuntu/vault/herbalism/edges-subclasses-classes.json'
edges_subclasses_classes = json_read(edges_subclasses_classes_filepath)
edges_classes_divisions_filepath = f'/home/ubuntu/vault/herbalism/edges-classes-divisions.json'
edges_classes_divisions = json_read(edges_classes_divisions_filepath)

edges_plants_preparations_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-preparations.json'
edges_plants_preparations = json_read(edges_plants_preparations_filepath)

edges_plants_ailments_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-ailments.json'
edges_plants_ailments = json_read(edges_plants_ailments_filepath)
'''

vertices = []
vertices_herbs = []
vertices_preparations = []
vertices_ailments = []
edges = []
edges_ai = []
edges_families_orders_filepath = []
edges_families_orders = []
edges_orders_subclasses_filepath = []
edges_orders_subclasses = []

edges_subclasses_classes_filepath = f'/home/ubuntu/vault/herbalism/edges-subclasses-classes.json'
edges_subclasses_classes = json_read(edges_subclasses_classes_filepath)
edges_classes_divisions_filepath = f'/home/ubuntu/vault/herbalism/edges-classes-divisions.json'
edges_classes_divisions = json_read(edges_classes_divisions_filepath)
edges_plants_preparations_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-preparations.json'
edges_plants_preparations = json_read(edges_plants_preparations_filepath)
edges_plants_ailments_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-ailments.json'
edges_plants_ailments = json_read(edges_plants_ailments_filepath)
vertices_plants = json_read(f'{vault}/herbalism/vertices-plants.json')
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

equipments_slugs = os.listdir(f'{vault}/amazon/equipments/json')

##################################################################
# ;utils
##################################################################
def img_resize(img, w=768, h=768):
    start_size = img.size
    end_size = (w, h)
    if start_size[0] / end_size [0] < start_size[1] / end_size [1]:
        ratio = start_size[0] / end_size[0]
        new_end_size = (end_size[0], int(start_size[1] / ratio))
    else:
        ratio = start_size[1] / end_size[1]
        new_end_size = (int(start_size[0] / ratio), end_size[1])
    img = img.resize(new_end_size)
    w_crop = new_end_size[0] - end_size[0]
    h_crop = new_end_size[1] - end_size[1]
    area = (
        w_crop // 2, 
        h_crop // 2,
        new_end_size[0] - w_crop // 2,
        new_end_size[1] - h_crop // 2
    )
    img = img.crop(area)
    return img

###############################################
# ;AMAZON
###############################################
def affiliate_disclaimer_gen():
    html = ''
    html += f'''
        <p class="text-14 mb-0"><i>Disclaimer: We earn a commission if you click this link and make a purchase at no additional cost to you.</i></p>
    '''
    return html

def amazon_buy_button(url, img_filepath=''):
    try:
        with open(img_filepath) as f: html_img = f.read()
    except: 
        html_img = ''
    affiliate_disclaimer_html = affiliate_disclaimer_gen()
    if html_img == '':
        html = f'''
            <div class="bg-lightgray px-24 py-32">
                <a class="button-amazon mb-16 mt-16" href="{url}" target="_blank">Buy On Amazon</a>
                {affiliate_disclaimer_html}
            </div>
        '''
    else:
        html = f'''
            <div class="bg-lightgray px-24 py-24 mb-24">
                <div class="mob-flex gap-48 items-center">
                    <div>
                        {html_img}
                    </div>
                    <div>
                        <a class="button-amazon mb-16" href="{url}" target="_blank">Buy On Amazon</a>
                        {affiliate_disclaimer_html}
                    </div>
                </div>
            </div>
        '''
    return html


###############################################
# ;COMPONENTS
###############################################
def html_article_layout_gen(html_article):
    html = f'''
        <section class="container-md">
            <main class>
                {html_article}
            </main>
        </section>
    '''
    return html

###############################################
# ;utils
###############################################
def today():
    today = datetime.datetime.now()
    year = today.year
    month = today.month
    day = today.day
    today = f'{year}-{month}-{day}'
    print(today)
    return today

def html_menu_gen():
    html = ''
    html += f'<p><a href="/herbs.html">herbs</a></p>'
    html += f'<p><a href="/preparations.html">preparations</a></p>'
    html += f'<p><a href="/equipments.html">equipments</a></p>'
    html += f'<p><a href="/ailments.html">ailments</a></p>'
    return html
html_menu = html_menu_gen()


###############################################
# ;data
###############################################
def get_vertices_plants_validated():
    # verity herbs in "wcpo"
    vertices_plants_filtered_tmp = [vertex for vertex in vertices_plants if vertex['plant_slug'] in plants_slugs_filtered] 
    vertices_plants_filtered_tmp = sorted(vertices_plants_filtered_tmp, key=lambda x: x['plant_slug'], reverse=False)
    # remove duplicates
    vertices_plants_filtered = []
    for vertex_plant in vertices_plants_filtered_tmp:
        plant_slug = vertex_plant['plant_slug']
        found = False
        for _vertex_plant in vertices_plants_filtered:
            _plant_slug = _vertex_plant['plant_slug']
            if plant_slug == _plant_slug:
                found = True
                break
        if not found:
            vertices_plants_filtered.append(vertex_plant)
    return vertices_plants_filtered
    
def p_home():
    title = f'herbalism'
    html_head = components.html_head(title)
    html_section_hero = f'''
        <section class="container-xl mb-48">
            <h1>Learn Herbalism, Improve Lives.</h1>
        </section>
    '''
    # ;herbs
    html_cards = ''
    for vertex_herb in vertices_herbs[:4]:
        herb_slug = vertex_herb['herb_slug']
        herb_scientific_name = vertex_herb['herb_name_scientific']
        herb_img_filepath = f'/images/herbs/{vertex_herb["herb_slug"]}.jpg'
        html_card = f'''
            <a href="/herbs/{herb_slug}.html">
                <div>
                    <img class="mb-8" src="{herb_img_filepath}">
                    <h3 class="mt-0">{herb_scientific_name.capitalize()}</h3>
                </div>
            </a>
        '''
        html_cards += html_card
    html_section_herbs = f'''
        <section class="container-xl">
            <div class="flex justify-between items-center mb-16">
                <h2 class="mt-0 mb-0">Herbs</h2>
                <p class="mb-0"><a href="/herbs.html">All Herbs ></a></p>
            </div>
            <div class="grid-4 gap-48">
                {html_cards}
            </div>
        </section>
    '''
    # ;equipments
    html_cards = ''
    for equipment_slug in equipments_slugs[:4]:
        equipment_name = equipment_slug.replace('-', ' ')
        html_card = f'''
            <a href="/equipments/{equipment_slug}.html">
                <div>
                    <img class="mb-8" src="/images/equipments/{equipment_slug}.jpg">
                    <h3 class="mt-0">{equipment_name.capitalize()}</h3>
                </div>
            </a>
        '''
        html_cards += html_card
    html_section_equipments = f'''
        <section class="container-xl">
            <div class="flex justify-between items-center mb-16">
                <h2 class="mt-0 mb-0">Equipments</h2>
                <p class="mb-0"><a href="/equipments.html">All Equipments ></a></p>
            </div>
            <div class="grid-4 gap-48">
                {html_cards}
            </div>
        </section>
    '''
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_section_hero}
            {html_section_herbs}
            {html_section_equipments}
            {components.html_footer()}
        </body>
        </html>
    '''
    with open(f'{g.WEBSITE_FOLDERPATH}/index.html', 'w') as f:
        f.write(html)
    
def ai_paragraph_gen(filepath, data, obj, key, prompt, regen=False, print_prompt=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        if print_prompt: print(prompt)
        reply = llm_reply(prompt)
        if reply.strip() != '':
            if reply.strip().startswith('I can\'t'): reply = 'N/A'
            elif reply.strip().startswith('I couldn\'t'): reply = 'N/A'
            elif 'cannot' in reply: return
            elif 'N/A' in reply: reply = 'N/A'
            obj[key] = reply
            json_write(filepath, data)

def p_plants(regen=False):
    vertices_plants_filtered = get_vertices_plants_validated()
    json_article_filepath = f'database/pages/herbs.json'
    json_article = json_read(json_article_filepath, create=True)
    if 'plants' not in json_article: json_article['plants'] = []
    if regen: json_article['plants'] = []
    # json_article['plants'] = []
    for vertex_plant in vertices_plants_filtered:
        plant_slug = vertex_plant['plant_slug']
        plant_name_scientific = vertex_plant['plant_name_scientific']
        plant_names_common = [item['name'] for item in vertex_plant['plant_names_common']]
        plant_name_common = plant_names_common[0]
        # add if doesn't exist
        found = False
        for _obj in json_article['plants']:
            if plant_slug == _obj['plant_slug']:
                found = True
                break
        if not found:
            json_article['plants'].append({
                'plant_slug': plant_slug,
                'plant_name_scientific': plant_name_scientific,
                'plant_name_common': plant_name_common,
            })
            json_write(json_article_filepath, json_article)
        # update
        plant_obj = {}
        for _plant_obj in json_article['plants']:
            if plant_slug == _plant_obj['plant_slug']:
                plant_obj = _plant_obj
                break
        ai_paragraph_gen(
            key = 'plant_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = plant_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following medicinal herb: {plant_name_scientific}.
                Start the reply with the following words: {plant_name_scientific}, also known as {plant_name_common}, .
            ''',
            regen = False,
        )
    html_article = ''
    plants_num = len(vertices_plants_filtered)
    html_article += f'''<h1>{plants_num} Best Medicinal Herbs For Herbalists</h1>'''
    for i, plant in enumerate(json_article['plants']):
        plant_slug = plant['plant_slug']
        plant_name_scientific = plant['plant_name_scientific']
        plant_name_common = plant['plant_name_common']
        plant_desc = plant['plant_desc']
        html_article += f'<h2>{i+1}. {plant_name_scientific.capitalize()} ({plant_name_common})</h2>\n'
        html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
        html_article += f'{utils.text_format_sentences_html(plant_desc)}\n'
        html_article += f'<p><a href="/herbs/{plant_slug}.html">{plant_name_scientific}</a></p>\n'
    title = 'herbs'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    with open(f'{g.WEBSITE_FOLDERPATH}/herbs.html', 'w') as f:
        f.write(html)

def a_plant(vertex_plant):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_name_common = vertex_plant['plant_names_common'][0]['name']
    json_article_filepath = f'database/pages/herbs/{plant_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}.html'
    json_write(json_article_filepath, json_article)
    ai_paragraph_gen(
        key = 'taxonomy', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the taxonomy of {plant_name_scientific}.
            include the data below.
            - family: {vertex_plant['plant_family']}
            start with the following words: {plant_name_scientific}, commonly known as {plant_name_common}, is .
        ''',
        regen = False,
    )
    ai_paragraph_gen(
        key = 'identification', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the identification of {plant_name_scientific}.
        ''',
        regen = False,
    )
    # ailments_slugs = [edge['vertex_2'] for edge in edges_plants_ailments if edge['vertex_1'] == plant_slug]
    # ailments_slugs_prompt = ', '.join(ailments_slugs)[:5]

    ########################################################
    # ;html
    ########################################################
    html_article = ''
    html_article += f'<h1>{plant_name_scientific.capitalize()} ({plant_name_common})</h1>'
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    ## what is
    html_article += f'<h2>What is {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['taxonomy'])}\n'''
    html_article += f'<h3>What is the taxonomy of this plant?</h3>\n'
    plant_family = vertex_plant['plant_family']
    plant_order = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'family_order' and edge['vertex_1'] == plant_family)][0]
    plant_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'order_subclass' and edge['vertex_1'] == plant_order)][0]
    plant_class = [edge['vertex_2'] for edge in edges_subclasses_classes if (edge['edge_type'] == 'subclass_class' and edge['vertex_1'] == plant_subclass)][0]
    plant_division = [edge['vertex_2'] for edge in edges_classes_divisions if (edge['edge_type'] == 'class_division' and edge['vertex_1'] == plant_class)][0]
    html_article += f'<p>The taxonomy of {plant_name_scientific} is presented in the table below using the Linnaean system of classification.</p>\n'
    html_article += f'''
        <table>
            <tr>
                <th>Taxonomy</th>
                <th>Category</th>
            </tr>
            <tr>
                <td>Kingdom</td>
                <td>Plantae</td>
            </tr>
            <tr>
                <td>Division</td>
                <td>{plant_division.capitalize()}</td>
            </tr>
            <tr>
                <td>Class</td>
                <td>{plant_class.capitalize()}</td>
            </tr>
            <tr>
                <td>Subclass</td>
                <td>{plant_subclass.capitalize()}</td>
            </tr>
            <tr>
                <td>Order</td>
                <td>{plant_order.capitalize()}</td>
            </tr>
            <tr>
                <td>Family</td>
                <td>{plant_family.capitalize()}</td>
            </tr>
            <tr>
                <td>Genus</td>
                <td>{plant_name_scientific.split()[0].capitalize()}</td>
            </tr>
            <tr>
                <td>Species</td>
                <td>{plant_name_scientific.capitalize()}</td>
            </tr>
        </table>
    '''
    
    # edges_families_orders = json_read('edges-families-orders.json')
    # edges_orders_subclasses = json_read('edges-orders-subclasses.json')
    ### botanical illustration
    html_article += f'<h3>Is there a botanical illustation of this plant?</h3>\n'
    html_article += f'''<p>Yes, the following drawing shows a botanical illustration of {plant_name_scientific}.</p>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}-illustation.jpg" alt="{plant_name_scientific} botanical illustration">\n'''
    ### identification
    # html_article += f'<h3>How to identify this plant?</h3>\n'
    # html_article += f'''{util.text_format_1N1_html(json_article['identification'])}\n'''
    ## ;uses
    html_article += f'<h2>What are the most common uses of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['uses'])}\n'''
    html_article += f'''<p>The following list summarizes the most common ailments treated with this plant.</p>\n'''
    html_article += f'''<ul>\n'''
    for ailment_slug in ailments_slugs[:10]:
        ailment_name = [vertex['ailment_name'] for vertex in vertices_ailments if vertex['ailment_slug'] == ailment_slug][0]
        html_article += f'''<li>{ailment_name.capitalize()}</li>\n'''
    html_article += f'''</ul>\n'''
    ## ;benefits
    json_article_plant_benefit_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    json_article_plant_benefit = json_read(json_article_plant_benefit_filepath)
    plant_benefits_num = json_article_plant_benefit['main_lst_num']
    html_article += f'<h2>What are the benefits of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['benefits'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/benefit.html">{plant_benefits_num} most common benefits of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    json_article_plant_benefit_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    json_article_plant_benefit = json_read(json_article_plant_benefit_filepath)
    i = 0
    for plant_benefit in json_article_plant_benefit['plant_benefits']:
        plant_benefit_name = plant_benefit['name']
        plant_benefit_desc = plant_benefit['plant_benefit_desc']
        if plant_benefit_desc.strip() == '': continue
        html_article += f'''<li>{plant_benefit_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_benefits_num: break
    html_article += f'''</ul>\n'''
    ## ;properties
    json_article_plant_property_filepath = f'database/pages/herbs/{plant_slug}/property.json'
    json_article_plant_property = json_read(json_article_plant_property_filepath)
    plant_properties_num = json_article_plant_property['main_lst_num']
    html_article += f'<h2>What are the therapeutic properties of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['properties'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/property.html">{plant_properties_num} most common therapeutic properties of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_property in json_article_plant_property['plant_properties']:
        plant_property_name = plant_property['name']
        plant_property_desc = plant_property['desc']
        if plant_property_desc.strip() == '': continue
        html_article += f'''<li>{plant_property_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_properties_num: break
    html_article += f'''</ul>\n'''
    ## ;parts
    json_article_plant_part_filepath = f'database/pages/herbs/{plant_slug}/part.json'
    json_article_plant_part = json_read(json_article_plant_part_filepath)
    plant_parts_num = json_article_plant_part['main_lst_num']
    html_article += f'<h2>What are the medicinal parts of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['parts'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/part.html">{plant_parts_num} most important medicinal parts of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_part in json_article_plant_part['plant_parts']:
        plant_part_name = plant_part['name']
        plant_part_desc = plant_part['desc']
        if plant_part_desc.strip() == '': continue
        html_article += f'''<li>{plant_part_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_parts_num: break
    html_article += f'''</ul>\n'''
    ## ;constituents
    json_article_plant_constituent_filepath = f'database/pages/herbs/{plant_slug}/constituent.json'
    json_article_plant_constituent = json_read(json_article_plant_constituent_filepath)
    plant_constituents_num = json_article_plant_constituent['main_lst_num']
    html_article += f'<h2>What are the active constituents of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['constituents'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/constituent.html">{plant_constituents_num} most common constituents of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_constituent in json_article_plant_constituent['plant_constituents']:
        plant_constituent_name = plant_constituent['name']
        plant_constituent_desc = plant_constituent['desc']
        if plant_constituent_desc.strip() == '': continue
        html_article += f'''<li>{plant_constituent_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_constituents_num: break
    html_article += f'''</ul>\n'''
    ## ;preparations
    json_article_plant_preparation_filepath = f'database/pages/herbs/{plant_slug}/preparation.json'
    json_article_plant_preparation = json_read(json_article_plant_preparation_filepath)
    plant_preparation_num = json_article_plant_preparation['main_lst_num']
    html_article += f'<h2>What are the medicinal preparations of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['preparations'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/preparation.html">{plant_preparation_num} {plant_name_scientific.capitalize()} best medicinal preparations</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_preparation in json_article_plant_preparation['preparations']:
        plant_preparation_name = plant_preparation['preparation_name']
        plant_preparation_desc = plant_preparation['preparation_desc']
        if plant_preparation_desc.strip() == '': continue
        html_article += f'''<li>{plant_preparation_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_preparation_num: break
    html_article += f'''</ul>\n'''
    ## ;side effects
    json_article_plant_side_effect_filepath = f'database/pages/herbs/{plant_slug}/side-effect.json'
    json_article_plant_side_effect = json_read(json_article_plant_side_effect_filepath)
    plant_side_effect_num = json_article_plant_side_effect['main_lst_num']
    html_article += f'<h2>What are the side effects of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['side_effects'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/side-effect.html">{plant_side_effect_num} most common side effects of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    json_article_plant_side_effect_filepath = f'database/pages/herbs/{plant_slug}/side-effect.json'
    json_article_plant_side_effect = json_read(json_article_plant_side_effect_filepath)
    i = 0
    for plant_side_effect in json_article_plant_side_effect['plant_side_effects']:
        plant_side_effect_name = plant_side_effect['name']
        plant_side_effect_desc = plant_side_effect['plant_side_effect_desc']
        if plant_side_effect_desc.strip() == '': continue
        html_article += f'''<li>{plant_side_effect_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_side_effect_num: break
    html_article += f'''</ul>\n'''
    title = f'{plant_name_scientific}'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs')
    with open(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}.html', 'w') as f:
        f.write(html)

def a_plant_2(vertex_plant):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_name_common = vertex_plant['plant_names_common'][0]['name']
    json_article_filepath = f'database/pages/herbs/{plant_slug}.json'
    # ;json
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}.html'
    json_write(json_article_filepath, json_article)
    ai_paragraph_gen(
        key = 'taxonomy', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the taxonomy of {plant_name_scientific}.
            include the data below.
            - family: {vertex_plant['plant_family']}
            start with the following words: {plant_name_scientific}, commonly known as {plant_name_common}, is .
        ''',
        regen = False,
    )
    ai_paragraph_gen(
        key = 'identification', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the identification of {plant_name_scientific}.
        ''',
        regen = False,
    )
    ailments_slugs = [edge['vertex_2'] for edge in edges_plants_ailments if edge['vertex_1'] == plant_slug]
    ailments_slugs_prompt = ', '.join(ailments_slugs)[:5]
    ai_paragraph_gen(
        key = 'uses', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the ailments that the plant {plant_name_scientific} heals.
            In specific, tell that this plant heals the following ailments: {ailments_slugs_prompt}.
            Write one sentence for ailment.
            Start the reply with the following words: {plant_name_scientific.capitalize()} is used .
        ''',
        regen = False,
    )
    names = [item['name'] for item in vertex_plant['plant_benefits']]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'benefits', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the benefits of the plant {plant_name_scientific}.
            In specific, tell that the benefits of this plant are: {names_prompt}.
            Write one sentence for each benefit.
            Start the reply with the following words: {plant_name_scientific.capitalize()} can .
        ''',
        regen = False,
        print_prompt = True,
    )
    ## ;properties
    names = [item['name'] for item in vertex_plant['plant_properties']]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'properties', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the therapeutic properties of the plant {plant_name_scientific}.
            In specific, tell that the properties of this plant are: {names_prompt}.
            Write one sentence for each active property.
            Start the reply with the following words: {plant_name_scientific.capitalize()} has many therapeutic properties, such as .
        ''',
        regen = False,
        print_prompt = True,
    )
    ## ;constituents
    names = [item['name'] for item in vertex_plant['plant_constituents']]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'constituents', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the medicinal active constituents of the plant {plant_name_scientific}.
            In specific, tell that the active constituents of this plant are: {names_prompt}.
            Write one sentence for each active constituent.
            Start the reply with the following words: {plant_name_scientific.capitalize()} contains .
        ''',
        regen = False,
        print_prompt = True,
    )
    ## ;parts
    names = [item['name'] for item in vertex_plant['plant_parts']]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'parts', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the medicinal parts of the plant {plant_name_scientific}.
            In specific, tell that the parts of this plant are: {names_prompt}.
            Write one sentence for each active part.
            Start the reply with the following words: {plant_name_scientific.capitalize()} has several medicinal parts, such as .
        ''',
        regen = False,
        print_prompt = True,
    )
    ## ;preparations
    # names = [item['name'] for item in plant['plant_preparations']]
    names = [edge['vertex_2'] for edge in edges_plants_preparations if edge['vertex_1'] == plant_slug]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'preparations', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the herbal preparations of the plant {plant_name_scientific} for medicinal purposes.
            In specific, tell that the parts of this plant are: {names_prompt}.
            Write one sentence for each active part.
            Start the reply with the following words: {plant_name_scientific.capitalize()} has several herbal preparations, such as .
        ''',
        regen = False,
        print_prompt = True,
    )
    ## ;side_effects
    names = [item['name'] for item in vertex_plant['plant_side_effects']]
    names_prompt = ', '.join(names[:5])
    ai_paragraph_gen(
        key = 'side_effects', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the most common negative health side effects of the plant {plant_name_scientific}.
            In specific, tell that the side effects of this plant are: {names_prompt}.
            Write one sentence for each side effect.
            Start the reply with the following words: {plant_name_scientific.capitalize()} can .
        ''',
        regen = False,
        print_prompt = True,
    )
    ########################################################
    # ;html
    ########################################################
    html_article = ''
    html_article += f'<h1>{plant_name_scientific.capitalize()} ({plant_name_common})</h1>'
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    ## what is
    html_article += f'<h2>What is {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['taxonomy'])}\n'''
    html_article += f'<h3>What is the taxonomy of this plant?</h3>\n'
    plant_family = vertex_plant['plant_family']
    plant_order = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'family_order' and edge['vertex_1'] == plant_family)][0]
    plant_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'order_subclass' and edge['vertex_1'] == plant_order)][0]
    plant_class = [edge['vertex_2'] for edge in edges_subclasses_classes if (edge['edge_type'] == 'subclass_class' and edge['vertex_1'] == plant_subclass)][0]
    plant_division = [edge['vertex_2'] for edge in edges_classes_divisions if (edge['edge_type'] == 'class_division' and edge['vertex_1'] == plant_class)][0]
    html_article += f'<p>The taxonomy of {plant_name_scientific} is presented in the table below using the Linnaean system of classification.</p>\n'
    html_article += f'''
        <table>
            <tr>
                <th>Taxonomy</th>
                <th>Category</th>
            </tr>
            <tr>
                <td>Kingdom</td>
                <td>Plantae</td>
            </tr>
            <tr>
                <td>Division</td>
                <td>{plant_division.capitalize()}</td>
            </tr>
            <tr>
                <td>Class</td>
                <td>{plant_class.capitalize()}</td>
            </tr>
            <tr>
                <td>Subclass</td>
                <td>{plant_subclass.capitalize()}</td>
            </tr>
            <tr>
                <td>Order</td>
                <td>{plant_order.capitalize()}</td>
            </tr>
            <tr>
                <td>Family</td>
                <td>{plant_family.capitalize()}</td>
            </tr>
            <tr>
                <td>Genus</td>
                <td>{plant_name_scientific.split()[0].capitalize()}</td>
            </tr>
            <tr>
                <td>Species</td>
                <td>{plant_name_scientific.capitalize()}</td>
            </tr>
        </table>
    '''
    
    # edges_families_orders = json_read('edges-families-orders.json')
    # edges_orders_subclasses = json_read('edges-orders-subclasses.json')
    ### botanical illustration
    html_article += f'<h3>Is there a botanical illustation of this plant?</h3>\n'
    html_article += f'''<p>Yes, the following drawing shows a botanical illustration of {plant_name_scientific}.</p>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}-illustation.jpg" alt="{plant_name_scientific} botanical illustration">\n'''
    ### identification
    # html_article += f'<h3>How to identify this plant?</h3>\n'
    # html_article += f'''{util.text_format_1N1_html(json_article['identification'])}\n'''
    ## ;uses
    html_article += f'<h2>What are the most common uses of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['uses'])}\n'''
    html_article += f'''<p>The following list summarizes the most common ailments treated with this plant.</p>\n'''
    html_article += f'''<ul>\n'''
    for ailment_slug in ailments_slugs[:10]:
        ailment_name = [vertex['ailment_name'] for vertex in vertices_ailments if vertex['ailment_slug'] == ailment_slug][0]
        html_article += f'''<li>{ailment_name.capitalize()}</li>\n'''
    html_article += f'''</ul>\n'''
    ## ;benefits
    json_article_plant_benefit_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    json_article_plant_benefit = json_read(json_article_plant_benefit_filepath)
    plant_benefits_num = json_article_plant_benefit['main_lst_num']
    html_article += f'<h2>What are the benefits of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['benefits'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/benefit.html">{plant_benefits_num} most common benefits of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    json_article_plant_benefit_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    json_article_plant_benefit = json_read(json_article_plant_benefit_filepath)
    i = 0
    for plant_benefit in json_article_plant_benefit['plant_benefits']:
        plant_benefit_name = plant_benefit['name']
        plant_benefit_desc = plant_benefit['plant_benefit_desc']
        if plant_benefit_desc.strip() == '': continue
        html_article += f'''<li>{plant_benefit_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_benefits_num: break
    html_article += f'''</ul>\n'''
    ## ;properties
    json_article_plant_property_filepath = f'database/pages/herbs/{plant_slug}/property.json'
    json_article_plant_property = json_read(json_article_plant_property_filepath)
    plant_properties_num = json_article_plant_property['main_lst_num']
    html_article += f'<h2>What are the therapeutic properties of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['properties'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/property.html">{plant_properties_num} most common therapeutic properties of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_property in json_article_plant_property['plant_properties']:
        plant_property_name = plant_property['name']
        plant_property_desc = plant_property['desc']
        if plant_property_desc.strip() == '': continue
        html_article += f'''<li>{plant_property_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_properties_num: break
    html_article += f'''</ul>\n'''
    ## ;parts
    json_article_plant_part_filepath = f'database/pages/herbs/{plant_slug}/part.json'
    json_article_plant_part = json_read(json_article_plant_part_filepath)
    plant_parts_num = json_article_plant_part['main_lst_num']
    html_article += f'<h2>What are the medicinal parts of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['parts'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/part.html">{plant_parts_num} most important medicinal parts of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_part in json_article_plant_part['plant_parts']:
        plant_part_name = plant_part['name']
        plant_part_desc = plant_part['desc']
        if plant_part_desc.strip() == '': continue
        html_article += f'''<li>{plant_part_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_parts_num: break
    html_article += f'''</ul>\n'''
    ## ;constituents
    json_article_plant_constituent_filepath = f'database/pages/herbs/{plant_slug}/constituent.json'
    json_article_plant_constituent = json_read(json_article_plant_constituent_filepath)
    plant_constituents_num = json_article_plant_constituent['main_lst_num']
    html_article += f'<h2>What are the active constituents of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['constituents'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/constituent.html">{plant_constituents_num} most common constituents of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_constituent in json_article_plant_constituent['plant_constituents']:
        plant_constituent_name = plant_constituent['name']
        plant_constituent_desc = plant_constituent['desc']
        if plant_constituent_desc.strip() == '': continue
        html_article += f'''<li>{plant_constituent_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_constituents_num: break
    html_article += f'''</ul>\n'''
    ## ;preparations
    json_article_plant_preparation_filepath = f'database/pages/herbs/{plant_slug}/preparation.json'
    json_article_plant_preparation = json_read(json_article_plant_preparation_filepath)
    plant_preparation_num = json_article_plant_preparation['main_lst_num']
    html_article += f'<h2>What are the medicinal preparations of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['preparations'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/preparation.html">{plant_preparation_num} {plant_name_scientific.capitalize()} best medicinal preparations</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    i = 0
    for plant_preparation in json_article_plant_preparation['preparations']:
        plant_preparation_name = plant_preparation['preparation_name']
        plant_preparation_desc = plant_preparation['preparation_desc']
        if plant_preparation_desc.strip() == '': continue
        html_article += f'''<li>{plant_preparation_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_preparation_num: break
    html_article += f'''</ul>\n'''
    ## ;side effects
    json_article_plant_side_effect_filepath = f'database/pages/herbs/{plant_slug}/side-effect.json'
    json_article_plant_side_effect = json_read(json_article_plant_side_effect_filepath)
    plant_side_effect_num = json_article_plant_side_effect['main_lst_num']
    html_article += f'<h2>What are the side effects of {plant_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{util.text_format_1N1_html(json_article['side_effects'])}\n'''
    html_article += f'''<p>The following list summarizes the <a href="/herbs/{plant_slug}/side-effect.html">{plant_side_effect_num} most common side effects of {plant_name_scientific.capitalize()}</a>.</p>\n'''
    html_article += f'''<ul>\n'''
    json_article_plant_side_effect_filepath = f'database/pages/herbs/{plant_slug}/side-effect.json'
    json_article_plant_side_effect = json_read(json_article_plant_side_effect_filepath)
    i = 0
    for plant_side_effect in json_article_plant_side_effect['plant_side_effects']:
        plant_side_effect_name = plant_side_effect['name']
        plant_side_effect_desc = plant_side_effect['plant_side_effect_desc']
        if plant_side_effect_desc.strip() == '': continue
        html_article += f'''<li>{plant_side_effect_name.capitalize()}</li>\n'''
        i += 1
        if i >= plant_side_effect_num: break
    html_article += f'''</ul>\n'''
    title = f'{plant_name_scientific}'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs')
    with open(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}.html', 'w') as f:
        f.write(html)


def a_plant_uses(vertex_plant, regen, regen_return):
    plant_slug = vertex_plant['plant_slug']
    plant_name = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/use.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name'] = plant_name
    json_article['plant_url'] = f'herbs/{plant_slug}/use.html'
    if 'uses' not in json_article: json_article['uses'] = []
    json_write(json_article_filepath, json_article)
    # json
    uses_slugs = [edge['vertex_2'] for edge in edges_plants_ailments if edge['vertex_1'] == plant_slug]
    for use_slug in uses_slugs:
        use_name = use_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['uses']:
            if use_slug == _obj['use_slug']:
                found = True
                break
        if not found:
            json_article['uses'].append({'use_slug': use_slug})
            json_write(json_article_filepath, json_article)
        # update
        use_obj = {}
        for _use_obj in json_article['uses']:
            if use_slug == _use_obj['use_slug']:
                use_obj = _use_obj
                break
        ai_paragraph_gen(
            key = 'use_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = use_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the use of {plant_name} for {use_name}.
                Start with the following words: {plant_name} is .
            ''',
            regen = False,
        )
    # html
    html_article = ''
    html_article += f'<h1>{plant_name} uses</h1>'
    for use in json_article['uses']:
        use_slug = use['use_slug']
        use_name = use_slug.replace('-', ' ')
        use_desc = use['use_desc']
        html_article += f'<h2>{use_name}</h2>\n'
        html_article += f'<p>{use_desc}</p>\n'
        html_article += f'<p><a href="/ailments/{use_slug}.html">{use_name}</a></p>'
    title = f'{plant_name} uses'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/use.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/use.html', 'w') as f:
        f.write(html)

def a_plant_benefits(vertex_plant, regen=False, regen_return=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_names_common = vertex_plant['plant_names_common']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/benefit.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
    if regen_return:
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_names_common'] = plant_names_common
    json_article['plant_url'] = f'herbs/{plant_slug}/benefit.html'
    json_article['title'] = f'{plant_name_scientific} benefits'
    json_article['url'] = f'herbs/{plant_slug}/benefit'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # json
    # init benefits
    key = 'plant_benefits'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    json_article_benefits_names = [obj['name'] for obj in json_article['plant_benefits']]
    for vertex_plant_benefit in vertex_plant[key][:]:
        if vertex_plant_benefit['name'] not in json_article_benefits_names:
            json_article[key].append(vertex_plant_benefit)
            json_write(json_article_filepath, json_article)
    
    for obj in json_article['plant_benefits'][:]:
        plant_benefit_name = obj['name']
        ai_paragraph_gen(
            key = 'plant_benefit_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following benefit of {plant_name_scientific}: for {plant_benefit_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} {plant_benefit_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )
    # ;html
    title = json_article['title']
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} Best Benefits of {plant_name_scientific.title()}</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for plant_benefit in json_article['plant_benefits'][:]:
        if plant_benefit['plant_benefit_desc'].strip() == "": continue
        html_article += f'''<h2>{i+1}. {plant_benefit['name'].title()}</h2>\n'''
        html_article += f'''<p>{plant_benefit['plant_benefit_desc']}</p>\n'''
        i += 1
        if i >= json_article['main_lst_num']: break
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/benefit.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def a_plant_properties(vertex_plant, regen=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/property.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/property.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}/property.html'
    json_article['title'] = f'{plant_name_scientific} properties'
    json_article['url'] = f'herbs/{plant_slug}/property'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # json
    # init
    key = 'plant_properties'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    json_article_properties_names = [obj['name'] for obj in json_article['plant_properties']]
    for vertex in vertex_plant[key][:]:
        if vertex['name'] not in json_article_properties_names:
            json_article[key].append(vertex)
            json_write(json_article_filepath, json_article)
    
    for obj in json_article['plant_properties'][:]:
        plant_property_name = obj['name']
        ai_paragraph_gen(
            key = 'desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following therapeutic property of {plant_name_scientific}: {plant_property_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} is {plant_property_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )
    # html
    title = json_article['title']
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} {plant_name_scientific.title()} Best Therapeutic Properties</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for item in json_article['plant_properties'][:]:
        if item['desc'].strip() == "": continue
        html_article += f'''<h2>{i+1}. {item['name'].title()}</h2>\n'''
        html_article += f'''<p>{item['desc']}</p>\n'''
        i += 1
        if i >= json_article['main_lst_num']: break
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/property.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def a_plant_parts(vertex_plant, regen=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/part.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/part.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}/part.html'
    json_article['title'] = f'{plant_name_scientific} parts'
    json_article['url'] = f'herbs/{plant_slug}/part'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # json
    key = 'plant_parts'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    json_article_parts_names = [obj['name'] for obj in json_article['plant_parts']]
    for vertex in vertex_plant[key][:]:
        if vertex['name'] not in json_article_parts_names:
            json_article[key].append(vertex)
            json_write(json_article_filepath, json_article)
    for obj in json_article['plant_parts'][:]:
        plant_part_name = obj['name']
        ai_paragraph_gen(
            key = 'desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following medicinal parts of {plant_name_scientific}: {plant_part_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} {plant_part_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )
    # html
    title = json_article['title']
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} {plant_name_scientific.title()} Best Medicinal Parts</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for item in json_article['plant_parts'][:]:
        if item['desc'].strip() == "": continue
        html_article += f'''<h2>{i+1}. {item['name'].title()}</h2>\n'''
        html_article += f'''<p>{item['desc']}</p>\n'''
        i += 1
        if i >= json_article['main_lst_num']: break
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/part.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def a_plant_constituents(vertex_plant, regen=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/constituent.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/constituent.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}/constituent.html'
    json_article['title'] = f'{plant_name_scientific} constituents'
    json_article['url'] = f'herbs/{plant_slug}/constituent'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # json
    key = 'plant_constituents'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    json_article_constituents_names = [obj['name'] for obj in json_article['plant_constituents']]
    for vertex in vertex_plant[key][:]:
        if vertex['name'] not in json_article_constituents_names:
            json_article[key].append(vertex)
            json_write(json_article_filepath, json_article)
    for obj in json_article['plant_constituents'][:]:
        plant_constituent_name = obj['name']
        ai_paragraph_gen(
            key = 'desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following medicinal active constituent of {plant_name_scientific}: {plant_constituent_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} {plant_constituent_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )
    # html
    title = json_article['title']
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} {plant_name_scientific.title()} Best Active Constituents</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for item in json_article['plant_constituents'][:]:
        if item['desc'].strip() == "": continue
        html_article += f'''<h2>{i+1}. {item['name'].title()}</h2>\n'''
        html_article += f'''<p>{item['desc']}</p>\n'''
        i += 1
        if i >= json_article['main_lst_num']: break
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/constituent.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def a_plant_preparations(vertex_plant, regen=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/preparation.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/preparation.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}/preparation.html'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    if 'preparations' not in json_article: json_article['preparations'] = []
    json_write(json_article_filepath, json_article)
    # json
    preparations_slugs = [edge['vertex_2'] for edge in edges_plants_preparations if edge['vertex_1'] == plant_slug]
    for preparation_slug in preparations_slugs:
        preparation_name = preparation_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['preparations']:
            if preparation_slug == _obj['preparation_slug']:
                found = True
                break
        if not found:
            preparation_name = preparation_slug.lower().strip().replace('-', ' ')
            json_article['preparations'].append({
                'preparation_slug': preparation_slug,
                'preparation_name': preparation_name,
            })
            json_write(json_article_filepath, json_article)
        # update
        preparation_obj = {}
        for _preparation_obj in json_article['preparations']:
            if preparation_slug == _preparation_obj['preparation_slug']:
                preparation_obj = _preparation_obj
                break
        ai_paragraph_gen(
            key = 'preparation_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = preparation_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name_scientific} {preparation_name}.
                Start with the following words: {plant_name_scientific} {preparation_name} is .
            ''',
            regen = False,
        )
    # ;html
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} {plant_name_scientific.title()} Best Medicinal Preparations</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for preparation in json_article['preparations']:
        preparation_slug = preparation['preparation_slug']
        preparation_name = preparation['preparation_name']
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{i+1}. {preparation_name.capitalize()}</h2>\n'
        html_article += f'<p>{preparation_desc}</p>\n'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{plant_slug}.html">{preparation_name}</a></p>\n'
        i += 1
        if i >= json_article['main_lst_num']: break
    title = f'{plant_name_scientific} preparations'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/preparation.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def a_plant_side_effects(vertex_plant, regen=False):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article_filepath = f'database/pages/herbs/{plant_slug}/side-effect.json'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}/side-effect.html'
    if regen:
        try: os.remove(json_article_filepath)
        except: pass
        try: os.remove(html_article_filepath)
        except: pass
        return
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_url'] = f'herbs/{plant_slug}/side-effect.html'
    json_article['title'] = f'{plant_name_scientific} side effects'
    json_article['url'] = f'herbs/{plant_slug}/side-effect'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # json
    # init main list
    key = 'plant_side_effects'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    json_article_side_effects_names = [obj['name'] for obj in json_article['plant_side_effects']]
    for vertex_plant_side_effect in vertex_plant[key][:]:
        if vertex_plant_side_effect['name'] not in json_article_side_effects_names:
            json_article[key].append(vertex_plant_side_effect)
            json_write(json_article_filepath, json_article)
    
    for obj in json_article['plant_side_effects'][:]:
        plant_side_effect_name = obj['name']
        ai_paragraph_gen(
            key = 'plant_side_effect_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following side effect of the {plant_name_scientific} plant: {plant_side_effect_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} {plant_side_effect_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )
    # html
    title = json_article['title']
    html_article = ''
    html_article += f'''<h1>{json_article['main_lst_num']} Most Common Side Effects of {plant_name_scientific.title()}</h1>\n'''
    html_article += f'''<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'''
    i = 0
    for plant_side_effect in json_article['plant_side_effects'][:]:
        if plant_side_effect['plant_side_effect_desc'].strip() == "": continue
        html_article += f'''<h2>{i+1}. {plant_side_effect['name'].title()}</h2>\n'''
        html_article += f'''<p>{plant_side_effect['plant_side_effect_desc']}</p>\n'''
        i += 1
        if i >= json_article['main_lst_num']: break
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/side-effect.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}')
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def p_preparations():
    json_article_filepath = f'database/pages/preparations.json'
    json_article = json_read(json_article_filepath, create=True)
    # json
    if 'preparations' not in json_article: json_article['preparations'] = []
    for preparation in vertices_preparations:
        preparation_slug = preparation['preparation_slug']
        preparation_name = preparation_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['preparations']:
            if preparation_slug == _obj['preparation_slug']:
                found = True
                break
        if not found:
            json_article['preparations'].append({'preparation_slug': preparation_slug})
            json_write(json_article_filepath, json_article)
        # update
        preparation_obj = {}
        for _preparation_obj in json_article['preparations']:
            if preparation_slug == _preparation_obj['preparation_slug']:
                preparation_obj = _preparation_obj
                break
        ai_paragraph_gen(
            key = 'preparation_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = preparation_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {preparation_name}.
            ''',
        )
    # html
    html_article = ''
    html_article += f'<h1>preparations</h1>'
    for i, preparation in enumerate(json_article['preparations']):
        slug_plural = preparation['preparation_slug']
        name_plural = slug_plural.replace('-', ' ')
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{i+1}. {name_plural}</h2>'
        html_article += f'<p>{preparation_desc}</p>'
        html_article += f'<p><a href="/preparations/{slug_plural}.html">{name_plural}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'preparations'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'preparations.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/preparations'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/preparations')
    with open(f'{g.WEBSITE_FOLDERPATH}/preparations.html', 'w') as f:
        f.write(html)


def a_preparation(vertex_preparation):
    preparation_slug = vertex_preparation['preparation_slug']
    preparation_name_singular = vertex_preparation['preparation_name']
    preparation_name_plural = vertex_preparation['preparation_name_plural']
    json_article_filepath = f'database/pages/preparations/{preparation_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['preparation_slug'] = preparation_slug
    json_article['preparation_name_singular'] = preparation_name_singular
    json_article['preparation_name_plural'] = preparation_name_plural
    json_article['preparation_url'] = f'preparations/{preparation_slug}.html'
    json_write(json_article_filepath, json_article)
    plants_slugs = [edge['vertex_1'] for edge in edges_plants_preparations if edge['vertex_2'] == preparation_slug]
    plants = []
    for plant_slug in plants_slugs:
        plants = [vertex for vertex in vertices_plants if vertex['plant_slug'] == plant_slug]
        if plants != []:
            plant = plants[0]
            plants.append(plant)
    # json
    if 'plants' not in json_article: json_article['plants'] = []
    # json_article['plants'] = []
    for plant in plants:
        plant_slug = plant['plant_slug']
        plant_name_scientific = plant['plant_name_scientific']
        # add if doesn't exist
        found = False
        for _obj in json_article['plants']:
            if plant_slug == _obj['plant_slug']:
                found = True
                break
        if not found:
            json_article['plants'].append({'plant_slug': plant_slug, 'plant_name_scientific': plant_name_scientific})
            json_write(json_article_filepath, json_article)
        # update
        plant_obj = {}
        for _plant_obj in json_article['plants']:
            if plant_slug == _plant_obj['plant_slug']:
                plant_obj = _plant_obj
                break
        ai_paragraph_gen(
            key = 'plant_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = plant_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name_scientific} {preparation_name_singular}.
            ''',
        )
    # html
    html_article = ''
    html_article += f'<h1>{preparation_name_plural}</h1>'
    for plant in json_article['plants']:
        plant_slug = plant['plant_slug']
        plant_name_scientific = plant['plant_name_scientific']
        plant_desc = plant['plant_desc']
        html_article += f'<h2>{plant_name_scientific}</h2>'
        html_article += f'<p>{plant_desc}</p>'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{plant_slug}.html">{plant_name_scientific} {preparation_name_singular}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'{preparation_slug}'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'preparations/{preparation_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        </head>
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    with open(f'{g.WEBSITE_FOLDERPATH}/preparations/{preparation_slug}.html', 'w') as f:
        f.write(html)


def a_preparation_plants(preparation):
    preparation_slug = preparation['preparation_slug']
    plants_slugs = [edge['vertex_1'] for edge in edges_plants_preparations if edge['vertex_2'] == preparation_slug]
    for plant_slug in plants_slugs:
        preparation_slug = preparation['preparation_slug']
        preparation_name_singular = preparation_slug.replace('-', ' ')
        preparation_name_plural = preparation_slug.replace('-', ' ')
        plant_name = plant_slug.replace('-', ' ')
        json_article_filepath = f'database/pages/preparations/{preparation_slug}/{plant_slug}.json'
        json_article = json_read(json_article_filepath, create=True)
        json_article['preparation_slug'] = preparation_slug
        json_article['preparation_name_plural'] = preparation_name_plural
        json_article['preparation_name_singular'] = preparation_name_singular
        json_article['preparation_url'] = f'preparations/{preparation_slug}/{plant_slug}.html'
        json_write(json_article_filepath, json_article)
        # update
        ai_paragraph_gen(
            key = 'intro', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name} {preparation_name_singular}.
            ''',
        )
        key = 'uses' 
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name} {preparation_name_singular} medicinal uses.
                If you know the answer, start the answer with the following words: {plant_name} {preparation_name_singular} is used to .
                If you don't know the answer or can't answer, reply ONLY with the words: "N/A".
            ''',
            regen = False,
            print_prompt = True,
        )
        key = 'benefits' 
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name} {preparation_name_singular} health benefits.
                If you know the answer, start the answer with the following words: {plant_name} {preparation_name_singular} has health benefits such as .
                If you don't know the answer or can't answer, reply ONLY with the words: "N/A".
            ''',
            regen = False,
            print_prompt = True,
        )
        key = 'properties' 
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name} {preparation_name_singular} therapeutic properties.
                If you know the answer, start the answer with the following words: {plant_name} {preparation_name_singular} has therapeutic properties such as .
                If you don't know the answer or can't answer, reply ONLY with the words: "N/A".
            ''',
            regen = False,
            print_prompt = True,
        )
        key = 'side_effects' 
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {plant_name} {preparation_name_singular} health side effects.
                If you know the answer, start the answer with the following words: {plant_name} {preparation_name_singular} can have side effects such as .
                If you don't know the answer or can't answer, reply ONLY with the words: "N/A".
            ''',
            regen = False,
            print_prompt = True,
        )
        key = 'recipe' 
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about how to make {plant_name} {preparation_name_singular} for medicinal use.
                If you know the answer, start the answer with the following words: To make {plant_name} {preparation_name_singular} for medicinal use, .
                If you don't know the answer or can't answer, reply ONLY with the words: "N/A".
            ''',
            regen = False,
            print_prompt = True,
        )
        # ;html
        html_article = ''
        html_article += f'<h1>What To Know About Medicinal {plant_name.title()} {preparation_name_singular.title()}?</h1>\n'
        html_article += f'''<img src="/images/herbs-preparations/{plant_slug}-{preparation_slug}.jpg" alt="{plant_name} {preparation_name_singular}">\n'''
        html_article += f'<p>{json_article["intro"]}</p>\n'
        html_article += f'<h2>What are the medicinal uses of {plant_name.capitalize()} {preparation_name_singular}?</h2>\n'
        html_article += f'{util.text_format_1N1_html(json_article["uses"])}\n'
        html_article += f'<h2>What are the health benefits of {plant_name.capitalize()} {preparation_name_singular}?</h2>\n'
        html_article += f'{util.text_format_1N1_html(json_article["benefits"])}\n'
        html_article += f'<h2>What are the therapeutic properties of {plant_name.capitalize()} {preparation_name_singular}?</h2>\n'
        html_article += f'{util.text_format_1N1_html(json_article["properties"])}\n'
        html_article += f'<h2>How to make {plant_name.capitalize()} {preparation_name_singular} for medicinal use?</h2>\n'
        html_article += f'{util.text_format_1N1_html(json_article["recipe"])}\n'
        html_article += f'<h2>What are the health side effects of {plant_name.capitalize()} {preparation_name_singular}?</h2>\n'
        html_article += f'{util.text_format_1N1_html(json_article["side_effects"])}\n'
        html_article += f'<h2>What to know about the {plant_name.capitalize()} plant?</h2>\n'
        html_article += f'<p>The following link provides general info about the <a href="/herbs/{plant_slug}.html">{plant_name.capitalize()} plant</a>.</p>\n'
        title = f'{plant_slug} {preparation_slug}'
        html_head = components.html_head(title)
        html_breadcrumbs = components.breadcrumbs(f'preparations/{preparation_slug}/{plant_slug}.html')
        html_article_layout = html_article_layout_gen(html_article)
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
            {html_head}
            <body>
                {components.html_header()}
                {html_breadcrumbs}
                {html_article_layout}
                {components.html_footer()}
            </body>
            </html>
        '''
        if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/preparations/{preparation_slug}'): 
            os.mkdir(f'{g.WEBSITE_FOLDERPATH}/preparations/{preparation_slug}')
        with open(f'{g.WEBSITE_FOLDERPATH}/preparations/{preparation_slug}/{plant_slug}.html', 'w') as f:
            f.write(html)

def p_equipments(equipments_slugs):
    equipments_slugs_singular = [slug for slug in equipments_slugs]
    for i in range(len(equipments_slugs_singular)):
        if equipments_slugs_singular[i][-1] == 's': equipments_slugs_singular[i] = equipments_slugs_singular[i][:-1]
    # ;json
    url = f'equipments'
    title = f'Equipments for herbalists'
    json_article_filepath = f'database/pages/{url}.json'
    json_article = json_read(json_article_filepath, create=True)
    if 'lastmod' not in json_article: json_article['lastmod'] = today()
    json_article['title'] = title
    json_article['url'] = url
    json_write(json_article_filepath, json_article)
    # intro
    key = 'intro'
    if key not in json_article: json_article[key] = ''
    if 0: json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence short paragraph about the most common equipment used by herbalists to make herbal preparations.
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    # ;equipments
    for i, equipment_slug in enumerate(equipments_slugs):
        # init
        key = 'equipments'
        if key not in json_article: json_article[key] = []
        found = False
        for obj in json_article[key]:
            if obj['equipment_slug'] == equipment_slug:
                found = True
                break
        if not found:
            equipment = {'equipment_slug': equipment_slug}
            json_article[key].append(equipment)
        json_write(json_article_filepath, json_article)
        # update
        for obj in json_article['equipments']:
            if obj['equipment_slug'] == equipment_slug:
                equipment_name = equipment_slug.strip().lower().replace('-', ' ')
                obj['equipment_name'] = equipment_name
                obj['equipment_title'] = equipment_name
                json_write(json_article_filepath, json_article)
                # ;desc
                if 'equipment_desc' not in obj: obj['equipment_desc'] = ''
                # obj['equipment_desc'] = ''
                if obj['equipment_desc'] == '':
                    prompt = f'''
                        Write a 4-sentence short paragraph about {equipment_name} for herbalists.
                        Include what this equipment is, why it's used, how it's used, and when it's best to use it.
                    '''
                    reply = llm_reply(prompt, model).strip()
                    # json_data = json.loads(reply)
                    if reply.strip() != '':
                        obj['equipment_desc'] = reply
                        json_write(json_article_filepath, json_article)
    # ;html
    html_article = ''
    html_article += f'<h1>Equipments for Herbalists</h1>\n'
    src = f'/images/equipments/herbalists-equipments.jpg'
    alt = f'equipments for herbalists'
    html_article += f'''<img style="margin-bottom: 16px;" src="{src}" alt="{alt}">\n'''
    html_article += f'{util.text_format_1N1_html(json_article["intro"])}\n'
    for i, equipment in enumerate(json_article['equipments']):
        equipment_slug = equipment['equipment_slug']
        equipment_name = equipment_slug.replace('-', ' ')
        equipment_slug_singular = equipments_slugs_singular[i]
        equipment_name_singular = equipment_slug_singular.replace('-', ' ')
        equipment_desc = equipment['equipment_desc']
        html_article += f'<h2>{equipment_name_singular.title()}</h2>\n'
        html_article += f'<img style="margin-bottom: 16px;" src="/images/equipments/{equipment_slug}.jpg" alt="{equipment_name} for herbalism">\n'
        html_article += f'{util.text_format_1N1_html(equipment_desc)}\n'
        html_article += f'<p><b>Resources:</b></p>'
        html_article += f'<p><a href="/equipments/{equipment_slug_singular}.html">What to know about {equipment_name_singular} for herbalism</a></p>'
        html_article += f'<p><a href="/equipments/{equipment_slug_singular}/best.html">Best {equipment_name} for herbalists</a></p>'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'equipments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/equipments'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/equipments')
    with open(f'{g.WEBSITE_FOLDERPATH}/equipments.html', 'w') as f:
        f.write(html)


def a_equipment(equipment_slug):
    equipment_name = equipment_slug.replace('-', ' ')
    equipment_slug_singular = equipment_slug[:-1]
    url = f'equipments/{equipment_slug_singular}'
    html_article_filepath = f'{g.WEBSITE_FOLDERPATH}/{url}.html'
    json_article_filepath = f'database/pages/{url}.json'
    ###########################################
    # ;json
    ###########################################
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    key = 'intro'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence pargraph about the following equipment: {equipment_name} for herbalism. 
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    key = 'what'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence pargraph about the following equipment: {equipment_name} for herbalism. 
            Answer the following:
            - What are {equipment_name} for herbalism (give a definition).
            - What types of {equipment_name} are used by herbalists.
            - What materials of {equipment_name} are best suited for herbalists.
            - What are the historical and cultural significance of {equipment_name} in herbalism.
            Start the reply with the following words: {equipment_name} are . 
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    key = 'why'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence pargraph about the following equipment: {equipment_name} for herbalism. 
            Answer the following:
            - Why are {equipment_name} used in herbal medicine.
            - Which hebal praparations are made with the help of {equipment_name}.
            Start the reply with the following words: {equipment_name} are used in herbal medicine to . 
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    key = 'how'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence pargraph about the following equipment: {equipment_name} for herbalism. 
            Answer the following:
            - How to use {equipment_name} step-by-step for in herbal medicine.
            Start the reply with the following words: To use {equipment_name} . 
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    key = 'care'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 4-sentence pargraph about the following equipment: {equipment_name} for herbalism. 
            Answer the following:
            - cleaning {equipment_name} after use.
            - storing {equipment_name} to prevent wear an tear.
            - disinfecting {equipment_name} for repeated use.
            - knowing when to replace a worn-out {equipment_name}.
            Start the reply with the following words: To use {equipment_name} . 
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    ##################################################################
    # ;img
    ##################################################################
    out_filepath = f'{g.WEBSITE_FOLDERPATH}/images/equipments/{equipment_slug}.jpg'
    ast_filepath = f'assets/images/equipments/{equipment_slug}.jpg'
    # if os.path.exists(ost_filepath):
    if True:
        print(ast_filepath)
        print(out_filepath)
        image_w = 768
        image_h = 768
        pin_w = image_w
        pin_h = image_h
        img = Image.new(mode="RGB", size=(pin_w, pin_h), color='#ffffff')
        _img = Image.open(ast_filepath)
        img.paste(_img, (0, 0))
        img.save(out_filepath, format='JPEG', subsampling=0, quality=70)

    ###########################################
    # ;html
    ###########################################
    html_article = ''
    html_article += f'<h1>What to know about {equipment_name.title()} for herbalism?</h1>\n'
    src = f'/images/equipments/{equipment_slug}.jpg'
    alt = f'{equipment_name} for herbalists'
    html_article += f'''<img class="mb-16" src="{src}" alt="{alt}">\n'''
    html_article += f'{util.text_format_1N1_html(json_article["intro"])}\n'
    html_article += f'<h2>What are {equipment_name} for herbalism?</h2>\n'
    html_article += f'{util.text_format_1N1_html(json_article["what"])}\n'
    html_article += f'<h2>Why are {equipment_name} used in herbal medicine?</h2>\n'
    html_article += f'{util.text_format_1N1_html(json_article["why"])}\n'
    html_article += f'<h2>How to use {equipment_name} to make medicinal preparations?</h2>\n'
    html_article += f'{util.text_format_1N1_html(json_article["how"])}\n'
    html_article += f'<h2>How to care for {equipment_name}?</h2>\n'
    html_article += f'{util.text_format_1N1_html(json_article["care"])}\n'
    '''
    html_article += f'<h2>What are the best {equipment_name} for herbalists?</h2>\n'
    html_article += f'{util.text_format_1N1_html(json_article["best"])}\n'
    html_article += f'<p><a href="/{url}/best.html">best {equipment_name}</a></p>\n'
    '''
    title = f'{equipment_slug}'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'{url}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/equipments'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/equipments')
    with open(html_article_filepath, 'w') as f:
        f.write(html)


def a_equipment_best(equipment_slug):
    equipment_slug_plural = equipment_slug
    equipment_slug_singular = equipment_slug_plural[:-1]
    equipment_name_plural = equipment_slug_plural.replace('-', ' ')
    equipment_name_singular = equipment_slug_singular.replace('-', ' ')
    equipment_amazon = equipment_slug_plural
    json_products_folderpath = f'{vault}/amazon/json/{equipment_amazon}'
    json_article_filepath = f'database/pages/equipments/{equipment_slug_singular}/best.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['title'] = f'best {equipment_name_plural} for herbalists'
    json_article['equipment_slug'] = equipment_slug_singular
    json_article['equipment_name'] = equipment_name_singular
    json_article['equipment_name_plural'] = f'{equipment_name_plural}'
    json_article['url'] = f'equipments/{equipment_slug_singular}/best'
    if 'products_num' not in json_article: json_article['products_num'] = random.choice([7, 9, 11, 13])
    products_num = json_article['products_num']
    json_write(json_article_filepath, json_article)
    #################################################################
    # ;article_json
    #################################################################
    # ;intro
    key = 'intro'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 5-sentence pargraph about the following product: {equipment_name_singular} for apothecaries. 
            Include what this product is and why apothecaries use it.
            Reply in less than 100 words.
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    # order filepaths by popularity
    products_jsons_filepaths = [f'{json_products_folderpath}/{x}' for x in os.listdir(json_products_folderpath)]
    products_jsons = []
    for i, product_json_filepath in enumerate(products_jsons_filepaths):
        product_data = json_read(product_json_filepath, create=True)
        product_asin = product_json_filepath.split('/')[-1].replace('.json', '')
        reviews_score_total = float(product_data['reviews_score_total'])
        products_jsons.append({'product_asin': product_asin, 'reviews_score_total': reviews_score_total})
    products_jsons_ordered = sorted(products_jsons, key=lambda x: x['reviews_score_total'], reverse=True)
    products_jsons_filepaths_ordered = []
    for product_json in products_jsons_ordered:
        product_asin = product_json['product_asin']
        product_filepath = f'{json_products_folderpath}/{product_asin}.json'
        products_jsons_filepaths_ordered.append(product_filepath)
    products_jsons_filepaths_ordered = products_jsons_filepaths_ordered[:products_num]
    # ;product
    for i, product_json_filepath in enumerate(products_jsons_filepaths_ordered):
        product_data = json_read(product_json_filepath)
        product_aff_link = product_data['affiliate_link']
        product_title = product_data['title']
        product_asin = product_json_filepath.split('/')[-1].replace('.json', '')
        # init product
        key = 'products'
        if key not in json_article: json_article[key] = []
        found = False
        for obj in json_article[key]:
            if obj['product_id'] == product_asin:
                found = True
                break
        if not found:
            product = {'product_id': product_asin}
            json_article[key].append(product)
        json_write(json_article_filepath, json_article)
        # update product
        if 'products' not in json_article: json_article['products'] = []
        for obj in json_article['products']:
            if obj['product_id'] == product_asin:
                obj['product_title'] = product_title
                obj['product_aff_link'] = product_aff_link
                json_write(json_article_filepath, json_article)
                # ;title
                key = 'title_ai'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    prompt = f'''
                        Rewrite the following TITLE of a product using the following GUIDELINES: 
                        {product_title}
                        GUIDELINES:
                        Reply in less than 10 words.
                        Keep only the most important things for the TITLE.
                        Keep the name of the brand if present at the beginning of the TITLE.
                        Reply in the following JSON format: 
                        {{"title": "insert the rewritten title here"}} 
                        Only reply with the JSON.
                    '''
                    reply = llm_reply(prompt, model).strip()
                    # json_data = json.loads(reply)
                    try: json_data = json.loads(reply)
                    except: json_data = {}
                    if json_data != {}:
                        try: line = json_data['title']
                        except: continue
                        obj[key] = line
                        json_write(json_article_filepath, json_article)
                # ;pros
                key = 'pros'
                if key not in obj: obj[key] = []
                # obj[key] = []
                if obj[key] == []:
                    positive_reviews_text = ' '.join(product_data['reviews_5s'].split()[:5000])
                    outputs = []
                    prompt = f'''
                        Extract a list of the most mentioned and recurring key features from the following CUSTOMERS REVIEWS.
                        Also, follow the GUIDELINES below.
                        CUSTOMERS REVIEWS:
                        {positive_reviews_text}
                        GUIDELINES:
                        Write the features in 7-10 words.
                        Reply in the following JSON format: 
                        [
                            {{"feature": "write feature 1 here"}}, 
                            {{"feature": "write feature 2 here"}}, 
                            {{"feature": "write feature 3 here"}}, 
                            {{"feature": "write feature 4 here"}}, 
                            {{"feature": "write feature 5 here"}} 
                        ]
                        Only reply with the JSON.
                    '''
                    print(prompt)
                    reply = llm_reply(prompt, model).strip()
                    try: json_data = json.loads(reply)
                    except: json_data = {}
                    if json_data != {}:
                        for item in json_data:
                            try: line = item['feature']
                            except: continue
                            outputs.append(line)
                    obj[key] = outputs
                    json_write(json_article_filepath, json_article)
                # ;cons
                key = 'cons'
                if key not in obj: obj[key] = []
                # obj[key] = []
                if obj[key] == []:
                    negative_reviews_text = product_data['reviews_1s']
                    outputs = []
                    if negative_reviews_text.strip() != '':
                        prompt = f'''
                            Extract a list of the most mentioned and recurring complaints from the following CUSTOMERS REVIEWS.
                            Also, follow the GUIDELINES below.
                            CUSTOMERS REVIEWS:
                            {negative_reviews_text}
                            GUIDELINES:
                            Write the features in 7-10 words.
                            Reply in the following JSON format: 
                            [
                                {{"complaint": "write complaint 1 here"}}, 
                                {{"complaint": "write complaint 2 here"}}, 
                                {{"complaint": "write complaint 3 here"}}, 
                                {{"complaint": "write complaint 4 here"}}, 
                                {{"complaint": "write complaint 5 here"}} 
                            ]
                            Only reply with the JSON.
                        '''
                        reply = llm_reply(prompt, model).strip()
                        try: json_data = json.loads(reply)
                        except: json_data = {}
                        if json_data != {}:
                            for item in json_data:
                                try: line = item['complaint']
                                except: continue
                                outputs.append(line)
                    obj[key] = outputs
                    json_write(json_article_filepath, json_article)
                # ;description
                key = 'desc'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    pros = '\n'.join(obj['pros'])
                    cons = '\n'.join(obj['cons'])
                    prompt = f'''
                        Write a short 5-sentence paragraph about the following product: {equipment_name_singular}.
                        The target audience for this product is: apothecary.
                        Use the following INFO to describe the features, and use the GUIDELINES below.
                        INFO:
                        {pros}
                        GUIDELIES:
                        Reply in paragraph format.
                        Don't write conclusory statements, like sentences that starts with "overall", "in conclusion", "to summarize", etc...
                        Start writing the features from the first sentence.
                        Start with the following words: These {equipment_name_singular} .
                    '''
                    reply = llm_reply(prompt)
                    obj[key] = reply
                    json_write(json_article_filepath, json_article)
                # ;cons_description
                key = 'warn'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    cons = '\n'.join(obj['cons'])
                    prompt = f'''
                        Write 1 short sentence about some of the complaints a few users had about the following product: {equipment_name_singular}.
                        Pick a few of the most relevant COMPLAINTS from the list below to write the 1 short sentence.
                        COMPLAINTS:
                        {cons}
                        GUIDELIES:
                        Reply only in 1 sentence, pick only the number of complaints needed to fit in 1 sentence.
                        Reply in as few words as possible.
                        Reply in paragraph format.
                        Don't write conclusory statements, like sentences that starts with "overall", "in conclusion", "to summarize", etc...
                        Try to include only the complaints that are specific to the characteristics of the products, not complaints about exernal factors (like bad shipping, etc.).
                        Start with the following words: Some users .
                    '''
                    reply = llm_reply(prompt)
                    obj[key] = reply
                    json_write(json_article_filepath, json_article)
    #################################################################
    # ;article_html
    #################################################################
    title = f'{products_num} best {equipment_name_plural}'.title()
    html_article = ''
    html_article += f'<h1>{title}</h1>'
    html_article += f'{util.text_format_1N1_html(json_article["intro"])}\n'
    if 'products' not in json_article: json_article['products'] = []
    for i, obj in enumerate(json_article['products'][:products_num]):
        asin = obj['product_id']
        title = obj['title_ai']
        desc = obj['desc']
        pros = obj['pros']
        warn = obj['warn']
        product_aff_link = obj['product_aff_link']
        # product_aff_link = obj['product_aff_link']
        html_article += f'<h2>{i+1}. {title}</h2>\n'
        html_article += f'{util.text_format_1N1_html(desc)}\n'
        html_article += f'<p class="font-bold text-black">Key Features:</p>\n'
        html_article += f'<ul>\n'
        for item in pros[:5]:
            html_article += f'<li>{item}</li>\n'
        html_article += f'</ul>\n'
        html_article += f'<p class="font-bold text-black">Warnings:</p>\n'
        html_article += f'{util.text_format_1N1_html(warn)}\n'
        product_img_filepath = f'{vault}/amazon/images/{equipment_amazon}/{asin}.txt'
        amazon_button_html = amazon_buy_button(product_aff_link, product_img_filepath)
        html_article += amazon_button_html
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'equipments/{equipment_slug_singular}/best.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/style.css">
            <title>{title}</title>
        </head>
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/equipments/{equipment_slug_singular}'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/equipments/{equipment_slug_singular}')
    with open(f'{g.WEBSITE_FOLDERPATH}/equipments/{equipment_slug_singular}/best.html', 'w') as f:
        f.write(html)


def p_ailments():
    json_article_filepath = f'database/pages/ailments.json'
    json_article = json_read(json_article_filepath, create=True)
    if 'ailments' not in json_article: json_article['ailments'] = []
    for ailment in vertices_ailments:
        ailment_slug = ailment['ailment_slug']
        ailment_name = ailment['ailment_name']
        # add if doesn't exist
        found = False
        for _obj in json_article['ailments']:
            if ailment_slug == _obj['ailment_slug']:
                found = True
                break
        if not found:
            json_article['ailments'].append({'ailment_slug': ailment_slug})
            json_write(json_article_filepath, json_article)
        # update
        ailment_obj = {}
        for _ailment_obj in json_article['ailments']:
            if ailment_slug == _ailment_obj['ailment_slug']:
                ailment_obj = _ailment_obj
                break
        ai_paragraph_gen(
            key = 'ailment_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = ailment_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {ailment_name}.
            ''',
        )

    html_article = ''
    html_article += f'<h1>ailments</h1>'
    for i, ailment in enumerate(json_article['ailments']):
        ailment_slug = ailment['ailment_slug']
        ailment_name = ailment_slug.replace('-', ' ')
        ailment_desc = ailment['ailment_desc']
        html_article += f'<h2>{i+1}. {ailment_name}</h2>\n'
        html_article += f'<p>{ailment_desc}</p>\n'
        html_article += f'<p><a href="/ailments/{ailment_slug}.html">{ailment_name}</a></p>\n'
    title = 'ailments'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'ailments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    with open(f'{g.WEBSITE_FOLDERPATH}/ailments.html', 'w') as f:
        f.write(html)

def a_ailment(ailment):
    ailment_slug = ailment['ailment_slug']
    ailment_name = ailment['ailment_name']
    json_article_filepath = f'database/pages/ailments/{ailment_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['ailment_slug'] = ailment_slug
    json_article['ailment_name'] = ailment_name
    json_article['ailment_url'] = f'ailments/{ailment_slug}.html'
    json_write(json_article_filepath, json_article)
    # update
    sections = [
        ['1', 'intro', f'write a short 3-sentence paragraph about the ailment: {ailment_name}.', f''],
    ]
    for section in sections:
        if section[0] != '1': continue
        key = section[1]
        prompt = section[2]
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = prompt,
        )
    # html
    html_article = ''
    html_article += f'<h1>{ailment_name}</h1>'
    for section in sections:
        if section[0] != '1': continue
        section_name = section[1]
        section_desc = json_article[section_name]
        section_link = section[3]
        html_article += f'<h2>{section_name}</h2>'
        html_article += f'<p>{section_desc}</p>\n'
        if section_link.strip() != '':
            html_article += f'<p><a href="/ailments/{ailment_slug}/{section_link}.html">{section_name}</a></p>'
    title = f'{ailment_name}'
    html_head = components.html_head(title)
    html_breadcrumbs = components.breadcrumbs(f'ailments/{ailment_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {components.html_header()}
            {html_breadcrumbs}
            {html_article_layout}
            {components.html_footer()}
        </body>
        </html>
    '''
    if not os.path.exists(f'{g.WEBSITE_FOLDERPATH}/ailments'): 
        os.mkdir(f'{g.WEBSITE_FOLDERPATH}/ailments')
    with open(f'{g.WEBSITE_FOLDERPATH}/ailments/{ailment_slug}.html', 'w') as f:
        f.write(html)

p_home()

# herbs
if 0:
    vertices_plants_filtered = get_vertices_plants_validated()
    print(vertices_plants_filtered)
    regen = False
    regen_return = False
    if 1:
        for vertex_plant in vertices_plants_filtered:
            gen_art_plant_benefits(vertex_plant)
    if 0:
        for vertex_plant in vertices_plants_filtered:
            a_plant_uses(vertex_plant, regen=regen, regen_return=regen_return)
            # a_plant_benefits(vertex_plant, regen=regen, regen_return=regen_return)
            a_plant_properties(vertex_plant, regen=regen)
            a_plant_constituents(vertex_plant, regen=regen)
            a_plant_parts(vertex_plant, regen=regen)
            a_plant_preparations(vertex_plant, regen=regen)
            a_plant_side_effects(vertex_plant, regen=regen)
    if 1:
        for vertex_plant in vertices_plants_filtered:
            # a_plant(vertex_plant) # NOTE: not working anymore, use only for code reference
            gen_art_plant(vertex_plant)
    if 1:
        p_plants(regen=False)

# preparations
if 0:
    for i, preparation in enumerate(vertices_preparations):
        print(f'{i}/{len(vertices_preparations)}')
        a_preparation_plants(preparation)
        a_preparation(preparation)
    p_preparations()

# equipments
if 0:
    for i, equipment_slug in enumerate(equipments_slugs):
        a_equipment(equipment_slug)
        a_equipment_best(equipment_slug)
    p_equipments(equipments_slugs)

# ailments
if 1:
    if 1:
        # p_ailments()
        gen_art_ailments()
    if 0:
        for vertex_ailment in vertices_ailments:
            a_ailment(vertex_ailment)

shutil.copy('style.css', f'{g.WEBSITE_FOLDERPATH}/style.css')

