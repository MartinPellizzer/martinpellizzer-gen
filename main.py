import os
import json
import random
import shutil

from nltk import tokenize

from oliark_llm import llm_reply
from oliark_io import json_read, json_write

vault = f'/home/ubuntu/vault'
website_folderpath = 'website'

model_8b = f'/home/ubuntu/vault-tmp/llms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'
model_validator_filepath = f'llms/Llama-3-Partonus-Lynx-8B-Instruct-Q4_K_M.gguf'
model = model_8b

vertices = json_read('vertices.json')
edges = json_read('edges.json')



###############################################
# ;COMPONENTS
###############################################
html_header = f'''
    <header class="container-xl flex justify-between">
        <a class="no-underline" href="/">Martin Pellizzer</a>
        <nav class="flex gap-16">
            <a class="no-underline" href="/herbs.html">Herbs</a>
            <a class="no-underline" href="/preparations.html">Preparations</a>
            <a class="no-underline" href="/equipments.html">Equipments</a>
            <a class="no-underline" href="/ailments.html">Ailments</a>
        </nav>
    </header>
'''

html_footer = f'''
    <footer class="container-xl flex justify-between">
        <span>martinpellizzer.com | all rights reserved</span>
        <nav class="flex gap-16">
            <a class="no-underline" href="/">About</a>
            <a class="no-underline" href="/">Contact</a>
        </nav>
    </footer>
'''

