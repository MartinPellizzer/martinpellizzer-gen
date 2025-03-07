import os
import random

from nltk import tokenize

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

import g
import llm
import utils
import studies
import components


vertices_ailments_filepath = f'/home/ubuntu/vault/herbalism/vertices-ailments.json'
vertices_ailments = json_read(vertices_ailments_filepath)

def gen_intro(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the herbal teas used to treat the {ailment_name} ailment.
            Include a definition of what herbal teas for {ailment_name} is.
            Include why herbal teas can treat this ailment.
            Include a lot of examples of herbal teas to treat this ailment and explain why.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: Herbal teas for {ailment_name.capitalize()} are .
        ''',
        regen = regen,
        print_prompt = True,
    )

def gen_list_init(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    key = 'teas'
    if key not in json_article: json_article[key] = []
    if regen: json_article[key] = []
    json_article_plants_slugs = [obj['plant_slug'] for obj in json_article['teas']]
    vertex_ailment = [vertex for vertex in vertices_ailments if vertex['ailment_slug'] == ailment_slug][0]
    teas = vertex_ailment['ailment_teas']
    for tea in teas:
        plant_name_scientific = tea['plant_name_scientific']
        plant_slug = tea['plant_slug']
        if plant_slug not in json_article_plants_slugs:
            json_article[key].append({
                'plant_slug': plant_slug,
                'plant_name_scientific': plant_name_scientific,
            })
            json_write(json_article_filepath, json_article)

def gen_list_desc(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    ailment_name = json_article['ailment_name']
    for obj in json_article['teas'][:]:
        plant_name_scientific = obj['plant_name_scientific']
        llm.ai_paragraph_gen(
            key = 'plant_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 4-sentence paragraph about {plant_name_scientific} tea to treat the {ailment_name} ailment.
                Include bioactive constituents of this tea that help to treat this ailment.
                Include the properties of this herbal tea that help to treat this ailment.
                Include how to make this tea to treat this ailment.
                Include how to consume this tea to treat this ailment.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} tea contains .
            ''',
            regen = regen,
            print_prompt = True,
        )

def gen_art_ailment_tea_json(ailment_name, json_article_filepath):
    ailment_slug = utils.sluggify(ailment_name)
    json_article = json_read(json_article_filepath, create=True)
    json_article['ailment_slug'] = ailment_slug
    json_article['ailment_name'] = ailment_name
    json_article['url'] = f'ailments/{ailment_slug}/tea'
    json_article['title'] = f'best herbal teas for {ailment_name}'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)

    gen_intro(json_article_filepath, regen=False)
    gen_list_init(json_article_filepath, regen=False)
    gen_list_desc(json_article_filepath, regen=False)

def gen_art_ailment_tea_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    main_lst_num = json_article['main_lst_num']
    page_title = f'best herbal teas for {ailment_name}'
    article_title = f'{main_lst_num} best herbal teas for {ailment_name}'.title()
    html_article = ''
    html_article += f'<h1>{article_title}</h1>\n'
    html_article += f'<img src="/images/ailments-teas/{ailment_slug}-teas.jpg" alt="{ailment_name} teas">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    for i, tea in enumerate(json_article['teas'][:main_lst_num]):
        plant_name_scientific = tea['plant_name_scientific']
        plant_slug = utils.sluggify(plant_name_scientific)
        plant_desc = tea['plant_desc']
        html_article += f'<h2>{i+1}. {plant_name_scientific.capitalize()} tea</h2>\n'
        html_article += f'<img src="/images/teas/{plant_slug}-tea.jpg" alt="{plant_name_scientific} tea">\n'
        html_article += f'{utils.text_format_sentences_html(plant_desc)}\n'
    # toc
    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'ailments/{ailment_slug}/tea.html')
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {components.html_head(page_title)}
        <body>
            {components.html_header()}
            <main style="margin-top: 24px;" class="container-xl mob-flex gap-48">
                <article style="flex: 2;" class="article">
                    {html_breadcrumbs}
                    {html_article}
                </article>
                <aside style="flex: 1; position: sticky; top: 100px; z-index: 999; align-self: flex-start; overflow-y: auto; height: 100vh;">
                    {html_toc_sidebar}
                </aside>
            </main>
            {components.html_footer()}
        </body>
        </html>
    '''
    html_article_folderpath = '/'.join(html_article_filepath.split('/')[:-1])
    if not os.path.exists(html_article_folderpath): os.mkdir(html_article_folderpath)
    with open(html_article_filepath, 'w') as f: f.write(html)

def gen_art_ailment_tea(ailment_name):
    ailment_slug = utils.sluggify(ailment_name)
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}/ailments/{ailment_slug}'
    html_article_filepath = f'{html_article_folderpath}/tea.html'
    json_article_filepath = f'database/pages/ailments/{ailment_slug}/tea.json'

    gen_art_ailment_tea_json(ailment_name, json_article_filepath)
    gen_art_ailment_tea_html(html_article_filepath, json_article_filepath)

