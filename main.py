import os
import json
import random
import shutil

from nltk import tokenize

from oliark_llm import llm_reply
from oliark_io import json_read, json_write

vault = f'/home/ubuntu/vault'
website_folderpath = 'website'

model_8b = f'/home/ubuntu/vault-tmp/llms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'
model_validator_filepath = f'llms/Llama-3-Partonus-Lynx-8B-Instruct-Q4_K_M.gguf'
model = model_8b

checkpoint_filepath = f'{vault}/stable-diffusion/checkpoints/juggernautXL_juggXIByRundiffusion.safetensors'

vertices = json_read('vertices.json')
vertices_herbs = json_read('vertices-herbs.json')
vertices_preparations = json_read('vertices-preparations.json')
vertices_ailments = json_read('vertices-ailments.json')

edges = json_read('edges.json')
edges_ai = json_read('edges.json')
# edges_herbs_preparations = [edge for edge in edges_ai if edge['type'] == 'herb_preparation']
edges_herbs_preparations = json_read('edges-herbs-preparations.json')
edges_herbs_ailments = json_read('edges-herbs-ailments.json')

edges_families_orders = json_read('edges-families-orders.json')
edges_orders_subclasses = json_read('edges-orders-subclasses.json')
edges_subclasses_classes = json_read('edges-subclasses-classes.json')
edges_classes_divisions = json_read('edges-classes-divisions.json')

def img_resize(img, w=768, h=768):
    start_size = img.size
    end_size = (w, h)
    if start_size[0] / end_size [0] < start_size[1] / end_size [1]:
        ratio = start_size[0] / end_size[0]
        new_end_size = (end_size[0], int(start_size[1] / ratio))
    else:
        ratio = start_size[1] / end_size[1]
        new_end_size = (int(start_size[0] / ratio), end_size[1])
    img = img.resize(new_end_size)
    w_crop = new_end_size[0] - end_size[0]
    h_crop = new_end_size[1] - end_size[1]
    area = (
        w_crop // 2, 
        h_crop // 2,
        new_end_size[0] - w_crop // 2,
        new_end_size[1] - h_crop // 2
    )
    img = img.crop(area)
    return img

###############################################
# ;AMAZON
###############################################
def affiliate_disclaimer_gen():
    html = ''
    html += f'''
        <p class="text-14 mb-0"><i>Disclaimer: We earn a commission if you click this link and make a purchase at no additional cost to you.</i></p>
    '''
    return html

def amazon_buy_button(url):
    affiliate_disclaimer_html = affiliate_disclaimer_gen()
    html = f'''
        <div class="bg-lightgray px-24 py-32">
            <a class="button-amazon mb-16" href="{url}" target="_blank">Buy On Amazon</a>
            {affiliate_disclaimer_html}
        </div>
    '''
    return html


###############################################
# ;COMPONENTS
###############################################
html_header = f'''
    <header class="container-xl flex justify-between">
        <a class="no-underline" href="/">Martin Pellizzer</a>
        <nav class="flex gap-16">
            <a class="no-underline" href="/herbs.html">Herbs</a>
            <a class="no-underline" href="/preparations.html">Preparations</a>
            <a class="no-underline" href="/equipments.html">Equipments</a>
            <a class="no-underline" href="/ailments.html">Ailments</a>
        </nav>
    </header>
'''

html_footer = f'''
    <footer class="container-xl flex justify-between">
        <span>martinpellizzer.com | all rights reserved</span>
        <nav class="flex gap-16">
            <a class="no-underline" href="/">About</a>
            <a class="no-underline" href="/">Contact</a>
        </nav>
    </footer>
'''

def html_head_gen(title):
    html = f'''
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/style.css">
            <title>{title}</title>
        </head>
    '''
    return html

def html_article_layout_gen(html_article):
    html = f'''
        <section class="container-md">
            <main class>
                {html_article}
            </main>
        </section>
    '''
    return html

