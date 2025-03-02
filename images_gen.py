import os

import torch
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from diffusers import DPMSolverMultistepScheduler
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from oliark_io import json_read, json_write

vault = f'/home/ubuntu/vault'
website_folderpath = 'website'

checkpoint_filepath = f'{vault}/stable-diffusion/checkpoints/xl/juggernautXL_juggXIByRundiffusion.safetensors'
pipe = StableDiffusionXLPipeline.from_single_file(
    checkpoint_filepath, 
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16"
).to('cuda')
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

vertices_plants = json_read(f'{vault}/herbalism/vertices-plants.json')
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

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
    
##############################################
# ;plants
##############################################

def gen_plants():
    vertices_plants_filtered = get_vertices_plants_validated()
    for vertex_plant in vertices_plants_filtered:
        plant_slug = vertex_plant['plant_slug']
        plant_name_scientific = vertex_plant['plant_name_scientific']
        # default
        images_to_validate_filepath = f'images/herbs/{plant_slug}.jpg'
        images_validated_filepath = f'{website_folderpath}/images/herbs/{plant_slug}.jpg'
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
        images_to_validate_filepath = f'images/herbs/{plant_slug}-illustation.jpg'
        images_validated_filepath = f'{website_folderpath}/images/herbs/{plant_slug}-illustation.jpg'
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

# herbs teas
if 0:
    for edge_herb_preparation in edges_herbs_preparations:
        herb_slug = edge_herb_preparation['vertex_1']
        preparation_slug = edge_herb_preparation['vertex_2']

        herb_name_scientific = [vertex['herb_name_scientific'] for vertex in vertices_herbs if vertex['herb_slug'] == herb_slug][0]
        preparation_name = [vertex['preparation_name'] for vertex in vertices_preparations if vertex['preparation_slug'] == preparation_slug][0]

        if preparation_slug != 'tea': continue

        images_to_validate_filepath = f'images/herbs-preparations/{herb_slug}-{preparation_slug}.jpg'
        images_validated_filepath = f'{website_folderpath}/images/herbs-preparations/{herb_slug}-{preparation_slug}.jpg'
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
# ;equipments
##################################################################################
prompt_style = f'''
    vintage,
'''

def p_equipments_intro():
    output_filepath = f'{website_folderpath}/images/equipments/herbalists-equipments.jpg'
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
    for equipment_slug in os.listdir(f'{vault}/amazon/json'):
        equipment_name = equipment_slug.lower().strip().replace('-', ' ')
        if equipment_name[-1] == 's': equipment_name = equipment_name[:-1]
        out_filepath = f'{website_folderpath}/images/equipments/{equipment_slug}.jpg'
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

gen_plants()