def html_head_gen(title):
    html = f'''
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/style.css">
            <title>{title}</title>
        </head>
    '''
    return html

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
# ;UTIL FORMAT
###############################################
def text_format_1N1_html(text):
    text_formatted = ''
    text = text.replace('var.', 'var,')
    lines_tmp = tokenize.sent_tokenize(text)
    lines = []
    for line in lines_tmp:
        line = line.replace('var,', 'var.')
        lines.append(line)
    lines_num = len(lines[1:-1])
    paragraphs = []
    if lines_num > 0: 
        paragraphs.append(lines[0])
    else:
        text_formatted += f'<p>{text}.</p>' + '\n'
        text_formatted = text_formatted.replace('..', '.')
        return text_formatted
    if lines_num > 3: 
        paragraphs.append('. '.join(lines[1:lines_num//2+1]))
        paragraphs.append('. '.join(lines[lines_num//2+1:-1]))
    else:
        paragraphs.append('. '.join(lines[1:-1]))
    paragraphs.append(lines[-1])
    for paragraph in paragraphs:
        if paragraph.strip() != '':
            text_formatted += f'<p>{paragraph}.</p>' + '\n'
    text_formatted = text_formatted.replace('..', '.')
    return text_formatted

###############################################
# ;UTIL COMPONENT
###############################################
def breadcrumbs_gen(filepath):
    breadcrumbs = ['<a class="no-underline" href="/">Home</a>']
    breadcrumbs_path = filepath.replace('website/', '')
    chunks = breadcrumbs_path.split('/')
    filepath_curr = ''
    for chunk in chunks[:-1]:
        filepath_curr += f'/{chunk}'
        chunk = chunk.strip().replace('-', ' ').title()
        breadcrumbs.append(f'<a class="no-underline" href="{filepath_curr}.html">{chunk}</a>')
    breadcrumbs = ' | '.join(breadcrumbs)
    breadcrumbs += f' | {chunks[-1].strip().replace(".html", "").replace("-", " ").title()}'
    breadcrumbs_section = f'''
        <section class="container-xl py-24">
            {breadcrumbs}
        </section>
    '''
    return breadcrumbs_section

def html_menu_gen():
    html = ''
    html += f'<p><a href="/herbs.html">herbs</a></p>'
    html += f'<p><a href="/preparations.html">preparations</a></p>'
    html += f'<p><a href="/equipments.html">equipments</a></p>'
    html += f'<p><a href="/ailments.html">ailments</a></p>'
    return html
html_menu = html_menu_gen()

def p_home():
    html_article = ''
    title = f'herbalism'
    html_head = html_head_gen(title)
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/index.html', 'w') as f:
        f.write(html)
    
def ai_paragraph_gen(filepath, data, obj, key, prompt, regen=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        reply = llm_reply(prompt)
        if reply.strip() != '':
            obj[key] = reply
            json_write(filepath, data)

def p_herbs(herbs_slugs):
    json_article_filepath = f'database/pages/herbs.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    if 'herbs' not in json_article: json_article['herbs'] = []
    for herb_slug in herbs_slugs:
        herb_name = herb_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['herbs']:
            if herb_slug == _obj['herb_slug']:
                found = True
                break
        if not found:
            json_article['herbs'].append({'herb_slug': herb_slug})
            json_write(json_article_filepath, json_article)
        # update
        herb_obj = {}
        for _herb_obj in json_article['herbs']:
            if herb_slug == _herb_obj['herb_slug']:
                herb_obj = _herb_obj
                break
        ai_paragraph_gen(
            key = 'herb_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = herb_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name}.
            ''',
        )

    html_article = ''
    html_article += f'<h1>herbs</h1>'
    for i, herb in enumerate(json_article['herbs']):
        herb_slug = herb['herb_slug']
        herb_name = herb_slug.replace('-', ' ')
        herb_desc = herb['herb_desc']
        html_article += f'<h2>{i+1}. {herb_name}</h2>\n'
        html_article += f'<p>{herb_desc}</p>\n'
        html_article += f'<p><a href="/herbs/{herb_slug}.html">{herb_name}</a></p>\n'
    title = 'herbs'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/herbs.html', 'w') as f:
        f.write(html)


def a_herb(herb):
    herb_slug = herb['herb_slug']
    herb_name = herb_slug.replace('-', ' ')
    json_article_filepath = f'database/pages/herbs/{herb_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name'] = herb_name
    json_article['herb_url'] = f'herbs/{herb_slug}.html'
    json_write(json_article_filepath, json_article)
    # update
    sections = [
        ['1', 'identification', f'write a short 3-sentence paragraph about the identification of {herb_name}.', f''],
        ['1', 'taxonomy', f'write a short 3-sentence paragraph about the taxonomy of {herb_name}.', f''],
        ['0', 'botany', f'write a short 3-sentence paragraph about the botanical characteristics of {herb_name}.', f''],

        ['1', 'uses', f'write a short 3-sentence paragraph about the medicinal uses of {herb_name}.', f''],
        ['1', 'benefits', f'write a short 3-sentence paragraph about the benefits of {herb_name}.', f'benefit'],
        ['1', 'properties', f'write a short 3-sentence paragraph about the therapeutic properties of {herb_name}.', f''],
        ['1', 'constituents', f'write a short 3-sentence paragraph about the active constituents of {herb_name}.', f''],
        ['1', 'parts', f'write a short 3-sentence paragraph about the parts of {herb_name}.', f''],
        ['1', 'preparations', f'write a short 3-sentence paragraph about the preparations of {herb_name}.', f'preparation'],
        ['1', 'side-effects', f'write a short 3-sentence paragraph about the side effects of {herb_name}.', f''],


        ['0', 'distribution', f'write a short 3-sentence paragraph about the distribution of {herb_name}.', f''],
        ['0', 'native', f'write a short 3-sentence paragraph about the native range of {herb_name}.', f''],
        ['0', 'habitat', f'write a short 3-sentence paragraph about the habitat of {herb_name}.', f''],

        ['1', 'cultivation', f'write a short 3-sentence paragraph about the cultivation of {herb_name}.', f''],
        ['0', 'growing-conditions', f'write a short 3-sentence paragraph about the growing conditions of {herb_name}.', f''],
        ['0', 'germination', f'write a short 3-sentence paragraph about the germination of {herb_name}.', f''],
        ['0', 'cultivars', f'write a short 3-sentence paragraph about the cultivars of {herb_name}.', f''],
    ]
    for section in sections:
        exe = section[0]
        if exe != '1': continue
        key = section[1]
        prompt = section[2]
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = prompt,
        )
    # amazon
    # html
    html_article = ''
    html_article += f'<h1>{herb_name}</h1>'
    for section in sections:
        exe = section[0]
        if exe != '1': continue
        section_name = section[1]
        section_desc = json_article[section_name]
        section_link = section[3]
        html_article += f'<h2>{section_name}</h2>'
        html_article += f'<p>{section_desc}</p>\n'
        if section_link.strip() != '':
            html_article += f'<p><a href="/herbs/{herb_slug}/{section_link}.html">{section_name}</a></p>'
    title = f'{herb_name}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs'): 
        os.mkdir(f'{website_folderpath}/herbs')
    with open(f'{website_folderpath}/herbs/{herb_slug}.html', 'w') as f:
        f.write(html)


def a_herb_benefits(herb):
    slug = herb['herb_slug']
    name = slug.replace('-', ' ')
    json_article_filepath = f'database/pages/herbs/{slug}/benefit.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['slug'] = slug
    json_article['name'] = name
    json_article['url'] = f'herbs/{slug}/benefit.html'
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>{name} benefits</h1>'
    title = f'{name} benefits'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{slug}/benefit.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs/{slug}'): 
        os.mkdir(f'{website_folderpath}/herbs/{slug}')
    with open(f'{website_folderpath}/herbs/{slug}/benefit.html', 'w') as f:
        f.write(html)


def a_herb_preparations(herb):
    herb_slug = herb['herb_slug']
    herb_name = herb_slug.replace('-', ' ')
    json_article_filepath = f'database/pages/herbs/{herb_slug}/preparation.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name'] = herb_name
    json_article['herb_url'] = f'herbs/{herb_slug}/preparation.html'
    if 'preparations' not in json_article: json_article['preparations'] = []
    json_write(json_article_filepath, json_article)
    # json
    preparations_slugs = herb['preparations_slugs']
    for preparation_slug in preparations_slugs:
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
                Write a short 3-sentence paragraph about {herb_name} {preparation_name}.
                Start with the following words: {herb_name} is .
            ''',
            regen = False,
        )
    # html
    html_article = ''
    html_article += f'<h1>{herb_name} preparations</h1>'
    for preparation in json_article['preparations']:
        preparation_slug = preparation['preparation_slug']
        preparation_name = preparation_slug.replace('-', ' ')
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{preparation_name}</h2>\n'
        html_article += f'<p>{preparation_desc}</p>\n'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{herb_slug}.html">{preparation_name}</a></p>'
    title = f'{herb_name} preparations'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}/preparation.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs/{herb_slug}'): 
        os.mkdir(f'{website_folderpath}/herbs/{herb_slug}')
    with open(f'{website_folderpath}/herbs/{herb_slug}/preparation.html', 'w') as f:
        f.write(html)


def p_preparations(preparations):
    preparation_slugs = []
    for preparation in preparations:
        if preparation['preparation_slug'] not in preparation_slugs: 
            preparation_slugs.append(preparation['preparation_slug'])
    json_article_filepath = f'database/pages/preparations.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    # json
    if 'preparations' not in json_article: json_article['preparations'] = []
    for preparation_slug in preparation_slugs:
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
    for preparation in json_article['preparations']:
        slug_plural = preparation['preparation_slug']
        name_plural = slug_plural.replace('-', ' ')
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{name_plural}</h2>'
        html_article += f'<p>{preparation_desc}</p>'
        html_article += f'<p><a href="/preparations/{slug_plural}.html">{name_plural}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'preparations'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'preparations.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/preparations'): 
        os.mkdir(f'{website_folderpath}/preparations')
    with open(f'{website_folderpath}/preparations.html', 'w') as f:
        f.write(html)


def a_preparation(preparation):
    preparation_slug = preparation['preparation_slug']
    preparation_name_singular = preparation_slug.replace('-', ' ')
    preparation_name_plural = preparation_slug.replace('-', ' ')
    herbs_slugs = preparation['herbs_slugs']
    json_article_filepath = f'database/pages/preparations/{preparation_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['preparation_slug'] = preparation_slug
    json_article['preparation_name_singular'] = preparation_name_singular
    json_article['preparation_name_plural'] = preparation_name_plural
    json_article['preparation_url'] = f'preparations/{preparation_slug}.html'
    json_write(json_article_filepath, json_article)
    # json
    if 'herbs' not in json_article: json_article['herbs'] = []
    for herb_slug in herbs_slugs:
        herb_name = herb_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['herbs']:
            if herb_slug == _obj['herb_slug']:
                found = True
                break
        if not found:
            json_article['herbs'].append({'herb_slug': herb_slug})
            json_write(json_article_filepath, json_article)
        # update
        herb_obj = {}
        for _herb_obj in json_article['herbs']:
            if herb_slug == _herb_obj['herb_slug']:
                herb_obj = _herb_obj
                break
        ai_paragraph_gen(
            key = 'herb_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = herb_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name} {preparation_name_singular}.
            ''',
        )
    # html
    html_article = ''
    html_article += f'<h1>{preparation_name_plural}</h1>'
    for herb in json_article['herbs']:
        slug_plural = herb['herb_slug']
        name_plural = slug_plural.replace('-', ' ')
        herb_desc = herb['herb_desc']
        html_article += f'<h2>{name_plural}</h2>'
        html_article += f'<p>{herb_desc}</p>'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{herb_slug}.html">{herb_name} {preparation_name_singular}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'{preparation_slug}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'preparations/{preparation_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        </head>
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/preparations/{preparation_slug}.html', 'w') as f:
        f.write(html)


def a_preparation_herbs(preparation):
    for herb_slug in preparation['herbs_slugs']:
        preparation_slug = preparation['preparation_slug']
        preparation_name_singular = preparation_slug.replace('-', ' ')
        preparation_name_plural = preparation_slug.replace('-', ' ')
        herb_name = herb_slug.replace('-', ' ')
        json_article_filepath = f'database/pages/preparations/{preparation_slug}/{herb_slug}.json'
        json_article = json_read(json_article_filepath, create=True)
        json_article['preparation_slug'] = preparation_slug
        json_article['preparation_name_plural'] = preparation_name_plural
        json_article['preparation_name_singular'] = preparation_name_singular
        json_article['preparation_url'] = f'preparations/{preparation_slug}/{herb_slug}.html'
        json_write(json_article_filepath, json_article)
        # update
        ai_paragraph_gen(
            key = 'intro', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name} {preparation_name_singular}.
            ''',
        )
        # html
        html_article = ''
        html_article += f'<h1>{herb_name} {preparation_name_singular}</h1>'
        html_article += f'<h2>intro</h2>'
        html_article += f'<p>{json_article["intro"]}</p>'
        html_article += f'<p><a href="/herbs/{herb_slug}.html">{herb_name}</a></p>'
        title = f'{herb_slug} {preparation_slug}'
        html_head = html_head_gen(title)
        html_breadcrumbs = breadcrumbs_gen(f'preparations/{preparation_slug}/{herb_slug}.html')
        html_article_layout = html_article_layout_gen(html_article)
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
            {html_head}
            <body>
                {html_header}
                {html_breadcrumbs}
                {html_article_layout}
                {html_footer}
            </body>
            </html>
        '''
        if not os.path.exists(f'{website_folderpath}/preparations/{preparation_slug}'): 
            os.mkdir(f'{website_folderpath}/preparations/{preparation_slug}')
        with open(f'{website_folderpath}/preparations/{preparation_slug}/{herb_slug}.html', 'w') as f:
            f.write(html)


def p_equipments(lst):
    equipments_slugs = [x['slug'] for x in lst]
    json_article_filepath = f'database/pages/equipments.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>equipments</h1>'
    for equipment_slug in equipments_slugs:
        equipment_name = equipment_slug.replace('-', ' ')
        html_article += f'<p><a href="/equipments/{equipment_slug}.html">{equipment_name}</a></p>'
    title = f'equipments'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments'): 
        os.mkdir(f'{website_folderpath}/equipments')
    with open(f'{website_folderpath}/equipments.html', 'w') as f:
        f.write(html)


def a_equipment(equipment):
    equipment_slug = equipment['slug']
    equipment_name = equipment_slug.replace('-', ' ')
    equipments_slugs = [x['slug'] for x in lst]
    json_article_filepath = f'database/pages/equipments/{equipment_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>{equipment_name}</h1>'
    html_article += f'<p><a href="/equipments/{equipment_slug}/best.html">best {equipment_name}</a></p>'
    title = f'{equipment_slug}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments/{equipment_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments'): 
        os.mkdir(f'{website_folderpath}/equipments')
    with open(f'{website_folderpath}/equipments/{equipment_slug}.html', 'w') as f:
        f.write(html)


def a_equipment_best(equipment):
    equipment_slug = equipment['slug']
    equipment_amazon = equipment['amazon']
    equipment_name = equipment_slug.replace('-', ' ')
    equipment_name_plural = f'{equipment_name}s'
    json_products_folderpath = f'{vault}/amazon/json/{equipment_amazon}'
    json_article_filepath = f'database/pages/equipments/{equipment_slug}/best.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['slug'] = equipment_slug
    json_article['name'] = equipment_name
    json_article['url'] = f'equipments/{equipment_slug}/best.html'
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
            Write a 5-sentence pargraph about the following product: {equipment_name} for apothecaries. 
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
        product_data = json_read(product_json_filepath, create=True)
        product_aff_link = product_data['affiliate_link']
        product_title = product_data['title']
        product_asin = product_json_filepath.split('/')[-1].replace('.json', '')
        print(product_aff_link)
        print(product_title)
        print(product_asin)
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
                    positive_reviews_text = product_data['reviews_5s']
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
                        Write a short 5-sentence paragraph about the following product: {equipment_name}.
                        The target audience for this product is: apothecary.
                        Use the following INFO to describe the features, and use the GUIDELINES below.
                        INFO:
                        {pros}
                        GUIDELIES:
                        Reply in paragraph format.
                        Don't write conclusory statements, like sentences that starts with "overall", "in conclusion", "to summarize", etc...
                        Start writing the features from the first sentence.
                        Start with the following words: These {equipment_name} .
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
                        Write 1 short sentence about some of the complaints a few users had about the following product: {equipment_name}.
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
    html_article += f'{text_format_1N1_html(json_article["intro"])}\n'
    if 'products' not in json_article: json_article['products'] = []
    for i, obj in enumerate(json_article['products'][:products_num]):
        title_ai = obj['title_ai']
        desc = obj['desc']
        pros = obj['pros']
        warn = obj['warn']
        # product_aff_link = obj['product_aff_link']
        html_article += f'<h2>{i+1}. {title_ai}</h2>\n'
        html_article += f'{text_format_1N1_html(desc)}\n'
        html_article += f'<p class="font-bold text-black">Key Features:</p>\n'
        html_article += f'<ul>\n'
        for item in pros[:5]:
            html_article += f'<li>{item}</li>\n'
        html_article += f'</ul>\n'
        html_article += f'<p class="font-bold text-black">Warnings:</p>\n'
        html_article += f'{text_format_1N1_html(warn)}\n'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments/{equipment_slug}/best.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments/{equipment_slug}'): 
        os.mkdir(f'{website_folderpath}/equipments/{equipment_slug}')
    with open(f'{website_folderpath}/equipments/{equipment_slug}/best.html', 'w') as f:
        f.write(html)


def p_ailments(slugs):
    json_article_filepath = f'database/pages/ailments.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>ailments</h1>'
    for slug in slugs:
        name = slug.replace('-', ' ')
        html_article += f'<p><a href="/ailments/{slug}.html">{name}</a></p>'
    title = f'ailment'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'ailments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/ailments'): 
        os.mkdir(f'{website_folderpath}/ailments')
    with open(f'{website_folderpath}/ailments.html', 'w') as f:
        f.write(html)


def a_ailment(slug):
    name = slug.replace('-', ' ')
    json_article_filepath = f'database/pages/ailments/{slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['slug'] = slug
    json_article['name'] = name
    json_article['url'] = f'ailments/{slug}.html'
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>{name}</h1>'
    title = f'{slug}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'ailments/{name}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/ailments/{slug}.html', 'w') as f:
        f.write(html)

if 0:
    vertex_1 = {
        'type': 'herb',
        'slug': 'achillea-millefolium',
    }

    vertex_2 = {
        'type': 'preparation',
        'slug': 'infusion',
    }

    edge_1 = {
        'vertex_1': vertex_1,
        'vertex_2': vertex_2,
    }

    vertices = [vertex_1, vertex_2]
    edges = [edge_1]

    herbs = []
    for vertex in vertices:
        if vertex['type'] == 'herb':
            herbs.append(vertex)


p_home()

# herbs
if 1:
    vertices_herbs = [vertex for vertex in vertices if vertex['type'] == 'herb']
    herbs = []
    for vertex_herb in vertices_herbs:
        herb_slug = vertex_herb['herb_slug']
        herb = {'herb_slug': herb_slug, 'preparations_slugs': []}
        preparations_slugs = []
        for edge in edges: 
            if edge['type'] == 'herb_preparation' and edge['vertex_1'] == herb_slug:
                herb['preparations_slugs'].append(edge['vertex_2'])
        herbs.append(herb)
    

    '''
    with open('database/csvs/herbs-preparations.txt') as f: content = f.read()
    llst = []
    lines = content.split('\n')
    for line in lines:
        if line.strip() == '': continue
        lst = line.split('\\')
        llst.append(lst)
    herbs = []
    for lst in llst:
        found = False
        for herb in herbs:
            if lst[0] == herb['herb_slug']:
                herb['preparations_slugs'].append(lst[1])
                found = True
                break
        if not found:
            herbs.append({'herb_slug': lst[0], 'preparations_slugs': [lst[1]]})
    '''

    herb_slugs = [x['herb_slug'] for x in herbs]
    p_herbs(herb_slugs)
    for herb in herbs:
        a_herb(herb)
        a_herb_benefits(herb)
        a_herb_preparations(herb)

# preparations
if 1:
    vertices_preparations = [vertex for vertex in vertices if vertex['type'] == 'preparation']
    preparations = []
    for vertex_preparation in vertices_preparations:
        preparation_slug = vertex_preparation['preparation_slug']
        preparation = {'preparation_slug': preparation_slug, 'herbs_slugs': []}
        herbs_slugs = []
        for edge in edges: 
            print(edge)
            if edge['type'] == 'herb_preparation' and edge['vertex_2'] == preparation_slug:
                preparation['herbs_slugs'].append(edge['vertex_1'])
        preparations.append(preparation)
    
    '''
    with open('database/csvs/herbs-preparations.txt') as f: content = f.read()
    llst = []
    lines = content.split('\n')
    for line in lines:
        if line.strip() == '': continue
        lst = line.split('\\')
        llst.append(lst)
    preparations = []
    for lst in llst:
        found = False
        for preparation in preparations:
            if lst[1] == preparation['preparation_slug']:
                preparation['herbs_slugs'].append(lst[0])
                found = True
                break
        if not found:
            preparations.append({
                'preparation_slug': lst[1], 
                'herbs_slugs': [lst[0]]
            })
    '''

    p_preparations(preparations)
    for preparation in preparations:
        a_preparation(preparation)
        a_preparation_herbs(preparation)

# equipments
if 1:
    lst = [
        {'slug': 'jar', 'amazon': 'jars',},
        {'slug': 'bottle', 'amazon': 'bottles',},
        {'slug': 'spatula', 'amazon': 'spatulas',},
        {'slug': 'coffee-grinder', 'amazon': 'coffee-grinders',},
        {'slug': 'mortar', 'amazon': 'mortars',},
        {'slug': 'pestle', 'amazon': 'pestles',},
        {'slug': 'measuring-cup', 'amazon': 'measuring-cups',},
        {'slug': 'lid-grip', 'amazon': 'lid-grips',},
    ]
    p_equipments(lst)
    for equipment in lst:
        a_equipment(equipment)
        a_equipment_best(equipment)

# ailments
if 1:
    lst = [
        {'slug': 'bad-breath',},
        {'slug': 'fever',},
    ]
    slugs = [x['slug'] for x in lst]
    p_ailments(slugs)
    for slug in slugs:
        a_ailment(slug)

shutil.copy('style.css', f'{website_folderpath}/style.css')

quit()
vertices = json_read('vertices.json')
edges = json_read('edges.json')

# find preparations of achillea millefolium
herb_slug = 'achillea-millefolium'
preparations_slugs = []
for edge in edges: 
    if edge['type'] == 'herb_preparation' and edge['vertex_1'] == herb_slug:
        preparations_slugs.append(edge['vertex_2'])

print(preparations_slugs)

herb_slug = 'acorus-calamus'
preparations_slugs = []
for edge in edges: 
    if edge['type'] == 'herb_preparation' and edge['vertex_1'] == herb_slug:
        preparations_slugs.append(edge['vertex_2'])

print(preparations_slugs)
