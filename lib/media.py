from PIL import Image

from lib import g

pipe = None
checkpoint_filepath = f'{g.vault_tmp_folderpath}/stable-diffusion/juggernautXL_ragnarokBy.safetensors'

def resize(img, target_w, target_h):
    original_w, original_h = img.size
    scale = max(target_w / original_w, target_h / original_h)
    new_size = (int(original_w * scale), int(original_h * scale))

    resized_img = img.resize(new_size, Image.LANCZOS)
    
    left = (resized_img.width - target_w) // 2
    top = (resized_img.height - target_h) // 2
    right = left + target_w
    bottom = left + target_h

    cropped_img = resized_img.crop((left, top, right, bottom))

    return cropped_img

def image_gen(prompt, width, height, steps=20, cfg=3):
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
    image = pipe(prompt=prompt, width=width, height=height, num_inference_steps=steps, guidance_scale=cfg).images[0]
    return image

