import os
import time
import random
import csv
from datetime import datetime
import re
from bs4 import BeautifulSoup

import torch
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from diffusers import DPMSolverMultistepScheduler
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from oliark_io import json_write, json_read
from oliark_io import csv_read_rows_to_json

vault = '/home/ubuntu/vault'
vault_tmp = '/home/ubuntu/vault-tmp'

checkpoint_filepath = f'{vault}/stable-diffusion/checkpoints/xl/juggernautXL_juggXIByRundiffusion.safetensors'

proj_filepath_abs = '/home/ubuntu/proj/martinpellizzer-gen'

PINTEREST_PINS_IMAGE_FOLDERPATH = 'pinterest/pins'

random_num = random.randint(-2, 2)
ARTICLES_NUM = 15 - random_num

pipe = StableDiffusionXLPipeline.from_single_file(
    checkpoint_filepath, 
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16"
).to('cuda')
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

equipments_folderpaths = [f.path for f in os.scandir('database/pages/equipments') if f.is_dir()]
equipments_filepaths = [f'{folder}/best.json' for folder in equipments_folderpaths]
equipments_filepaths = [filepath for filepath in equipments_filepaths if os.path.exists(filepath)]
random.shuffle(equipments_filepaths)

herbs_folderpaths = [f.path for f in os.scandir('database/pages/herbs') if f.is_dir()]
herbs_benefits_filepaths = [f'{folder}/benefit.json' for folder in herbs_folderpaths if os.path.exists(f'{folder}/benefit.json')]
random.shuffle(herbs_benefits_filepaths)

articles_filepaths = []

equipments_filepaths_tmp = []
herbs_benefits_filepaths_tmp = []

for i in range(999):
    try: equipments_filepaths_tmp.append(equipments_filepaths[i])
    except: pass
    try: herbs_benefits_filepaths_tmp.append(herbs_benefits_filepaths[i])
    except: pass
    if len(equipments_filepaths_tmp) + \
        len(herbs_benefits_filepaths_tmp) \
        >= ARTICLES_NUM:
        break

equipments_filepaths = equipments_filepaths_tmp
herbs_benefits_filepaths = herbs_benefits_filepaths_tmp

for filepath in equipments_filepaths: articles_filepaths.append(filepath)
for filepath in herbs_benefits_filepaths: articles_filepaths.append(filepath)

print(ARTICLES_NUM)
print(len(equipments_filepaths))
print(len(herbs_benefits_filepaths))

###########################################################################
# UTILS
###########################################################################

def img_resize(img, w=768, h=578):
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

def pin_save(img, filename):
    img_filepath = f'pinterest/images/{filename}.jpg'
    img.save(
        img_filepath,
        format='JPEG',
        subsampling=0,
        quality=100,
    )
    return img_filepath
    

###########################################################################
# TEMPLATES
###########################################################################

