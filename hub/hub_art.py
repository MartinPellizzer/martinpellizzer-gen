import os
import json
import random

from lib import g
from lib import io
from lib import llm
from lib import media
from lib import sections

def has_year(text):
    import re
    match = re.match(r'.*([1-3][0-9]{3})', text)
    if match:
        return True
    return False

def art_gen_images_branch(article_slug, keyword_main, image_prompt, images_num=10, dispel=False):
    print(f'ART: crafts pumpkin carving ideas easy [images branch]')

def art_gen_images(article_slug, keyword_main, image_prompt, images_num, dispel=False):
    print(f'ART: crafts pumpkin carving ideas easy [images]')
    keyword_main_slug = keyword_main.lower().strip().replace(' ', '-')
    images_folderpath = f'{g.website_folderpath}/images/{article_slug}'
    io.folders_recursive_gen(images_folderpath)
    if dispel:
        # TODO: delete only if file, not foler
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            os.remove(image_filepath)
        return
    for i in range(images_num):
        image_filename = f'''{i}-{keyword_main_slug}.jpg'''
        image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
        found = False
        for image_filename in os.listdir(images_folderpath):
            if image_filename.startswith(f'{i}-'):
                found = True
                break
        if not found:
            print(f'{i}/{images_num}')
            # image = media.image_gen(image_prompt, 832, 1216)
            image = media.image_gen(image_prompt, 1024, 1024)
            image.save(image_filepath)
    ### featured
    image_filename = f'''{keyword_main_slug}.jpg'''
    image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
    if not os.path.exists(image_filepath):
        image = media.image_gen(image_prompt, 1024, 1024)
        image.save(image_filepath)


def art_gen_json(article_slug, keyword_main, links=[]):
    print(f'ART: {article_slug} [json]')
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['article_type'] = f'listicle'
    json_article['main_list_num'] = f'10'
    json_article['entity_name_singular'] = f'''pumpkin'''
    json_article['entity_name_plural'] = f'''pumpkins'''
    json_article['entity_slug_singular'] = f'''pumpkin'''
    json_article['entity_slug_plural'] = f'''pumpkins'''
    json_article['keyword_main'] = keyword_main
    json_article['keyword_main_slug'] = keyword_main.lower().strip().replace(' ', '-')
    json_article['links'] = links
    io.json_write(json_article_filepath, json_article)
    if json_article['article_type'] == 'listicle':
        art_gen_title(article_slug, regen=False, dispel=False)
        art_gen_intro(article_slug, regen=False, dispel=False)
        art_gen_list_init(article_slug, regen=False, dispel=False)
        art_gen_list_desc(article_slug, regen=False, dispel=False)
        art_gen_list_alt(article_slug, regen=False, dispel=False)

def art_gen_html(article_slug):
    print(f'ART: crafts pumpkin carving ideas easy [html]')
    html_folderpath = f'{g.website_folderpath}/{article_slug}'
    io.folders_recursive_gen(html_folderpath)
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    html_article = ''
    html_article += f'<h1>{json_article["article_title"].title()}</h1>\n'
    src = f'''/images/{json_article['article_slug']}/{json_article['keyword_main_slug']}.jpg'''
    alt = f'''{json_article['keyword_main']}.jpg'''
    html_article += f'''<img src="{src}" alt="{alt}">\n'''
    html_article += f'<p>{json_article["intro"]}</p>\n'
    html_article += f'<h2>{json_article["keyword_main"].title()}</h2>\n'
    main_list = json_article['main_list']
    html_article += f'''<div class="listicle">\n'''
    for i, item in enumerate(main_list):
        image_filename = f'''{item['image_filename']}'''
        image_desc = f'''{i+1}. {item['image_desc']}'''
        src = f'/images/{article_slug}/{image_filename}'
        alt = f'''{item['image_alt']}'''
        html_article += f'''<p>{image_desc}</p>\n'''
        html_article += f'''<img src="{src}" alt="{alt}">\n'''
    if json_article['links'] != []:
        html_article += f'<h2>Additional Resources</h2>\n'
        html_article += f'''<ul>\n'''
        for link in json_article['links']:
            html_article += f'''<li><a href="{link['href']}">{link['keyword'].title()}</a></li>\n'''
        html_article += f'''</ul>\n'''
        
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

def art_crafts_pumpkin_carving_ideas_cat_gen():
    print(f'ART: crafts pumpkin carving ideas cat')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas/cat'''
    image_prompt = f'''cat pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas cat'''
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main)
    art_gen_html(article_slug)

def art_crafts_pumpkin_carving_ideas_cute_gen():
    print(f'ART: crafts pumpkin carving ideas cute')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas/cute'''
    image_prompt = f'''cute pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas cute'''
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main)
    art_gen_html(article_slug)

def art_crafts_pumpkin_carving_ideas_cool_gen():
    print(f'ART: crafts pumpkin carving ideas cool')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas/cool'''
    image_prompt = f'''cool pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas cool'''
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main)
    art_gen_html(article_slug)

def art_crafts_pumpkin_carving_ideas_unique_gen():
    print(f'ART: crafts pumpkin carving ideas easy')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas/unique'''
    image_prompt = f'''unique pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas unique'''
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main)
    art_gen_html(article_slug)

