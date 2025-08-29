import os
import random

from lib import g
from lib import io
from lib import llm
from lib import media
from lib import sections

flower_slug_singular = 'tulip'
flower_slug_plural = 'tulips'
flower_name_singular = 'tulip'
flower_name_plural = 'tulips'

keyword_main = f'{flower_name_singular} aesthetic'
keyword_main_slug = f'{flower_slug_singular}-aesthetic'

def images_gen(article_slug, dispel=False):
    output_folderpath = f'{g.website_folderpath}/images/{article_slug}'
    ### dispel
    if dispel:
        for output_filename in os.listdir(output_folderpath):
            output_filepath = f'{output_folderpath}/{output_filename}'
            os.remove(output_filepath)
    lighting_list = [
        'golden hour',
        'soft morning light',
        'sunset glow',
        'moonlight',
        'starlight',
        'cloudy overcast',
        'dramatic backlighting',
        'silhouette lighting',
        'dappled forest light',
        'neon glow',
    ]
    atmosphere_list = [
        'calm',
        'peaceful',
        'dramatic',
        'moody',
        'dreamy',
        'ethereal',
        'vibrant',
        'lively',
        'mysterious',
        'surreal',
        'romantic',
        'soft glow',
        'cinematic',
        'epic scene',
        'cozy',
        'nostalgic',
        'enchanted',
        'fantasy',
        'minimalist',
        'zen',
    ]
    composition_list = [
        'close-up',
        'top-down view',
        'font view',
        'midshot',
        'side view',
        'scenic view',
        'studio shot',
        'wide-angle shot',
    ]
    for i in range(100):
        lighting = random.choice(lighting_list)
        lighting_slug = lighting.lower().strip().replace(' ', '-')
        atmosphere = random.choice(atmosphere_list)
        atmosphere_slug = atmosphere.lower().strip().replace(' ', '-').replace(',', '')
        composition = random.choice(composition_list)
        composition_slug = composition.lower().strip().replace(' ', '-').replace(',', '')
        output_filename = f'{i}-{flower_slug_singular}-aesthetic-{lighting_slug}-{atmosphere_slug}-{composition_slug}.jpg'
        output_filepath = f'{g.website_folderpath}/images/{article_slug}/{output_filename}' 
        found = False
        for output_filename in os.listdir(output_folderpath):
            if output_filename.startswith(f'{i}-'):
                found = True
                break
        if not found:
            print(f'{i}/100')
            prompt = f'''
                {flower_name_singular},
                {lighting},
                {atmosphere},
                {composition},
                soft focus,
                depth of field,
                bokeh,
                nature photography,
                high resolution,
            '''.replace('  ', ' ')
            image = media.image_gen(prompt, 832, 1216)
            image.save(output_filepath)
    ### featured
    lighting = random.choice(lighting_list)
    lighting_slug = lighting.lower().strip().replace(' ', '-')
    atmosphere = random.choice(atmosphere_list)
    atmosphere_slug = atmosphere.lower().strip().replace(' ', '-').replace(',', '')
    composition = random.choice(composition_list)
    composition_slug = composition.lower().strip().replace(' ', '-').replace(',', '')
    output_filename = f'{flower_slug_singular}-aesthetic.jpg'
    output_filepath = f'{g.website_folderpath}/images/{article_slug}/{output_filename}' 
    if not os.path.exists(output_filepath):
        prompt = f'''
            {flower_name_singular},
            {lighting},
            {atmosphere},
            {composition},
            soft focus,
            depth of field,
            bokeh,
            nature photography,
            high resolution,
        '''.replace('  ', ' ')
        # image = media.image_gen(prompt, 832, 1216)
        image = media.image_gen(prompt, 1024, 1024)
        image.save(output_filepath)

