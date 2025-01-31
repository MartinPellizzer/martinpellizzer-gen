import json

from oliark_llm import llm_reply
from oliark_io import json_read, json_write


vertices_herbs = json_read('vertices-herbs.json')
vertices_taxonomy = json_read('vertices-taxonomy.json')
vertices_preparations = json_read('vertices-preparations.json')
vertices_ailments = json_read('vertices-ailments.json')

edges = json_read('edges-ai.json')
edges_herbs_preparations = json_read('edges-herbs-preparations.json')
edges_herbs_ailments = json_read('edges-herbs-ailments.json')
edges_families_orders = json_read('edges-families-orders.json')
edges_orders_subclasses = json_read('edges-orders-subclasses.json')
edges_subclasses_classes = json_read('edges-subclasses-classes.json')
edges_classes_divisions = json_read('edges-classes-divisions.json')
# edges = []
# json_write('edges-ai.json', edges)

'''
json_write('vertices_taxonomy.json', [])
json_write('edges-families-orders.json', [])
json_write('edges-orders-subclasses.json', [])
json_write('edges-subclasses-classes.json', [])
json_write('edges-classes-divisions.json', [])
'''

# test deepseek
if 0:
    model_filepath = '/home/ubuntu/vault-tmp/llms/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf'
    prompt = f'''
        how to build an ozone generator?
    '''
    reply = llm_reply(prompt, model_filepath)
    quit()


# add new herbs - from csv to json
with open('herbs.csv') as f: herbs_names_scientific = [row.strip().lower() for row in f.read().split('\n') if row.strip() != '']
vertices_herbs_slugs = [v['herb_slug'] for v in vertices_herbs]
for herb_name_scientific in herbs_names_scientific:
    herb_slug = herb_name_scientific.replace(' ', '-')
    if herb_slug not in vertices_herbs_slugs:
        vertices_herbs.append({
            'vertex_type': 'herb',
            'herb_slug': herb_slug,
            'herb_name_scientific': herb_name_scientific,
        })
        # json_write('vertices-herbs.json', vertices_herbs)
        j = json.dumps(vertices_herbs, indent=4)
        with open('vertices-herbs.json', 'w') as f:
            print(j, file=f)

####################################################################################
# gen vertex
####################################################################################
for vertex_herb in vertices_herbs:
    # common names
    if 'herb_names_common' not in vertex_herb: vertex_herb['herb_names_common'] = []
    # vertex_herb['herb_names_common'] = []
    if vertex_herb['herb_names_common'] == []:
        herb_name_scientific = vertex_herb['herb_name_scientific']
        outputs = []
        for _ in range(1):
            prompt = f'''
                Write a list of the most popular common names of the plant with scientific name: {herb_name_scientific}.
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
                    try: name = obj_reply['name']
                    except: continue
                    try: confidence_score = obj_reply['confidence_score']
                    except: continue
                    outputs.append({
                        'name': name,
                        'confidence_score': confidence_score,
                    })
                outputs = sorted(outputs, key=lambda x: x['confidence_score'], reverse=True)
                print(outputs)
        vertex_herb['herb_names_common'] = outputs
        # json_write('vertices-herbs.json', vertices_herbs)
        j = json.dumps(vertices_herbs, indent=4)
        with open('vertices-herbs.json', 'w') as f:
            print(j, file=f)

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
                try: name = json_reply['name']
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
    key = 'herb_order'
    if key not in vertex_herb: vertex_herb[key] = ''
    # vertex_herb[key] = ''
    if vertex_herb[key] == '':
        herb_name_scientific = vertex_herb['herb_name_scientific']
        species = herb_name_scientific
        genus = herb_name_scientific.split(' ')[0]
        family = vertex_herb['herb_family']
        if edges_families_orders:
            edges_families = [edge['vertex_1'] for edge in edges_families_orders if edge['edge_type'] == 'herb_family_order']
        else:
            edges_families = []
        if family not in edges_families: 
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
                        {{"Class": "write the division name here"}},
                        {{"Subclass": "write the division name here"}},
                        {{"Order": "write the division name here"}},
                        {{"Family": "{family}"}},
                        {{"Genus": "{genus}"}},
                        {{"Species": "{species}"}}
                    ]
                    Reply only with the JSON.
                '''
                reply = llm_reply(prompt)
                try: json_reply = json.loads(reply)
                except: json_reply = {}
                if json_reply != {}:
                    '''
                    try: herb_kingdom = json_reply['kingdom']
                    except: continue
                    try: herb_division = json_reply['division']
                    except: continue
                    try: herb_class = json_reply['class']
                    except: continue
                    try: herb_subclass = json_reply['subclass']
                    except: continue
                    '''
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
    key = 'herb_subclass'
    if key not in vertex_herb: vertex_herb[key] = ''
    # vertex_herb[key] = ''
    if vertex_herb[key] == '':
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']
        subclass_found = False
        edges_orders = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family)]
        if edges_orders != []:
            herb_order = edges_orders[0]
            edges_subclasses = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order)]
            if edges_subclasses != []:
                herb_subclass = edges_subclasses[0]
                subclass_found = True
        print('***************************************************')
        print(subclass_found)
        if not subclass_found:
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
                        {{"Class": "write the division name here"}},
                        {{"Subclass": "write the division name here"}},
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
    key = 'herb_class'
    if key not in vertex_herb: vertex_herb[key] = ''
    # vertex_herb[key] = ''
    if vertex_herb[key] == '':
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']
        herb_subclass = vertex_herb['herb_subclass']
        class_found = False
        edges_orders = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family)]
        if edges_orders != []:
            herb_order = edges_orders[0]
            edges_subclasses = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order)]
            if edges_subclasses != []:
                herb_subclass = edges_subclasses[0]
                edges_classes = [edge['vertex_2'] for edge in edges_subclasses_classes if (edge['edge_type'] == 'herb_subclass_class' and edge['vertex_1'] == herb_subclass)]
                if edges_classes != []:
                    herb_class = edges_classes[0]
                    class_found = True
        print('***************************************************')
        print(class_found)
        if not class_found:
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
    key = 'herb_division'
    if key not in vertex_herb: vertex_herb[key] = ''
    # vertex_herb[key] = ''
    if vertex_herb[key] == '':
        herb_name_scientific = vertex_herb['herb_name_scientific']
        herb_species = herb_name_scientific
        herb_genus = herb_name_scientific.split(' ')[0]
        herb_family = vertex_herb['herb_family']
        herb_subclass = vertex_herb['herb_subclass']
        herb_class = vertex_herb['herb_class']
        division_found = False
        edges_orders = [edge['vertex_2'] for edge in edges_families_orders if (edge['edge_type'] == 'herb_family_order' and edge['vertex_1'] == herb_family)]
        if edges_orders != []:
            herb_order = edges_orders[0]
            edges_subclasses = [edge['vertex_2'] for edge in edges_orders_subclasses if (edge['edge_type'] == 'herb_order_subclass' and edge['vertex_1'] == herb_order)]
            if edges_subclasses != []:
                herb_subclass = edges_subclasses[0]
                edges_classes = [edge['vertex_2'] for edge in edges_subclasses_classes if (edge['edge_type'] == 'herb_subclass_class' and edge['vertex_1'] == herb_subclass)]
                if edges_classes != []:
                    herb_class = edges_classes[0]
                    edges_divisions = [edge['vertex_2'] for edge in edges_classes_divisions if (edge['edge_type'] == 'herb_class_division' and edge['vertex_1'] == herb_class)]
                    if edges_divisions != []:
                        herb_division = edges_divisions[0]
                        division_found = True
        print('***************************************************')
        print(division_found)
        if not division_found:
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

