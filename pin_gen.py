import os
import random
from datetime import datetime

from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from lib import g
from lib import io
from lib import llm
from lib import data
from lib import media

pins_num_max = 38
pins_delta_perc = 20
pins_delta_perc_random = random.randint(0, pins_delta_perc)
pins_delta_perc_random_sign = random.randint(0, 1)
if pins_delta_perc_random_sign == 0:
    pins_num = pins_num_max - int((pins_num_max/100)*pins_delta_perc_random)
else:
    pins_num = pins_num_max + int((pins_num_max/100)*pins_delta_perc_random)

data = io.csv_to_dict('articles.csv')

pipe = None
checkpoint_filepath = f'{g.vault_tmp_folderpath}/stable-diffusion/juggernautXL_ragnarokBy.safetensors'

def pin_image_save(img, filename):
    img_filepath = f'{g.pinterest_tmp_image_folderpath}/images/{filename}.jpg'
    img.save(
        img_filepath,
        format='JPEG',
        subsampling=0,
        quality=100,
    )
    return img_filepath

def text_to_lines(text, font, max_w):
    lines = []
    line = ''
    for word in text.split():
        _, _, word_w, word_h = font.getbbox(word)
        _, _, line_w, line_h = font.getbbox(line.strip())
        if  line_w + word_w < max_w:
            line += f'{word} '
        else:
            lines.append(line.strip())
            line = f'{word} '
    if line.strip() != '':
        lines.append(line.strip())
    return lines

