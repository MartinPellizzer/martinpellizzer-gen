import os

from oliark_io import json_read, json_write

import g
import llm
import utils
import studies
import components

def gen_intro(json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the {ailment_name} ailment.
            Include a definition of what this ailment is.
            Include why medicinal herbs can treat this ailment.
            Include examples of medicinal herbs to treat this ailment.
            Include examples of herbal preparations (ex. infusions, tinctures, etc...) to treat this ailment.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {ailment_name.capitalize()} is .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_what(json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'what',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about what is the {ailment_name} ailment.
            Include a detailed definition of what this ailment is.
            Include the common symptoms that identifies this ailment.
            Include the negative effects this ailment has on the body.
            Include examples on how this ailment affects your life if you don't treat it.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {ailment_name.capitalize()} is .
        ''',
        regen =  False,
        print_prompt = True,
    )

def gen_causes(json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'causes',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about what are the causes of {ailment_name} ailment.
            Include a lot of examples of what are the causes of this ailment.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {ailment_name.capitalize()} is .
        ''',
        regen =  False,
        print_prompt = True,
    )

def gen_plants(json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'plants',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the medicinal herbs used to treat the {ailment_name} ailment.
            Include a lot of examples of medicinal herbs used to treat this ailment.
            Include why these herbs helps treat this ailmet.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {ailment_name.capitalize()} is treated with herbs such as .
        ''',
        regen =  False,
        print_prompt = True,
    )

def gen_preparations(json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    llm.ai_paragraph_gen(
        key = 'preparations',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the herbal preparations used to treat the {ailment_name} ailment.
            Examples of preparations are: infusions, tinctures, etc...
            Include a lot of examples of preparations used to treat this ailment.
            Include why these preparations helps treat this ailmet.
            Never include names of herbs, only include general preparations.
            Always include "teas" in the preparations.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {ailment_name.capitalize()} is treated with herbal preparations such as .
        ''',
        regen =  False,
        print_prompt = True,
    )

def gen_art_ailment_json(ailment_name, json_article_filepath):
    ailment_slug = utils.sluggify(ailment_name)
    json_article = json_read(json_article_filepath, create=True)
    json_article['ailment_slug'] = ailment_slug
    json_article['ailment_name'] = ailment_name
    json_article['url'] = f'ailments/{ailment_slug}.html'
    json_article['title'] = f'{ailment_name}'
    json_write(json_article_filepath, json_article)

    gen_intro(json_article_filepath)
    gen_what(json_article_filepath)
    gen_causes(json_article_filepath)
    gen_plants(json_article_filepath)
    gen_preparations(json_article_filepath)

def gen_art_ailment_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    ailment_slug = json_article['ailment_slug']
    ailment_name = json_article['ailment_name']
    page_title = json_article['title']
    html_article = ''
    html_article += f'<h1>{page_title.title()}</h1>\n'
    html_article += f'<img src="/images/ailments/{ailment_slug}.jpg" alt="{ailment_name}">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    html_article += f'<h2>What is {ailment_name}?</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["what"])}\n'
    html_article += f'<h2>Causes</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["causes"])}\n'
    html_article += f'<h2>Herbs</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["plants"])}\n'
    html_article += f'<h2>Preparations</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["preparations"])}\n'
    html_article += f'<p>Find out the <a href="/ailments/{ailment_slug}/tea.html">best herbal teas for {ailment_name}</a>.</p>\n'
    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'ailments/{ailment_slug}.html')
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
    if not os.path.exists(html_article_folderpath): 
        os.mkdir(html_article_folderpath)
    with open(html_article_filepath, 'w') as f:
        f.write(html)

def gen_art_ailment(ailment_name):
    ailment_slug = utils.sluggify(ailment_name)
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}/ailments'
    html_article_filepath = f'{html_article_folderpath}/{ailment_slug}.html'
    json_article_filepath = f'database/pages/ailments/{ailment_slug}.json'

    gen_art_ailment_json(ailment_name, json_article_filepath)
    gen_art_ailment_html(html_article_filepath, json_article_filepath)