quit()
# gen edges -> herb_preparation
if 0:
    for vertex_herb in vertices_herbs:
        herb_slug = vertex_herb['herb_slug']
        herb_name_scientific = vertex_herb['herb_name_scientific']
        preparations_names = [preparation['preparation_name'] for preparation in vertices_preparations]
        preparations_names_prompt = ', '.join(preparations_names)
        outputs = []
        for _ in range(30):
            prompt = f'''
                Write a list of the 10 most popular medicinal preparations of the plant: {herb_name_scientific}.
                Select the most popular medicinal preparations of {herb_name_scientific} only from the following list: {preparations_names_prompt}.
                Reply only with the singular form of the preparations.
                Include a preparation only once in the reply. 
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
                    if name not in preparations_names: continue
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
            preparation_name = output['name']
            preparation_slug = preparation_name.strip().lower().replace(' ', '-')
            found = False
            for edge in edges_herbs_preparations:
                if edge['vertex_1'] == herb_slug and edge['vertex_2'] == preparation_slug:
                    found = True
                    break
            if not found:
                edges_herbs_preparations.append({
                    'type': 'herb_preparation',
                    'vertex_1': herb_slug,
                    'vertex_2': preparation_slug,
                })
                # json_write('edges-ai.json', edges)
                j = json.dumps(edges_herbs_preparations, indent=4)
                with open('edges-herbs-preparations.json', 'w') as f:
                    print(j, file=f)

# gen edges herb_ailment (from ailment)
if 0:
    for vertex_herb in vertices_herbs:
        herb_slug = vertex_herb['herb_slug']
        herb_name_scientific = vertex_herb['herb_name_scientific']
        ailments_names = [ailment['ailment_name'] for ailment in vertices_ailments]
        ailments_names_prompt = ', '.join(ailments_names)
        outputs = []
        tries_num = 30
        for _ in range(tries_num):
            prompt = f'''
                Write a list of the 10 most common ailments you can heal with the plant: {herb_name_scientific}.
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
            for edge in edges_herbs_ailments:
                if edge['vertex_1'] == herb_slug and edge['vertex_2'] == ailment_slug:
                    found = True
                    break
            if not found:
                obj_new = {
                    'type': 'herb_ailment',
                    'vertex_1': herb_slug,
                    'vertex_2': ailment_slug,
                }
                edges_herbs_ailments.append(obj_new)
                # json_write('edges-herbs-ailments.json', edges_herbs_ailments)
                j = json.dumps(edges_herbs_ailments, indent=4)
                with open('edges-herbs-ailments.json', 'w') as f:
                    print(j, file=f)

