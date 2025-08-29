from lib import io
from llama_cpp import Llama

from lib import utils

llm = None
def reply(prompt, model_filepath=''):
    global llm
    if model_filepath == '':
        model_filepath = '/home/ubuntu/vault-tmp/llm/Qwen3-8B-Q4_K_M.gguf'
    if llm == None:
        llm = Llama(
              model_path=model_filepath,
              n_gpu_layers=-1, # Uncomment to use GPU acceleration
              # seed=1337, # Uncomment to set a specific seed
              n_ctx=4096, # Uncomment to increase the context window
        )
    chat_history = []
    chat_history.append({'role': 'user', 'content': prompt})
    stream = llm.create_chat_completion(
        messages = chat_history,
        stream=True,
        temperature=0.8,
    )
    llm_response = ''
    for piece in stream:
        if 'content' in piece['choices'][0]['delta'].keys():
            response_piece = piece['choices'][0]['delta']['content']
            llm_response += response_piece
            print(response_piece, end='', flush=True)
    return llm_response

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
                reply = llm_reply(prompt, model_filepath=model_filepath).strip()
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
