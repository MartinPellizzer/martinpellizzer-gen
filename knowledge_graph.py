import json
import random
import numpy

from oliark_llm import llm_reply
from oliark_io import json_read, json_write

import utils

vertices_plants_filepath = f'/home/ubuntu/vault/herbalism/vertices-plants.json'
vertices_plants = json_read(vertices_plants_filepath)
with open('herbs.csv') as f: 
    plants_slugs_filtered = [
        line.lower().strip().replace(' ', '-').replace('.', '') 
        for line in f.read().split('\n')
        if line.strip() != ''
]

edges_families_orders_filepath = f'/home/ubuntu/vault/herbalism/edges-families-orders.json'
edges_families_orders = json_read(edges_families_orders_filepath)
edges_orders_subclasses_filepath = f'/home/ubuntu/vault/herbalism/edges-orders-subclasses.json'
edges_orders_subclasses = json_read(edges_orders_subclasses_filepath)
edges_subclasses_classes_filepath = f'/home/ubuntu/vault/herbalism/edges-subclasses-classes.json'
edges_subclasses_classes = json_read(edges_subclasses_classes_filepath)
edges_classes_divisions_filepath = f'/home/ubuntu/vault/herbalism/edges-classes-divisions.json'
edges_classes_divisions = json_read(edges_classes_divisions_filepath)

edges_plants_preparations_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-preparations.json'
edges_plants_preparations = json_read(edges_plants_preparations_filepath)

edges_plants_ailments_filepath = f'/home/ubuntu/vault/herbalism/edges-plants-ailments.json'
edges_plants_ailments = json_read(edges_plants_ailments_filepath)

# edges = []
# json_write('edges-ai.json', edges)

vertices_ailments_filepath = f'/home/ubuntu/vault/herbalism/vertices-ailments.json'
vertices_ailments = json_read(vertices_ailments_filepath)

####################################################################################
# ailments
####################################################################################
def attr_list_gen(vertices_filepath, vertices, vertex, key, prompt, regen=False):
    if key not in vertex: vertex[key] = []
    if regen == True: vertex[key] = []
    if vertex[key] == []:
        outputs = []
        for _ in range(1):
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for item in json_reply:
                    try: name = item['name'].strip().lower()
                    except: continue
                    try: confidence_score = item['confidence_score']
                    except: continue
                    if name.endswith('.'): name = name[:-1]
                    outputs.append({
                        'name': name,
                        'confidence_score': confidence_score,
                    })
        outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
        for output in outputs:
            print(output)
        vertex[key] = outputs
        utils.json_write(vertices_filepath, vertices)

def ailments_add():
    with open('ailments.csv') as f: 
        ailments_names = [line for line in f.read().split('\n') if line.strip() != '']
    for ailment_name in ailments_names:
        ailment_slug = utils.sluggify(ailment_name)
        vertices_ailments_slugs = [vertex['ailment_slug'] for vertex in vertices_ailments]
        if ailment_slug not in vertices_ailments_slugs:
            vertices_ailments.append({
                'ailment_slug': ailment_slug,
                'ailment_name': ailment_name,
            })
            utils.json_write(vertices_ailments_filepath, vertices_ailments)

