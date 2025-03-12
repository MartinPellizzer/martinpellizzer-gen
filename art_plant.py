import os

from oliark_io import json_read, json_write

import g
import llm
import utils
import studies
import components

def gen_intro(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'intro',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the {plant_name_scientific} plant.
            Include a definition of what this plant is.
            Include the medicinal properties.
            Include the health benefits.
            Include the herbal preparations.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_intro_study(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    key = 'intro_study'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        reply = studies.gen_plant_study_intro(plant_name_scientific.capitalize())
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)

def gen_benefits_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'benefits_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the benefits of the {plant_name_scientific} plant.
            Include the medicinal uses.
            Include the health benefits.
            Don't include the bioactive constituents.
            Don't include the therapeutic properties.
            Make a lot of examples of health benefits.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} is used to .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_benefits_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'benefits_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 benefits names and descriptions of the {plant_name_scientific} plant.
            Reply in JSON using the following format:
            [
                {{"name": "write name of benefit 1 here", "description": "write description of benefit 1 here"}},
                {{"name": "write name of benefit 2 here", "description": "write description of benefit 2 here"}},
                {{"name": "write name of benefit 3 here", "description": "write description of benefit 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_actions_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'actions_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the therapeutic actions of the {plant_name_scientific} plant.
            Include the therapeutic actions (ex. anti-inflammatory, nervine, etc...).
            Include the body systems most affected by these actions (ex. digestive system, cardiovascular system, etc...).
            Don't include the uses.
            Don't include the ailments.
            Make a lot of examples of therapeutic actions of this plant.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} has .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_actions_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'actions_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 therapeutic actions names and descriptions of the {plant_name_scientific} plant.
            Examples of actions are: antiseptic, nervine, etc.
            Reply in JSON using the following format:
            [
                {{"name": "write name of action 1 here", "description": "write description of action 1 here"}},
                {{"name": "write name of action 2 here", "description": "write description of action 2 here"}},
                {{"name": "write name of action 3 here", "description": "write description of action 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_constituents_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'constituents_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the bioactive constituents of the {plant_name_scientific} plant for health purposes.
            Include the bioactive constituents (ex. flavonoids, tannins, etc...).
            Include the healing properties each of these constituents has.
            Don't include the ailments.
            Make a lot of examples of bioactive constituents of this plant.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} has .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_constituents_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'constituents_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 biochemical costituents names and descriptions of the {plant_name_scientific} plant.
            Examples of constituents are: tannins, flavonoids, etc.
            Reply in JSON using the following format:
            [
                {{"name": "write name of constituent 1 here", "description": "write description of constituent 1 here"}},
                {{"name": "write name of constituent 2 here", "description": "write description of constituent 2 here"}},
                {{"name": "write name of constituent 3 here", "description": "write description of constituent 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_parts_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'parts_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the most commonly used parts of the {plant_name_scientific} plant for health purposes.
            Include the parts names (ex. roots, leaves, flowers, etc...).
            Include the uses of those parts.
            Make a lot of examples of uses of these parts.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: The most commoly used parts of {plant_name_scientific.capitalize()} are .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_parts_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'parts_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 medicinal parts names and descriptions of the {plant_name_scientific} plant.
            Examples of parts are: leaves, flowers, roots, etc.
            Reply in JSON using the following format:
            [
                {{"name": "write name of part 1 here", "description": "write description of part 1 here"}},
                {{"name": "write name of part 2 here", "description": "write description of part 2 here"}},
                {{"name": "write name of part 3 here", "description": "write description of part 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_preparations_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'preparations_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the most commonly used herbal preparations of the {plant_name_scientific} plant for health purposes.
            Include the preparations names (ex. infusions, tinctures, etc...).
            Include the uses of those preparations.
            Make a lot of examples of uses of these preparations.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} most common herbal preparations are .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_preparations_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'preparations_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 herbal preparations names and descriptions of the {plant_name_scientific} plant.
            Examples of parts are: infusions, tinctures, etc.
            Reply in JSON using the following format:
            [
                {{"name": "write name of preparation 1 here", "description": "write description of preparation 1 here"}},
                {{"name": "write name of preparation 2 here", "description": "write description of preparation 2 here"}},
                {{"name": "write name of preparation 3 here", "description": "write description of preparation 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_side_effects_desc(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.ai_paragraph_gen(
        key = 'side_effects_desc',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 4-sentence paragraph about the side effects of the {plant_name_scientific} plant.
            Include the side effects.
            Include who is most likely to experience these side effects.
            Include precautions.
            Don't include suggestions to consult a health care provider or a doctor.
            Make a lot of examples of side effects of this plant.
            If you can't answer, reply with only "I can't reply".
            Start with the following words: {plant_name_scientific.capitalize()} side effects are .
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_side_effects_list(vertex_plant, json_article_filepath):
    plant_name_scientific = vertex_plant['plant_name_scientific']
    json_article = json_read(json_article_filepath)
    llm.gen_json_list(
        key = 'side_effects_list',
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a list of 7 side effects names and descriptions of the {plant_name_scientific} plant.
            Reply in JSON using the following format:
            [
                {{"name": "write name of side effect 1 here", "description": "write description of side effect 1 here"}},
                {{"name": "write name of side effect 2 here", "description": "write description of side effect 2 here"}},
                {{"name": "write name of side effect 3 here", "description": "write description of side effect 3 here"}}
            ]
            Always start the reply with character "[" and end it with character "]".
            If you can answer, reply with only the JSON.
            If you can't answer, reply with only "I can't reply".
        ''',
        regen = False,
        print_prompt = True,
    )

def gen_art_plant_json(vertex_plant, json_article_filepath):
    plant_slug = vertex_plant['plant_slug']
    plant_name_scientific = vertex_plant['plant_name_scientific']
    plant_names_common = vertex_plant['plant_names_common']
    json_article = json_read(json_article_filepath, create=True)
    json_article['plant_slug'] = plant_slug
    json_article['plant_name_scientific'] = plant_name_scientific
    json_article['plant_names_common'] = plant_names_common
    json_article['plant_url'] = f'herbs/{plant_slug}.html'
    json_article['title'] = f'{plant_name_scientific}'
    json_write(json_article_filepath, json_article)

    gen_intro(vertex_plant, json_article_filepath)
    gen_intro_study(vertex_plant, json_article_filepath)
    gen_benefits_desc(vertex_plant, json_article_filepath)
    gen_benefits_list(vertex_plant, json_article_filepath)
    gen_actions_desc(vertex_plant, json_article_filepath)
    gen_actions_list(vertex_plant, json_article_filepath)
    gen_constituents_desc(vertex_plant, json_article_filepath)
    gen_constituents_list(vertex_plant, json_article_filepath)
    gen_parts_desc(vertex_plant, json_article_filepath)
    gen_parts_list(vertex_plant, json_article_filepath)
    gen_preparations_desc(vertex_plant, json_article_filepath)
    gen_preparations_list(vertex_plant, json_article_filepath)
    gen_side_effects_desc(vertex_plant, json_article_filepath)
    gen_side_effects_list(vertex_plant, json_article_filepath)

def gen_art_plant_html(html_article_filepath, json_article_filepath):
    json_article = json_read(json_article_filepath)
    plant_slug = json_article['plant_slug']
    plant_name_scientific = json_article['plant_name_scientific'].capitalize()
    page_title = f'{plant_name_scientific.title()} Complete Medicinal Profile'
    html_article = ''
    html_article += f'<h1>{plant_name_scientific.title()}: Complete Medicinal Profile</h1>\n'
    html_article += f'<img src="/images/herbs/{plant_slug}.jpg" alt="{plant_name_scientific}">\n'
    html_article += f'{utils.text_format_sentences_html(json_article["intro"])}\n'
    if json_article['intro_study'] != '' and json_article['intro_study'] != 'N/A':
        html_article += f'''
            <div class="study">
                <div class="study-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" />
                    </svg>
                    <p>Study of the Day</p>
                </div>
                <p>
                    {json_article['intro_study']}
                </p>
            </div>
        '''
    html_article += f'<p style="margin-top: 16px; margin-bottom: 32px;">This page analize the most important medicinal aspects of {plant_name_scientific.capitalize()}.</p>\n'
    html_article += f'[html_intro_toc]\n'
    html_article += f'<h2>Uses and Benefits</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["benefits_desc"])}\n'
    html_article += f'<p>The health benefits of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'benefits_list' in json_article:
        html_article += f'<ul>\n'
        for benefit_list in json_article['benefits_list']:
            benefit_name = benefit_list['name']
            benefit_desc = benefit_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{benefit_name.capitalize()}</span>: {benefit_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'
    html_article += f'<p>Here are the <a href="/herbs/{plant_slug}/benefit.html">best health benefits of {plant_name_scientific}</a>.</p>\n'

    html_article += f'<h2>Actions</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["actions_desc"])}\n'
    html_article += f'<p>The therapeutic actions of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'actions_list' in json_article:
        html_article += f'<ul>\n'
        for action_list in json_article['actions_list']:
            action_name = action_list['name']
            action_desc = action_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{action_name.capitalize()}</span>: {action_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'

    html_article += f'<h2>Constituents</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["constituents_desc"])}\n'
    html_article += f'<p>The bioactive constituents of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'constituents_list' in json_article:
        html_article += f'<ul>\n'
        for constituent_list in json_article['constituents_list']:
            constituent_name = constituent_list['name']
            constituent_desc = constituent_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{constituent_name.capitalize()}</span>: {constituent_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'
    html_article += f'<h2>Parts</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["parts_desc"])}\n'
    html_article += f'<p>The medicinal parts of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'parts_list' in json_article:
        html_article += f'<ul>\n'
        for part_list in json_article['parts_list']:
            part_name = part_list['name']
            part_desc = part_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{part_name.capitalize()}</span>: {part_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'

    html_article += f'<h2>Preparations</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["preparations_desc"])}\n'
    html_article += f'<p>The herbal preparations of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'preparations_list' in json_article:
        html_article += f'<ul>\n'
        for preparation_list in json_article['preparations_list']:
            preparation_name = preparation_list['name']
            preparation_desc = preparation_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{preparation_name.capitalize()}</span>: {preparation_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'

    html_article += f'<h2>Side Effects</h2>\n'
    html_article += f'{utils.text_format_sentences_html(json_article["side_effects_desc"])}\n'
    html_article += f'<p>The possible side effects of {plant_name_scientific.capitalize()} are listed below.</p>\n'
    if 'side_effects_list' in json_article:
        html_article += f'<ul>\n'
        for side_effect_list in json_article['side_effects_list']:
            side_effect_name = side_effect_list['name']
            side_effect_desc = side_effect_list['desc']
            html_article += f'<li><span style="font-weight: bold;">{side_effect_name.capitalize()}</span>: {side_effect_desc.capitalize()}</li>\n'
        html_article += f'</ul>\n'

    html_article, json_toc = components.toc(html_article)
    html_intro_toc = components.toc_json_to_html_article(json_toc)
    html_article = html_article.replace('[html_intro_toc]', html_intro_toc)
    html_toc_sidebar = components.toc_json_to_html_sidebar(json_toc)
    html_breadcrumbs = components.breadcrumbs(f'herbs/{plant_slug}.html')
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

def gen_art_plant(vertex_plant):
    plant_slug = vertex_plant['plant_slug']
    html_article_folderpath = f'{g.WEBSITE_FOLDERPATH}/herbs'
    html_article_filepath = f'{html_article_folderpath}/{plant_slug}.html'
    json_article_filepath = f'database/pages/herbs/{plant_slug}.json'

    gen_art_plant_json(vertex_plant, json_article_filepath)
    gen_art_plant_html(html_article_filepath, json_article_filepath)

