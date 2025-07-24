import os
from string import ascii_lowercase

from oliark_llm import llm_reply

from lib import g
from lib import io
from lib import llm
from lib import data
from lib import utils

model_filepath = '/home/ubuntu/vault-tmp/llms/Qwen3-8B-Q4_K_M.gguf'

for item in os.listdir('.'):
    if os.path.isdir(item):
        print(item, len(os.listdir(item)))

for c in ascii_lowercase:
    try: os.makedirs(f'plants-{c}')
    except: pass

def ai_intro(json_article_filepath, regen=False, clear=False):
    json_article = io.json_read(json_article_filepath)
    plant_name_scientific = json_article['plant_name_scientific']
    reply_start = f'{plant_name_scientific.capitalize()}, commonly known as '
    llm.paragraph_ai(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the botanical aspects of the following plant: {plant_name_scientific}.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {reply_start} .
            /no_think
        ''',
        reply_start = reply_start,
        regen = regen,
        clear = clear,
        print_prompt = True,
        model_filepath = model_filepath,
    )

def ai_llm_taxonomy(json_article_filepath, regen=False, clear=False):
    json_article = io.json_read(json_article_filepath)
    plant_name_scientific = json_article['plant_name_scientific']
    if 'taxonomy' not in json_article: return
    taxonomy = json_article['taxonomy']
    taxonomy_kingdom = taxonomy['kingdom']
    taxonomy_phylum = taxonomy['phylum']
    taxonomy_class = taxonomy['class']
    taxonomy_subclass = taxonomy['subclass']
    taxonomy_order = taxonomy['order']
    taxonomy_family = taxonomy['family']
    taxonomy_genus = taxonomy['genus']
    taxonomy_species = taxonomy['species']
    ###
    if taxonomy_kingdom.strip() == '': return
    if taxonomy_phylum.strip() == '': return
    if taxonomy_class.strip() == '': return
    if taxonomy_subclass.strip() == '': return
    if taxonomy_order.strip() == '': return
    if taxonomy_family.strip() == '': return
    if taxonomy_genus.strip() == '': return
    if taxonomy_species.strip() == '': return
    ###
    taxonomy_prompt = ''
    for key, val in taxonomy.items():
        taxonomy_prompt += f'- {key.capitalize()}: {val}\n'
    reply_start = f'{plant_name_scientific.capitalize()} belongs '
    ###
    llm.paragraph_ai(
        key = 'taxonomy_art_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short paragraph in 8 sentences about the taxonomical classification of the following plant: {plant_name_scientific}.
            Use the data below for the taxonomy:
            {taxonomy_prompt}
            Reply Structure:
            In sentence 1, write the following: {plant_name_scientific.capitalize()} belongs to the kingdom {taxonomy_kingdom}. Don't write anything else in this sentence.
            In sentence 2, write that its phylum is {taxonomy_phylum} and explain this phylum.
            In sentence 3, write that its class is {taxonomy_class} and explain this class.
            In sentence 4, write that its subclass is {taxonomy_subclass} and explain this subclass.
            In sentence 5, write that its order is {taxonomy_order} and explain this order.
            In sentence 6, write that its family is {taxonomy_family} and explain this family.
            In sentence 7, write that its genus is {taxonomy_genus} and explain this genus.
            In sentence 8, write that its species is {taxonomy_species} and explain this species.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {reply_start} .
            /no_think
        ''',
        reply_start = reply_start,
        regen = regen,
        clear = clear,
        print_prompt = True,
        model_filepath = model_filepath,
    )