def ailment_teas_gen():
    vertices_plants_names_scientific = [vertex['plant_name_scientific'] for vertex in vertices_plants]
    for vertex_ailment in vertices_ailments:
        ailment_slug = vertex_ailment['ailment_slug']
        ailment_name = vertex_ailment['ailment_name']
        key = 'ailment_teas'
        if key not in vertex_ailment: vertex_ailment[key] = []
        # vertex_ailment[key] = []
        if vertex_ailment[key] == []:
            outputs = []
            for _ in range(10):
                n_items = random.randint(10, 20)
                prompt = f'''
                    Write a list of the {n_items} best herbal teas names to treat the {ailment_name} ailment.
                    Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
                    Always reply only with the scientific names of the plants used in the herbal teas. Never reply with common names.
                    Write as few words as possible.
                    Reply in JSON using the format below:
                    [
                        {{"name": "write name 1 here", "confidence_score": 10}},
                        {{"name": "write name 2 here", "confidence_score": 5}},
                        {{"name": "write name 3 here", "confidence_score": 7}}
                    ]
                    Reply only with the JSON.
                '''
                reply = llm_reply(prompt)
                try: json_reply = json.loads(reply)
                except: json_reply = {}
                if json_reply != {}:
                    for item in json_reply:
                        try: name = item['name'].strip().lower()
                        except: continue
                        try: confidence_score = item['confidence_score']
                        except: continue
                        for vertex_plant in vertices_plants:
                            plant_slug = vertex_plant['plant_slug']
                            plant_name_scientific = vertex_plant['plant_name_scientific']
                            if name == plant_name_scientific:
                                found = False
                                for output in outputs:
                                    if plant_slug == output['plant_slug']: 
                                        found = True
                                        output['confidence_score'] += confidence_score
                                        break
                                if not found:
                                    outputs.append({
                                        'plant_slug': plant_slug,
                                        'plant_name_scientific': plant_name_scientific,
                                        'confidence_score': confidence_score,
                                    })
                                break
            outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
            for output in outputs:
                print(output)
            vertex_ailment[key] = outputs[:20]
            utils.json_write(vertices_ailments_filepath, vertices_ailments)

ailments_add()
ailment_teas_gen()

