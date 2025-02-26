import os

from nltk import tokenize

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

import g
import llm
import components
import utils

def gen_art_plant(vertex_plant):
    pass

def gen_art_plant_benefits_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_slug = json_article['plant_slug']
    plant_name_scientific = json_article['plant_name_scientific']
    page_title = plant_name_scientific
    article_title = f'{json_article["main_lst_num"]} best benefits of {page_title}'.title()
    html_article = ''
    html_article += f'<h1>{article_title}</h1>\n'
    html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
    i = 0
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    for plant_benefit in json_article['plant_benefits'][:]:
        i += 1
        benefit_name = plant_benefit['benefit_name'].capitalize()
        benefit_desc = plant_benefit['benefit_desc']
        benefit_desc = plant_benefit['benefit_desc']
        html_article += f'<h2>{i}. {benefit_name}</h2>\n'
        html_article += f'{utils.text_format_sentences_html(benefit_desc)}\n'
    # toc
    html_article, json_toc = components.toc(html_article)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/benefit.html')
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {components.html_head(page_title)}
        <body>
            {components.html_header()}
            <main style="margin-top: 48px;" class="container-xl mob-flex gap-48">
                <article style="flex: 2;">
                    {html_breadcrumbs}
                    {html_article}
                </article>
                <aside style="flex: 1; position: sticky; top: 124px; z-index: 999; align-self: flex-start; overflow-y: auto; height: 100vh;">
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

# Before this function:
#     knowledge graph benefits
#     image plant
def gen_art_plant_benefits(vertex_plant):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_names_common = vertex_plant['plant_names_common']
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'
    html_article_filepath = f'{html_article_folderpath}/benefit.html'
    json_article_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
    # ;json
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_names_common'] = plant_names_common
    json_article['plant_url'] = f'herbs/{plant_slug}/benefit.html'
    json_article['title'] = f'{plant_name_scientific} benefits'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)
    # ;json intro
    benefits_names = [benefit['benefit_name'] for benefit in json_article['plant_benefits']]
    benefits_names_prompt = ', '.join(benefits_names[:3])
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the benefit of the {plant_name_scientific} plant.
            Include a definition of what this plant is.
            Include the bioactive compounds that gives this plant these benefits.
            Include the following benefits: {benefits_names_prompt}.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} .
        ''',
        regen = False,
        print_prompt = True,
    )

    # ;json list
    key = 'plant_benefits'
    if key not in json_article: json_article[key] = []
    # json_article[key] = [] # uncomment this line to regen
    json_article_benefits_names = [obj['benefit_name'] for obj in json_article['plant_benefits']]
    # ;json list init
    for vertex_plant_benefit in vertex_plant[key][:json_article['main_lst_num']]:
        if vertex_plant_benefit['name'] not in json_article_benefits_names:
            json_article[key].append({
                'benefit_name': vertex_plant_benefit['name']
            })
            json_write(json_article_filepath, json_article)
    # ;json list update
    for obj in json_article['plant_benefits'][:]:
        plant_benefit_name = obj['benefit_name']
        llm.ai_paragraph_gen(
            key = 'benefit_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 4-sentence paragraph about the following benefit of the {plant_name_scientific} plant: {plant_benefit_name}.
                In sentence 1, explain what this benefit is (give definition).
                In sentence 2, explain why this benefit is important (include examples).
                In sentence 3, explain why this plant has this benefit (include bioactive constituents).
                In sentence 4, explain how to use this plant best to get this benefit (include herbal preparations).
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name_scientific.capitalize()} {plant_benefit_name.lower()} .
            ''',
            regen = False,
            print_prompt = True,
        )

    gen_art_plant_benefits_html(html_article_filepath, json_article_filepath)
