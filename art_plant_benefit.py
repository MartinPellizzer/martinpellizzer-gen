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

def gen_intro(vertex_plant, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_name_scientific = vertex_plant['plant_name_scientific']
    benefits_names = [benefit['name'] for benefit in vertex_plant['plant_benefits']]
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

def gen_intro_study(vertex_plant, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_name_scientific = vertex_plant['plant_name_scientific']
    key = 'intro_study'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        reply = studies.gen_study_snippet(plant_name_scientific.capitalize())
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)

def gen_list_init(vertex_plant, json_article_filepath):
    json_article = json_read(json_article_filepath)
    key = 'plant_benefits'
    if key not in json_article: json_article[key] = []
    # json_article[key] = [] # uncomment this line to regen
    json_article_benefits_names = [obj['benefit_name'] for obj in json_article['plant_benefits']]
    for vertex_plant_benefit in vertex_plant[key][:json_article['main_lst_num']]:
        if vertex_plant_benefit['name'] not in json_article_benefits_names:
            json_article[key].append({
                'benefit_name': vertex_plant_benefit['name']
            })
            json_write(json_article_filepath, json_article)

def gen_list_update(vertex_plant, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_name_scientific = vertex_plant['plant_name_scientific']
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

def gen_benefit_preparations(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    for obj in json_article['plant_benefits']:
        benefit_name = obj['benefit_name']
        llm.gen_json_list_base(
            key = 'benefit_preparations',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a list of 3-5 herbal preparations names of the {plant_name_scientific} plant that best give the following benefit: {benefit_name}.
                Reply in JSON using the following format:
                [
                    {{"name": "write name of preparation 1 here"}},
                    {{"name": "write name of preparation 2 here"}},
                    {{"name": "write name of preparation 3 here"}}
                ]
                Always end the reply with the character "]".
                Reply in as few words as possible.
                Include the scientific name of the plant at the start of the preparation.
                If you can answer, reply with only the JSON.
                If you can't answer, reply with only "I can't reply".
            ''',
            regen = False,
            print_prompt = True,
        )

def gen_benefit_constituents_table(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    for obj in json_article['plant_benefits']:
        benefit_name = obj['benefit_name']
        llm.gen_json_list_name_and_list(
            key = 'benefit_constituents',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a list of 3-5 medicinal consitutents names of the {plant_name_scientific} plant that best give the following benefit: {benefit_name}.
                Also, for each of these constituents write a list of 3-5 ailments related to the above mentioned benefit that it helps cure.
                Reply in JSON using the following format:
                [
                    {{"name": "write name of preparation 1 here", "list": ["ailment 1", "ailment 2", "ailment 3"]}},
                    {{"name": "write name of preparation 2 here", "list": ["ailment 1", "ailment 2", "ailment 3"]}},
                    {{"name": "write name of preparation 3 here", "list": ["ailment 1", "ailment 2", "ailment 3"]}}
                ]
                Always end the reply with the character "]".
                Reply in as few words as possible.
                If you can answer, reply with only the JSON.
                If you can't answer, reply with only "I can't reply".
            ''',
            regen=False, 
            print_prompt=False,
        )


def gen_art_plant_benefits_json(vertex_plant, json_article_filepath):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_names_common = vertex_plant['plant_names_common']
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_names_common'] = plant_names_common
    json_article['url'] = f'herbs/{plant_slug}/benefit'
    json_article['title'] = f'best benefits of {plant_name_scientific}'
    if 'main_lst_num' not in json_article: json_article['main_lst_num'] = random.choice([7, 9, 11, 13])
    json_write(json_article_filepath, json_article)

    gen_intro(vertex_plant, json_article_filepath)
    gen_intro_study(vertex_plant, json_article_filepath)
    gen_list_init(vertex_plant, json_article_filepath)
    gen_list_update(vertex_plant, json_article_filepath)
    gen_benefit_preparations(vertex_plant, json_article_filepath)
    gen_benefit_constituents_table(vertex_plant, json_article_filepath)

def gen_art_plant_benefits_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_slug = json_article['plant_slug']
    plant_name_scientific = json_article['plant_name_scientific']
    page_title = plant_name_scientific
    article_title = f'{json_article["main_lst_num"]} best benefits of {page_title}'.title()
    html_article = ''
    html_article += f'<h1>{article_title}</h1>\n'
    html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    # study
    intro_study = json_article['intro_study']
    if intro_study != '' and intro_study != 'N/A':
        html_article += f'''
            <div class="study">
                <div class="study-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" />
                    </svg>
                    <p>Featured Study</p>
                </div>
                <p>
                    {intro_study}
                </p>
            </div>
        '''
    html_article += f'<p style="margin-top: 16px; margin-bottom: 32px;">This page lists the most important health benefits of {plant_name_scientific.capitalize()}.</p>\n'
    # toc
    html_article += '[html_intro_toc]\n'
    i = 0
    for plant_benefit in json_article['plant_benefits'][:]:
        i += 1
        benefit_name = plant_benefit['benefit_name'].capitalize()
        benefit_desc = plant_benefit['benefit_desc']
        benefit_desc = plant_benefit['benefit_desc']
        html_article += f'<h2>{i}. {benefit_name}</h2>\n'
        html_article += f'{utils.text_format_sentences_html(benefit_desc)}\n'
        html_article += f'<p style="font-weight: bold;">Top Preparations:</p>\n'
        html_article += f'<ul>\n'
        for benefit_preparation in plant_benefit['benefit_preparations']:
            preparation_name = benefit_preparation['name']
            preparation_name = preparation_name.lower().replace(plant_name_scientific.lower(), '').strip()
            html_article += f'<li>{preparation_name.capitalize()}</li>\n'
        html_article += f'</ul>\n'
        # plant preparations table 
        plant_constituents = plant_benefit['benefit_constituents']
        html_article += f'<p>The following table displays the major constituents of {plant_name_scientific.capitalize()} and examples of ailments they help cure that are related to {benefit_name}.</p>\n'
        html_article += f'<table style="width: 100%;">\n'
        html_article += f'<tr>\n'
        html_article += f'<th>Constituents</th>\n'
        html_article += f'<th>Ailments</th>\n'
        html_article += f'</tr>\n'
        for constituent in plant_constituents:
            constituent_name = constituent['name'].capitalize()
            constituent_list = constituent['list']
            constituent_list_prompt = ', '.join(constituent['list']).capitalize()
            html_article += f'<tr>\n'
            html_article += f'<td>{constituent_name}</td>\n'
            html_article += f'<td>{constituent_list_prompt}</td>\n'
            html_article += f'</tr>\n'
        html_article += f'</table>\n'
    # toc
    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}/benefit.html')
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

# Before this function:
#     knowledge graph benefits
#     image plant
def gen_art_plant_benefits(vertex_plant):
    plant_slug = vertex_plant['plant_slug']
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}/herbs/{plant_slug}'
    html_article_filepath = f'{html_article_folderpath}/benefit.html'
    json_article_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'

    gen_art_plant_benefits_json(vertex_plant, json_article_filepath)
    gen_art_plant_benefits_html(html_article_filepath, json_article_filepath)