###############################################
# ;UTIL FORMAT
###############################################
def text_format_1N1_html(text):
    text_formatted = ''
    text = text.replace('var.', 'var,')
    lines_tmp = tokenize.sent_tokenize(text)
    lines = []
    for line in lines_tmp:
        line = line.replace('var,', 'var.')
        lines.append(line)
    lines_num = len(lines[1:-1])
    paragraphs = []
    if lines_num > 0: 
        paragraphs.append(lines[0])
    else:
        text_formatted += f'<p>{text}.</p>' + '\n'
        text_formatted = text_formatted.replace('..', '.')
        return text_formatted
    if lines_num > 3: 
        paragraphs.append('. '.join(lines[1:lines_num//2+1]))
        paragraphs.append('. '.join(lines[lines_num//2+1:-1]))
    else:
        paragraphs.append('. '.join(lines[1:-1]))
    paragraphs.append(lines[-1])
    for paragraph in paragraphs:
        if paragraph.strip() != '':
            text_formatted += f'<p>{paragraph}.</p>' + '\n'
    text_formatted = text_formatted.replace('..', '.')
    return text_formatted

###############################################
# ;UTIL COMPONENT
###############################################
def breadcrumbs_gen(filepath):
    breadcrumbs = ['<a class="no-underline" href="/">Home</a>']
    breadcrumbs_path = filepath.replace('website/', '')
    chunks = breadcrumbs_path.split('/')
    filepath_curr = ''
    for chunk in chunks[:-1]:
        filepath_curr += f'/{chunk}'
        chunk = chunk.strip().replace('-', ' ').title()
        breadcrumbs.append(f'<a class="no-underline" href="{filepath_curr}.html">{chunk}</a>')
    breadcrumbs = ' | '.join(breadcrumbs)
    breadcrumbs += f' | {chunks[-1].strip().replace(".html", "").replace("-", " ").title()}'
    breadcrumbs_section = f'''
        <section class="container-xl py-24">
            {breadcrumbs}
        </section>
    '''
    return breadcrumbs_section

def html_menu_gen():
    html = ''
    html += f'<p><a href="/herbs.html">herbs</a></p>'
    html += f'<p><a href="/preparations.html">preparations</a></p>'
    html += f'<p><a href="/equipments.html">equipments</a></p>'
    html += f'<p><a href="/ailments.html">ailments</a></p>'
    return html
html_menu = html_menu_gen()

def p_home():
    html_article = ''
    title = f'herbalism'
    html_head = html_head_gen(title)
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/index.html', 'w') as f:
        f.write(html)
    
def ai_paragraph_gen(filepath, data, obj, key, prompt, regen=False, print_prompt=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        if print_prompt: print(prompt)
        reply = llm_reply(prompt)
        if reply.strip() != '':
            if 'can\'t' in reply: return
            obj[key] = reply
            json_write(filepath, data)

def p_herbs():
    json_article_filepath = f'database/pages/herbs.json'
    json_article = json_read(json_article_filepath, create=True)
    if 'herbs' not in json_article: json_article['herbs'] = []
    # json_article['herbs'] = []
    for herb in vertices_herbs:
        herb_slug = herb['herb_slug']
        herb_name_scientific = herb['herb_name_scientific']
        herb_names_common = [item['name'] for item in herb['herb_names_common']]
        herb_name_common = herb_names_common[0]
        # add if doesn't exist
        found = False
        for _obj in json_article['herbs']:
            if herb_slug == _obj['herb_slug']:
                found = True
                break
        if not found:
            json_article['herbs'].append({
                'herb_slug': herb_slug,
                'herb_name_scientific': herb_name_scientific,
                'herb_name_common': herb_name_common,
            })
            json_write(json_article_filepath, json_article)
        # update
        herb_obj = {}
        for _herb_obj in json_article['herbs']:
            if herb_slug == _herb_obj['herb_slug']:
                herb_obj = _herb_obj
                break
        ai_paragraph_gen(
            key = 'herb_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = herb_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name_scientific}.
                Start the reply with the following words: {herb_name_scientific}, also known as {herb_name_common}, .
            ''',
            regen = False,
        )

    html_article = ''
    herbs_num = len(vertices_herbs)
    html_article += f'''<h1>{herbs_num} Best Medicinal Herbs For Apothecaries</h1>'''
    for i, herb in enumerate(json_article['herbs']):
        herb_slug = herb['herb_slug']
        herb_name_scientific = herb['herb_name_scientific']
        herb_name_common = herb['herb_name_common']
        herb_desc = herb['herb_desc']
        html_article += f'<h2>{i+1}. {herb_name_scientific.capitalize()} ({herb_name_common})</h2>\n'
        html_article += f'''<img src="/images/herbs/{herb_slug}.jpg" alt="{herb_name_scientific}">\n'''
        html_article += f'''{text_format_1N1_html(herb_desc)}\n'''
        html_article += f'<p><a href="/herbs/{herb_slug}.html">{herb_name_scientific}</a></p>\n'
    title = 'herbs'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/herbs.html', 'w') as f:
        f.write(html)


def a_herb(herb):
    herb_slug = herb['herb_slug']
    herb_name_scientific = herb['herb_name_scientific']
    herb_name_common = herb['herb_names_common'][0]['name']
    json_article_filepath = f'database/pages/herbs/{herb_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name_scientific'] = herb_name_scientific
    json_article['herb_url'] = f'herbs/{herb_slug}.html'
    json_write(json_article_filepath, json_article)
    # update
    sections = [
        ['0', 'botany', f'write a short 3-sentence paragraph about the botanical characteristics of {herb_name_scientific}.', f''],

        ['1', 'benefits', f'write a short 3-sentence paragraph about the benefits of {herb_name_scientific}.', f'benefit'],
        ['1', 'properties', f'write a short 3-sentence paragraph about the therapeutic properties of {herb_name_scientific}.', f''],
        ['1', 'constituents', f'write a short 3-sentence paragraph about the active constituents of {herb_name_scientific}.', f''],
        ['1', 'parts', f'write a short 3-sentence paragraph about the parts of {herb_name_scientific}.', f''],
        ['1', 'preparations', f'write a short 3-sentence paragraph about the preparations of {herb_name_scientific}.', f'preparation'],
        ['1', 'side-effects', f'write a short 3-sentence paragraph about the side effects of {herb_name_scientific}.', f''],


        ['0', 'distribution', f'write a short 3-sentence paragraph about the distribution of {herb_name_scientific}.', f''],
        ['0', 'native', f'write a short 3-sentence paragraph about the native range of {herb_name_scientific}.', f''],
        ['0', 'habitat', f'write a short 3-sentence paragraph about the habitat of {herb_name_scientific}.', f''],

        ['1', 'cultivation', f'write a short 3-sentence paragraph about the cultivation of {herb_name_scientific}.', f''],
        ['0', 'growing-conditions', f'write a short 3-sentence paragraph about the growing conditions of {herb_name_scientific}.', f''],
        ['0', 'germination', f'write a short 3-sentence paragraph about the germination of {herb_name_scientific}.', f''],
        ['0', 'cultivars', f'write a short 3-sentence paragraph about the cultivars of {herb_name_scientific}.', f''],
    ]
    ai_paragraph_gen(
        key = 'taxonomy', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the taxonomy of {herb_name_scientific}.
            include the data below.
            - family: {herb['herb_family']}
            start with the following words: {herb_name_scientific}, commonly known as {herb_name_common}, is .
        ''',
        regen = False,
    )
    ai_paragraph_gen(
        key = 'identification', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            write a short 3-sentence paragraph about the identification of {herb_name_scientific}.
        ''',
        regen = False,
    )
    ailments_slugs = [edge['vertex_2'] for edge in edges_herbs_ailments if edge['vertex_1'] == herb_slug]
    ailments_slugs_prompt = ', '.join(ailments_slugs)[:5]
    ai_paragraph_gen(
        key = 'uses', 
        filepath = json_article_filepath, 
        data = json_article, 
        obj = json_article, 
        prompt = f'''
            Write a short 5-sentence paragraph about the ailments that the plant {herb_name_scientific} heals.
            In specific, tell that this plant heals the following ailments: {ailments_slugs_prompt}.
            Write one sentence for ailment.
            Start the reply with the following words: {herb_name_scientific.capitalize()} is used .
        ''',
        regen = False,
    )
    for section in sections:
        exe = section[0]
        if exe != '1': continue
        key = section[1]
        prompt = section[2]
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = prompt,
        )

    # amazon
    # html
    html_article = ''
    html_article += f'<h1>{herb_name_scientific.capitalize()} ({herb_name_common})</h1>'
    html_article += f'''<img src="/images/herbs/{herb_slug}.jpg" alt="{herb_name_scientific}">\n'''

    ## what is
    html_article += f'<h2>What is {herb_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{text_format_1N1_html(json_article['taxonomy'])}\n'''
    html_article += f'<h3>What is the taxonomy of this plant?</h3>\n'
    herb_family = herb['herb_family']
    herb_order = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family)][0]
    herb_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order)][0]
    herb_class = [edge['vertex_2'] for edge in edges_subclasses_classes if (edge['edge_type'] == 'herb_subclass_class' and edge['vertex_1'] == herb_subclass)][0]
    herb_division = [edge['vertex_2'] for edge in edges_classes_divisions if (edge['edge_type'] == 'herb_class_division' and edge['vertex_1'] == herb_class)][0]
    html_article += f'<p>The taxonomy of {herb_name_scientific} is presented in the table below using the Linnaean system of classification.</p>\n'
    html_article += f'''
        <table>
            <tr>
                <th>Taxonomy</th>
                <th>Category</th>
            </tr>
            <tr>
                <td>Kingdom</td>
                <td>Plantae</td>
            </tr>
            <tr>
                <td>Division</td>
                <td>{herb_division.capitalize()}</td>
            </tr>
            <tr>
                <td>Class</td>
                <td>{herb_class.capitalize()}</td>
            </tr>
            <tr>
                <td>Subclass</td>
                <td>{herb_subclass.capitalize()}</td>
            </tr>
            <tr>
                <td>Order</td>
                <td>{herb_order.capitalize()}</td>
            </tr>
            <tr>
                <td>Family</td>
                <td>{herb_family.capitalize()}</td>
            </tr>
            <tr>
                <td>Genus</td>
                <td>{herb_name_scientific.split()[0].capitalize()}</td>
            </tr>
            <tr>
                <td>Species</td>
                <td>{herb_name_scientific.capitalize()}</td>
            </tr>
        </table>
    '''
    
    # edges_families_orders = json_read('edges-families-orders.json')
    # edges_orders_subclasses = json_read('edges-orders-subclasses.json')
    ### botanical illustration
    html_article += f'<h3>Is there a botanical illustation of this plant?</h3>\n'
    html_article += f'''<p>Yes, the following drawing shows a botanical illustration of {herb_name_scientific}.</p>\n'''
    html_article += f'''<img src="/images/herbs/{herb_slug}-illustation.jpg" alt="{herb_name_scientific} botanical illustration">\n'''
    ### identification
    # html_article += f'<h3>How to identify this plant?</h3>\n'
    # html_article += f'''{text_format_1N1_html(json_article['identification'])}\n'''
    ## ;uses
    html_article += f'<h2>What are the most common uses of {herb_name_scientific.capitalize()}?</h2>\n'
    html_article += f'''{text_format_1N1_html(json_article['uses'])}\n'''
    html_article += f'''<p>The following list summarizes the most common ailments treated with this plant.</p>\n'''
    html_article += f'''<ul>\n'''
    for ailment_slug in ailments_slugs[:10]:
        ailment_name = [vertex['ailment_name'] for vertex in vertices_ailments if vertex['ailment_slug'] == ailment_slug][0]
        html_article += f'''<li>{ailment_name.capitalize()}</li>\n'''
    html_article += f'''</ul>\n'''
    ## sections to re-organize
    for section in sections:
        exe = section[0]
        if exe != '1': continue
        section_name = section[1]
        section_desc = json_article[section_name]
        section_link = section[3]
        html_article += f'<h2>{section_name}</h2>'
        html_article += f'<p>{section_desc}</p>\n'
        if section_link.strip() != '':
            html_article += f'<p><a href="/herbs/{herb_slug}/{section_link}.html">{section_name}</a></p>'
    title = f'{herb_name_scientific}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs'): 
        os.mkdir(f'{website_folderpath}/herbs')
    with open(f'{website_folderpath}/herbs/{herb_slug}.html', 'w') as f:
        f.write(html)


def a_herb_uses(herb):
    herb_slug = herb['herb_slug']
    herb_name = herb['herb_name_scientific']
    json_article_filepath = f'database/pages/herbs/{herb_slug}/use.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name'] = herb_name
    json_article['herb_url'] = f'herbs/{herb_slug}/use.html'
    if 'uses' not in json_article: json_article['uses'] = []
    json_write(json_article_filepath, json_article)
    # json
    uses_slugs = [edge['vertex_2'] for edge in edges_herbs_ailments if edge['vertex_1'] == herb_slug]
    for use_slug in uses_slugs:
        use_name = use_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['uses']:
            if use_slug == _obj['use_slug']:
                found = True
                break
        if not found:
            json_article['uses'].append({'use_slug': use_slug})
            json_write(json_article_filepath, json_article)
        # update
        use_obj = {}
        for _use_obj in json_article['uses']:
            if use_slug == _use_obj['use_slug']:
                use_obj = _use_obj
                break
        ai_paragraph_gen(
            key = 'use_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = use_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about the use of {herb_name} for {use_name}.
                Start with the following words: {herb_name} is .
            ''',
            regen = False,
        )
    # html
    html_article = ''
    html_article += f'<h1>{herb_name} uses</h1>'
    for use in json_article['uses']:
        use_slug = use['use_slug']
        use_name = use_slug.replace('-', ' ')
        use_desc = use['use_desc']
        html_article += f'<h2>{use_name}</h2>\n'
        html_article += f'<p>{use_desc}</p>\n'
        html_article += f'<p><a href="/ailments/{use_slug}.html">{use_name}</a></p>'
    title = f'{herb_name} uses'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}/use.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs/{herb_slug}'): 
        os.mkdir(f'{website_folderpath}/herbs/{herb_slug}')
    with open(f'{website_folderpath}/herbs/{herb_slug}/use.html', 'w') as f:
        f.write(html)



def a_herb_benefits(herb):
    herb_slug = herb['herb_slug']
    herb_name_scientific = herb['herb_name_scientific']
    json_article_filepath = f'database/pages/herbs/{herb_slug}/benefit.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name_scientific'] = herb_name_scientific
    json_article['herb_url'] = f'herbs/{herb_slug}/benefit.html'
    json_write(json_article_filepath, json_article)
    # json
    key = 'benefits'
    if key not in json_article: json_article[key] = []
    # json_article[key] = []
    if json_article[key] == []:
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write a list of the 20 most important health benefits of the plant {herb_name_scientific}.
                Also, write a confidence score from 1 to 10 for each benefit, indicating how much sure you are about that answer.
                Start each benefit with a third presron singular action verb.
                Write as few words as possible.
                Reply in JSON using the format below:
                [
                    {{"benefit": "write benefit 1 here", "confidence_score": 10}},
                    {{"benefit": "write benefit 2 here", "confidence_score": 5}},
                    {{"benefit": "write benefit 3 here", "confidence_score": 7}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for item in json_reply:
                    try: benefit_name = item['benefit'].strip().lower()
                    except: continue
                    try: confidence_score = item['confidence_score']
                    except: continue
                    if benefit_name.endswith('.'): benefit_name = benefit_name[:-1]
                    outputs.append({
                        'benefit_name': benefit_name,
                        'confidence_score': confidence_score,
                    })
        outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
        for output in outputs:
            print(output)
        json_article['benefits'] = outputs
        json_write(json_article_filepath, json_article)

    for json_benefit in json_article['benefits'][:10]:
        benefit_name = json_benefit['benefit_name']
        ai_paragraph_gen(
            key = 'benefit_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_benefit, 
            prompt = f'''
                Write a short 3-sentence paragraph about the following benefit of {herb_name_scientific}: for {benefit_name}.
                If you can't answer, reply with only "I can't reply".
                Start with the following words: {herb_name_scientific.capitalize()} {benefit_name} .
            ''',
            regen = False,
            print_prompt = True,
        )

    # html
    title = f'{herb_name_scientific} benefits'
    html_article = ''
    html_article += f'<h1>10 Best {herb_name_scientific.title()} Benefits</h1>\n'
    html_article += f'''<img src="/images/herbs/{herb_slug}.jpg" alt="{herb_name_scientific}">\n'''
    for i, benefit in enumerate(json_article['benefits'][:10]):
        html_article += f'''<h2>{i+1}. {benefit['benefit_name'].title()}</h2>\n'''
        html_article += f'''<p>{benefit['benefit_desc']}</p>\n'''
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}/benefit.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs/{herb_slug}'): 
        os.mkdir(f'{website_folderpath}/herbs/{herb_slug}')
    with open(f'{website_folderpath}/herbs/{herb_slug}/benefit.html', 'w') as f:
        f.write(html)


def a_herb_preparations(herb):
    herb_slug = herb['herb_slug']
    herb_name = herb['herb_name_scientific']
    json_article_filepath = f'database/pages/herbs/{herb_slug}/preparation.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['herb_slug'] = herb_slug
    json_article['herb_name'] = herb_name
    json_article['herb_url'] = f'herbs/{herb_slug}/preparation.html'
    if 'preparations' not in json_article: json_article['preparations'] = []
    json_write(json_article_filepath, json_article)
    # json
    preparations_slugs = [edge['vertex_2'] for edge in edges_herbs_preparations if edge['vertex_1'] == herb_slug]
    for preparation_slug in preparations_slugs:
        preparation_name = preparation_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['preparations']:
            if preparation_slug == _obj['preparation_slug']:
                found = True
                break
        if not found:
            json_article['preparations'].append({'preparation_slug': preparation_slug})
            json_write(json_article_filepath, json_article)
        # update
        preparation_obj = {}
        for _preparation_obj in json_article['preparations']:
            if preparation_slug == _preparation_obj['preparation_slug']:
                preparation_obj = _preparation_obj
                break
        ai_paragraph_gen(
            key = 'preparation_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = preparation_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name} {preparation_name}.
                Start with the following words: {herb_name} {preparation_name} is .
            ''',
            regen = False,
        )
    # html
    html_article = ''
    html_article += f'<h1>{herb_name} preparations</h1>'
    for preparation in json_article['preparations']:
        preparation_slug = preparation['preparation_slug']
        preparation_name = preparation_slug.replace('-', ' ')
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{preparation_name}</h2>\n'
        html_article += f'<p>{preparation_desc}</p>\n'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{herb_slug}.html">{preparation_name}</a></p>'
    title = f'{herb_name} preparations'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'herbs/{herb_slug}/preparation.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/herbs/{herb_slug}'): 
        os.mkdir(f'{website_folderpath}/herbs/{herb_slug}')
    with open(f'{website_folderpath}/herbs/{herb_slug}/preparation.html', 'w') as f:
        f.write(html)


def p_preparations():
    json_article_filepath = f'database/pages/preparations.json'
    json_article = json_read(json_article_filepath, create=True)
    # json
    if 'preparations' not in json_article: json_article['preparations'] = []
    for preparation in vertices_preparations:
        preparation_slug = preparation['preparation_slug']
        preparation_name = preparation_slug.replace('-', ' ')
        # add if doesn't exist
        found = False
        for _obj in json_article['preparations']:
            if preparation_slug == _obj['preparation_slug']:
                found = True
                break
        if not found:
            json_article['preparations'].append({'preparation_slug': preparation_slug})
            json_write(json_article_filepath, json_article)
        # update
        preparation_obj = {}
        for _preparation_obj in json_article['preparations']:
            if preparation_slug == _preparation_obj['preparation_slug']:
                preparation_obj = _preparation_obj
                break
        ai_paragraph_gen(
            key = 'preparation_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = preparation_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {preparation_name}.
            ''',
        )
    # html
    html_article = ''
    html_article += f'<h1>preparations</h1>'
    for i, preparation in enumerate(json_article['preparations']):
        slug_plural = preparation['preparation_slug']
        name_plural = slug_plural.replace('-', ' ')
        preparation_desc = preparation['preparation_desc']
        html_article += f'<h2>{i+1}. {name_plural}</h2>'
        html_article += f'<p>{preparation_desc}</p>'
        html_article += f'<p><a href="/preparations/{slug_plural}.html">{name_plural}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'preparations'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'preparations.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/preparations'): 
        os.mkdir(f'{website_folderpath}/preparations')
    with open(f'{website_folderpath}/preparations.html', 'w') as f:
        f.write(html)


def a_preparation(preparation):
    preparation_slug = preparation['preparation_slug']
    preparation_name_singular = preparation['preparation_name']
    preparation_name_plural = preparation['preparation_name_plural']
    json_article_filepath = f'database/pages/preparations/{preparation_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['preparation_slug'] = preparation_slug
    json_article['preparation_name_singular'] = preparation_name_singular
    json_article['preparation_name_plural'] = preparation_name_plural
    json_article['preparation_url'] = f'preparations/{preparation_slug}.html'
    json_write(json_article_filepath, json_article)
    # get herbs
    herbs_slugs = [edge['vertex_1'] for edge in edges_herbs_preparations if edge['vertex_2'] == preparation_slug]
    herbs = []
    for herb_slug in herbs_slugs:
        herb = [vertex for vertex in vertices_herbs if vertex['herb_slug'] == herb_slug][0]
        herbs.append(herb)
    # json
    if 'herbs' not in json_article: json_article['herbs'] = []
    for herb in herbs:
        herb_slug = herb['herb_slug']
        herb_name_scientific = herb['herb_name_scientific']
        # add if doesn't exist
        found = False
        for _obj in json_article['herbs']:
            if herb_slug == _obj['herb_slug']:
                found = True
                break
        if not found:
            json_article['herbs'].append({'herb_slug': herb_slug, 'herb_name_scientific': herb_name_scientific})
            json_write(json_article_filepath, json_article)
        # update
        herb_obj = {}
        for _herb_obj in json_article['herbs']:
            if herb_slug == _herb_obj['herb_slug']:
                herb_obj = _herb_obj
                break
        ai_paragraph_gen(
            key = 'herb_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = herb_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name_scientific} {preparation_name_singular}.
            ''',
        )
    # html
    html_article = ''
    html_article += f'<h1>{preparation_name_plural}</h1>'
    for herb in json_article['herbs']:
        herb_slug = herb['herb_slug']
        herb_name_scientific = herb['herb_name_scientific']
        herb_desc = herb['herb_desc']
        html_article += f'<h2>{herb_name_scientific}</h2>'
        html_article += f'<p>{herb_desc}</p>'
        html_article += f'<p><a href="/preparations/{preparation_slug}/{herb_slug}.html">{herb_name_scientific} {preparation_name_singular}</a></p>'
        html_article += f'<div style="margin-bottom: 48px;"></div>'
    title = f'{preparation_slug}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'preparations/{preparation_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        </head>
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/preparations/{preparation_slug}.html', 'w') as f:
        f.write(html)


def a_preparation_herbs(preparation):
    preparation_slug = preparation['preparation_slug']
    herbs_slugs = [edge['vertex_1'] for edge in edges_herbs_preparations if edge['vertex_2'] == preparation_slug]
    for herb_slug in herbs_slugs:
        preparation_slug = preparation['preparation_slug']
        preparation_name_singular = preparation_slug.replace('-', ' ')
        preparation_name_plural = preparation_slug.replace('-', ' ')
        herb_name = herb_slug.replace('-', ' ')
        json_article_filepath = f'database/pages/preparations/{preparation_slug}/{herb_slug}.json'
        json_article = json_read(json_article_filepath, create=True)
        json_article['preparation_slug'] = preparation_slug
        json_article['preparation_name_plural'] = preparation_name_plural
        json_article['preparation_name_singular'] = preparation_name_singular
        json_article['preparation_url'] = f'preparations/{preparation_slug}/{herb_slug}.html'
        json_write(json_article_filepath, json_article)
        # update
        ai_paragraph_gen(
            key = 'intro', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = f'''
                Write a short 3-sentence paragraph about {herb_name} {preparation_name_singular}.
            ''',
        )
        # html
        html_article = ''
        html_article += f'<h1>{herb_name} {preparation_name_singular}</h1>'
        html_article += f'<h2>intro</h2>'
        html_article += f'<p>{json_article["intro"]}</p>'
        html_article += f'<p><a href="/herbs/{herb_slug}.html">{herb_name}</a></p>'
        title = f'{herb_slug} {preparation_slug}'
        html_head = html_head_gen(title)
        html_breadcrumbs = breadcrumbs_gen(f'preparations/{preparation_slug}/{herb_slug}.html')
        html_article_layout = html_article_layout_gen(html_article)
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
            {html_head}
            <body>
                {html_header}
                {html_breadcrumbs}
                {html_article_layout}
                {html_footer}
            </body>
            </html>
        '''
        if not os.path.exists(f'{website_folderpath}/preparations/{preparation_slug}'): 
            os.mkdir(f'{website_folderpath}/preparations/{preparation_slug}')
        with open(f'{website_folderpath}/preparations/{preparation_slug}/{herb_slug}.html', 'w') as f:
            f.write(html)


def p_equipments(lst):
    equipments_slugs = [x['slug'] for x in lst]
    json_article_filepath = f'database/pages/equipments.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>equipments</h1>'
    for equipment_slug in equipments_slugs:
        equipment_name = equipment_slug.replace('-', ' ')
        html_article += f'<p><a href="/equipments/{equipment_slug}.html">{equipment_name}</a></p>'
    title = f'equipments'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments'): 
        os.mkdir(f'{website_folderpath}/equipments')
    with open(f'{website_folderpath}/equipments.html', 'w') as f:
        f.write(html)


def a_equipment(equipment):
    equipment_slug = equipment['slug']
    equipment_name = equipment_slug.replace('-', ' ')
    equipments_slugs = [x['slug'] for x in lst]
    json_article_filepath = f'database/pages/equipments/{equipment_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_write(json_article_filepath, json_article)
    html_article = ''
    html_article += f'<h1>{equipment_name}</h1>'
    html_article += f'<p><a href="/equipments/{equipment_slug}/best.html">best {equipment_name}</a></p>'
    title = f'{equipment_slug}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments/{equipment_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments'): 
        os.mkdir(f'{website_folderpath}/equipments')
    with open(f'{website_folderpath}/equipments/{equipment_slug}.html', 'w') as f:
        f.write(html)


def a_equipment_best(equipment):
    equipment_slug = equipment['slug']
    equipment_amazon = equipment['amazon']
    equipment_name = equipment_slug.replace('-', ' ')
    equipment_name_plural = f'{equipment_name}s'
    json_products_folderpath = f'{vault}/amazon/json/{equipment_amazon}'
    json_article_filepath = f'database/pages/equipments/{equipment_slug}/best.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['title'] = f'best {equipment_name_plural} for herbalists'
    json_article['equipment_slug'] = equipment_slug
    json_article['equipment_name'] = equipment_name
    json_article['equipment_name_plural'] = f'{equipment_name}s'
    json_article['url'] = f'equipments/{equipment_slug}/best'
    if 'products_num' not in json_article: json_article['products_num'] = random.choice([7, 9, 11, 13])
    products_num = json_article['products_num']
    json_write(json_article_filepath, json_article)
    #################################################################
    # ;article_json
    #################################################################
    # ;intro
    key = 'intro'
    if key not in json_article: json_article[key] = ''
    # json_article[key] = ''
    if json_article[key] == '':
        prompt = f'''
            Write a 5-sentence pargraph about the following product: {equipment_name} for apothecaries. 
            Include what this product is and why apothecaries use it.
            Reply in less than 100 words.
        '''
        reply = llm_reply(prompt, model).strip()
        if reply.strip() != '':
            json_article[key] = reply
            json_write(json_article_filepath, json_article)
    # order filepaths by popularity
    products_jsons_filepaths = [f'{json_products_folderpath}/{x}' for x in os.listdir(json_products_folderpath)]
    products_jsons = []
    for i, product_json_filepath in enumerate(products_jsons_filepaths):
        product_data = json_read(product_json_filepath, create=True)
        product_asin = product_json_filepath.split('/')[-1].replace('.json', '')
        reviews_score_total = float(product_data['reviews_score_total'])
        products_jsons.append({'product_asin': product_asin, 'reviews_score_total': reviews_score_total})
    products_jsons_ordered = sorted(products_jsons, key=lambda x: x['reviews_score_total'], reverse=True)
    products_jsons_filepaths_ordered = []
    for product_json in products_jsons_ordered:
        product_asin = product_json['product_asin']
        product_filepath = f'{json_products_folderpath}/{product_asin}.json'
        products_jsons_filepaths_ordered.append(product_filepath)
    products_jsons_filepaths_ordered = products_jsons_filepaths_ordered[:products_num]
    # ;product
    for i, product_json_filepath in enumerate(products_jsons_filepaths_ordered):
        product_data = json_read(product_json_filepath)
        product_aff_link = product_data['affiliate_link']
        product_title = product_data['title']
        product_asin = product_json_filepath.split('/')[-1].replace('.json', '')
        # init product
        key = 'products'
        if key not in json_article: json_article[key] = []
        found = False
        for obj in json_article[key]:
            if obj['product_id'] == product_asin:
                found = True
                break
        if not found:
            product = {'product_id': product_asin}
            json_article[key].append(product)
        json_write(json_article_filepath, json_article)
        # update product
        if 'products' not in json_article: json_article['products'] = []
        for obj in json_article['products']:
            if obj['product_id'] == product_asin:
                obj['product_title'] = product_title
                obj['product_aff_link'] = product_aff_link
                json_write(json_article_filepath, json_article)
                # ;title
                key = 'title_ai'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    prompt = f'''
                        Rewrite the following TITLE of a product using the following GUIDELINES: 
                        {product_title}
                        GUIDELINES:
                        Reply in less than 10 words.
                        Keep only the most important things for the TITLE.
                        Keep the name of the brand if present at the beginning of the TITLE.
                        Reply in the following JSON format: 
                        {{"title": "insert the rewritten title here"}} 
                        Only reply with the JSON.
                    '''
                    reply = llm_reply(prompt, model).strip()
                    # json_data = json.loads(reply)
                    try: json_data = json.loads(reply)
                    except: json_data = {}
                    if json_data != {}:
                        try: line = json_data['title']
                        except: continue
                        obj[key] = line
                        json_write(json_article_filepath, json_article)
                # ;pros
                key = 'pros'
                if key not in obj: obj[key] = []
                # obj[key] = []
                if obj[key] == []:
                    positive_reviews_text = product_data['reviews_5s']
                    outputs = []
                    prompt = f'''
                        Extract a list of the most mentioned and recurring key features from the following CUSTOMERS REVIEWS.
                        Also, follow the GUIDELINES below.
                        CUSTOMERS REVIEWS:
                        {positive_reviews_text}
                        GUIDELINES:
                        Write the features in 7-10 words.
                        Reply in the following JSON format: 
                        [
                            {{"feature": "write feature 1 here"}}, 
                            {{"feature": "write feature 2 here"}}, 
                            {{"feature": "write feature 3 here"}}, 
                            {{"feature": "write feature 4 here"}}, 
                            {{"feature": "write feature 5 here"}} 
                        ]
                        Only reply with the JSON.
                    '''
                    reply = llm_reply(prompt, model).strip()
                    try: json_data = json.loads(reply)
                    except: json_data = {}
                    if json_data != {}:
                        for item in json_data:
                            try: line = item['feature']
                            except: continue
                            outputs.append(line)
                    obj[key] = outputs
                    json_write(json_article_filepath, json_article)
# ;cons
                key = 'cons'
                if key not in obj: obj[key] = []
                # obj[key] = []
                if obj[key] == []:
                    negative_reviews_text = product_data['reviews_1s']
                    outputs = []
                    if negative_reviews_text.strip() != '':
                        prompt = f'''
                            Extract a list of the most mentioned and recurring complaints from the following CUSTOMERS REVIEWS.
                            Also, follow the GUIDELINES below.
                            CUSTOMERS REVIEWS:
                            {negative_reviews_text}
                            GUIDELINES:
                            Write the features in 7-10 words.
                            Reply in the following JSON format: 
                            [
                                {{"complaint": "write complaint 1 here"}}, 
                                {{"complaint": "write complaint 2 here"}}, 
                                {{"complaint": "write complaint 3 here"}}, 
                                {{"complaint": "write complaint 4 here"}}, 
                                {{"complaint": "write complaint 5 here"}} 
                            ]
                            Only reply with the JSON.
                        '''
                        reply = llm_reply(prompt, model).strip()
                        try: json_data = json.loads(reply)
                        except: json_data = {}
                        if json_data != {}:
                            for item in json_data:
                                try: line = item['complaint']
                                except: continue
                                outputs.append(line)
                    obj[key] = outputs
                    json_write(json_article_filepath, json_article)
                # ;description
                key = 'desc'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    pros = '\n'.join(obj['pros'])
                    cons = '\n'.join(obj['cons'])
                    prompt = f'''
                        Write a short 5-sentence paragraph about the following product: {equipment_name}.
                        The target audience for this product is: apothecary.
                        Use the following INFO to describe the features, and use the GUIDELINES below.
                        INFO:
                        {pros}
                        GUIDELIES:
                        Reply in paragraph format.
                        Don't write conclusory statements, like sentences that starts with "overall", "in conclusion", "to summarize", etc...
                        Start writing the features from the first sentence.
                        Start with the following words: These {equipment_name} .
                    '''
                    reply = llm_reply(prompt)
                    obj[key] = reply
                    json_write(json_article_filepath, json_article)
                # ;cons_description
                key = 'warn'
                if key not in obj: obj[key] = ''
                # obj[key] = ''
                if obj[key] == '':
                    cons = '\n'.join(obj['cons'])
                    prompt = f'''
                        Write 1 short sentence about some of the complaints a few users had about the following product: {equipment_name}.
                        Pick a few of the most relevant COMPLAINTS from the list below to write the 1 short sentence.
                        COMPLAINTS:
                        {cons}
                        GUIDELIES:
                        Reply only in 1 sentence, pick only the number of complaints needed to fit in 1 sentence.
                        Reply in as few words as possible.
                        Reply in paragraph format.
                        Don't write conclusory statements, like sentences that starts with "overall", "in conclusion", "to summarize", etc...
                        Try to include only the complaints that are specific to the characteristics of the products, not complaints about exernal factors (like bad shipping, etc.).
                        Start with the following words: Some users .
                    '''
                    reply = llm_reply(prompt)
                    obj[key] = reply
                    json_write(json_article_filepath, json_article)
    #################################################################
    # ;article_html
    #################################################################
    title = f'{products_num} best {equipment_name_plural}'.title()
    html_article = ''
    html_article += f'<h1>{title}</h1>'
    html_article += f'{text_format_1N1_html(json_article["intro"])}\n'
    if 'products' not in json_article: json_article['products'] = []
    for i, obj in enumerate(json_article['products'][:products_num]):
        title = obj['title_ai']
        desc = obj['desc']
        pros = obj['pros']
        warn = obj['warn']
        product_aff_link = obj['product_aff_link']
        # product_aff_link = obj['product_aff_link']
        html_article += f'<h2>{i+1}. {title}</h2>\n'
        html_article += f'{text_format_1N1_html(desc)}\n'
        html_article += f'<p class="font-bold text-black">Key Features:</p>\n'
        html_article += f'<ul>\n'
        for item in pros[:5]:
            html_article += f'<li>{item}</li>\n'
        html_article += f'</ul>\n'
        html_article += f'<p class="font-bold text-black">Warnings:</p>\n'
        html_article += f'{text_format_1N1_html(warn)}\n'
        amazon_button_html = amazon_buy_button(product_aff_link)
        html_article += amazon_button_html
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'equipments/{equipment_slug}/best.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/equipments/{equipment_slug}'): 
        os.mkdir(f'{website_folderpath}/equipments/{equipment_slug}')
    with open(f'{website_folderpath}/equipments/{equipment_slug}/best.html', 'w') as f:
        f.write(html)


def p_ailments():
    json_article_filepath = f'database/pages/ailments.json'
    json_article = json_read(json_article_filepath, create=True)
    if 'ailments' not in json_article: json_article['ailments'] = []
    for ailment in vertices_ailments:
        ailment_slug = ailment['ailment_slug']
        ailment_name = ailment['ailment_name']
        # add if doesn't exist
        found = False
        for _obj in json_article['ailments']:
            if ailment_slug == _obj['ailment_slug']:
                found = True
                break
        if not found:
            json_article['ailments'].append({'ailment_slug': ailment_slug})
            json_write(json_article_filepath, json_article)
        # update
        ailment_obj = {}
        for _ailment_obj in json_article['ailments']:
            if ailment_slug == _ailment_obj['ailment_slug']:
                ailment_obj = _ailment_obj
                break
        ai_paragraph_gen(
            key = 'ailment_desc', 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = ailment_obj, 
            prompt = f'''
                Write a short 3-sentence paragraph about {ailment_name}.
            ''',
        )

    html_article = ''
    html_article += f'<h1>ailments</h1>'
    for i, ailment in enumerate(json_article['ailments']):
        ailment_slug = ailment['ailment_slug']
        ailment_name = ailment_slug.replace('-', ' ')
        ailment_desc = ailment['ailment_desc']
        html_article += f'<h2>{i+1}. {ailment_name}</h2>\n'
        html_article += f'<p>{ailment_desc}</p>\n'
        html_article += f'<p><a href="/ailments/{ailment_slug}.html">{ailment_name}</a></p>\n'
    title = 'ailments'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'ailments.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    with open(f'{website_folderpath}/ailments.html', 'w') as f:
        f.write(html)

def a_ailment(ailment):
    ailment_slug = ailment['ailment_slug']
    ailment_name = ailment['ailment_name']
    json_article_filepath = f'database/pages/ailments/{ailment_slug}.json'
    json_article = json_read(json_article_filepath, create=True)
    json_article['ailment_slug'] = ailment_slug
    json_article['ailment_name'] = ailment_name
    json_article['ailment_url'] = f'ailments/{ailment_slug}.html'
    json_write(json_article_filepath, json_article)
    # update
    sections = [
        ['1', 'intro', f'write a short 3-sentence paragraph about the ailment: {ailment_name}.', f''],
    ]
    for section in sections:
        if section[0] != '1': continue
        key = section[1]
        prompt = section[2]
        ai_paragraph_gen(
            key = key, 
            filepath = json_article_filepath, 
            data = json_article, 
            obj = json_article, 
            prompt = prompt,
        )
    # html
    html_article = ''
    html_article += f'<h1>{ailment_name}</h1>'
    for section in sections:
        if section[0] != '1': continue
        section_name = section[1]
        section_desc = json_article[section_name]
        section_link = section[3]
        html_article += f'<h2>{section_name}</h2>'
        html_article += f'<p>{section_desc}</p>\n'
        if section_link.strip() != '':
            html_article += f'<p><a href="/ailments/{ailment_slug}/{section_link}.html">{section_name}</a></p>'
    title = f'{ailment_name}'
    html_head = html_head_gen(title)
    html_breadcrumbs = breadcrumbs_gen(f'ailments/{ailment_slug}.html')
    html_article_layout = html_article_layout_gen(html_article)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        {html_head}
        <body>
            {html_header}
            {html_breadcrumbs}
            {html_article_layout}
            {html_footer}
        </body>
        </html>
    '''
    if not os.path.exists(f'{website_folderpath}/ailments'): 
        os.mkdir(f'{website_folderpath}/ailments')
    with open(f'{website_folderpath}/ailments/{ailment_slug}.html', 'w') as f:
        f.write(html)

p_home()

# herbs
if 1:
    p_herbs()
    for herb in vertices_herbs:
        a_herb(herb)
        a_herb_uses(herb)
        a_herb_benefits(herb)
        a_herb_preparations(herb)

# preparations
if 1:
    p_preparations()
    for preparation in vertices_preparations:
        a_preparation(preparation)
        a_preparation_herbs(preparation)

# equipments
if 0:
    lst = [
        {'slug': 'jar', 'amazon': 'jars',},
        {'slug': 'bottle', 'amazon': 'bottles',},
        {'slug': 'spatula', 'amazon': 'spatulas',},
        {'slug': 'coffee-grinder', 'amazon': 'coffee-grinders',},
        {'slug': 'mortar', 'amazon': 'mortars',},
        {'slug': 'pestle', 'amazon': 'pestles',},
        {'slug': 'measuring-cup', 'amazon': 'measuring-cups',},
        {'slug': 'lid-grip', 'amazon': 'lid-grips',},
    ]
    p_equipments(lst)
    for equipment in lst:
        a_equipment(equipment)
        a_equipment_best(equipment)

# ailments
if 0:
    p_ailments()
    for vertex_ailment in vertices_ailments:
        a_ailment(vertex_ailment)

shutil.copy('style.css', f'{website_folderpath}/style.css')

