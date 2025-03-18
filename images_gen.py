import os
import random

import torch
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from diffusers import DPMSolverMultistepScheduler
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from oliark_io import json_read, json_write

import g
import utils

checkpoint_filepath = f'{g.VAULT}/stable-diffusion/checkpoints/xl/juggernautXL_juggXIByRundiffusion.safetensors'
pipe = StableDiffusionXLPipeline.from_single_file(
    checkpoint_filepath, 
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16"
).to('cuda')
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

vertices_plants = json_read(f'{g.VAULT}/herbalism/vertices-plants.json')
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

with open('herbs-450.csv') as f: 
    plants450_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

vertices_ailments_filepath = f'{g.VAULT}/herbalism/vertices-ailments.json'
vertices_ailments = json_read(vertices_ailments_filepath)

###################################################
# ;UTILS
###################################################
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

def get_vertices_plants_validated(plants_slugs):
    # verity herbs in "wcpo"
    vertices_plants_filtered_tmp = [vertex for vertex in vertices_plants if vertex['plant_slug'] in plants_slugs] 
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
    
##############################################
# ;plants
##############################################

def gen_plants(plants_slugs):
    vertices_plants_filtered = get_vertices_plants_validated(plants_slugs)
    for vertex_plant in vertices_plants_filtered:
        plant_slug = vertex_plant['plant_slug']
        plant_name_scientific = vertex_plant['plant_name_scientific']
        # default
        images_to_validate_filepath = f'images/to-validate/{plant_slug}.jpg'
        images_validated_filepath = f'{g.WEBSITE_FOLDERPATH}/images/herbs/{plant_slug}.jpg'
        if not os.path.exists(images_validated_filepath):
            prompt = f'''
                {plant_name_scientific} plant,
                natural light,
                depth of field, bokeh,
                high resolution,
                cinematic
            '''
            print(prompt)
            image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=768)
            image.save(images_to_validate_filepath)
        # botanical illustration
        images_to_validate_filepath = f'images/to-validate/{plant_slug}-illustation.jpg'
        images_validated_filepath = f'{g.WEBSITE_FOLDERPATH}/images/herbs/{plant_slug}-illustation.jpg'
        if not os.path.exists(images_validated_filepath):
            prompt = f'''
                {plant_name_scientific} plant,
                botanical illustration,
                drawing,
                watercolor
            '''
            print(prompt)
            image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=768)
            image.save(images_to_validate_filepath)