def art_crafts_pumpkin_carving_ideas_easy_gen():
    print(f'ART: crafts pumpkin carving ideas easy')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas/easy'''
    image_prompt = f'''easy pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas easy'''
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main)
    art_gen_html(article_slug)

def art_crafts_pumpkin_carving_ideas_gen_images(article_slug, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    images_folderpath = f'{g.website_folderpath}/images/{article_slug}'
    io.folders_recursive_gen(images_folderpath)
    if dispel:
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            os.remove(image_filepath)
    for i in range(10):
        image_filename = f'''{i}-{json_article['keyword_main_slug']}.jpg'''
        image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
        found = False
        for image_filename in os.listdir(images_folderpath):
            if image_filename.startswith(f'{i}-'):
                found = True
                break
        if not found:
            print(f'{i}/100')
            prompt = f'''
                pumpkin carving,
                bokeh,
                depth of field,
                high resolution,
            '''.replace('  ', ' ')
            image = media.image_gen(prompt, 832, 1216)
            image.save(image_filepath)
    ### featured
    image_filename = f'''{json_article['keyword_main_slug']}.jpg'''
    image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
    if not os.path.exists(image_filepath):
        prompt = f'''
            pumpkin carving,
            bokeh,
            depth of field,
            high resolution,
        '''.replace('  ', ' ')
        image = media.image_gen(prompt, 1024, 1024)
        image.save(image_filepath)

def art_gen_title(article_slug, regen=False, dispel=False):
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
            # The main context is {json_article['keyword_main']}, and the secondary context is plants.
        prompt = f'''
            Write a list of 15 title seo optimized ideas for an article with the following topic: {json_article['main_list_num']} {json_article['keyword_main']}.
            Use semantic topical authority frameworks, rules, and guidelines to write the titles.
            The main keywords of this article is: {json_article['keyword_main']}.
            Always include the main keyword in each title idea.
            Start each title with the following: {json_article['main_list_num']}.
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
            if has_year(line): continue
            lines.append(line)
        title = random.choice(lines)
        json_article[key] = title
        io.json_write(json_article_filepath, json_article)

def art_gen_intro(article_slug, regen=False, dispel=False):
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

def art_gen_list_init(article_slug, regen=False, dispel=False):
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

def art_gen_list_desc(article_slug, regen=False, dispel=False):
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
                Write a small description in about 40 words for the following image: {image_prompt}.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def art_gen_list_alt(article_slug, regen=False, dispel=False):
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

def art_crafts_pumpkin_carving_ideas_json_gen(article_slug):
    print(f'ART: crafts pumpkin carving ideas [json]')
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['article_type'] = f'listicle'
    json_article['main_list_num'] = f'10'
    json_article['entity_name_singular'] = f'''pumpkin'''
    json_article['entity_name_plural'] = f'''pumpkins'''
    json_article['entity_slug_singular'] = f'''pumpkin'''
    json_article['entity_slug_plural'] = f'''pumpkins'''
    json_article['keyword_main'] = f'''pumpkin carving ideas'''
    json_article['keyword_main_slug'] = f'''pumpkin-carving-ideas'''
    io.json_write(json_article_filepath, json_article)
    if json_article['article_type'] == 'listicle':
        art_gen_title(article_slug, regen=False, dispel=False)
        art_gen_intro(article_slug, regen=False, dispel=False)
        art_gen_list_init(article_slug, regen=False, dispel=False)
        art_gen_list_desc(article_slug, regen=False, dispel=False)
        art_gen_list_alt(article_slug, regen=False, dispel=False)

def art_gen_html_branch(article_slug):
    print(f'ART: crafts pumpkin carving ideas [html]')
    html_folderpath = f'{g.website_folderpath}/{article_slug}'
    io.folders_recursive_gen(html_folderpath)
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    html_article = ''
    html_article += f'<h1>{json_article["article_title"].title()}</h1>\n'
    src = f'''/images/{json_article['article_slug']}/{json_article['keyword_main_slug']}.jpg'''
    alt = f'''{json_article['keyword_main']}.jpg'''
    html_article += f'''<img src="{src}" alt="{alt}">\n'''
    html_article += f'<p>{json_article["intro"]}</p>\n'
    for i, item in enumerate(json_article['outline']):
        html_article += f'''<h2>{item['heading'].title()}</h2>\n'''
        html_article += f'''<p>{item['desc']}</p>\n'''
    if 0:
        html_article += f'<h2>{json_article["keyword_main"].title()}</h2>\n'
        main_list = json_article['main_list']
        html_article += f'''<div class="listicle">\n'''
        for i, item in enumerate(main_list):
            image_filename = f'''{item['image_filename']}'''
            image_desc = f'''{i+1}. {item['image_desc']}'''
            src = f'/images/{article_slug}/{image_filename}'
            alt = f'''{item['image_alt']}'''
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

