# TODO: fix breadcrumbs for plant article
# TODO: complete chatgpt suggestions for paginated pages

import os
import json
import random
import shutil
from pathlib import Path

from lib import g
from lib import io
from lib import llm
from lib import polish
from lib import components
from lib import sections

plants_num = 10000

wcvp_data = io.csv_to_dict(f'{g.WCVP_FOLDERPATH}/wcvp_names.csv', '|')
wcvp_data = wcvp_data[:plants_num]

def sitemaps_gen():
    web_urls = []
    for cluster_i, cluster in enumerate(clusters):
        print(f'>>> {cluster_i}/{len(clusters)} - {cluster}')
        cluster_folderpath = f'''{g.DATABASE_FOLDERPATH}/json/plants-{cluster['plants_letter_first']}'''
        plants = cluster['plants']
        for plant_i, plant in enumerate(plants):
            plant_name_scientific = plant['plant_name_scientific']
            plant_family = plant['plant_family']
            plant_slug = polish.sluggify(plant_name_scientific)
            web_urls.append(f'''{g.WEB_PLANTS_URL}/plants-{cluster['plants_letter_first']}/{plant_slug}/''')
    for web_url in web_urls[:]:
        print(web_url)
    print()
    quit()
    sitemaps_folderpath = f'{g.WEBSITE_FOLDERPATH}/sitemaps'
    try: os.makedirs(sitemaps_folderpath)
    except: pass
    herbs_folderpath = f'{g.SSOT_FOLDERPATH}/herbs/herbs-wcvp/medicinal'
    filenames = []
    for filename in os.listdir(f'{herbs_folderpath}'):
        filename_base = filename.split('.')[0]
        filenames.append(f'{g.WEB_HERBS_URL}/{filename_base}.html')
    ### chunks
    chunks = []
    chunk = []
    chunk_len = 0
    for filename in filenames:
        if chunk_len >= 30000:
            chunks.append(chunk)
            chunk = [filename]
            chunk_len = 0
        else:
            chunk.append(filename)
            chunk_len += 1
    if chunk_len != 0:
        chunks.append(chunk)
    ### sitemaps
    for chunk_i, chunk in enumerate(chunks):
        sitemap = ''
        sitemap += '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for filepath in chunk:
            sitemap += f'''
                <url>
                <loc>{filepath}</loc>
                </url>
            '''.strip() + '\n'
        sitemap += '</urlset>\n'
        io.file_write(f'{sitemaps_folderpath}/sitemap-herbs-wcvs-medicinal-{chunk_i}.xml', sitemap.strip())

def answer_score_extract(json_data):
    _objs = []
    for item in json_data:
        try: answer = item['answer']
        except: continue
        try: score = item['score']
        except: continue
        _objs.append({
            "answer": answer, 
            "score": score,
        })
    return _objs

def total_score_calc(outputs):
    outputs_final = []
    for output in outputs:
        outputs_final.append({
            'answer': output['answer'],
            'mentions': int(output['mentions']),
            'confidence_score': int(output['confidence_score']),
            'total_score': int(output['mentions']) * int(output['confidence_score']),
        })
    outputs_final = sorted(outputs_final, key=lambda x: x['total_score'], reverse=True)
    print('***********************')
    print('***********************')
    print('***********************')
    for output in outputs_final:
        print(output)
    print('***********************')
    print('***********************')
    print('***********************')
    return outputs_final

def breadcrumbs_gen(url):
    breadcrumb_list = url.split('/')
    breadcrumb_href = f'/'
    breadcrumb_html = f'<a href="{breadcrumb_href}">Home</a>'
    for breadcrumb_i, breadcrumb_text in enumerate(breadcrumb_list):
        breadcrumb_href += '/' + breadcrumb_text
        breadcrumb_href = breadcrumb_href.replace('//', '/')
        breadcrumb_text = breadcrumb_text.strip().replace('-', ' ').title()
        if breadcrumb_i == len(breadcrumb_list)-1:
            breadcrumb_html += f' > {breadcrumb_text}'
        else:
            breadcrumb_html += f' > <a href="{breadcrumb_href}">{breadcrumb_text}</a>'
    html = f'''
        <section class="breadcrumbs">
            <div class="container-xl">
                {breadcrumb_html}
            </div>
        </section>
    '''
    return html