def ai_llm_distribution_native(json_article_filepath, regen=False, clear=False):
    json_article = io.json_read(json_article_filepath)
    plant_name_scientific = json_article['plant_name_scientific']
    if 'distribution_native' not in json_article: return
    distribution_native = json_article['distribution_native']
    distribution_native = ', '.join(distribution_native)
    ###
    reply_start = f'{plant_name_scientific.capitalize()} is primarily native to  '
    llm.paragraph_ai(
        key = 'distribution_native_art_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a 5 sentences about the native distribution of the following plant: {plant_name_scientific}.
            Write that this plant is native to the data below:
            {distribution_native}
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {reply_start} .
            /no_think
        ''',
        reply_start = reply_start,
        regen = regen,
        clear = clear,
        print_prompt = True,
        model_filepath = model_filepath,
    )

def ai_llm_distribution_introduced(json_article_filepath, regen=False, clear=False):
    json_article = io.json_read(json_article_filepath)
    plant_name_scientific = json_article['plant_name_scientific']
    if 'distribution_introduced' not in json_article: return
    distribution_introduced = json_article['distribution_introduced']
    distribution_introduced = ', '.join(distribution_introduced)
    ###
    reply_start = f'{plant_name_scientific.capitalize()} was mainly introduced to  '
    llm.paragraph_ai(
        key = 'distribution_introduced_art_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a 5 sentences about the introduced distribution of the following plant: {plant_name_scientific}.
            Write that this plant is introduced to the data below:
            {distribution_introduced}
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {reply_start} .
            /no_think
        ''',
        reply_start = reply_start,
        regen = regen,
        clear = clear,
        print_prompt = True,
        model_filepath = model_filepath,
    )

def json_gen(plants_folderpath, plant_slug, plant_name_scientific):
    json_article_filepath = f'{plants_folderpath}/{plant_slug}.json'
    json_article = io.json_read(json_article_filepath, create=True)
    if 'lastmod' not in json_article: json_article['lastmod'] = utils.today()
    json_article['page_url'] = ''
    json_article['page_title'] = plant_name_scientific.capitalize()
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    io.json_write(json_article_filepath, json_article)
    ###
    ai_intro(json_article_filepath, regen=False, clear=False)
    ai_llm_taxonomy(json_article_filepath, regen=False, clear=False)
    ai_llm_distribution_native(json_article_filepath, regen=False, clear=False)
    ai_llm_distribution_introduced(json_article_filepath, regen=False, clear=False)

def gen():
    plants = data.plants_wcvp_get()
    plants = plants[:g.plant_n]
    for plant_i, plant_name_scientific in enumerate(plants):
        print(f'{plant_i}/{len(plants)} - {plant_name_scientific}')
        if len(plant_name_scientific.split()) < 2: continue
        first_char = plant_name_scientific.lower().strip()[0]
        if first_char.isalpha():
            plants_folderpath = f'plants-{first_char}'
            plant_slug = utils.sluggify(plant_name_scientific)
            ###
            json_article_filepath = f'{plants_folderpath}/{plant_slug}.json'
            json_gen(plants_folderpath, plant_slug, plant_name_scientific)
            #######################################################################
            # html
            #######################################################################
            json_article = io.json_read(json_article_filepath, create=True)
            html_article = ''
            html_article += f'<h1>{json_article["page_title"]}</h1>\n'
            html_article += f'{utils.text_format_1N1_html(json_article["intro"])}\n'
            if 'taxonomy_art_desc' in json_article:
                html_article += f'<h2>Taxonomy</h2>\n'
                html_article += f'{utils.text_format_1N1_html(json_article["taxonomy_art_desc"])}\n'
            if 'distribution_native_art_desc' in json_article:
                html_article += f'<h2>Native Distribution</h2>\n'
                html_article += f'{utils.text_format_1N1_html(json_article["distribution_native_art_desc"])}\n'
            if 'distribution_introduced_art_desc' in json_article:
                html_article += f'<h2>Introduced Distribution</h2>\n'
                html_article += f'{utils.text_format_1N1_html(json_article["distribution_introduced_art_desc"])}\n'
            html = f'''
                <!DOCTYPE html>
                <html lang="en">
                <body>
                    <main>
                        {html_article}
                    </main>
                </body>
                </html>
            '''
            with open(f'{g.WEBSITE_FOLDERPATH}/{plants_folderpath}/{plant_slug}.html', 'w') as f:
                f.write(html)

