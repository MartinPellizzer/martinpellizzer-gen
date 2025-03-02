import json

from oliark_llm import llm_reply

with open('database/keywords/herbal-teas-for.txt') as f:
    keywords_to_process = [line.strip() for line in f.read().split('\n') if line.strip() != '']

keywords_filtered = []
for keyword in keywords_to_process[:]:
    prompt = f'''
        Tell me if the following text include the name of an ailment: "{keyword}".
        Reply only with "YES" or "NO".
    '''
    reply = llm_reply(prompt)
    print(prompt)
    if 'yes' in reply.lower():
        prompt = f'''
            Extract a list of ailments from the following keyword: "{keyword}".
            If you don't find ailments in the keyword above, reply with an empty JSON list.
            If you find ailments in the keyword above, reply with the JSON format below:
            [
                {{"name": "enter name of ailment 1 found in keywor here"}},
                {{"name": "enter name of ailment 2 found in keywor here"}}
            ]
            Reply only with the JSON.
        '''
        reply = llm_reply(prompt)
        json_data = json.loads(reply)
        if json_data != []:
            for obj in json_data:
                try: name = obj['name']
                except: continue
                prompt = f'''
                    Tell me if the ailment "{name}" is included in the LIST below. Reply only with "YES" or "NO".
                    LIST:
                    {keywords_filtered}
                '''
                reply = llm_reply(prompt)
                print(prompt)
                if 'no' in reply.lower():
                    keywords_filtered.append(name.strip().lower())
    print()
    print()
    print()

for keyword in keywords_filtered:
    print(keyword)