def clusters_get():
    clusters = []
    for wcvp_item_i, wcvp_item in enumerate(wcvp_data):
        print(f'>>> {wcvp_item_i}/{len(wcvp_data)} - {wcvp_item}')
        plant_scientific_name = wcvp_item['taxon_name']
        plant_family = wcvp_item['family']
        found = False
        plant_letter_first = plant_scientific_name.lower()[0]
        letters_valid = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        if plant_letter_first not in letters_valid: continue
        _obj = {
            'plant_name_scientific': plant_scientific_name,
            'plant_family': plant_family,
        }
        for cluster in clusters:
            if cluster['plants_letter_first'] == plant_letter_first:
                cluster['plants'].append(_obj)
                found = True
                break
        if not found:
            clusters.append(
                {
                    'plants_letter_first': plant_letter_first,
                    'plants': [_obj],
                }
            )
    return clusters
clusters = clusters_get()
clusters = sorted(clusters, key=lambda x: x['plants_letter_first'], reverse=False)

def cluster_gen(cluster):
    cluster_letter = cluster['plants_letter_first']
    cluster_size = 50
    page_url_slug = f'''plants-{cluster['plants_letter_first']}'''
    cluster_folderpath = f'''{g.WEBSITE_FOLDERPATH}/plants-{cluster['plants_letter_first']}'''
    if not os.path.exists(cluster_folderpath):
        os.makedirs(cluster_folderpath)
    _folder = Path(f'{g.WEBSITE_FOLDERPATH}/{page_url_slug}/page')
    if _folder.exists() and _folder.is_dir():
        shutil.rmtree(_folder)
    ### pages
    pages = []
    page_cur = []
    plants = cluster['plants']
    for plant_i, plant in enumerate(plants):
        if len(page_cur) < cluster_size:
            page_cur.append(plant)
        else:
            pages.append(page_cur)
            page_cur = [plant]
    if page_cur != []: pages.append(page_cur)
    ########################################
    # html
    ########################################
    for page_i, page in enumerate(pages):
        html_article = ''
        ### hero
        html_article += f'''
            <div class="container-md">
                <h1>
                    Plants Starting with {cluster['plants_letter_first'].upper()} - Page {page_i+1} | Plant Encyclopedia
                </h1>
                <p>
                    This page lists plants that start with the letter {cluster_letter.upper()}. It features a seletion of plants (from number {page_i*cluster_size} to {(page_i+1)*cluster_size-1}). Each entry includes scientific details and quick links to related topics.
                </p>
            </div>
        '''
        ### cards
        html_article += f'''<div class="container-xl" style="margin-bottom: 9.6rem;">\n'''
        html_article += f'''<ul itemscope itemtype="https://schema.org/ItemList" class="grid-4" style="list-style: none; margin: 0; padding: 0; gap: 4.8rem;">\n'''
        for plant_i, plant in enumerate(page):
            plant_name_scientific = plant['plant_name_scientific']
            plant_family = plant['plant_family']
            plant_slug = polish.sluggify(plant_name_scientific)
            json_plant_folderpath = f'{g.DATABASE_FOLDERPATH}/ssot/plants'
            json_plant_filepath = f'''{json_plant_folderpath}/{plant_slug}.json'''
            json_plant_data = io.json_read(json_plant_filepath)
            plant_name_common = json_plant_data['plants_names_common'][0]['answer'].capitalize()
            plant_origin = json_plant_data['plant_origin'][0]['answer'].capitalize()
            html_article += f'''
                <li itemscope itemtype="https://schema.org/ListItem">
                    <meta itemprop="position" content="{plant_i+1}">
                    <div itemscope itemtype="https://schema.org/Taxon" itemprop="item">
                        <a href="/{page_url_slug}/{plant_slug}/" itemprop="url" style="text-decoration: none;">
                            <h3 itemprop="name">{plant_name_common}</h3>
                        </a>
                        <p>
                            <span itemprop="scientificName">{plant_name_scientific}</span>
                        </p>
                        <ul style="list-style: none; margin: 0; padding: 0;">
                            <li><strong>Origin:</strong> <span itemprop="nativeRange">{plant_origin}</span></li>
                        </ul>
                    </div>
                </li>
            '''
        html_article += f'''</ul>\n'''
        html_article += f'''</div>\n'''
        ### pagination links
        if page_i == 0: 
            html_article += f'''
                <div class="container-md">
                    <a href="/{page_url_slug}/page/{page_i+2}">Next</a>
                </div>
            '''
        elif page_i == 1: 
            if page_i == len(pages) - 1: 
                html_article += f'''
                    <div class="container-md">
                        <a href="/{page_url_slug}">Prev</a>
                    </div>
                '''
            else:
                html_article += f'''
                    <div class="container-md">
                        <a href="/{page_url_slug}">Prev</a>
                        <a href="/{page_url_slug}/page/{page_i+2}">Next</a>
                    </div>
                '''
        elif page_i == len(pages) - 1: 
            html_article += f'''
                <div class="container-md">
                    <a href="/{page_url_slug}/page/{page_i}">Prev</a>
                </div>
            '''
        else:
            html_article += f'''
                <div class="container-md">
                    <a href="/{page_url_slug}/page/{page_i}">Prev</a>
                    <a href="/{page_url_slug}/page/{page_i+2}">Next</a>
                </div>
            '''
        letter = f'''{cluster['plants_letter_first']}'''
        ### breadcrumbs
        html_breadcrumbs = f'''
            <section class="breadcrumbs">
                <div class="container-xl">
                    <a href="/">Home</a> 
                    <a href="/plants/"> > Plants</a> 
                    <span> > Plants {letter.upper()}</span> 
                </div>
            </section>
        '''
        meta_title = ''
        meta_description = ''
        meta_pagination = ''
        meta_href_canonical = ''
        meta_href_prev = ''
        meta_href_next = ''
        if page_i + 1 == 1: 
            meta_href_canonical = f'''/plants-{letter}/'''
            meta_href_next = f'''/plants-{letter}/page/2'''
        elif page_i + 1 == 2: 
            meta_href_canonical = f'''/plants-{letter}/page/{page_i+1}/'''
            meta_href_prev = f'''/plants-{letter}/'''
            meta_href_next = f'''/plants-{letter}/page/{page_i+1+1}'''
        elif page_i + 1 == len(pages): 
            meta_href_canonical = f'''/plants-{letter}/page/{page_i+1}/'''
            meta_href_prev = f'''/plants-{letter}/page/{page_i+1-1}'''
        else:
            meta_href_canonical = f'''/plants-{letter}/page/{page_i+1}/'''
            meta_href_prev = f'''/plants-{letter}/page/{page_i+1-1}'''
            meta_href_next = f'''/plants-{letter}/page/{page_i+1+1}'''
        if meta_href_canonical != '': meta_pagination += f'''<link rel="canonical" href="{meta_href_canonical}">\n'''
        if meta_href_prev != '': meta_pagination += f'''<link rel="prev" href="{meta_href_prev}">\n'''
        if meta_href_next != '': meta_pagination += f'''<link rel="next" href="{meta_href_next}">\n'''
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta name="viewport" content="width=device-width, inital-scale=1">
                <link rel="stylesheet" href="/style.css">
                {meta_pagination}
            </head>
            <body>
                {sections.header()}
                <main>
                    {html_breadcrumbs}
                    <div class="article">
                        {html_article}
                    </div>
                </main>
                {sections.footer()}
            </body>
            </html>
        '''
        if page_i == 0:
            html_filepath = f'{g.WEBSITE_FOLDERPATH}/{page_url_slug}/index.html'
        else:
            folderpath = f'''{g.WEBSITE_FOLDERPATH}/{page_url_slug}/page'''
            if not os.path.exists(folderpath): os.makedirs(folderpath)
            folderpath = f'''{g.WEBSITE_FOLDERPATH}/{page_url_slug}/page/{page_i+1}'''
            if not os.path.exists(folderpath): os.makedirs(folderpath)
            html_filepath = f'{g.WEBSITE_FOLDERPATH}/{page_url_slug}/page/{page_i+1}/index.html'
        print(html_filepath)
        with open(html_filepath, 'w') as f: f.write(html)

def plant_names_common_gen(json_filepath, regen=False, clear=False):
    json_data = io.json_read(json_filepath)
    plant_name_scientific = json_data['plant_name_scientific']
    key = 'plants_names_common'
    if key not in json_data: json_data[key] = ''
    if regen: json_data[key] = ''
    if clear: 
        json_data[key] = ''
        io.json_write(json_filepath, json_data)
        return
    if json_data[key] == '' or json_data[key] == []:
        outputs = []
        for i in range(10):
            print(f'{i} - {plant_name_scientific}')
            prompt = f'''
                Write a list of the most well known and popular common names for the following plant with scientific name: {plant_name_scientific}.
                Also write a confidence score from 1 to 10, indicating how sure you are about your answer.
                Reply using the following JSON format:
                [
                    {{"answer": "write common name 1 here", "score": "write score 1 here"}},
                    {{"answer": "write common name 2 here", "score": "write score 2 here"}},
                    {{"answer": "write common name 3 here", "score": "write score 3 here"}}
                ]
                Reply only with the JSON.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt)
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply_data = {}
            try: reply_data = json.loads(reply)
            except: pass 
            if reply_data != {}:
                _objs = answer_score_extract(reply_data)
                for _obj in _objs:
                    answer = _obj['answer'].lower()
                    score = _obj['score']
                    found = False
                    for output in outputs:
                        if answer in output['answer']: 
                            output['mentions'] += 1
                            output['confidence_score'] += int(score)
                            found = True
                            break
                    if not found:
                        outputs.append({
                            'answer': answer, 
                            'mentions': 1, 
                            'confidence_score': int(score), 
                        })
        outputs = total_score_calc(outputs)
        json_data[key] = outputs
        # print(json_filepath)
        # print(json_data)
        io.json_write(json_filepath, json_data)

