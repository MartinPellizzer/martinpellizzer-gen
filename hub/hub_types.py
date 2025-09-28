import json

from lib import g
from lib import io
from lib import llm
from lib import polish
from lib import article
from lib import sections


flowers = [
    {
        'flower_slug_singular': 'tulip',
        'flower_slug_plural': 'tulips',
        'flower_name_singular': 'tulip',
        'flower_name_plural': 'tulips',
    },
    {
        'flower_slug_singular': 'sunflower',
        'flower_slug_plural': 'sunflowers',
        'flower_name_singular': 'sunflower',
        'flower_name_plural': 'sunflowers',
    },
    {
        'flower_slug_singular': 'rose',
        'flower_slug_plural': 'roses',
        'flower_name_singular': 'rose',
        'flower_name_plural': 'roses',
    },
    {
        'flower_slug_singular': 'cherry-blossom',
        'flower_slug_plural': 'cherry-blossoms',
        'flower_name_singular': 'cherry blossom',
        'flower_name_plural': 'cherry blossoms',
    },
    {
        'flower_slug_singular': 'lily',
        'flower_slug_plural': 'lilies',
        'flower_name_singular': 'lily',
        'flower_name_plural': 'lilies',
    },
    {
        'flower_slug_singular': 'lavender',
        'flower_slug_plural': 'lavenders',
        'flower_name_singular': 'lavender',
        'flower_name_plural': 'lavenders',
    },
    {
        'flower_slug_singular': 'daisy',
        'flower_slug_plural': 'daisies',
        'flower_name_singular': 'daisy',
        'flower_name_plural': 'daisies',
    },
    {
        'flower_slug_singular': 'peony',
        'flower_slug_plural': 'peonies',
        'flower_name_singular': 'peony',
        'flower_name_plural': 'peonies',
    },
    {
        'flower_slug_singular': 'hydrangea',
        'flower_slug_plural': 'hydrangeas',
        'flower_name_singular': 'hydrangea',
        'flower_name_plural': 'hydrangeas',
    },
    {
        'flower_slug_singular': 'jasmine',
        'flower_slug_plural': 'jasmines',
        'flower_name_singular': 'jasmine',
        'flower_name_plural': 'jasmines',
    },
    {
        'flower_slug_singular': 'lotus',
        'flower_slug_plural': 'lotuses',
        'flower_name_singular': 'lotus',
        'flower_name_plural': 'lotuses',
    },
    {
        'flower_slug_singular': 'hibiscus',
        'flower_slug_plural': 'hibiscuses',
        'flower_name_singular': 'hibiscus',
        'flower_name_plural': 'hibiscuses',
    },
    {
        'flower_slug_singular': 'carnation',
        'flower_slug_plural': 'carnations',
        'flower_name_singular': 'carnation',
        'flower_name_plural': 'carnations',
    },
    {
        'flower_slug_singular': 'sakura',
        'flower_slug_plural': 'sakuras',
        'flower_name_singular': 'sakura',
        'flower_name_plural': 'sakuras',
    },
    {
        'flower_slug_singular': 'poppy',
        'flower_slug_plural': 'poppies',
        'flower_name_singular': 'poppy',
        'flower_name_plural': 'poppies',
    },
    {
        'flower_slug_singular': 'dahlia',
        'flower_slug_plural': 'dahlias',
        'flower_name_singular': 'dahlia',
        'flower_name_plural': 'dahlias',
    },
    {
        'flower_slug_singular': 'cosmos',
        'flower_slug_plural': 'cosmoses',
        'flower_name_singular': 'cosmos',
        'flower_name_plural': 'cosmoses',
    },
]

def folders_recursive_gen(folderpath):
    folderpath_cur = ''
    for chunk in folderpath.split('/'):
        folderpath_cur += f'{chunk}/'
        try: os.mkdir(f'{g.database_folderpath}/json/{folderpath_cur}')
        except: pass

