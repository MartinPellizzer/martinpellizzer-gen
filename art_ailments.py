import os
import random

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

import g
import llm
import utils
import studies
import components

def get_ailments_names():
    with open('ailments.csv') as f: 
        ailments_names = [line.lower().strip() for line in f.read().split('\n') if line.strip() != '']
    return ailments_names

def gen_intro(json_article_filepath):
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about medicinal herbs for common ailments.
            Include a definition of what common ailments are.
            Include why medicinal herbs are a great way to treat common ailments.
            Include examples of common ailments you can tread with medicinal herbs.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: Ailments are .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_list_init(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    key = 'ailments'
    if key not in json_article: json_article[key] = []
    if regen: json_article[key] = []
    ailments_names = get_ailments_names()
    ailments_slugs = [utils.sluggify(ailment_name) for ailment_name in ailments_names]
    json_article_ailments_names = [obj['ailment_name'] for obj in json_article['ailments']]
    for ailment_name in ailments_names:
        if ailment_name not in json_article_ailments_names:
            json_article[key].append({
                'ailment_name': ailment_name
            })
            json_write(json_article_filepath, json_article)

def gen_list_desc(json_article_filepath, regen=False):
    json_article = json_read(json_article_filepath)
    for obj in json_article['ailments'][:]:
        ailment_name = obj['ailment_name']
        llm.ai_paragraph_gen(
            key = 'ailment_desc',
            filepath = json_article_filepath, 
            data = json_article, 
            obj = obj, 
            prompt = f'''
                Write a short 4-sentence paragraph about the {ailment_name} ailment and the best medicinal herbs to treat this ailment.
                Include a definition of the {ailment_name} ailment.
                Include why it's important to treat this ailment.
                Include the best medicinal herbs to treat this ailment.
                Include how to use the above mentioned herbs to treat this ailment.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {ailment_name.capitalize()} is .
            ''',
            regen = regen,
            print_prompt = True,
        )

def gen_art_ailments_json(json_article_filepath):
    json_article = json_read(json_article_filepath, create=True)
    json_article['url'] = f'ailments.html'
    json_article['title'] = f'ailments'
    json_write(json_article_filepath, json_article)

    gen_intro(json_article_filepath)
    gen_list_init(json_article_filepath, regen=False)
    gen_list_desc(json_article_filepath, regen=False)

def gen_art_ailments_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    page_title = 'ailments'
    html_article = ''
    html_article += f'<h1>Ailments</h1>\n'
    # html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    for i, ailment in enumerate(json_article['ailments']):
        ailment_name = ailment['ailment_name']
        ailment_desc = ailment['ailment_desc']
        ailment_slug = utils.sluggify(ailment_name)
        html_article += f'<h2>{i+1}. {ailment_name.capitalize()}</h2>\n'
        html_article += f'{utils.text_format_sentences_html(ailment_desc)}\n'
        html_article += f'<p>Check the <a href="/ailments/{ailment_slug}.html">best herbal remedies for {ailment_name}</a>.</p>\n'
    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'ailments.html')
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

def gen_art_ailments():
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}'
    html_article_filepath = f'{html_article_folderpath}/ailments.html'
    json_article_filepath = f'database/pages/ailments.json'

    gen_art_ailments_json(json_article_filepath)
    gen_art_ailments_html(html_article_filepath, json_article_filepath)

