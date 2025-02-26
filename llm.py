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
