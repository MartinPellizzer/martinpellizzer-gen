import llm
import time

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

vault = f'/home/ubuntu/vault'
vault_tmp = f'/home/ubuntu/vault-tmp'

model_filepath = f'{vault_tmp}/llms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'
model_filepath = f'{vault_tmp}/llms/Qwen2.5-0.5B-Instruct.Q4_K_M.gguf'
model_filepath = f'{vault_tmp}/llms/Qwen2.5-1.5B-Instruct.Q4_K_M.gguf'
model_filepath = f'{vault_tmp}/llms/Qwen2.5-7B-Instruct.Q4_K_M.gguf'

vertices_plants = json_read(f'{vault}/herbalism/vertices-plants.json')
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

vertices_plants_filtered_tmp = [vertex for vertex in vertices_plants if vertex['plant_slug'] in plants_slugs_filtered] 
vertices_plants_filtered_tmp = sorted(vertices_plants_filtered_tmp, key=lambda x: x['plant_slug'], reverse=False)
# remove duplicates
vertices_plants_filtered = []

start_time = time.time()
for vertex_plant in vertices_plants_filtered_tmp[:10]:
    plant_name_scientific = vertex_plant['plant_name_scientific']
    prompt = f'''
        Write a short 4-sentence paragraph about {plant_name_scientific}.
        Include a definition of this plant.
        Include the health benefits of this plant.
        Include the bioactive constitiuents of this plant.
        Include the herbal preparations made with this plant.
        Start with the following words: {plant_name_scientific.capitalize()} is .
    '''

    reply = llm_reply(prompt, model_path=model_filepath)
print(f'--- {time.time() - start_time}')