def art_flowers_flower_json_gen_outline(item, regen=False, dispel=False):
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'outline'
    if key not in json_article: 
        json_article[key] = ''
    if dispel: 
        json_article[key] = ''
        io.json_write(json_article_filepath, json_article)
        return
    if regen: 
        json_article[key] = ''
    if json_article[key] == '':
        output_list = []
            # Include sections for the following keywords: aesthetic.
            # Include one section for the following keyword: aesthetic.
        prompt = f'''
            I have to write an article about: {json_article['keyword_main']}.
            Write a SEO optimized outline based on semantic topical authority principles.
            Include one section for the following keyword: aesthetic.
            Write only the headings of the sections in the outline, don't include the content inside.
            Reply only with the outline.
            Reply using the JSON structure below:
            [
                {{"heading": "write section 1 heading here", "keyword": "write asked keyword 1 here"}},
            ]
        '''
        prompt += f'/no_think'
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        prompt = f'''
            Order the following list of json objects in logical order and reply only with the reordered list:
            {reply}
        '''
        prompt += f'/no_think'
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        try: json_reply = json.loads(reply)
        except: json_reply = {}
        if json_reply != {}:
            for json_obj in json_reply:
                try: heading = json_obj['heading'].strip().lower()
                except: continue
                try: keyword = json_obj['keyword'].strip().lower()
                except: continue
                _obj = {
                    "heading": heading, 
                    "keyword": keyword,
                }
                output_list.append(_obj)

        json_article[key] = output_list
        io.json_write(json_article_filepath, json_article)

def art_flowers_flower_json_gen_headings_questions(item, regen=False, dispel=False):
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'heading_question'
    for json_obj in json_article['outline']:
        if key not in json_obj: 
            json_obj[key] = ''
        if dispel: 
            json_obj[key] = ''
            io.json_write(json_article_filepath, json_article)
            return
        if regen: 
            json_obj[key] = ''
        if json_obj[key] == '':
            prompt = f'''
                Rewrite the following title in question format: {json_obj['heading']}.
                Use as few words as possible.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = reply.replace('*', '')
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def art_flowers_flower_json_gen_desc(item, regen=False, dispel=False):
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'section_desc'
    for json_obj in json_article['outline']:
        if key not in json_obj: 
            json_obj[key] = ''
        if dispel: 
            json_obj[key] = ''
            io.json_write(json_article_filepath, json_article)
            return
        if regen: 
            json_obj[key] = ''
        if json_obj[key] == '':
            prompt = f'''
                Write a detailed paragraph in 5 sentences about {json_obj['heading']}.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = reply.replace('*', '')
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def art_flowers_flower_json_gen(item):
    print(f'ART: flowers flower [json]')
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['article_type'] = f'applications'
    json_article['entity_name_singular'] = f'''{item['flower_name_singular']}'''
    json_article['entity_name_plural'] = f'''{item['flower_name_plural']}'''
    json_article['entity_slug_singular'] = f'''{item['flower_slug_singular']}'''
    json_article['entity_slug_plural'] = f'''{item['flower_slug_plural']}'''
    json_article['keyword_main'] = f'''{item['flower_name_plural']} flower'''
    json_article['keyword_main_slug'] = f'''{item['flower_slug_plural']}-flower'''
    json_article['article_title'] = f'''{item['flower_name_plural']} flower'''
    io.json_write(json_article_filepath, json_article)
    art_flowers_flower_json_gen_outline(item, regen=False, dispel=False)
    art_flowers_flower_json_gen_headings_questions(item, regen=False, dispel=False)
    art_flowers_flower_json_gen_desc(item, regen=False, dispel=False)

