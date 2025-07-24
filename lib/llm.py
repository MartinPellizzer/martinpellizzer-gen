from lib import io
from oliark_llm import llm_reply

from lib import utils

reply_errors = [
    '[CANT]',
    '[WRONG START]',
    '[SENTENCE NUM]',
]

def plants_corrections(reply):
    reply = reply.replace('Ferula asafoeteta', 'Ferula asafoetida')
    return reply

def paragraph_ai(filepath, data, obj, key, prompt, sentence_n='', reply_start='', regen=False, clear=False, print_prompt=False, model_filepath=''):
    if key not in obj: obj[key] = ''
    if regen: obj[key] = ''
    if clear: 
        obj[key] = ''
        io.json_write(filepath, data)
        return
    if obj[key] == '':
        for i in range(1): 
            if print_prompt: print(prompt)
            if model_filepath != '':
                reply = llm_reply(prompt, model_path=model_filepath).strip()
            else:
                reply = llm_reply(prompt).strip()
            if '</think>' in reply:
                reply = reply.split('</think>')[1].strip()
            reply = plants_corrections(reply)
            if reply != '':
                if reply.startswith('I can\'t'): reply = reply_errors[0] + ' ' + reply
                if reply.startswith('I couldn\'t'): reply = reply_errors[0] + ' ' + reply
                if reply.startswith('I cannot'): reply = reply_errors[0] + ' ' + reply
                else:
                    if reply_start != '':
                        reply_start = reply_start.strip()
                        if not reply.startswith(reply_start): 
                            print(f'########################################')
                            print(f'WRONG START')
                            print(f'########################################')
                            print(f'TARGET REPLY START: {reply_start}')
                            print(f'REPLY:              {reply[:40]}')
                            print(f'########################################')
                            reply = reply_errors[1] + ' ' + reply
                        elif sentence_n != '':
                            sentences = utils.text_to_sentences(reply)
                            if len(sentences) != sentence_n:
                                reply = reply_errors[2] + ' ' + reply
                                print(f'SENTENCE NUM ERR: {len(sentences)}/{sentence_n}')
                                print(f'{sentences}')
                obj[key] = reply
                io.json_write(filepath, data)
                break
