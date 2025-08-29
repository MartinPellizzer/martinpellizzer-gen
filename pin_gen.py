import os
import random

from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from lib import g
from lib import io
from lib import llm
from lib import data
from lib import media

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

def image_ai(prompt, width, height):
    import torch
    from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
    from diffusers import DPMSolverMultistepScheduler
    global pipe
    if not pipe:
        pipe = StableDiffusionXLPipeline.from_single_file(
            checkpoint_filepath, 
            torch_dtype=torch.float16, 
            use_safetensors=True, 
            variant="fp16"
        ).to('cuda')
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    print(prompt)
    image = pipe(prompt=prompt, width=width, height=height, num_inference_steps=20, guidance_scale=3.0).images[0]
    return image

def images_gen_old(prompt, images, i, width, height):
    print(prompt)
    image = image_ai(prompt, width, height)
    image.save(f'{g.pinterest_tmp_image_folderpath}/tmp/img-{i}.jpg')
    images.append(f'{g.pinterest_tmp_image_folderpath}/tmp/img-{i}.jpg')

def images_gen(prompt, i, width, height):
    image = image_ai(prompt, width, height)
    image.save(f'{g.pinterest_tmp_image_folderpath}/tmp/img-{i}.jpg')

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

def pin_image_gen(item, images_tmp_filepaths, export_filename):
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}/aesthetic'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    article_slug = json_article['article_slug']
    article_title = json_article['article_title']
    article_desc = article_title
    entity_name = json_article['entity_name']
    keyword_main = json_article['keyword_main']
    keyword_main_slug = json_article['keyword_main_slug']
    main_lst_num = json_article['main_lst_num']
    article_desc = article_desc.lower()
    article_desc = article_desc.replace(f'{main_lst_num}', '')
    article_desc = article_desc.replace(f'+', '')
    article_desc = article_desc.replace(f'{keyword_main.lower()}', '')
    article_desc = article_desc.replace(f'images', '')
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
    text = main_lst_num
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
    text = f'{keyword_main} images'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{g.assets_folderpath}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    lines = text_to_lines(text, font, 900)
    for line in lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    y_cur += 32
    ### subtitle
    text = article_desc
    text = f'{text}'.title()
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

'''
data = [
    {
        'article_keyword': 'tulips wallpaper',
        'article_slug': 'plants/types/flowers/tulips/wallpaper',
        'image_text_number': '15',
        'image_text_keyword': 'Gorgeous Tulips Wallpapers',
        'image_text_subtitle': 'for Mobile and Desktop',
    },
    {
        'article_keyword': 'sunflower aesthetic',
        'article_slug': 'plants/types/flowers/sunflower/aesthetic',
        'image_text_number': '100+',
        'image_text_keyword': 'Sunflower Aesthetic Photos',
        'image_text_subtitle': 'for Plant Lovers',
    },
    {
        'article_keyword': 'best indoor plants',
        'article_slug': 'plants/home/indoor/best',
        'image_text_number': '10',
        'image_text_keyword': 'Best Indoor Plants',
        'image_text_subtitle': 'for a Healthier, Greener Home',
    },
]
'''
pins_num_max = 3
pins_delta_perc = 50
pins_delta_perc_random = random.randint(0, pins_delta_perc)
pins_delta_perc_random_sign = random.randint(0, 1)
if pins_delta_perc_random_sign == 0:
    pins_num = pins_num_max - int((pins_num_max/100)*pins_delta_perc_random)
else:
    pins_num = pins_num_max + int((pins_num_max/100)*pins_delta_perc_random)

flowers_data = data.flowers_data
random.shuffle(flowers_data)
for item_i, item in enumerate(flowers_data[:pins_num]):
    article_slug = f'''plants/types/flowers/{item['flower_slug_plural']}/aesthetic'''
    json_article_filepath = f'''{g.database_folderpath}/json/{article_slug}.json'''
    json_article = io.json_read(json_article_filepath, create=True)
    article_slug = json_article['article_slug']
    article_title = json_article['article_title']
    entity_name = json_article['entity_name']
    keyword_main = json_article['keyword_main']
    keyword_main_slug = json_article['keyword_main_slug']
    ### gen tmp images
    width = 1024
    height = 1024
    for i in range(4):
        prompt = f'''
            {entity_name} flower,
            soft focus,
            depth of field,
            bokeh,
            nature photography,
            high resolution,
        '''.replace('  ', ' ')
        images_gen(prompt, i, width, height)
        ###
        export_filename = f'{keyword_main_slug}'
        images_tmp_filepaths = []
        images_tmp_folderpath = f'{g.pinterest_tmp_image_folderpath}/tmp'
        for image_tmp_filename in os.listdir(images_tmp_folderpath):
            image_tmp_filepath = f'{images_tmp_folderpath}/{image_tmp_filename}'
            images_tmp_filepaths.append(image_tmp_filepath)
    print(images_tmp_filepaths)
    ### gen pin image
    pin_image_filepath = pin_image_gen(item, images_tmp_filepaths, export_filename)
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
    board_name = 'flowers'.title()
    article_url = f'http://terrawhisper.com/{article_slug}.html'
    obj = {
        'img_filepath': pin_image_filepath,
        'title': article_title,
        'description': article_description,
        'url': article_url,
        'board_name': board_name
    }
    io.json_write(f'{g.pinterest_tmp_image_folderpath}/pins/{item_i}.json', obj)

    # quit()