def art_flowers_flower_html_gen(item):
    print(f'ART: flowers flower [html]')
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    meta_title = f'''{json_article['article_title']}'''
    meta_description = f''
    html_article = ''
    html_article += f'''<h1>{json_article['article_title'].title()}</h1>'''
    for section in json_article['outline']:
        html_article += f'''<h2>{section['heading_question'].title()}</h2>'''
        html_article += f'''{polish.format_1N1(section['section_desc'])}'''
        if section['keyword'] == 'aesthetic':
            src = f'''/images/{article_slug}/aesthetic/{json_article['entity_slug_singular']}-aesthetic.jpg'''
            alt = f'''{json_article['entity_name_singular']} aesthetic'''
            html_article += f'''<img src="{src}" alt="{alt}">\n'''
            html_article += f'''<p>Check the following <a href="/{article_slug}/aesthetic.html">100+ {item['flower_name_singular'].title()} Aesthetic Images</a>.</p>\n'''
            
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <header>
                <div class="container-xl" style="display: flex; justify-content: space-between;">
                    <a href="/">Martin Pellizzer</a>
                    <ul>
                        <a href="plants">Plants</a>
                    </ul>
                </div>
            </header>
            <main>
                {sections.breadcrumbs(article_slug)}
                <div class="article container-md">
                    {html_article}
                </div>
            </main>
            <footer>
                <div class="container-xl" style="display: flex; justify-content: space-between;">
                    <span href="/">martinpellizzer.com | all rights reserved</span>
                </div>
            </footer>
        </body>
        </html>
    '''
    html_filepath = f'''{g.website_folderpath}/{article_slug}.html'''
    with open(html_filepath, 'w') as f: f.write(html)

def art_flowers_flower_gen_old(item):
    print(f'ART: flowers flower')
    folders_recursive_gen(f'plants/types/flowers')
    art_flowers_flower_json_gen(item)
    art_flowers_flower_html_gen(item)
    # quit()





def article_plants_types_flowers_wallpaper_gen():
    article_slug = f'''plants/types/flowers/wallpaper'''
    print(f'ARTICLE: {article_slug}')
    article_obj = {
        'article_slug': article_slug,
        'keyword_main': 'flower wallpaper',
        'keyword_main_slug': 'flower-wallpaper',
        'keyword_main_pretty': 'flower wallpapers',
        'keyword_main_title': 'flower wallpaper images',
        'pin_board_name': 'plants',
        'main_list_num': '10',
        'article_type': 'listicle',
        'images_prompts': ['flower wallpaper, bokeh, depth of field, high resolution'],
        'links': [],
    }
    article.images_gen(article_obj, regen=False, dispel=False)
    article.json_gen(article_obj, regen=False, dispel=False)
    article.html_gen(article_slug)

def article_plants_types_flowers_aesthetic_gen():
    article_slug = f'''plants/types/flowers/aesthetic'''
    print(f'ARTICLE: {article_slug}')
    article_obj = {
        'article_slug': article_slug,
        'keyword_main': 'flowers aesthetic',
        'keyword_main_slug': 'flowers-aesthetic',
        'keyword_main_pretty': 'flowers aesthetics',
        'keyword_main_title': 'flowers aesthetic photos',
        'pin_board_name': 'plants',
        'main_list_num': '10',
        'article_type': 'listicle',
        'images_prompts': ['flowers in nature, bokeh, depth of field, high resolution'],
        'links': [],
    }
    article.images_gen(article_obj, regen=False, dispel=False)
    article.json_gen(article_obj, regen=False, dispel=False)
    article.html_gen(article_slug)

def article_plants_types_flowers_gen():
    article_slug = f'''plants/types/flowers'''
    print(f'ARTICLE: {article_slug}')
    article_plants_types_flowers_aesthetic_gen()
    article_plants_types_flowers_wallpaper_gen()

def article_plants_types_gen():
    article_slug = f'''plants/types'''
    print(f'ARTICLE: {article_slug}')
    # for item in flowers:
        # art_flowers_flower_gen(item)
    article_plants_types_flowers_gen()

def gen():
    print(f'HUB: types')
    article_plants_types_gen()

