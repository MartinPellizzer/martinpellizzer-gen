import os
import random

from lib import g
from lib import io
from lib import llm
from lib import media
from lib import polish
from lib import sections

def has_year(text):
    import re
    match = re.match(r'.*([1-3][0-9]{3})', text)
    if match:
        return True
    return False

def images_listicle_gen(article_obj, regen=False, dispel=False):
    article_slug = article_obj["article_slug"]
    print(f'ARTICLE: {article_slug} [images]')
    images_folderpath = f'{g.website_folderpath}/images/{article_slug}'
    io.folders_recursive_gen(images_folderpath)
    if regen:
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            if os.path.isfile(image_filepath):
                os.remove(image_filepath)
    if dispel:
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            if os.path.isfile(image_filepath):
                os.remove(image_filepath)
        return
    for i in range(int(article_obj['main_list_num'])):
        found = False
        for filename in os.listdir(images_folderpath):
            if filename.startswith(f'{i}-'):
                found = True
                break
        if not found:
            image_prompt = article_obj['images_prompts'][i % len(article_obj['images_prompts'])]
            prompt = f'''
                Write a slug in less than 7 words about the following title: {image_prompt.split(',')[0].lower()}.
                Include only the most important words and do not include stop words.
                Separate the words with the character "-", which is common for slugs.
                Start the slug with the following words: {article_obj['keyword_main_slug']}.
                Use only ascii characters.
                Reply only with the slug.
            '''
            prompt += f'/no_think'
            print(prompt)
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = reply.strip().lower().replace(' ', '-')
            image_filename = f'''{i}-{reply}.jpg'''
            image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
            print(f'''{i}/{article_obj['main_list_num']}''')
            if article_obj['article_type'] == 'listicle':
                image = media.image_gen(image_prompt, 832, 1216)
            else:
                image = media.image_gen(image_prompt, 1024, 1024)
            image.save(image_filepath)
    ### featured
    image_prompt = random.choice(article_obj['images_prompts'])
    image_filename = f'''{article_obj['keyword_main_slug']}.jpg'''
    image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
    if not os.path.exists(image_filepath):
        image = media.image_gen(image_prompt, 1024, 1024)
        image.save(image_filepath)

def images_category_gen(article_obj, regen=False, dispel=False):
    article_slug = article_obj["article_slug"]
    print(f'ARTICLE: {article_slug} [images]')
    images_folderpath = f'{g.website_folderpath}/images/{article_slug}'
    io.folders_recursive_gen(images_folderpath)
    if regen:
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            if os.path.isfile(image_filepath):
                os.remove(image_filepath)
    if dispel:
        for image_filename in os.listdir(images_folderpath):
            image_filepath = f'{images_folderpath}/{image_filename}'
            if os.path.isfile(image_filepath):
                os.remove(image_filepath)
        return
    ### featured
    image_prompt = random.choice(article_obj['images_prompts'])
    image_filename = f'''{article_obj['keyword_main_slug']}.jpg'''
    image_filepath = f'{g.website_folderpath}/images/{article_slug}/{image_filename}' 
    if not os.path.exists(image_filepath):
        image = media.image_gen(image_prompt, 1024, 1024)
        image.save(image_filepath)

def images_gen(article_obj, regen=False, dispel=False):
    if article_obj['article_type'] == 'category':
        images_category_gen(article_obj, regen=False, dispel=False)
    elif article_obj['article_type'] == 'listicle':
        images_listicle_gen(article_obj, regen=False, dispel=False)

def json_title_gen(article_slug, regen=False, dispel=False):
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
            Write a list of 15 title seo optimized ideas for an article with the following topic: {json_article['main_list_num']} {json_article['keyword_main_title']}.
            Use semantic topical authority frameworks, rules, and guidelines to write the titles.
            The main keyword of this article is: {json_article['keyword_main_pretty']}.
            Always include the main keyword in each title idea.
            Each title must be less than 10 words.
            Start each title with the following: {json_article['main_list_num']} {json_article['keyword_main_pretty']}.
            Reply in english.
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
        title = polish.sanitize(title)
        json_article[key] = title
        io.json_write(json_article_filepath, json_article)