##############################################
# ;preparations
##############################################
def ailments_teas_intro():
    for vertex_ailment in vertices_ailments:
        ailment_slug = vertex_ailment['ailment_slug']
        ailment_name = vertex_ailment['ailment_name']
        images_to_validate_filepath = f'images/to-validate/{ailment_slug}-teas.jpg'
        images_validated_filepath = f'{g.WEBSITE_FOLDERPATH}/images/ailments-teas/{ailment_slug}-teas.jpg'
        if not os.path.exists(images_validated_filepath):
            plants_names_scientific = []
            for tea in vertex_ailment['ailment_teas']:
                plant_name_scientific = tea['plant_name_scientific']
                if plant_name_scientific not in plants_names_scientific:
                    plants_names_scientific.append(plant_name_scientific)
            random.shuffle(plants_names_scientific)
            img_0000_filepath = 'images/tmp/tmp-0000.jpg'
            prompt = f'''
                a close-up cup of {plants_names_scientific[0]} tea,
                on a wooden table,
                surrounded by medicinal herbs,
                indoor,
                natural light,
                depth of field, bokeh,
                high resolution,
                cinematic
            '''
            image = pipe(prompt=prompt, width=1216, height=832, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=512)
            image.save(img_0000_filepath)
            text_color = '#ffffff'
            background_color = '#000000'
            img_w = 768
            img_h = 768
            img = Image.new(mode="RGB", size=(img_w, img_h), color=background_color)
            draw = ImageDraw.Draw(img)
            img_0000 = Image.open(img_0000_filepath)
            img.paste(img_0000, (0, 0))
            font_sizes = [96, 88, 80, 72, 64, 56, 48, 40,32]
            text_1 = f'best herbal teas for'.upper()
            text_1_size = 0
            text_2 = f'{ailment_name}'.upper()
            text_2_size = 0
            font_family, font_weight = 'Lato', 'Bold'
            font_path = f"{g.VAULT}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
            for font_size in font_sizes:
                font = ImageFont.truetype(font_path, font_size)
                _, _, text_w, text_h = font.getbbox(text_1)
                if text_w + 32*2 < img_w:
                    text_1_size = font_size
                    break
            for font_size in font_sizes:
                font = ImageFont.truetype(font_path, font_size)
                _, _, text_w, text_h = font.getbbox(text_2)
                if text_w + 32*2 < img_w:
                    text_2_size = font_size
                    break
            text_1_y = 0
            text_2_y = text_1_y + text_1_size
            text_total_h = text_2_y + text_2_size
            text_offset_y = 512 + (768-512)//2 - text_total_h//2
            font = ImageFont.truetype(font_path, text_1_size)
            _, _, text_w, text_h = font.getbbox(text_1)
            draw.text((img_w//2 - text_w//2, text_1_y + text_offset_y), text_1, text_color, font=font)
            font = ImageFont.truetype(font_path, text_2_size)
            _, _, text_w, text_h = font.getbbox(text_2)
            draw.text((img_w//2 - text_w//2, text_2_y + text_offset_y), text_2, text_color, font=font)
            img.save(
                images_to_validate_filepath,
                format='JPEG',
                subsampling=0,
                quality=70,
            )

def teas_gen():
    plants_names_scientific = []
    for vertex_ailment in vertices_ailments:
        for tea in vertex_ailment['ailment_teas']:
            plant_name_scientific = tea['plant_name_scientific']
            if plant_name_scientific not in plants_names_scientific:
                plants_names_scientific.append(plant_name_scientific)
    for plant_name_scientific in plants_names_scientific:
        plant_slug = utils.sluggify(plant_name_scientific)
        images_to_validate_filepath = f'images/to-validate/{plant_slug}-tea.jpg'
        images_validated_filepath = f'{g.WEBSITE_FOLDERPATH}/images/teas/{plant_slug}-tea.jpg'
        if not os.path.exists(images_validated_filepath):
            prompt = f'''
                a close-up cup of {plant_name_scientific} tea,
                on a wooden table,
                surrounded by medicinal herbs,
                indoor,
                natural light,
                depth of field, bokeh,
                high resolution,
                cinematic
            '''
            print(prompt)
            image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=768)
            image.save(images_to_validate_filepath)

# herbs teas
if 0:
    for edge_herb_preparation in edges_herbs_preparations:
        herb_slug = edge_herb_preparation['vertex_1']
        preparation_slug = edge_herb_preparation['vertex_2']
        herb_name_scientific = [vertex['herb_name_scientific'] for vertex in vertices_herbs if vertex['herb_slug'] == herb_slug][0]
        preparation_name = [vertex['preparation_name'] for vertex in vertices_preparations if vertex['preparation_slug'] == preparation_slug][0]
        if preparation_slug != 'tea': continue
        images_to_validate_filepath = f'images/herbs-preparations/{herb_slug}-{preparation_slug}.jpg'
        images_validated_filepath = f'{g.WEBSITE_FOLDERPATH}/images/herbs-preparations/{herb_slug}-{preparation_slug}.jpg'
        if not os.path.exists(images_validated_filepath):
            prompt = f'''
                a close-up cup of {herb_name_scientific} {preparation_slug},
                on a wooden table,
                surrounded by medicinal herbs,
                indoor,
                natural light,
                depth of field, bokeh,
                high resolution,
                cinematic
            '''
            print(prompt)
            image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=768)
            image.save(images_to_validate_filepath)

##################################################################################
# ;ailments
##################################################################################
def gen_ailments_intros():
    img_w = 768
    img_h = 768
    text_color = '#ffffff'
    background_color = '#000000'
    for vertex_ailment in vertices_ailments:
        ailment_name = vertex_ailment['ailment_name']
        ailment_slug = vertex_ailment['ailment_slug']
        img = Image.new(mode="RGB", size=(img_w, img_h), color=background_color)
        draw = ImageDraw.Draw(img)
        font_sizes = [96, 88, 80, 72, 64, 56, 48, 40, 32]
        text_1 = f'{ailment_name}'.upper()
        text_1_size = 0
        font_family, font_weight = 'Lato', 'Bold'
        font_path = f"{g.VAULT}/fonts/{font_family}/{font_family}-{font_weight}.ttf"
        for font_size in font_sizes:
            font = ImageFont.truetype(font_path, font_size)
            _, _, text_w, text_h = font.getbbox(text_1)
            if text_w + 32*2 < img_w:
                text_1_size = font_size
                break
        font = ImageFont.truetype(font_path, text_1_size)
        _, _, text_w, text_h = font.getbbox(text_1)
        draw.text((img_w//2 - text_w//2, img_h//2 - text_h//2), text_1, text_color, font=font)
        img.save(f'{g.WEBSITE_FOLDERPATH}/images/ailments/{ailment_slug}.jpg')
        

##################################################################################
# ;equipments
##################################################################################
def p_equipments_intro():
    output_filepath = f'{g.WEBSITE_FOLDERPATH}/images/equipments/herbalists-equipments.jpg'
    if not os.path.exists(output_filepath):
    # if True:
        prompt = f'''
            close-up of jar,
            on a wooden table,
            with herbs,
            indoor, 
        '''
        prompt += prompt_style
        negative_prompt = f'''
            text, watermark 
        '''
        print(prompt)
        image = pipe(prompt=prompt, negative_prompt=negative_prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
        image = img_resize(image, w=768, h=768)
        image.save(output_filepath)

def a_equipments_intro():
    for equipment_slug in os.listdir(f'{g.VAULT}/amazon/json'):
        equipment_name = equipment_slug.lower().strip().replace('-', ' ')
        if equipment_name[-1] == 's': equipment_name = equipment_name[:-1]
        out_filepath = f'{g.WEBSITE_FOLDERPATH}/images/equipments/{equipment_slug}.jpg'
        ast_filepath = f'assets/images/equipments/{equipment_slug}.jpg'
        tmp_filepath = f'assets/images/equipments-tmp/{equipment_slug}.jpg'
        if not os.path.exists(ast_filepath):
        # if True:
            prompt = f'''
                close-up of {equipment_name},
                on a wooden table,
                with herbs,
                indoor, 
            '''
            prompt += prompt_style
            negative_prompt = f'''
                text, watermark 
            '''
            print(prompt)
            image = pipe(prompt=prompt, negative_prompt=negative_prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
            image = img_resize(image, w=768, h=768)
            image.save(tmp_filepath)

# p_equipments_intro()
# a_equipments_intro()

prompt_style = f'''
    vintage,
'''

gen_plants(plants_slugs_filtered)
gen_plants(plants450_slugs_filtered)
# teas_gen()
# ailments_teas_intro()
# gen_ailments_intros()

