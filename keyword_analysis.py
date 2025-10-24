import os
from pathlib import Path 

from lib import g
from lib import io

def word_cluster(keywords):
    keywords_density = []
    for i, k in enumerate(keywords[:20000]): 
        found = False
        keyword_list = k['Label'].split()
        for word in keyword_list:
            word.strip().lower()
            for keyword_density in keywords_density:
                if word == keyword_density['Label']:
                    keyword_density['mentions'] += 1
                    found = True
                    break
            if not found:
                keywords_density.append(
                    {
                        'Label': word,
                        'mentions': 1,
                    }
                )
    keywords_density = sorted(keywords_density, key=lambda x: int(x['mentions']), reverse=True)
    for k in keywords_density[:200]:
        print(k)
    keywords_export = '\n'.join(k['Label'] for k in keywords_density[:200])
    with open('keywords_density.txt', 'w') as f: f.write(keywords_export)

def keywords_get(folderpath, seed='', target_keyword='', keywords_num=1000, keywords_volume_min=0, keywords_volume_max=100000000, export_keywords=False):
    keywords_all = []
    results = list(Path(folderpath).rglob("*.csv"))
    for filepath in results:
        keywords_rows = io.csv_to_dict(filepath, ',')
        for k in keywords_rows:
            try: int(k['Search Volume'])
            except: continue
            keywords_all.append(k)
    keywords_rows = keywords_all
    keywords_rows = [
        k for k in keywords_all 
        if int(k['Search Volume']) >= keywords_volume_min and int(k['Search Volume']) <= keywords_volume_max
    ]
    if target_keyword == '':
        pass
    else:
        keywords_rows = [k for k in keywords_rows if target_keyword.lower() in k['Label'].lower()]
    keywords_rows = sorted(keywords_rows, key=lambda x: int(x['Search Volume']), reverse=True)
    keywords_no_dup = []
    keyword_prev = ''
    for keyword_row in keywords_rows:
        if keyword_row['Label'] == keyword_prev:
            continue
        else:
            keywords_no_dup.append(keyword_row)
            keyword_prev = keyword_row['Label']
    for keyword_row in keywords_no_dup[:keywords_num]:
        print(keyword_row['Search Volume'], keyword_row['Label'])
    print(len(keywords_no_dup))
    if export_keywords:
        keywords_export = '\n'.join(f'''{k['Search Volume']} {k['Label']}''' for k in keywords_no_dup[:keywords_num])
        with open('keywords_export.txt', 'w') as f: f.write(keywords_export)
    return keywords_no_dup
    
project = 'terrawhisper'
project = 'martinpellizzer'
base_foldername = f'herbal-medicine'
base_foldername = f''
target_keyword = ''
target_keyword = 'boho bedroom'
keywords_num = 1000
keywords_volume_min = 10000
keywords_volume_min = 1000000
keywords_volume_min = 100000
keywords_volume_min = 0
keywords_volume_max = 1000000
word_cluster_flag = 1
export_keywords = True
export_keywords = False

base_folderpath = f'{g.vault_folderpath}/{project}/database/keywords/pinterest-pinclicks/{base_foldername}'
print(base_folderpath)
keywords = keywords_get(base_folderpath, seed='', target_keyword=target_keyword, keywords_num=keywords_num, keywords_volume_min=keywords_volume_min, keywords_volume_max=keywords_volume_max, export_keywords=export_keywords)
if word_cluster_flag == True:
    word_cluster(keywords)
quit()

