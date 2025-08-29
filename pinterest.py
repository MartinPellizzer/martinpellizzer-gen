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

def keywords_get(folderpath, keywords_num=1000, keywords_volume_min=100000):
    keywords_all = []
    results = list(Path(folderpath).rglob("*.csv"))
    for filepath in results:
        keywords_rows = io.csv_to_dict(filepath, ',')
        for k in keywords_rows:
            try: int(k['Search Volume'])
            except: continue
            keywords_all.append(k)
    keywords_rows = keywords_all
    keywords_rows = [k for k in keywords_all if int(k['Search Volume']) >= keywords_volume_min]
    keywords_rows = sorted(keywords_rows, key=lambda x: int(x['Search Volume']), reverse=True)
    keywords_export = '\n'.join(k['Label'] for k in keywords_rows[:keywords_num])
    with open('keywords_export.txt', 'w') as f: f.write(keywords_export)
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
        # print(keyword_row['Label'])
    print(len(keywords_no_dup))
    return keywords_no_dup
    
folderpath = f'{g.vault_folderpath}/martinpellizzer/database/keywords/pinterest-pinclicks/03 flowers/types/sunflower'
terrawhisper_folderpath = f'{g.vault_folderpath}/terrawhisper/database/keywords/pinterest-pinclicks/herbalism'
keywords = keywords_get(terrawhisper_folderpath, keywords_num=10000, keywords_volume_min=50000)
# word_cluster(keywords)
quit()

def keywords_get(folderpath='', foldername='', seed=''):
    keywords_all = []
    folderpath_00 = f'{g.vault_folderpath}/martinpellizzer/database/keywords/pinterest-pinclicks/{folderpath}'
    if foldername == '':
        for foldername_00 in os.listdir(folderpath_00):
            folderpath_01 = f'{folderpath_00}/{foldername_00}'
            for filename_01 in os.listdir(folderpath_01):
                filepath = f'{folderpath_01}/{filename_01}'
                if seed == '':
                    keywords_rows = io.csv_to_dict(filepath, ',')
                    for k in keywords_rows:
                        try: int(k['Search Volume'])
                        except: continue
                        keywords_all.append(k)
                else:
                    if seed in filename_01:
                        keywords_rows = io.csv_to_dict(filepath, ',')
                        for k in keywords_rows:
                            try: int(k['Search Volume'])
                            except: continue
                            keywords_all.append(k)
    else:
        folderpath_01 = f'{folderpath_00}/{foldername}'
        for filename_01 in os.listdir(folderpath_01):
            filepath = f'{folderpath_01}/{filename_01}'
            if seed == '':
                keywords_rows = io.csv_to_dict(filepath, ',')
                for k in keywords_rows:
                    try: int(k['Search Volume'])
                    except: continue
                    keywords_all.append(k)
            else:
                if seed in filename_01:
                    keywords_rows = io.csv_to_dict(filepath, ',')
                    for k in keywords_rows:
                        try: int(k['Search Volume'])
                        except: continue
                        keywords_all.append(k)
    keywords_rows = keywords_all
    keywords_rows = [k for k in keywords_all if int(k['Search Volume']) >= 100000]
    keywords_rows = sorted(keywords_rows, key=lambda x: int(x['Search Volume']), reverse=True)
    for keyword_row in keywords_rows[:1000]:
        print(keyword_row['Search Volume'], keyword_row['Label'])
        # print(keyword_row['Label'])
    print(len(keywords_rows))
    keywords_export = '\n'.join(k['Label'] for k in keywords_rows[:1000])
    with open('keywords_export.txt', 'w') as f: f.write(keywords_export)
    return keywords_rows

keywords = keywords_get(folderpath='03 flowers', foldername='dahlia', seed='')

quit()