def json_intro_gen(article_slug, regen=False, dispel=False):
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
            Reply in english.
        '''
        prompt += f'/no_think'
        reply = llm.reply(prompt).strip()
        if '</think>' in reply:
            reply = reply.split('</think>')[1].strip()
        reply = polish.sanitize(reply)
        json_article[key] = reply
        io.json_write(json_article_filepath, json_article)

def json_list_init_gen(article_slug, regen=False, dispel=False):
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
        io.folders_recursive_gen(images_folderpath)
        output_list = []
        for image_filename in sorted(os.listdir(images_folderpath)):
            if not image_filename[0].isdigit(): continue
            output_list.append({
                'image_filename': image_filename,
            })
        json_article[key] = output_list
        io.json_write(json_article_filepath, json_article)

def json_list_desc_gen(article_slug, regen=False, dispel=False):
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
                Reply in english.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = polish.sanitize(reply)
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def json_list_alt_gen(article_slug, regen=False, dispel=False):
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
                Reply in english.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = polish.sanitize(reply)
            json_obj[key] = reply
            io.json_write(json_article_filepath, json_article)

def json_category_title_gen(article_slug, regen=False, dispel=False):
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
            Write a list of 15 title seo optimized ideas for an article with the following topic: {json_article['keyword_main_title'].capitalize()}.
            Use semantic topical authority frameworks, rules, and guidelines to write the titles.
            Write each title in less than 10 words.
            Start each title with the following: {json_article['keyword_main_pretty'].capitalize()}.
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

def json_category_sections_gen(article_slug, regen=False, dispel=False):
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
        output_list = []
        folderpath = f'''{g.database_folderpath}/json/{article_slug}'''
        for filename in os.listdir(folderpath):
            filepath = f'''{folderpath}/{filename}'''
            filename_base = filename.split('.')[0]
            if not os.path.isfile(filepath): continue
            json_subarticle = io.json_read(filepath)
            json_subarticle_title = json_subarticle['article_title']
            json_subarticle_intro = json_subarticle['intro']
            html_subarticle_filename = filename.replace('.json', '.html')
            image_filepath = f'''/images/{article_slug}/{filename_base}/{json_subarticle['keyword_main_slug']}.jpg'''
            output_list.append(
                {
                    'title': json_subarticle['keyword_main_pretty'],
                    'desc': json_subarticle_intro,
                    'href': f'/{article_slug}/{html_subarticle_filename}',
                    'anchor': json_subarticle_title,
                    'image_src': image_filepath,
                    'image_alt': f'''{json_subarticle['keyword_main']}''',
                }
            )
        json_article[key] = output_list
        io.json_write(json_article_filepath, json_article)

def json_gen(article_obj, regen=False, dispel=False):
    article_slug = article_obj["article_slug"]
    print(f'ARTICLE: {article_slug} [json]')
    json_article_filepath = f'{g.database_folderpath}/json/{article_slug}.json'
    json_article = io.json_read(json_article_filepath, create=True)
    json_article['article_slug'] = article_slug
    json_article['article_type'] = article_obj['article_type']
    json_article['main_list_num'] = article_obj['main_list_num']
    json_article['keyword_main'] = article_obj['keyword_main']
    json_article['keyword_main_pretty'] = article_obj['keyword_main_pretty']
    json_article['keyword_main_title'] = article_obj['keyword_main_title']
    json_article['keyword_main_slug'] = article_obj['keyword_main_slug']
    json_article['pin_board_name'] = article_obj['pin_board_name']
    json_article['links'] = article_obj['links']
    json_article['images_prompts'] = article_obj['images_prompts']
    io.json_write(json_article_filepath, json_article)
    if json_article['article_type'] == 'listicle':
        json_title_gen(article_slug, regen=regen, dispel=dispel)
        json_intro_gen(article_slug, regen=regen, dispel=dispel)
        json_list_init_gen(article_slug, regen=regen, dispel=dispel)
        json_list_desc_gen(article_slug, regen=regen, dispel=dispel)
        json_list_alt_gen(article_slug, regen=regen, dispel=dispel)
    elif json_article['article_type'] == 'category':
        json_category_title_gen(article_slug, regen=regen, dispel=dispel)
        json_intro_gen(article_slug, regen=regen, dispel=dispel)
        json_category_sections_gen(article_slug, regen=True, dispel=dispel)

def html_gen_old(article_slug, article_obj=None):
    print(f'ARTICLE: {article_slug} [html]')
    html_folderpath = f'{g.website_folderpath}/{article_slug}'
    io.folders_recursive_gen(html_folderpath)
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    html_article = ''
    html_article += f'<h1>{polish.sanitize(json_article["article_title"].title())}</h1>\n'
    src = f'''/images/{json_article['article_slug']}/{json_article['keyword_main_slug']}.jpg'''
    alt = f'''{json_article['keyword_main']}.jpg'''
    html_article += f'''<img src="{src}" alt="{alt}">\n'''
    html_article += f'<p>{polish.sanitize(json_article["intro"])}</p>\n'
    html_article += f'<h2>{polish.sanitize(json_article["keyword_main_pretty"].title())}</h2>\n'
    main_list = json_article['main_list']
    html_article += f'''<div class="listicle">\n'''
    for i, item in enumerate(main_list):
        image_filename = f'''{item['image_filename']}'''
        image_desc = f'''{i+1}. {polish.sanitize(item['image_desc'])}'''
        src = f'/images/{article_slug}/{image_filename}'
        alt = f'''{item['image_alt']}'''
        html_article += f'''<p>{polish.sanitize(image_desc)}</p>\n'''
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

def html_category_gen(article_obj):
    article_slug = article_obj['article_slug']
    print(f'ARTICLE: {article_slug} [html]')
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
    main_list = json_article['main_list']
    for i, item in enumerate(main_list):
        html_article += f'<h2>{item["title"].title()}</h2>\n'
        html_article += f'''<img src="{item['image_src']}" alt="{item['image_alt']}">\n'''
        html_article += f'<p>{item["desc"].capitalize()}</p>\n'
        html_article += f'''<p>See <a href="{item['href']}">{item['anchor']}</a> for more.</p>\n'''
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

def html_listicle_gen(article_slug):
    print(f'ARTICLE: {article_slug} [html]')
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
        html_article += f'''<div style="margin-bottom: 4.8rem;"><a class="button-default" href="{src}">Download Image</a></div>'''
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

def html_gen(article_slug, article_obj=None):
    if article_obj:
        if article_obj['article_type'] == 'category':
            html_category_gen(article_obj)
        elif article_obj['article_type'] == 'listicle':
            html_listicle_gen(article_slug)
    else:
        html_listicle_gen(article_slug)

