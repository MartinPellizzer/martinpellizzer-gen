import os
import random

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

import g
import llm
import utils
import studies
import components

vault = f'/home/ubuntu/vault'

vertices_plants = json_read(f'{vault}/herbalism/vertices-plants.json')
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

def get_vertices_plants_validated():
    # verity herbs in "wcpo"
    vertices_plants_filtered_tmp = [vertex for vertex in vertices_plants if vertex['plant_slug'] in plants_slugs_filtered] 
    vertices_plants_filtered_tmp = sorted(vertices_plants_filtered_tmp, key=lambda x: x['plant_slug'], reverse=False)
    # remove duplicates
    vertices_plants_filtered = []
    for vertex_plant in vertices_plants_filtered_tmp:
        plant_slug = vertex_plant['plant_slug']
        found = False
        for _vertex_plant in vertices_plants_filtered:
            _plant_slug = _vertex_plant['plant_slug']
            if plant_slug == _plant_slug:
                found = True
                break
        if not found:
            vertices_plants_filtered.append(vertex_plant)
    return vertices_plants_filtered
    
def gen_intro(json_article_filepath, regen):
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about medicinal herbs.
            Include a definition of what medicinal herbs are.
            Include why medicinal herbs are a great natural remedies.
            Include examples of popular medicinal herbs.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: Ailments are .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_list_init(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    key = 'plants'
    if key not in json_article: json_article[key] = []
    if regen: json_article[key] = []
    vertices_plants_filtered = get_vertices_plants_validated()
    plants_names_scientific = [vertex['plant_name_scientific'] for vertex in vertices_plants_filtered]
    plants_slugs = [utils.sluggify(plant_name_scientific) for plant_name_scientific in plants_names_scientific]
    json_article_plants_names = [obj['plant_name_scientific'] for obj in json_article['plants']]
    for plant_name_scientific in plants_names_scientific:
        if plant_name_scientific not in json_article_plants_names:
            json_article[key].append({
                'plant_name_scientific': plant_name_scientific,
            })
            json_write(json_article_filepath, json_article)

def gen_list_desc(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    for obj in json_article['plants'][:]:
        plant_name = obj['plant_name_scientific']
        llm.ai_paragraph_gen(
            key = 'plant_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 4-sentence paragraph about the {plant_name} herb.
                Include a definition of the {plant_name} herb.
                Include examples of bioactive constituents of this herb.
                Include examples of benefits of this herb.
                Include examples of uses of this herb.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {plant_name.capitalize()} is .
            ''',
            regen = regen,
            print_prompt = True,
        )

def gen_art_plants_json(json_article_filepath):
    json_article = json_read(json_article_filepath, create=True)
    json_article['url'] = f'herbs'
    json_article['title'] = f'medicinal herbs'
    json_write(json_article_filepath, json_article)

    gen_intro(json_article_filepath, regen=False)
    gen_list_init(json_article_filepath, regen=False)
    gen_list_desc(json_article_filepath, regen=False)

def gen_art_plants_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    page_title = f'Medicinal Herbs'
    html_article = ''
    html_article += f'<h1>Medicinal Herbs</h1>\n'
    # html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    html_article += f'<p style="margin-top: 16px; margin-bottom: 32px;">This page lists the best medicinal herbs used in herbalism.</p>\n'
    html_article += f'[html_intro_toc]\n'
    for i, plant in enumerate(json_article['plants']):
        plant_name_scientific = plant['plant_name_scientific']
        plant_desc = plant['plant_desc']
        plant_slug = utils.sluggify(plant_name_scientific)
        html_article += f'<h2>{i+1}. {plant_name_scientific.capitalize()}</h2>\n'
        html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
        html_article += f'{utils.text_format_sentences_html(plant_desc)}\n'
        # plant benefits list
        html_article += f'<p style="font-weight: bold;">Example Benefits:</p>\n'
        json_article_plant_benefits_filepath = f'database/pages/herbs/{plant_slug}/benefit.json'
        json_article_plant_benefits = json_read(json_article_plant_benefits_filepath)
        benefits_names = [benefit['benefit_name'] for benefit in json_article_plant_benefits['plant_benefits']]
        html_article += f'<ul>\n'
        rnd_benefit_num = random.randint(3, 5)
        for benefit_name in benefits_names[:rnd_benefit_num]:
            html_article += f'<li>{benefit_name.capitalize()}</li>\n'
        html_article += f'</ul>\n'
        # link
        html_article += f'<p>Check <a href="/herbs/{plant_slug}.html">{plant_name_scientific.title()} Complete Medicinal Profile</a>.</p>\n'
    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'herbs.html')
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
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def gen_art_plants():
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}'
    html_article_filepath = f'{html_article_folderpath}/herbs.html'
    json_article_filepath = f'database/pages/herbs.json'

    gen_art_plants_json(json_article_filepath)
    gen_art_plants_html(html_article_filepath, json_article_filepath)

