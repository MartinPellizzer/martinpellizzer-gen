# TODO: fix breadcrumbs for plant article
# TODO: complete chatgpt suggestions for paginated pages

import os

from lib import g
from lib import io
from lib import llm
from lib import polish
from lib import components
from lib import sections

plants_num = 1000

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

def cluster_gen(cluster):
    page_url_slug = f'''plants-{cluster['plants_letter_first']}'''
    cluster_folderpath = f'''{g.WEBSITE_FOLDERPATH}/plants-{cluster['plants_letter_first']}'''
    if not os.path.exists(cluster_folderpath):
        os.makedirs(cluster_folderpath)
    pages = []
    page_cur = []
    plants = cluster['plants']
    for plant_i, plant in enumerate(plants):
        if len(page_cur) < 10:
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
        html_article += f'''<h1>Plants Starting with {cluster['plants_letter_first'].upper()} - Page {page_i+1} | Plant Encyclopedia</h1>\n'''
        html_article += f'''<ul>\n'''
        for plant_i, plant in enumerate(page):
            plant_name_scientific = plant['plant_name_scientific']
            plant_family = plant['plant_family']
            plant_slug = polish.sluggify(plant_name_scientific)
            html_article += f'''<li><a href="/{page_url_slug}/{plant_slug}/">{plant_name_scientific}</a></li>\n'''
        html_article += f'''</ul>\n'''

        if page_i == 0: 
            html_article += f'''
                <div>
                    <a href="/{page_url_slug}/page/{page_i+2}">Next</a>
                </div>
            '''
        elif page_i == 1: 
            html_article += f'''
                <div>
                    <a href="/{page_url_slug}">Prev</a>
                    <a href="/{page_url_slug}/page/{page_i+2}">Next</a>
                </div>
            '''
        elif page_i == len(pages) - 1: 
            html_article += f'''
                <div>
                    <a href="/{page_url_slug}/page/{page_i}">Prev</a>
                </div>
            '''
        else:
            html_article += f'''
                <div>
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
                    <a href="/plants/plants-{letter}"> > Plants {letter.upper()}</a> 
                </div>
            </section>
        '''

        meta_title = ''
        meta_description = ''

        # TODO: split cluster plants in pages
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
                    <div class="article container-md">
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
    quit()

def main():
    wcvp_data = io.csv_to_dict(f'{g.WCVP_FOLDERPATH}/wcvp_names.csv', '|')
    wcvp_data = wcvp_data[:plants_num]
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
    ### json plant
    for cluster_i, cluster in enumerate(clusters):
        print(f'>>> {cluster_i}/{len(clusters)} - {cluster}')
        cluster_folderpath = f'''{g.DATABASE_FOLDERPATH}/json/plants-{cluster['plants_letter_first']}'''
        if not os.path.exists(cluster_folderpath):
            os.makedirs(cluster_folderpath)
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
        cluster_gen(cluster)
        ### json article
        plants = cluster['plants']
        for plant_i, plant in enumerate(plants):
            plant_name_scientific = plant['plant_name_scientific']
            plant_family = plant['plant_family']
            plant_slug = polish.sluggify(plant_name_scientific)

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
                    Write a detailed intro paragraph in 5 sentences for an article about the following plant: {json_article['plant_name_scientific']}.
                    Write only the paragaraph.
                    Use only ascii characters.
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

