import json

from oliark_io import json_read, json_write
from oliark_llm import llm_reply

def ai_paragraph_gen(filepath, data, obj, key, prompt, regen=False, print_prompt=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        if print_prompt: print(prompt)
        reply = llm_reply(prompt)
        if reply.strip() != '':
            if reply.strip().startswith('I can\'t'): reply = 'N/A'
            elif reply.strip().startswith('I couldn\'t'): reply = 'N/A'
            elif 'cannot' in reply: return
            elif 'N/A' in reply: reply = 'N/A'
            obj[key] = reply
            json_write(filepath, data)

def gen_json_list(filepath, data, obj, key, prompt, regen=False, print_prompt=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        if print_prompt: print(prompt)
        reply = llm_reply(prompt)
        try: json_reply = json.loads(reply)
        except: json_reply = {}
        if json_reply != {}:
            outputs = []
            for item in json_reply:
                try: name = item['name'].strip().lower()
                except: continue
                try: desc = item['description'].strip().lower()
                except: continue
                if name.endswith('.'): name = name[:-1]
                outputs.append({
                    'name': name,
                    'desc': desc,
                })
            if outputs != []:
                obj[key] = outputs
                json_write(filepath, data)

def gen_json_list_base(filepath, data, obj, key, prompt, regen=False, print_prompt=False):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if obj[key] == '':
        if print_prompt: print(prompt)
        reply = llm_reply(prompt)
        try: json_reply = json.loads(reply)
        except: json_reply = {}
        if json_reply != {}:
            outputs = []
            for item in json_reply:
                try: name = item['name'].strip().lower()
                except: continue
                if name.endswith('.'): name = name[:-1]
                outputs.append({
                    'name': name,
                })
            if outputs != []:
                obj[key] = outputs
                json_write(filepath, data)