def template_text_2(data, images_file_paths, export_file_name):
    pin_w = 1000
    pin_h = 1500
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color='#ffffff')
    draw = ImageDraw.Draw(img)
    gap = 8
    rect_h = 320
    img_0000 = Image.open(images_file_paths[0])
    img_0001 = Image.open(images_file_paths[1])
    img_0000 = img_resize(img_0000, int(pin_w*1), int(pin_h*0.5))
    img_0001 = img_resize(img_0001, int(pin_w*1), int(pin_h*0.5))
    img.paste(img_0000, (0, 0))
    img.paste(img_0001, (0, int(pin_h*0.5) + gap))
    random_theme = random.randint(0, 1)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    # rect
    draw.rectangle(((0, pin_h//2 - rect_h//2), (pin_w, pin_h//2 + rect_h//2)), fill=bg_color)
    # circle
    circle_size = 300
    x1 = pin_w//2 - circle_size//2
    y1 = pin_h//2 - 160 - circle_size//2
    x2 = pin_w//2 + circle_size//2
    y2 = pin_h//2 - 160 + circle_size//2
    draw.ellipse((x1, y1, x2, y2), fill=bg_color)
    # draw.rectangle(((0, pin_h//2 - rect_h//2), (pin_w, pin_h//2 + rect_h//2)), fill=bg_color)
    
    ## text split
    try: status_name = data['ailment_name']
    except: pass
    try: status_name = data['status_name']
    except: pass
    text = f'{status_name}'.upper()
    #text = 'Breastfeeding pain'.upper()
    #text = 'Breastfeeding'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 80:
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
        words = text.split(' ')
        words_per_line = len(words)//2
        line_1 = ' '.join(words[:words_per_line])
        line_2 = ' '.join(words[words_per_line:])
        _, _, text_w, text_h = font.getbbox(line_1)
        draw.text((pin_w//2 - text_w//2, pin_h//2 - text_h//2), line_1, text_color, font=font)
        _, _, text_w, text_h = font.getbbox(line_2)
        draw.text((pin_w//2 - text_w//2, pin_h//2 - text_h//2 + text_h), line_2, text_color, font=font)
        remedies_num = data['remedies_num']
        preparation_name = data['preparation_name']
        text = f'best herbal {preparation_name} for'.title()
        font_size = 48
        font_family, font_weight = 'Lato', 'Regular'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        draw.text((pin_w//2 - text_w//2, pin_h//2 - text_h//2 - text_h*1.5), text, text_color, font=font)
        text = str(data['remedies_num'])
        font_size = 160
        font_family, font_weight = 'Lato', 'Regular'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        x1 = pin_w//2 - text_w//2
        y1 = pin_h//2 - text_h//2 - 210
        draw.text((x1, y1), text, text_color, font=font)
    else:
        draw.text((pin_w//2 - text_w//2, pin_h//2 - text_h//2 + 16), text, text_color, font=font)
        remedies_num = data['remedies_num']
        preparation_name = data['preparation_name']
        text = f'best herbal {preparation_name} for'.title()
        font_size = 48
        font_family, font_weight = 'Lato', 'Regular'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        draw.text((pin_w//2 - text_w//2, pin_h//2 - text_h//2 - text_h*1.2), text, text_color, font=font)
        text = '10'
        font_size = 160
        font_family, font_weight = 'Lato', 'Regular'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        x1 = pin_w//2 - text_w//2
        y1 = pin_h//2 - text_h//2 - 210
        draw.text((x1, y1), text, text_color, font=font)
    # text
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def gen_image_herb(images, i, item_name, image_style, width, height):
    if image_style == '':
        prompt = f'''
            {item_name} plant,
            natural light,
            depth of field, bokeh,
            high resolution,
            cinematic
        '''
    elif image_style == 'watercolor':
        prompt = f'''
            {item_name} plant,
            watercolor
        '''
    print(prompt)
    image = pipe(prompt=prompt, width=width, height=height, num_inference_steps=30, guidance_scale=7.0).images[0]
    image.save(f'pinterest/tmp/img-{i}.jpg')
    images.append(f'pinterest/tmp/img-{i}.jpg')

def gen_image_equipment(images, i, equipment_name, image_style, width, height):
    rnd_table = random.choice(['wooden', 'dark'])
    if image_style == '':
        prompt = f'''
            {equipment_name},
            on a {rnd_table} table, 
            surrounded by herbs,
            indoor, 
            natural light,
            earth tones,
            neutral colors,
            soft focus,
            warm tones,
            vintage,
            high resolution,
            cinematic
        '''
    elif image_style == 'watercolor':
        prompt = f'''
            {equipment_name},
            on a {rnd_table} table, 
            surrounded by herbs,
            indoor, 
            watercolor,
            high resolution
        '''
    print(prompt)
    image = pipe(prompt=prompt, width=width, height=height, num_inference_steps=30, guidance_scale=7.0).images[0]
    image.save(f'pinterest/tmp/img-{i}.jpg')
    images.append(f'pinterest/tmp/img-{i}.jpg')


def gen_image(images, i, preparation_name, image_style, width, height):
    rnd_herb_name_scientific = random.choice(herbs_names_scientific).strip()
    if preparation_name[-1] == 's': preparation_name_singular = preparation_name[:-1]
    else: preparation_name_singular = preparation_name
    preparation_container = ''
    if preparation_name_singular == 'tea': preparation_container = 'a cup of'
    if preparation_name_singular == 'tincture': preparation_container = 'a bottle of'
    if preparation_name_singular == 'cream': preparation_container = 'a jar of'
    if preparation_name_singular == 'essential oil': preparation_container = 'a bottle of'
    rnd_table = random.choice(['wooden', 'dark'])
    prompt_juggernaut_xi = f'''
        close-up of {preparation_container} herbal {preparation_name},
        on a {rnd_table} table, 
        surrounded by dry {rnd_herb_name_scientific} herbs,
        indoor, 
        natural light,
        earth tones,
        neutral colors,
        soft focus,
        warm tones,
        vintage,
        high resolution,
        cinematic
    '''.replace('  ', ' ')
    prompt = prompt_juggernaut_xi
    print(prompt)
    image = pipe(prompt=prompt, width=width, height=height, num_inference_steps=30, guidance_scale=7.0).images[0]
    image.save(f'pinterest/tmp/img-{i}.jpg')
    images.append(f'pinterest/tmp/img-{i}.jpg')


def equipment_template_1_img_b(data, images_file_paths, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    rect_h = 500
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        img_0000 = Image.open(images_file_paths[0])
        img_0000 = img_resize(img_0000, pin_w, pin_w)
        img.paste(img_0000, (0, pin_h//3))
    elif random_images_num == 2:
        img_0000 = Image.open(images_file_paths[0])
        img_0001 = Image.open(images_file_paths[1])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w)
        img.paste(img_0000, (0, pin_h//3))
        img.paste(img_0001, (pin_w//2+gap, pin_h//3))
    y_cur = 0
    # number
    try: text = str(data['products_num'])
    except: text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    try: text = f'best {data["product_type"]}'.upper()
    except: text = f'best {data["equipment_name_plural"]}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = 'for herbalists'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path


def equipment_template_1_img_t(data, images_file_paths, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        img_0000 = Image.open(images_file_paths[0])
        img_0000 = img_resize(img_0000, pin_w, pin_w)
        img.paste(img_0000, (0, 0))
    elif random_images_num == 2:
        img_0000 = Image.open(images_file_paths[0])
        img_0001 = Image.open(images_file_paths[1])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w)
        img.paste(img_0000, (0, 0))
        img.paste(img_0001, (pin_w//2+gap, 0))
    y_cur = 1000
    # number
    try: text = str(data['products_num'])
    except: text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    try: text = f'best {data["product_type"]}'.upper()
    except: text = f'best {data["equipment_name_plural"]}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = 'for herbalists'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def equipment_template_1_img_c(data, images_file_paths, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        img_0000 = Image.open(images_file_paths[0])
        img_0000 = img_resize(img_0000, pin_w, 500)
        img.paste(img_0000, (0, 0))
        img_0001 = Image.open(images_file_paths[1])
        img_0001 = img_resize(img_0001, pin_w, 500)
        img.paste(img_0001, (0, 1000))
    elif random_images_num == 2:
        img_0000 = Image.open(images_file_paths[0])
        img_0001 = Image.open(images_file_paths[1])
        img_0002 = Image.open(images_file_paths[2])
        img_0003 = Image.open(images_file_paths[3])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w//2)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w//2)
        img_0002 = img_resize(img_0002, pin_w//2, pin_w//2)
        img_0003 = img_resize(img_0003, pin_w//2, pin_w//2)
        img.paste(img_0000, (0, 0))
        img.paste(img_0001, (pin_w//2+gap, 0))
        img.paste(img_0002, (0, 1000))
        img.paste(img_0003, (pin_w//2+gap, 1000))
    y_cur = 500
    draw.rectangle(((0, y_cur), (pin_w, y_cur + 500)), fill=bg_color)
    # y_cur += 30
    # number
    try: text = str(data['products_num'])
    except: text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    try: text = f'best {data["product_type"]}'.upper()
    except: text = f'best {data["equipment_name_plural"]}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = 'for herbalists'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def herb_template_1_img_b(data, images, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    images = []
    image_style = random.choice(['', 'watercolor'])
    herb_name_scientific = data['herb_name_scientific']
    herb_name_common = data['herb_names_common'][0]['name']
    herb_name = random.choice([herb_name_scientific, herb_name_common])
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    rect_h = 500
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        for i in range(1):
            gen_image_herb(images, i, herb_name_scientific, image_style, 1024, 1024)
        img_0000 = Image.open(images[0])
        img_0000 = img_resize(img_0000, pin_w, pin_w)
        img.paste(img_0000, (0, pin_h//3))
    elif random_images_num == 2:
        for i in range(2):
            gen_image_herb(images, i, herb_name_scientific, image_style, 832, 1216)
        img_0000 = Image.open(images[0])
        img_0001 = Image.open(images[1])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w)
        img.paste(img_0000, (0, pin_h//3))
        img.paste(img_0001, (pin_w//2+gap, pin_h//3))
    y_cur = 0
    # number
    text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    text = f'best benefits of'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = f'{herb_name}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        if text_w > pin_w - 100:
            font_size = 64
            font_family, font_weight = 'Lato', 'Bold'
            font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
            font = ImageFont.truetype(font_path, font_size)
            _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def herb_template_1_img_t(data, images, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    images = []
    image_style = random.choice(['', 'watercolor'])
    herb_name_scientific = data['herb_name_scientific']
    herb_name_common = data['herb_names_common'][0]['name']
    herb_name = random.choice([herb_name_scientific, herb_name_common])
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        for i in range(1):
            gen_image_herb(images, i, herb_name_scientific, image_style, 1024, 1024)
        img_0000 = Image.open(images[0])
        img_0000 = img_resize(img_0000, pin_w, pin_w)
        img.paste(img_0000, (0, 0))
    elif random_images_num == 2:
        for i in range(2):
            gen_image_herb(images, i, herb_name_scientific, image_style, 832, 1216)
        img_0000 = Image.open(images[0])
        img_0001 = Image.open(images[1])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w)
        img.paste(img_0000, (0, 0))
        img.paste(img_0001, (pin_w//2+gap, 0))
    y_cur = 1000
    # number
    text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    text = f'best benefits of'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = f'{herb_name}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        if text_w > pin_w - 100:
            font_size = 64
            font_family, font_weight = 'Lato', 'Bold'
            font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
            font = ImageFont.truetype(font_path, font_size)
            _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def herb_template_1_img_c(data, images, export_file_name):
    random_theme = random.randint(0, 1)
    random_images_num = random.randint(1, 2)
    images = []
    image_style = random.choice(['', 'watercolor'])
    herb_name_scientific = data['herb_name_scientific']
    herb_name_common = data['herb_names_common'][0]['name']
    herb_name = random.choice([herb_name_scientific, herb_name_common])
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    if random_images_num == 1:
        for i in range(2):
            gen_image_herb(images, i, herb_name_scientific, image_style, 1216, 832)
        img_0000 = Image.open(images[0])
        img_0000 = img_resize(img_0000, pin_w, 500)
        img.paste(img_0000, (0, 0))
        img_0001 = Image.open(images[1])
        img_0001 = img_resize(img_0001, pin_w, 500)
        img.paste(img_0001, (0, 1000))
    elif random_images_num == 2:
        for i in range(4):
            gen_image_herb(images, i, herb_name_scientific, image_style, 1024, 1024)
        img_0000 = Image.open(images[0])
        img_0001 = Image.open(images[1])
        img_0002 = Image.open(images[2])
        img_0003 = Image.open(images[3])
        img_0000 = img_resize(img_0000, pin_w//2, pin_w//2)
        img_0001 = img_resize(img_0001, pin_w//2, pin_w//2)
        img_0002 = img_resize(img_0002, pin_w//2, pin_w//2)
        img_0003 = img_resize(img_0003, pin_w//2, pin_w//2)
        img.paste(img_0000, (0, 0))
        img.paste(img_0001, (pin_w//2+gap, 0))
        img.paste(img_0002, (0, 1000))
        img.paste(img_0003, (pin_w//2+gap, 1000))
    y_cur = 500
    draw.rectangle(((0, y_cur), (pin_w, y_cur + 500)), fill=bg_color)
    # y_cur += 30
    # number
    text = str(data['main_lst_num'])
    font_size = 192
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # product
    text = f'best benefits of'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # for what
    text = f'{herb_name}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    if text_w > pin_w - 100:
        font_size = 80
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = font.getbbox(text)
        if text_w > pin_w - 100:
            font_size = 64
            font_family, font_weight = 'Lato', 'Bold'
            font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
            font = ImageFont.truetype(font_path, font_size)
            _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    export_file_path = pin_save(img, export_file_name)
    return export_file_path



def gen_template_1_img_b(data, images_file_paths, export_file_name):
    random_theme = random.randint(0, 1)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    rect_h = 500
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    img_0000 = Image.open(images_file_paths[0])
    img_0000 = img_resize(img_0000, pin_w, pin_w)
    img.paste(img_0000, (0, pin_h//3))
    # draw.rectangle(((0, 0), (img_w, img_h//3)), fill=bg_color)
    ## text split
    try: ailment_name = data['ailment_name']
    except: pass
    try: ailment_name = data['status_name']
    except: pass
    ailment_text = f'{ailment_name}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, ailment_w, ailment_h = font.getbbox(ailment_text)
    ailment_lines = []
    if ailment_w > pin_w - 80:
        '''
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
        '''
        words = ailment_text.split(' ')
        words_per_line = len(words)//2
        line_1 = ' '.join(words[:words_per_line])
        line_2 = ' '.join(words[words_per_line:])
        ailment_lines.append(line_1)
        ailment_lines.append(line_2)
    else:
        ailment_lines.append(ailment_text)
    # number
    y_start = 0
    if len(ailment_lines) == 2:
        y_start = 0
    elif len(ailment_lines) == 1:
        y_start = 50
    y_cur = y_start
    y_cur += 0
    text = str(data['remedies_num'])
    font_size = 160
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # preparations
    preparation_name = data['preparation_name']
    text = f'best herbal {preparation_name} for'.title()
    font_size = 48
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # ailment
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    for line in ailment_lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    print('****************************************')
    print(data['remedies_num'])
    print(data['preparation_name'])
    print(ailment_lines)
    print(x1)
    print(y_cur)
    print('****************************************')
    export_file_path = pin_save(img, export_file_name)
    return export_file_path

def pin_gen_equipments(article_filepath, article_i, equipment_slug):
    data = json_read(article_filepath)
    equipment_name = data['equipment_name']
    equipment_name_plural = data['equipment_name_plural']
    title = data['title']
    url = data["url"]
    img_slug = url.replace('/', '-')
    filename_out = url.replace('/', '-')
    products = data['products']
    products_descriptions = [x['desc'] for x in products]
    if products_descriptions:
        random.shuffle(products_descriptions)
        description = products_descriptions[0][:490] + '...'
    else:
        description = ''
    board_name = f'herbalist equipments'.title()
    styles = ['', 'watercolor']
    templates = ['1_img_b', '1_img_t', '']
    image_style = random.choice(styles)
    template = random.choice(templates)
    print(template)
    images = []
    width = 0
    height = 0
    # template = '1_img_c'
    for i in range(4):
        gen_image_equipment(images, i, equipment_name, image_style, width, height)
    if template == '1_img_b': 
        width = 1024
        height = 1024
    elif template == '1_img_t': 
        width = 1024
        height = 1024
    else:
        width = 1216
        height = 832
    # gen pins
    if template == '1_img_b':
        img_filepath = equipment_template_1_img_b(data, images, filename_out)
    elif template == '1_img_t':
        img_filepath = equipment_template_1_img_t(data, images, filename_out)
    else:
        img_filepath = equipment_template_1_img_c(data, images, filename_out)
    obj = {
        'equipment_slug': equipment_slug,
        'equipment_name': equipment_name,
        'title': title,
        'url': url,
        'description': description,
        'img_filepath': img_filepath,
        'board_name': board_name
    }
    json_write(f'{PINTEREST_PINS_IMAGE_FOLDERPATH}/{article_i}.json', obj)



def gen_template_1_img_t(data, images_file_paths, export_file_name):
    random_theme = random.randint(0, 1)
    if random_theme == 0:
        text_color = '#ffffff'
        bg_color = '#000000'    
    else:
        text_color = '#000000'    
        bg_color = '#ffffff'
    pin_w = 1000
    pin_h = 1500
    gap = 8
    img = Image.new(mode="RGB", size=(pin_w, pin_h), color=bg_color)
    draw = ImageDraw.Draw(img)
    img_0000 = Image.open(images_file_paths[0])
    img_0000 = img_resize(img_0000, pin_w, pin_w)
    img.paste(img_0000, (0, 0))
    # draw.rectangle(((0, 0), (img_w, img_h//3)), fill=bg_color)
    ## text split
    try: ailment_name = data['ailment_name']
    except: pass
    try: ailment_name = data['status_name']
    except: pass
    ailment_text = f'{ailment_name}'.upper()
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, ailment_w, ailment_h = font.getbbox(ailment_text)
    ailment_lines = []
    if ailment_w > pin_w - 80:
        '''
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
        '''
        words = ailment_text.split(' ')
        words_per_line = len(words)//2
        line_1 = ' '.join(words[:words_per_line])
        line_2 = ' '.join(words[words_per_line:])
        ailment_lines.append(line_1)
        ailment_lines.append(line_2)
    else:
        ailment_lines.append(ailment_text)
    # number
    y_start = 1000
    if len(ailment_lines) == 2:
        y_start = 1000
    elif len(ailment_lines) == 1:
        y_start = 1050
    y_cur = y_start
    y_cur += 0
    text = str(data['remedies_num'])
    font_size = 160
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    x1 = pin_w//2 - text_w//2
    draw.text((x1, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # preparations
    preparation_name = data['preparation_name']
    text = f'best herbal {preparation_name} for'.title()
    font_size = 48
    font_family, font_weight = 'Lato', 'Regular'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    _, _, text_w, text_h = font.getbbox(text)
    draw.text((pin_w//2 - text_w//2, y_cur), text, text_color, font=font)
    y_cur += font_size * 1.2
    # ailment
    font_size = 96
    font_family, font_weight = 'Lato', 'Bold'
    font_path = f"{vault}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
    font = ImageFont.truetype(font_path, font_size)
    for line in ailment_lines:
        _, _, line_w, line_h = font.getbbox(line)
        draw.text((pin_w//2 - line_w//2, y_cur), line, text_color, font=font)
        y_cur += font_size
    print('****************************************')
    print(data['remedies_num'])
    print(data['preparation_name'])
    print(ailment_lines)
    print(x1)
    print(y_cur)
    print('****************************************')
    export_file_path = pin_save(img, export_file_name)
    return export_file_path


def pin_gen_equipments(article_filepath, article_i, equipment_slug):
    data = json_read(article_filepath)
    equipment_name = data['equipment_name']
    equipment_name_plural = data['equipment_name_plural']
    title = data['title']
    url = data["url"]
    img_slug = url.replace('/', '-')
    filename_out = url.replace('/', '-')
    products = data['products']
    products_descriptions = [x['desc'] for x in products]
    if products_descriptions:
        random.shuffle(products_descriptions)
        description = products_descriptions[0][:490] + '...'
    else:
        description = ''
    board_name = f'herbalist equipments'.title()
    styles = ['', 'watercolor']
    templates = ['1_img_b', '1_img_t', '']
    image_style = random.choice(styles)
    template = random.choice(templates)
    print(template)
    images = []
    width = 0
    height = 0
    # template = '1_img_c'
    for i in range(4):
        gen_image_equipment(images, i, equipment_name, image_style, width, height)
    if template == '1_img_b': 
        width = 1024
        height = 1024
    elif template == '1_img_t': 
        width = 1024
        height = 1024
    else:
        width = 1216
        height = 832
    # gen pins
    if template == '1_img_b':
        img_filepath = equipment_template_1_img_b(data, images, filename_out)
    elif template == '1_img_t':
        img_filepath = equipment_template_1_img_t(data, images, filename_out)
    else:
        img_filepath = equipment_template_1_img_c(data, images, filename_out)
    obj = {
        'equipment_slug': equipment_slug,
        'equipment_name': equipment_name,
        'title': title,
        'url': url,
        'description': description,
        'img_filepath': img_filepath,
        'board_name': board_name
    }
    json_write(f'{PINTEREST_PINS_IMAGE_FOLDERPATH}/{article_i}.json', obj)



def pin_gen_equipments(article_filepath, article_i, equipment_slug):
    data = json_read(article_filepath)
    equipment_name = data['equipment_name']
    equipment_name_plural = data['equipment_name_plural']
    title = data['title']
    url = data["url"]
    img_slug = url.replace('/', '-')
    filename_out = url.replace('/', '-')
    products = data['products']
    products_descriptions = [x['desc'] for x in products]
    if products_descriptions:
        random.shuffle(products_descriptions)
        description = products_descriptions[0][:490] + '...'
    else:
        description = ''
    board_name = f'herbalist equipments'.title()
    styles = ['', 'watercolor']
    templates = ['1_img_b', '1_img_t', '']
    image_style = random.choice(styles)
    template = random.choice(templates)
    print(template)
    images = []
    width = 0
    height = 0
    # template = '1_img_c'
    for i in range(4):
        gen_image_equipment(images, i, equipment_name, image_style, width, height)
    if template == '1_img_b': 
        width = 1024
        height = 1024
    elif template == '1_img_t': 
        width = 1024
        height = 1024
    else:
        width = 1216
        height = 832
    # gen pins
    if template == '1_img_b':
        img_filepath = equipment_template_1_img_b(data, images, filename_out)
    elif template == '1_img_t':
        img_filepath = equipment_template_1_img_t(data, images, filename_out)
    else:
        img_filepath = equipment_template_1_img_c(data, images, filename_out)
    obj = {
        'equipment_slug': equipment_slug,
        'equipment_name': equipment_name,
        'title': title,
        'url': url,
        'description': description,
        'img_filepath': img_filepath,
        'board_name': board_name
    }
    json_write(f'{PINTEREST_PINS_IMAGE_FOLDERPATH}/{article_i}.json', obj)


def pin_gen_herbs_benefits(article_filepath, article_i, herb_slug):
    data = json_read(article_filepath)
    herb_name_scientific = data['herb_name_scientific']
    title = data['title']
    url = data["url"]
    img_slug = url.replace('/', '-')
    filename_out = url.replace('/', '-')
    herb_benefits = data['herb_benefits']
    herb_benefits_descriptions = [x['benefit_desc'] for x in herb_benefits if 'benefit_desc' in x]
    if herb_benefits_descriptions:
        random.shuffle(herb_benefits_descriptions)
        herb_benefit_description = herb_benefits_descriptions[0][:490] + '...'
    else:
        herb_benefit_description = ''
    board_name = f'healing herbs'.title()
    styles = ['', 'watercolor']
    templates = ['1_img_b', '1_img_t', '']
    image_style = random.choice(styles)
    template = random.choice(templates)
    print(template)
    images = []
    width = 0
    height = 0
    # template = '1_img_b'
    # image_style = 'watercolor'
    # gen pins
    if template == '1_img_b':
        img_filepath = herb_template_1_img_b(data, images, filename_out)
    elif template == '1_img_t':
        img_filepath = herb_template_1_img_t(data, images, filename_out)
    else:
        img_filepath = herb_template_1_img_c(data, images, filename_out)
    obj = {
        'slug': herb_slug,
        'name': herb_name_scientific,
        'title': title,
        'url': url,
        'description': herb_benefit_description,
        'img_filepath': img_filepath,
        'board_name': board_name
    }
    json_write(f'{PINTEREST_PINS_IMAGE_FOLDERPATH}/{article_i}.json', obj)


i = 0
for article_filepath in articles_filepaths:
    i += 1
    print(f'{i}/{len(articles_filepaths)} >> {article_filepath}')

for filename in os.listdir('pinterest/tmp'):
    os.remove(f'pinterest/tmp/{filename}')
    
for filename in os.listdir('pinterest/pins'):
    os.remove(f'pinterest/pins/{filename}')
    
for filename in os.listdir('pinterest/images'):
    os.remove(f'pinterest/images/{filename}')
    
i = 0
# PINS EQUIPMENTS
if 1:
    for article_filepath in equipments_filepaths:
        print(f'{i}/{len(articles_filepaths)} >> {article_filepath}')
        equipment_slug = article_filepath.split('/')[-2].replace('.json', '')
        pin_gen_equipments(article_filepath, i, equipment_slug)
        i += 1

# PINS HERBS BENEFITS
if 1:
    for article_filepath in herbs_benefits_filepaths:
        print(f'{i}/{len(articles_filepaths)} >> {article_filepath}')
        herb_slug = article_filepath.split('/')[-2].replace('.json', '')
        pin_gen_herbs_benefits(article_filepath, i, herb_slug)
        i += 1