####################################################################################
# plants
####################################################################################
for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    if 'plant_names_common' not in vertex_plant: vertex_plant['plant_names_common'] = []
    # vertex_plant['plant_names_common'] = []
    if vertex_plant['plant_names_common'] == []:
        plant_name_scientific = vertex_plant['plant_name_scientific']
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write a list of the most popular common names of the plant with scientific name: {plant_name_scientific}.
                Also give a confidence score from 1 to 10 for each list item, indicating how much you are sure about your answer.
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"name": "write name 1 here", "confidence_score": 10}},
                    {{"name": "write name 2 here", "confidence_score": 5}},
                    {{"name": "write name 3 here", "confidence_score": 7}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for obj_reply in json_reply:
                    try: name = obj_reply['name'].lower().strip()
                    except: continue
                    try: confidence_score = obj_reply['confidence_score']
                    except: continue
                    outputs.append({
                        'name': name,
                        'confidence_score': confidence_score,
                    })
                outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
                print(outputs)
        vertex_plant['plant_names_common'] = outputs
        j = json.dumps(vertices_plants, indent=4)
        with open(vertices_plants_filepath, 'w') as f:
            print(j, file=f)

def gen_vertex_plant_attr_list_json(vertex, key, prompt, regen=False):
    if key not in vertex_plant: vertex_plant[key] = []
    # vertex_plant[key] = []
    if regen == True: vertex_plant[key] = []
    if vertex_plant[key] == []:
        plant_name_scientific = vertex_plant['plant_name_scientific']
        outputs = []
        for _ in range(1):
            reply = llm_reply(prompt)
            print('###############################')
            print(plant_name_scientific)
            print('###############################')
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for item in json_reply:
                    try: name = item['name'].strip().lower()
                    except: continue
                    try: confidence_score = item['confidence_score']
                    except: continue
                    if name.endswith('.'): name = name[:-1]
                    outputs.append({
                        'name': name,
                        'confidence_score': confidence_score,
                    })
        outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
        for output in outputs:
            print(output)
        vertex_plant[key] = outputs
        j = json.dumps(vertices_plants, indent=4)
        with open(vertices_plants_filepath, 'w') as f:
            print(j, file=f)

##################################################################################
# attributes
##################################################################################
for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    plant_name_scientific = vertex_plant['plant_name_scientific']
    gen_vertex_plant_attr_list_json(
        vertex = vertex_plant,
        key = 'plant_benefits', 
        prompt = f'''
            Write a list of the 20 most important health benefits names of the plant {plant_name_scientific}.
            Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
            Start each benefit with a third-person singular action verb.
            Write as few words as possible.
            Reply in JSON using the format below:
            [
                {{"name": "write name 1 here", "confidence_score": 10}},
                {{"name": "write name 2 here", "confidence_score": 5}},
                {{"name": "write name 3 here", "confidence_score": 7}}
            ]
            Reply only with the JSON.
        ''',
        regen = False,
    )

for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    plant_name_scientific = vertex_plant['plant_name_scientific']
    gen_vertex_plant_attr_list_json(
        vertex = vertex_plant,
        key = 'plant_properties', 
        prompt = f'''
            Write a list of the 20 best therapeutic properties names of the plant {plant_name_scientific}.
            Examples of therapeutic properties are: antiseptic, antispasmodic, etc.
            Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
            Write as few words as possible.
            Reply in JSON using the format below:
            [
                {{"name": "write name 1 here", "confidence_score": 10}},
                {{"name": "write name 2 here", "confidence_score": 5}},
                {{"name": "write name 3 here", "confidence_score": 7}}
            ]
            Reply only with the JSON.
        ''',
        regen = False,
    )

for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    plant_name_scientific = vertex_plant['plant_name_scientific']
    gen_vertex_plant_attr_list_json(
        vertex = vertex_plant,
        key = 'plant_constituents', 
        prompt = f'''
            Write a list of the 20 most important medicinal constituents names of the plant {plant_name_scientific}.
            Examples of medicinal constituents are: tannins, flavonoids, etc.
            Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
            Write as few words as possible.
            Reply in JSON using the format below:
            [
                {{"name": "write name 1 here", "confidence_score": 10}},
                {{"name": "write name 2 here", "confidence_score": 5}},
                {{"name": "write name 3 here", "confidence_score": 7}}
            ]
            Reply only with the JSON.
        ''',
        regen = False,
    )

for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    plant_name_scientific = vertex_plant['plant_name_scientific']
    gen_vertex_plant_attr_list_json(
        vertex = vertex_plant,
        key = 'plant_parts', 
        prompt = f'''
            Write a list of the 20 most important parts names of the plant {plant_name_scientific} used for medicinal purposes.
            Examples of parts are: leaf, root, etc.
            Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
            Write as few words as possible.
            Reply in JSON using the format below:
            [
                {{"name": "write name 1 here", "confidence_score": 10}},
                {{"name": "write name 2 here", "confidence_score": 5}},
                {{"name": "write name 3 here", "confidence_score": 7}}
            ]
            Reply only with the JSON.
        ''',
        regen = False,
    )

for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    if plant_slug not in plants_slugs_filtered: continue
    plant_name_scientific = vertex_plant['plant_name_scientific']
    gen_vertex_plant_attr_list_json(
        vertex = vertex_plant,
        key = 'plant_side_effects', 
        prompt = f'''
            Write a list of the 20 most common negative health side effects names of the plant {plant_name_scientific}.
            Start each side effect with a third-person singular action verb.
            Also, write a confidence score from 1 to 10 for each list item, indicating how much sure you are about that answer.
            Write as few words as possible.
            Reply in JSON using the format below:
            [
                {{"name": "write name 1 here", "confidence_score": 10}},
                {{"name": "write name 2 here", "confidence_score": 5}},
                {{"name": "write name 3 here", "confidence_score": 7}}
            ]
            Reply only with the JSON.
        ''',
        regen = False,
    )

# gen edges -> herb_preparation
if 0:
    for vertex_plant in vertices_plants:
        plant_slug = vertex_plant['plant_slug']
        if plant_slug not in plants_slugs_filtered: continue
        plant_slug = vertex_plant['plant_slug']
        plants_slugs = [edge['vertex_1'] for edge in edges_plants_preparations]
        if plant_slug in plants_slugs: continue
        plant_name_scientific = vertex_plant['plant_name_scientific']
        preparations_names = [vertex['preparation_name'] for vertex in vertices_preparations]
        preparations_names_prompt = ', '.join(preparations_names)
        outputs = []
        tries_num = 30
        for _ in range(tries_num):
            prompt = f'''
                Write a list of the 10 most popular medicinal preparations of the plant: {plant_name_scientific}.
                Select the most popular medicinal preparations of {plant_name_scientific} only from the following list: {preparations_names_prompt}.
                Also, write a confidence score from 1 to 10 for each preparation, indicating how sure you are about that answer.
                Reply only with the singular form of the preparations.
                Include a preparation only once in the reply. 
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"name": "write name 1 here", "confidence_score": 10}},
                    {{"name": "write name 2 here", "confidence_score": 5}},
                    {{"name": "write name 3 here", "confidence_score": 7}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for item_reply in json_reply:
                    try: name = item_reply['name'].strip().lower()
                    except: continue
                    try: confidence_score = int(item_reply['confidence_score'])
                    except: continue
                    if name not in preparations_names: continue
                    found = False
                    for output in outputs:
                        if output['name'] == name:
                            output['confidence_score'] += confidence_score
                            output['mentions'] += 1
                            output['confidence_score_avg'] = output['confidence_score'] / output['mentions']
                            found = True
                            break
                    if not found:
                        outputs.append({
                            'name': name, 
                            'confidence_score': confidence_score, 
                            'mentions': 1,
                            'confidence_score_avg': confidence_score / 1,
                        })
        outputs = sorted(outputs, key=lambda x: x['confidence_score_avg'], reverse=True)
        for output in outputs:
            print(output)
        for output in outputs[:]:
            preparation_name = output['name']
            edge_strength_percentage = int(output['confidence_score_avg'] * 10)
            preparation_slug = preparation_name.strip().lower().replace(' ', '-')
            found = False
            for edge in edges_plants_preparations:
                if edge['vertex_1'] == plant_slug and edge['vertex_2'] == preparation_slug:
                    found = True
                    break
            if not found:
                edges_plants_preparations.append({
                    'edge_type': 'plant_preparation',
                    'vertex_1': plant_slug,
                    'vertex_2': preparation_slug,
                    'edge_strength': edge_strength_percentage,
                })
                # json_write('edges-ai.json', edges)
                j = json.dumps(edges_plants_preparations, indent=4)
                with open(edges_plants_preparations_filepath, 'w') as f:
                    print(j, file=f)

# gen edges herb_ailment (from ailment)
if 0:
    for vertex_plant in vertices_plants:
        plant_slug = vertex_plant['plant_slug']
        if plant_slug not in plants_slugs_filtered: continue
        plant_slug = vertex_plant['plant_slug']
        plants_slugs = [edge['vertex_1'] for edge in edges_plants_ailments]
        if plant_slug in plants_slugs: continue
        plant_name_scientific = vertex_plant['plant_name_scientific']
        ailments_names = [ailment['ailment_name'] for ailment in vertices_ailments]
        ailments_names_prompt = ', '.join(ailments_names)
        outputs = []
        tries_num = 30
        for _ in range(tries_num):
            prompt = f'''
                Write a list of the 10 most common ailments you can heal with the plant: {plant_name_scientific}.
                Select the most common ailments only from the following list: {ailments_names_prompt}.
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"name": "write name 1 here"}},
                    {{"name": "write name 2 here"}},
                    {{"name": "write name 3 here"}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                for item_reply in json_reply:
                    try: name = item_reply['name'].strip().lower()
                    except: continue
                    if name not in ailments_names: continue
                    found = False
                    for output in outputs:
                        if output['name'] == name:
                            output['mentions'] += 1
                            found = True
                            break
                    if not found:
                        outputs.append({'name': name, 'mentions': 1})
        outputs = sorted(outputs, key=lambda x: x['mentions'], reverse=True)
        for output in outputs:
            print(output)
        for output in outputs[:11]:
            ailment_mentions = output['mentions']
            if ailment_mentions < tries_num/2: continue
            ailment_name = output['name']
            ailment_slug = ailment_name.strip().lower().replace(' ', '-')
            found = False
            for edge in edges_plants_ailments:
                if edge['vertex_1'] == plant_slug and edge['vertex_2'] == ailment_slug:
                    found = True
                    break
            if not found:
                obj_new = {
                    'type': 'plant_ailment',
                    'vertex_1': plant_slug,
                    'vertex_2': ailment_slug,
                }
                edges_plants_ailments.append(obj_new)
                j = json.dumps(edges_plants_ailments, indent=4)
                with open(edges_plants_ailments_filepath, 'w') as f:
                    print(j, file=f)

quit()