def ai_llm_title(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'article_title'
    if key not in json_article: 
        json_article[key] = ''
    if dispel: 
        json_article[key] = ''
        io.json_write(json_article_filepath, json_article)
        return
    if regen: 
        json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a list of 15 title seo optimized ideas for an article with the following topic: {json_article['main_lst_num']} {json_article['keyword_main']} images.
            Use the koray semantic topical authority framework, rules, and guidelines to write the titles.
            The main context is living in nature, and the central core entity is plants.
            The main keywords of this article is: {json_article['keyword_main']}.
            Always include the main keyword in each title idea.
            Start each title with the following: {json_article['main_lst_num']}+.
            Use only ascii characters.
            Reply only with the list.
        '''
        prompt += f'/no_think'
        print(prompt)
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        lines = []
        for line in reply.split('\n'):
            line = line.strip()
            if line == '': continue
            lines.append(line)
        title = random.choice(lines)
        json_article[key] = title
        io.json_write(json_article_filepath, json_article)
        # quit()

def ai_llm_intro(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'intro'
    if key not in json_article: 
        json_article[key] = ''
    if dispel: 
        json_article[key] = ''
        io.json_write(json_article_filepath, json_article)
        return
    if regen: 
        json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a detailed intro paragraph in 5 sentences for an article with the following title: {json_article['article_title']}.
            Write only the paragaraph.
            Use only ascii characters.
        '''
        prompt += f'/no_think'
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        json_article[key] = reply
        io.json_write(json_article_filepath, json_article)

def ai_llm_list_init(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'main_list'
    if key not in json_article: 
        json_article[key] = []
    if dispel: 
        json_article[key] = []
        io.json_write(json_article_filepath, json_article)
        return
    if regen: 
        json_article[key] = []
    if json_article[key] == []:
        images_folderpath = f'''{g.website_folderpath}/images/{article_slug}'''
        output_list = []
        for image_filename in os.listdir(images_folderpath):
            output_list.append({
                'image_filename': image_filename,
            })
        json_article[key] = output_list
        io.json_write(json_article_filepath, json_article)

def ai_llm_list_desc(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'image_desc'
    for json_obj in json_article['main_list']:
        if key not in json_obj: 
            json_obj[key] = ''
        if dispel: 
            json_obj[key] = ''
            io.json_write(json_article_filepath, json_article)
            return
        if regen: 
            json_obj[key] = ''
        if json_obj[key] == '':
            images_folderpath = f'''{g.website_folderpath}/images/{article_slug}'''
            image_filename = json_obj['image_filename']
            image_filepath = f'{images_folderpath}/{image_filename}'
            image_prompt = image_filename
            image_prompt = image_prompt.replace('.jpg', '')
            if image_prompt[0].isdigit():
                image_prompt = '-'.join(image_prompt.split('-')[1:])
            image_prompt = image_prompt.replace('-', ' ')
            print(image_prompt)
            prompt = f'''
                Write a small description in less than 40 words for the following image: {image_prompt}.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def ai_llm_list_alt(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'image_alt'
    for json_obj in json_article['main_list']:
        if key not in json_obj: 
            json_obj[key] = ''
        if dispel: 
            json_obj[key] = ''
            io.json_write(json_article_filepath, json_article)
            return
        if regen: 
            json_obj[key] = ''
        if json_obj[key] == '':
            images_folderpath = f'''{g.website_folderpath}/images/{article_slug}'''
            image_filename = json_obj['image_filename']
            image_filepath = f'{images_folderpath}/{image_filename}'
            image_prompt = image_filename
            image_prompt = image_prompt.replace('.jpg', '')
            if image_prompt[0].isdigit():
                image_prompt = '-'.join(image_prompt.split('-')[1:])
            image_prompt = image_prompt.replace('-', ' ')
            print(image_prompt)
            prompt = f'''
                Write a small alt description in less than 10 words for the following image: {image_prompt}.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def json_gen(article_slug):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['entity_name'] = flower_name_singular
    json_article['entity_slug'] = flower_slug_singular
    json_article['keyword_main'] = keyword_main
    json_article['keyword_main_slug'] = keyword_main_slug
    json_article['main_lst_num'] = 100
    # json_article['article_title'] = f'''100+ {flower_name_singular.title()} Aesthetic Photos for Plant Lovers: Nature's Brightest Inspiration'''
    io.json_write(json_article_filepath, json_article)
    ###
    ai_llm_title(article_slug, regen=False, dispel=False)
    ai_llm_intro(article_slug, regen=False, dispel=False)
    ai_llm_list_init(article_slug, regen=False, dispel=False)
    ai_llm_list_desc(article_slug, regen=False, dispel=False)
    ai_llm_list_alt(article_slug, regen=False, dispel=False)

def html_gen(article_slug):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    html_article = ''
    html_article += f'<h1>{json_article["article_title"]}</h1>\n'
    src = f'''/images/{json_article['article_slug']}/{json_article['keyword_main_slug']}.jpg'''
    html_article += f'''<img src="{src}" alt="{json_article['keyword_main']}">\n'''
    html_article += f'<p>{json_article["intro"]}</p>\n'
    html_article += f'<h2>{keyword_main.title()} Images</h2>\n'
    main_list = json_article['main_list']
    html_article += f'''<div class="listicle">\n'''
    for i, item in enumerate(main_list):
        image_filename = f'''{item['image_filename']}'''
        image_desc = f'''{i+1}. {item['image_desc']}'''
        image_alt = f'''{item['image_alt']}'''
        src = f'/images/{article_slug}/{image_filename}'
        alt = image_alt
        html_article += f'''<p>{image_desc}</p>\n'''
        html_article += f'''<img src="{src}" alt="{alt}">\n'''
    html_article += f'''</div>\n'''
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            {sections.header()}
            <main>
                {sections.breadcrumbs(article_slug)}
                <div class="article container-md">
                    {html_article}
                </div>
            </main>
            {sections.footer()}
        </body>
        </html>
    '''
    with open(f'{g.website_folderpath}/{article_slug}.html', 'w') as f: f.write(html)

def gen():
    article_slug = f'plants/types/flowers/{flower_slug_plural}/aesthetic'
    images_gen(article_slug)
    json_gen(article_slug)
    html_gen(article_slug)