def pin_gen(article_slug):
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    try: article_slug = json_article['article_slug']
    except: article_slug = json_article['article_url_slug']
    article_title = json_article['article_title']
    try: keyword_main = json_article['keyword_main']
    except: keyword_main = json_article['article_keyword']
    try: keyword_main_slug = json_article['keyword_main_slug']
    except: keyword_main_slug = json_article['article_keyword_slug']
    try: keyword_main_pretty = json_article['keyword_main_pretty']
    except: keyword_main_pretty = json_article['article_keyword'] + 's'
    main_list_num = json_article['main_list_num']
    '''
    article_desc = article_title
    article_desc = article_desc.lower()
    article_desc = article_desc.replace(f'{main_list_num}', '')
    article_desc = article_desc.replace(f':', '').strip()
    for word in keyword_main_pretty.lower().split('\n'):
        article_desc = article_desc.replace(f'{word.lower()}', '')
    article_desc = ' '.join([word for word in article_desc.split() if word != ''])
    '''
    article_desc = 'for plant lovers'
    ###
    images_tmp_filepaths = []
    images_tmp_folderpath = f'{g.pinterest_tmp_image_folderpath}/tmp'
    for image_tmp_filename in os.listdir(images_tmp_folderpath):
        image_tmp_filepath = f'{images_tmp_folderpath}/{image_tmp_filename}'
        images_tmp_filepaths.append(image_tmp_filepath)
    export_filename = f'{keyword_main_slug}'
    ###
    text_color = '#ffffff'
    bg_color = '#000000'    
    ###
    pin_w = 1000
    pin_h = 1500
    gap = 8
    rect_h = 500
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    img_0000 = Image.open(images_tmp_filepaths[0])
    img_0000 = media.resize(img_0000, pin_w//2, pin_w//2)
    img_0001 = Image.open(images_tmp_filepaths[1])
    img_0001 = media.resize(img_0001, pin_w//2, pin_w//2)
    img_0002 = Image.open(images_tmp_filepaths[2])
    img_0002 = media.resize(img_0002, pin_w//2, pin_w//2)
    img_0003 = Image.open(images_tmp_filepaths[3])
    img_0003 = media.resize(img_0003, pin_w//2, pin_w//2)
    img.paste(img_0000, (0, int(pin_h*0.0) - gap))
    img.paste(img_0001, (0, int(pin_h*0.66) + gap))
    img.paste(img_0002, (int(pin_w*0.5) + gap, int(pin_h*0.0) - gap))
    img.paste(img_0003, (int(pin_w*0.5) + gap, int(pin_h*0.66) + gap))
    y_cur = 500
    ### rect
    draw.rectangle(((0, 500), (1000, 1000)), fill=bg_color)
    ### number
    text = main_list_num
    text = f'{text}'.upper()
    font_size = 160
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{g.assets_folderpath}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    lines = text_to_lines(text, font, 800)
    for line in lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    y_cur += 16
    ### keyword
    text = f'{keyword_main_pretty}'.upper()
    font_size = 96
    y_off = 0
    line_w_max = 900
    for _ in range(10):
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{g.assets_folderpath}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        lines = text_to_lines(text, font, line_w_max)
        if len(lines) == 2: break
        if len(lines) > 2:
            font_size -= 4
            y_off += 4
        else:
            # font_size += 4
            # y_off -= 4
            line_w_max -= 50
    y_cur += y_off
    for line in lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    y_cur += 32
    ### subtitle
    text = article_desc
    text = f'{text}'.lower()
    font_size = 32
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{g.assets_folderpath}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    lines = text_to_lines(text, font, 800)
    for line in lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    ###
    export_filepath = pin_image_save(img, export_filename)
    return export_filepath

def pin_tmp_image_gen(json_article, keyword_main_slug):
    width = 1024
    height = 1024
    for i in range(4):
        prompt = json_article['images_prompts'][0]
        image = media.image_gen(prompt, width, height)
        image.save(f'{g.pinterest_tmp_image_folderpath}/tmp/img-{i}.jpg')

### clear folder
if 1:
    for filename in os.listdir(f'{g.pinterest_tmp_image_folderpath}/pins'):
        os.remove(f'{g.pinterest_tmp_image_folderpath}/pins/{filename}')
    for filename in os.listdir(f'{g.pinterest_tmp_image_folderpath}/images'):
        os.remove(f'{g.pinterest_tmp_image_folderpath}/images/{filename}')
    pass

### randomize articles
articles_slugs = []
for item in data:
    if item['article_type'] == 'listicle':
        article_slug = f'''{item['article_slug']}'''
        articles_slugs.append([article_slug])
random.shuffle(articles_slugs)

########################################
### aesthetic
########################################
from data import art_data
# articles_slugs = []

art_aesthetic_articles_slugs = [item['article_url_slug'] for item in art_data.art_aesthetic_data]

for item in art_aesthetic_articles_slugs:
    articles_slugs.append([item])
    pass

random.shuffle(articles_slugs)

item_i = 0
for cluster_slugs in articles_slugs:
    if item_i >= pins_num: break
    article_slug = random.choice(cluster_slugs)
    print(article_slug)
    ### try pumpkin pin
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath)
    try: article_slug = json_article['article_slug']
    except: article_slug = json_article['article_url_slug']
    article_title = json_article['article_title']
    try: keyword_main = json_article['keyword_main']
    except: keyword_main = json_article['article_keyword']
    try: keyword_main_slug = json_article['keyword_main_slug']
    except: keyword_main_slug = json_article['article_keyword_slug']
    try: pin_board_name = json_article['pin_board_name'].title()
    except: pin_board_name = 'Plant Art'
    ### gen tmp images
    pin_tmp_image_gen(json_article, keyword_main_slug)
    ### gen pin image
    pin_image_filepath = pin_gen(article_slug)
    ### gen pin json
    article_description = ''
    prompt = f'''
        Write a description in less that 500 characters for a pinterest pin with the following title: {article_title}.
        Write only the description.
        Use only ascii characters.
    '''
    prompt += f'/no_think'
    reply = llm.reply(prompt).strip()
    if '</think>' in reply:
        reply = reply.split('</think>')[1].strip()
    if len(article_description) >= 500:
        article_description = reply[:490] + '...'
    else:
        article_description = reply
    # board_name = 'plants art'.title()
    article_url = f'https://martinpellizzer.com/{article_slug}.html'
    obj = {
        'img_filepath': pin_image_filepath,
        'title': article_title,
        'description': article_description,
        'url': article_url,
        'board_name': pin_board_name
    }
    io.json_write(f'{g.pinterest_tmp_image_folderpath}/pins/{item_i}.json', obj)
    # quit()
    item_i += 1

print(datetime.now())