def plant_origin_gen(json_filepath, regen=False, clear=False):
    json_data = io.json_read(json_filepath)
    plant_name_scientific = json_data['plant_name_scientific']
    key = 'plant_origin'
    if key not in json_data: json_data[key] = ''
    if regen: json_data[key] = ''
    if clear: 
        json_data[key] = ''
        io.json_write(json_filepath, json_data)
        return
    if json_data[key] == '' or json_data[key] == []:
        outputs = []
        for i in range(10):
            print(f'{i} - {plant_name_scientific}')
            rand_num = random.randint(7, 13)
            prompt = f'''
                Write a list of {rand_num} geographical regions of origin of the plant with scientific name: {plant_name_scientific}.
                Also write a confidence score from 1 to 10, indicating how sure you are about your answer.
                Reply using the following JSON format:
                [
                    {{"answer": "write origin region 1 here", "score": "write score 1 here"}},
                    {{"answer": "write origin region 2 here", "score": "write score 2 here"}},
                    {{"answer": "write origin region 3 here", "score": "write score 3 here"}}
                ]
                Reply only with the JSON.
            '''
            prompt += f'/no_think'
            reply = llm.reply(prompt)
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply_data = {}
            try: reply_data = json.loads(reply)
            except: pass 
            if reply_data != {}:
                _objs = answer_score_extract(reply_data)
                for _obj in _objs:
                    answer = _obj['answer'].lower()
                    score = _obj['score']
                    found = False
                    for output in outputs:
                        if answer in output['answer']: 
                            output['mentions'] += 1
                            output['confidence_score'] += int(score)
                            found = True
                            break
                    if not found:
                        outputs.append({
                            'answer': answer, 
                            'mentions': 1, 
                            'confidence_score': int(score), 
                        })
        outputs = total_score_calc(outputs)
        json_data[key] = outputs
        io.json_write(json_filepath, json_data)

