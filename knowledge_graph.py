import json
import random
import numpy

from oliark_llm import llm_reply
from oliark_io import json_read, json_write

vertices_herbs = json_read('vertices-herbs.json')
vertices_taxonomy = json_read('vertices-taxonomy.json')
vertices_preparations = json_read('vertices-preparations.json')
vertices_ailments = json_read('vertices-ailments.json')

edges = json_read('edges-ai.json')
'''
edges_families_orders = json_read('edges-families-orders.json')
edges_orders_subclasses = json_read('edges-orders-subclasses.json')
edges_subclasses_classes = json_read('edges-subclasses-classes.json')
edges_classes_divisions = json_read('edges-classes-divisions.json')
'''

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

####################################################################################
# gen vertex
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

'''
for vertex_plant in vertices_plants:
    plant_slug = vertex_plant['plant_slug']
    family_slug = vertex_plant['plant_family']
    if plant_slug not in plants_slugs_filtered: continue
    print(plant_slug, family_slug)
    plant_order = [edge['vertex_2'] for edge in edges_families_orders if edge['vertex_1'] == family_slug][0]
    print(plant_order)
    print()
'''


if 0:
    for vertex_herb in vertices_herbs:
        # family
        key = 'herb_family'
        if key not in vertex_herb: vertex_herb[key] = ''
        # vertex_herb[key] = ''
        if vertex_herb[key] == '':
            herb_name_scientific = vertex_herb['herb_name_scientific']
            outputs = []
            for _ in range(1):
                prompt = f'''
                    Write a the name of the taxonomical family of the plant with scientific name: {herb_name_scientific}.
                    Examples of taxonomical families are: asteraceae, araceae, etc...
                    Also give a confidence score from 1 to 10 for the answer, indicating how much you are sure about your answer.
                    If you don't know the answer, reply with the name "unknown".
                    Use as few words as possible.
                    Reply with the following JSON format:
                    {{"name": "write only the name here", "confidence_score": 8}}
                    Reply only with the JSON.
                '''
                reply = llm_reply(prompt)
                try: json_reply = json.loads(reply)
                except: json_reply = {}
                if json_reply != {}:
                    try: name = json_reply['name'].lower().strip()
                    except: continue
                    try: confidence_score = json_reply['confidence_score']
                    except: continue
                    vertex_herb[key] = {
                        'name': name,
                        'confidence_score': confidence_score,
                    }
                    j = json.dumps(vertices_herbs, indent=4)
                    with open('vertices-herbs.json', 'w') as f:
                        print(j, file=f)

    quit()
    ####################################################################################
    # gen taxonomy (vertices + edges)
    ####################################################################################
    # family vertices
    for vertex_herb in vertices_herbs:
        herbs_families = [vertex for vertex in vertices_taxonomy if vertex['vertex_type'] == 'herb_family']
        herbs_slugs = [vertex['family_slug'] for vertex in herbs_families]
        herb_family = vertex_herb['herb_family']
        if herb_family not in herbs_slugs:
            vertices_taxonomy.append({
                'vertex_type': 'herb_family',
                'family_slug': herb_family,
            })
            j = json.dumps(vertices_taxonomy, indent=4)
            with open('vertices-taxonomy.json', 'w') as f:
                print(j, file=f)

    for vertex_herb in vertices_herbs:
        # linnaean system -> order
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']['name']
        try: 
            herb_order = [edge['vertex_2'] for edge in edges_families_orders if edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family][0]
            continue
        except: pass
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write the Linnaean system of classification for the plant: {herb_name_scientific}.
                The Linnaean system is classified by: Kingdom, Division, Class, Subclass, Order, Family, Genus, Species.
                I will give you the Species, Genus, Family of this plant and you have to fill the rest. 
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"Kingdom": "write the kingdom name here"}},
                    {{"Division": "write the division name here"}},
                    {{"Class": "write the class name here"}},
                    {{"Subclass": "write the subclass name here"}},
                    {{"Order": "write the order name here"}},
                    {{"Family": "{herb_family}"}},
                    {{"Genus": "{herb_genus}"}},
                    {{"Species": "{herb_species}"}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                try: herb_kingdom = json_reply[0]['Kingdom'].strip().lower()
                except: continue
                try: herb_division = json_reply[1]['Division'].strip().lower()
                except: continue
                try: herb_class = json_reply[2]['Class'].strip().lower()
                except: continue
                try: herb_subclass = json_reply[3]['Subclass'].strip().lower()
                except: continue
                try: herb_order = json_reply[4]['Order'].strip().lower()
                except: continue
                try: herb_family = json_reply[5]['Family'].strip().lower()
                except: continue
                print('***************************************')
                edge_new = {
                    'edge_type': 'herb_family_order',
                    'vertex_1': herb_family,
                    'vertex_2': herb_order,
                }
                edges_families_orders.append(edge_new)
                j = json.dumps(edges_families_orders, indent=4)
                with open('edges-families-orders.json', 'w') as f:
                    print(j, file=f)
                vertices_taxonomy_orders_slugs = [vertex['order_slug'] for vertex in vertices_taxonomy if vertex['vertex_type'] == 'herb_order']
                if herb_order not in vertices_taxonomy_orders_slugs:
                    vertex_new = {
                        'vertex_type': 'herb_order',
                        'order_slug': herb_order,
                    }
                    vertices_taxonomy.append(vertex_new)
                    j = json.dumps(vertices_taxonomy, indent=4)
                    with open('vertices-taxonomy.json', 'w') as f:
                        print(j, file=f)

    for vertex_herb in vertices_herbs:
        # linnaean system -> subclass
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']['name']
        try:
            herb_order = [edge['vertex_2'] for edge in edges_families_orders if edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family][0]
        except: continue
        try: 
            herb_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order][0]
            continue
        except: pass
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write the Linnaean system of classification for the plant: {herb_name_scientific}.
                The Linnaean system is classified by: Kingdom, Division, Class, Subclass, Order, Family, Genus, Species.
                I will give you the Species, Genus, Family, Order of this plant and you have to fill the rest. 
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"Kingdom": "write the kingdom name here"}},
                    {{"Division": "write the division name here"}},
                    {{"Class": "write the class name here"}},
                    {{"Subclass": "write the subclass name here"}},
                    {{"Order": "{herb_order}"}},
                    {{"Family": "{herb_family}"}},
                    {{"Genus": "{herb_genus}"}},
                    {{"Species": "{herb_species}"}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                try: herb_kingdom = json_reply[0]['Kingdom'].strip().lower()
                except: continue
                try: herb_division = json_reply[1]['Division'].strip().lower()
                except: continue
                try: herb_class = json_reply[2]['Class'].strip().lower()
                except: continue
                try: herb_subclass = json_reply[3]['Subclass'].strip().lower()
                except: continue
                try: herb_order = json_reply[4]['Order'].strip().lower()
                except: continue
                try: herb_family = json_reply[5]['Family'].strip().lower()
                except: continue
                edge_new = {
                    'edge_type': 'herb_order_subclass',
                    'vertex_1': herb_order,
                    'vertex_2': herb_subclass,
                }
                edges_orders_subclasses.append(edge_new)
                j = json.dumps(edges_orders_subclasses, indent=4)
                with open('edges-orders-subclasses.json', 'w') as f:
                    print(j, file=f)
                vertices_slugs = [v['subclass_slug'] for v in vertices_taxonomy if v['vertex_type'] == 'herb_subclass']
                if herb_subclass not in vertices_slugs:
                    vertex_new = {
                        'vertex_type': 'herb_subclass',
                        'subclass_slug': herb_subclass,
                    }
                    vertices_taxonomy.append(vertex_new)
                    j = json.dumps(vertices_taxonomy, indent=4)
                    with open('vertices-taxonomy.json', 'w') as f:
                        print(j, file=f)

    for vertex_herb in vertices_herbs:
        # linnaean system -> class
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']['name']
        try:
            herb_order = [edge['vertex_2'] for edge in edges_families_orders if edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family][0]
        except: continue
        try: 
            herb_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order][0]
        except: continue
        try: 
            herb_class = [edge['vertex_2'] for edge in edges_subclasses_classes if edge['edge_type'] == 'herb_subclass_class' and edge['vertex_1'] == herb_subclass][0]
            continue
        except: pass
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write the Linnaean system of classification for the plant: {herb_name_scientific}.
                The Linnaean system is classified by: Kingdom, Division, Class, Subclass, Order, Family, Genus, Species.
                I will give you the Species, Genus, Family, Order, Subclass of this plant and you have to fill the rest. 
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"Kingdom": "write the kingdom name here"}},
                    {{"Division": "write the division name here"}},
                    {{"Class": "write the division name here"}},
                    {{"Subclass": "{herb_subclass}"}},
                    {{"Order": "{herb_order}"}},
                    {{"Family": "{herb_family}"}},
                    {{"Genus": "{herb_genus}"}},
                    {{"Species": "{herb_species}"}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                try: herb_kingdom = json_reply[0]['Kingdom'].strip().lower()
                except: continue
                try: herb_division = json_reply[1]['Division'].strip().lower()
                except: continue
                try: herb_class = json_reply[2]['Class'].strip().lower()
                except: continue
                try: herb_subclass = json_reply[3]['Subclass'].strip().lower()
                except: continue
                try: herb_order = json_reply[4]['Order'].strip().lower()
                except: continue
                try: herb_family = json_reply[5]['Family'].strip().lower()
                except: continue
                if 1:
                    edge_new = {
                        'edge_type': 'herb_subclass_class',
                        'vertex_1': herb_subclass,
                        'vertex_2': herb_class,
                    }
                    edges_subclasses_classes.append(edge_new)
                    j = json.dumps(edges_subclasses_classes, indent=4)
                    with open('edges-subclasses-classes.json', 'w') as f:
                        print(j, file=f)
                    vertices_slugs = [v['class_slug'] for v in vertices_taxonomy if v['vertex_type'] == 'herb_class']
                    if herb_class not in vertices_slugs:
                        vertex_new = {
                            'vertex_type': 'herb_class',
                            'class_slug': herb_class,
                        }
                        vertices_taxonomy.append(vertex_new)
                        j = json.dumps(vertices_taxonomy, indent=4)
                        with open('vertices-taxonomy.json', 'w') as f:
                            print(j, file=f)

    for vertex_herb in vertices_herbs:
        # linnaean system -> division
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']['name']
        try:
            herb_order = [edge['vertex_2'] for edge in edges_families_orders if edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family][0]
        except: continue
        try: 
            herb_subclass = [edge['vertex_2'] for edge in edges_orders_subclasses if edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order][0]
        except: continue
        try: 
            herb_class = [edge['vertex_2'] for edge in edges_subclasses_classes if edge['edge_type'] == 'herb_subclass_class' and edge['vertex_1'] == herb_subclass][0]
        except: continue
        try: 
            herb_division = [edge['vertex_2'] for edge in edges_classes_divisions if edge['edge_type'] == 'herb_class_division' and edge['vertex_1'] == herb_class][0]
            continue
        except: pass
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write the Linnaean system of classification for the plant: {herb_name_scientific}.
                The Linnaean system is classified by: Kingdom, Division, Class, Subclass, Order, Family, Genus, Species.
                I will give you the Species, Genus, Family, Order, Subclass, Class of this plant and you have to fill the rest. 
                Use as few words as possible.
                Reply with the following JSON format:
                [
                    {{"Kingdom": "write the kingdom name here"}},
                    {{"Division": "write the division name here"}},
                    {{"Class": "{herb_class}"}},
                    {{"Subclass": "{herb_subclass}"}},
                    {{"Order": "{herb_order}"}},
                    {{"Family": "{herb_family}"}},
                    {{"Genus": "{herb_genus}"}},
                    {{"Species": "{herb_species}"}}
                ]
                Reply only with the JSON.
            '''
            reply = llm_reply(prompt)
            try: json_reply = json.loads(reply)
            except: json_reply = {}
            if json_reply != {}:
                try: herb_kingdom = json_reply[0]['Kingdom'].strip().lower()
                except: continue
                try: herb_division = json_reply[1]['Division'].strip().lower()
                except: continue
                try: herb_class = json_reply[2]['Class'].strip().lower()
                except: continue
                try: herb_subclass = json_reply[3]['Subclass'].strip().lower()
                except: continue
                try: herb_order = json_reply[4]['Order'].strip().lower()
                except: continue
                try: herb_family = json_reply[5]['Family'].strip().lower()
                except: continue
                if 1:
                    edge_new = {
                        'edge_type': 'herb_class_division',
                        'vertex_1': herb_class,
                        'vertex_2': herb_division,
                    }
                    edges_classes_divisions.append(edge_new)
                    j = json.dumps(edges_classes_divisions, indent=4)
                    with open('edges-classes-divisions.json', 'w') as f:
                        print(j, file=f)
                    vertices_slugs = [v['division_slug'] for v in vertices_taxonomy if v['vertex_type'] == 'division_class']
                    if herb_division not in vertices_slugs:
                        vertex_new = {
                            'vertex_type': 'herb_division',
                            'division_slug': herb_division,
                        }
                        vertices_taxonomy.append(vertex_new)
                        j = json.dumps(vertices_taxonomy, indent=4)
                        with open('vertices-taxonomy.json', 'w') as f:
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
if 1:
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
if 1:
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