def art_gen_outline(article_slug, keywords_links, regen=False, dispel=False):
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
            Include sections for the following keywords: {keywords_links}.
            Don't include introduction and conclusion.
            Write only the headings of the sections in the outline, don't include the content inside.
            Reply only with the outline.
            Reply using the JSON structure below:
            [
                {{"heading": "write section 1 heading here", "keyword": "write asked keyword 1 here, empty otherwhise"}},
            ]
        '''
        prompt += f'/no_think'
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        if 0: 
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

def art_gen_desc(article_slug, regen=False, dispel=False):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    key = 'desc'
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

def art_gen_json_branch(article_slug, keywords_links):
    print(f'ART: crafts pumpkin carving ideas [json]')
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['article_type'] = f'listicle'
    json_article['main_list_num'] = f'10'
    json_article['entity_name_singular'] = f'''pumpkin'''
    json_article['entity_name_plural'] = f'''pumpkins'''
    json_article['entity_slug_singular'] = f'''pumpkin'''
    json_article['entity_slug_plural'] = f'''pumpkins'''
    json_article['keyword_main'] = f'''pumpkin carving ideas'''
    json_article['keyword_main_slug'] = f'''pumpkin-carving-ideas'''
    io.json_write(json_article_filepath, json_article)
    if json_article['article_type'] == 'listicle':
        art_gen_outline(article_slug, keywords_links, regen=False, dispel=False)
        art_gen_desc(article_slug, regen=False, dispel=False)
        '''
        art_gen_title(article_slug, regen=False, dispel=False)
        art_gen_intro(article_slug, regen=False, dispel=False)
        art_gen_list_init(article_slug, regen=False, dispel=False)
        art_gen_list_desc(article_slug, regen=False, dispel=False)
        art_gen_list_alt(article_slug, regen=False, dispel=False)
        '''

# ;jump
def art_crafts_pumpkin_carving_ideas_gen():
    print(f'ART: crafts pumpkin carving ideas')
    article_slug = f'''plants/art/crafts/pumpkin/carving/ideas'''
    image_prompt = f'''pumpkin carving, bokeh, depth of field, high resolution,'''
    keyword_main = f'''pumpkin carving ideas'''
    links = [
        {'keyword': f'easy pumpkin carving ideas', 'href': f'/{article_slug}/easy.html'}, 
        {'keyword': f'unique pumpkin carving ideas', 'href': f'/{article_slug}/unique.html'}, 
        {'keyword': f'cool pumpkin carving ideas', 'href': f'/{article_slug}/cool.html'}, 
        {'keyword': f'cute pumpkin carving ideas', 'href': f'/{article_slug}/cute.html'}, 
        {'keyword': f'cat pumpkin carving ideas', 'href': f'/{article_slug}/cat.html'}, 
    ]
    # art_gen_images_branch(article_slug, keyword_main, images_prompts, images_num=10, dispel=False)
    # art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    # art_gen_json_branch(article_slug, keywords_links)
    # art_gen_html_branch(article_slug)
    # quit()
    # art_crafts_pumpkin_carving_ideas_json_gen(article_slug)
    art_gen_images(article_slug, keyword_main, image_prompt, images_num=10, dispel=False)
    art_gen_json(article_slug, keyword_main, links)
    art_gen_html(article_slug)
    ###
    art_crafts_pumpkin_carving_ideas_easy_gen()
    art_crafts_pumpkin_carving_ideas_unique_gen()
    art_crafts_pumpkin_carving_ideas_cool_gen()
    art_crafts_pumpkin_carving_ideas_cute_gen()
    art_crafts_pumpkin_carving_ideas_cat_gen()

def art_crafts_pumpkin_carving_json_gen():
    print(f'ART: crafts pumpkin carving [json]')

def art_crafts_pumpkin_carving_html_gen():
    print(f'ART: crafts pumpkin carving [html]')

def art_crafts_pumpkin_carving_gen():
    print(f'ART: crafts pumpkin carving')
    art_crafts_pumpkin_carving_json_gen()
    art_crafts_pumpkin_carving_html_gen()
    art_crafts_pumpkin_carving_ideas_gen()

def art_crafts_pumpkin_json_gen():
    print(f'ART: crafts pumpkin [json]')

def art_crafts_pumpkin_html_gen():
    print(f'ART: crafts pumpkin [html]')

def art_crafts_pumpkin_gen():
    print(f'ART: crafts pumpkin')
    art_crafts_pumpkin_json_gen()
    art_crafts_pumpkin_html_gen()
    art_crafts_pumpkin_carving_gen()

def art_crafts_json_gen():
    print(f'ART: crafts [json]')

def art_crafts_html_gen():
    print(f'ART: crafts [html]')

def art_crafts_gen():
    print(f'ART: crafts')
    art_crafts_json_gen()
    art_crafts_html_gen()
    art_crafts_pumpkin_gen()

def gen():
    print(f'ART: art')
    art_crafts_gen()