def plants_json_gen():
    json_folderpath = f'{g.DATABASE_FOLDERPATH}/ssot/plants'
    try: os.mkdir(json_folderpath)
    except: pass
    ###
    for wcvp_item_i, wcvp_item in enumerate(wcvp_data):
        print(f'>>> {wcvp_item_i}/{len(wcvp_data)} - {wcvp_item}')
        plant_name_scientific = wcvp_item['taxon_name']
        plant_family = wcvp_item['family']
        plant_slug = polish.sluggify(plant_name_scientific)
        ###
        json_filepath = f'''{json_folderpath}/{plant_slug}.json'''
        json_data = io.json_read(json_filepath, create=True)
        json_data['plant_slug'] = plant_slug
        json_data['plant_name_scientific'] = plant_name_scientific
        json_data['plant_family'] = plant_family
        io.json_write(json_filepath, json_data)
        ###
        plant_names_common_gen(json_filepath, regen=False, clear=False)
        plant_origin_gen(json_filepath, regen=False, clear=False)

def plants_html_gen():
    ########################################
    # HUB -> /plants-[letter]/[plant]
    ########################################
    page_url_slug = f'''plants'''
    ########################################
    # html
    ########################################
    html_article = ''
    html_article += f'<h1>Plants</h1>\n'
    html_article += f'''<ul>\n'''
    for cluster_i, cluster in enumerate(clusters):
        html_article += f'''
            <li>
                <a href="/plants-{cluster['plants_letter_first']}/">Plants {cluster['plants_letter_first'].title()}</a>
            </li>\n'''
    html_article += f'''</ul>\n'''
    meta_title = ''
    meta_description = ''
    html_breadcrumbs = f'''
        <section class="breadcrumbs">
            <div class="container-xl">
                <a href="/">Home</a> 
                <span> > Plants</span> 
            </div>
        </section>
    '''
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, inital-scale=1">
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            {sections.header()}
            <main>
                {html_breadcrumbs}
                <div class="article container-md">
                    {html_article}
                </div>
            </main>
            {sections.footer()}
        </body>
        </html>
    '''
    html_filepath = f'{g.WEBSITE_FOLDERPATH}/plants/index.html'
    print(html_filepath)
    with open(html_filepath, 'w') as f: f.write(html)

def main():
    sitemaps_gen()
    quit()
    plants_json_gen()
    # quit()
    plants_html_gen()
    ########################################
    # HUB -> /plants
    ########################################
    ### json plants-[letter] pages
    for cluster_i, cluster in enumerate(clusters):
        print(f'>>> {cluster_i}/{len(clusters)} - {cluster}')
        cluster_folderpath = f'''{g.DATABASE_FOLDERPATH}/json/plants-{cluster['plants_letter_first']}'''
        if not os.path.exists(cluster_folderpath): os.makedirs(cluster_folderpath)
        plants = cluster['plants']
        for plant_i, plant in enumerate(plants):
            plant_name_scientific = plant['plant_name_scientific']
            plant_slug = polish.sluggify(plant_name_scientific)
            json_plant_filepath = f'''{cluster_folderpath}/{plant_slug}/index.json'''
            json_plant = io.json_read(json_plant_filepath, create=True)
            json_plant['plant_name_scientific'] = plant_name_scientific
            json_plant['plant_slug'] = plant_slug
            io.json_write(json_plant_filepath, json_plant)
    ### json page
    for cluster_i, cluster in enumerate(clusters):
        print(f'>>> {cluster_i}/{len(clusters)} - {cluster}')
        cluster_folderpath = f'''{g.DATABASE_FOLDERPATH}/json/plants-{cluster['plants_letter_first']}'''
        ########################################
        # HUB -> /plants/plants-[letter]
        ########################################
        cluster_gen(cluster)
        ########################################
        # HUB -> /plants-[letter]/[plant]
        ########################################
        plants = cluster['plants']
        for plant_i, plant in enumerate(plants):
            plant_name_scientific = plant['plant_name_scientific']
            plant_family = plant['plant_family']
            plant_slug = polish.sluggify(plant_name_scientific)
            ### ssot data
            json_plant_folderpath = f'{g.DATABASE_FOLDERPATH}/ssot/plants'
            json_plant_filepath = f'''{json_plant_folderpath}/{plant_slug}.json'''
            json_plant_data = io.json_read(json_plant_filepath)
            plant_name_common = json_plant_data['plants_names_common'][0]['answer'].capitalize()
            ### article data
            article_url_slug = f'''plants-{cluster['plants_letter_first']}/{plant_slug}'''
            article_folderpath = f'''{g.WEBSITE_FOLDERPATH}/plants-{cluster['plants_letter_first']}/{plant_slug}'''
            if not os.path.exists(article_folderpath): os.makedirs(article_folderpath)
            json_article_filepath = f'''{cluster_folderpath}/{plant_slug}/index.json'''
            json_article = io.json_read(json_article_filepath, create=True)
            json_article['plant_name_scientific'] = plant_name_scientific
            json_article['plant_slug'] = plant_slug
            json_article['article_title'] = plant_name_scientific
            io.json_write(json_plant_filepath, json_plant)
            ########################################
            # json
            ########################################
            regen = False
            dispel = False
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
                    Write a detailed intro paragraph in 5 sentences for an article about the following plant: {plant_name_common} ({plant_name_scientific}).
                    Write only the paragaraph.
                    Use only ascii characters.
                    Start with the following words: {plant_name_common.capitalize()}, scientifically known as {plant_name_scientific}, 
                '''
                prompt += f'/no_think'
                reply = llm.reply(prompt).strip()
                if '</think>' in reply:
                    reply = reply.split('</think>')[1].strip()
                json_article[key] = reply
                io.json_write(json_article_filepath, json_article)
            ########################################
            # html
            ########################################
            html_article = ''
            html_article += f'<h1>{json_article["article_title"].title()}</h1>\n'
            html_article += f'<p>{json_article["intro"]}</p>\n'
            meta_title = ''
            meta_description = ''
            html = f'''
                <!DOCTYPE html>
                <html lang="en">
                {components.html_head(meta_title, meta_description)}
                <body>
                    {sections.header()}
                    <main>
                        {breadcrumbs_gen(article_url_slug)}
                        <div class="article container-md">
                            {html_article}
                        </div>
                    </main>
                    {sections.footer()}
                </body>
                </html>
            '''
            html_filepath = f'{g.WEBSITE_FOLDERPATH}/{article_url_slug}/index.html'
            print(html_filepath)
            with open(html_filepath, 'w') as f: f.write(html)

