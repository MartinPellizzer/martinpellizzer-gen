import os

import torch
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from diffusers import DPMSolverMultistepScheduler
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageOps

from oliark_io import json_read, json_write

vault = f'/home/ubuntu/vault'
website_folderpath = 'website'

vertices_herbs = json_read('vertices-herbs.json')

checkpoint_filepath = f'{vault}/stable-diffusion/checkpoints/juggernautXL_juggXIByRundiffusion.safetensors'
pipe = None
def pipe_init():
    global pipe
    if pipe is None:
        pipe = StableDiffusionXLPipeline.from_single_file(
            checkpoint_filepath, 
            torch_dtype=torch.float16, 
            use_safetensors=True, 
            variant="fp16"
        ).to('cuda')
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

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

##############################################
# ;plants
##############################################

for vertex_herb in vertices_herbs:
    herb_slug = vertex_herb['herb_slug']
    herb_name_scientific = vertex_herb['herb_name_scientific']
    # default
    images_to_validate_filepath = f'images/herbs/{herb_slug}.jpg'
    images_validated_filepath = f'{website_folderpath}/images/herbs/{herb_slug}.jpg'
    if not os.path.exists(images_validated_filepath):
        prompt = f'''
            {herb_name_scientific} plant,
            natural light,
            depth of field, bokeh,
            high resolution,
            cinematic
        '''
        print(prompt)
        pipe_init()
        image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
        image = img_resize(image, w=768, h=768)
        image.save(images_to_validate_filepath)
    # botanical illustration
    images_to_validate_filepath = f'images/herbs/{herb_slug}-illustation.jpg'
    images_validated_filepath = f'{website_folderpath}/images/herbs/{herb_slug}-illustation.jpg'
    if not os.path.exists(images_validated_filepath):
        prompt = f'''
            {herb_name_scientific} plant,
            botanical illustration,
            drawing,
            watercolor
        '''
        print(prompt)
        pipe_init()
        image = pipe(prompt=prompt, width=1024, height=1024, num_inference_steps=30, guidance_scale=7.0).images[0]
        image = img_resize(image, w=768, h=768)
        image.save(images_to_validate_filepath)

