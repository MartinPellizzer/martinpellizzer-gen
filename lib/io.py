import os
import csv
import json

#######################
# ;folder
#######################

def folder_create(folderpath):
    chunks = folderpath.split('/')
    chunk_curr = ''
    for chunk in chunks:
        chunk_curr += chunk + '/'
        if not os.path.exists(chunk_curr):
            os.makedirs(chunk_curr)

def folder_create_from_filepath(filepath):
    chunks = filepath.split('/')
    chunk_curr = ''
    for chunk in chunks[:-1]:
        chunk_curr += chunk + '/'
        if not os.path.exists(chunk_curr):
            os.makedirs(chunk_curr)

#######################
# ;file
#######################

def file_read(path):
    with open(path) as f:
        content = f.read()
    return content

def file_append(path, text):
    with open(path, 'a') as f:
        f.write(text)

def file_write(path, text):
    with open(path, 'w') as f:
        f.write(text)

#######################
# ;json
#######################

def json_write(filepath, data):
    j = json.dumps(data, indent=4)
    with open(filepath, 'w') as f:
        print(j, file=f)

def json_read(filepath, create=False):
    if create:
        folder_create_from_filepath(filepath)
        if not os.path.exists(filepath):
            file_append(filepath, '')
        if file_read(filepath).strip() == '':
            file_append(filepath, '{}')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

#######################
# ;csv
#######################
def csv_read_rows(path, delimiter='\\'):
    rows = []
    with open(path, encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for line in reader:
                rows.append(line)
    return rows

def csv_to_dict(path, delimiter='\\', debug=False):
    rows = csv_read_rows(path, delimiter)
    if debug:
        print('#######################################')
        print('ALL: path')
        print('#######################################')
        print(rows)
    head = rows[0]
    body = rows[1:]
    if debug:
        print('#######################################')
        print('HEAD/BODY: path')
        print('#######################################')
        print(head)
        print(body)
    objects = []
    if debug:
        print('#######################################')
        print('HEAD/BODY: path')
        print('#######################################')
    for row in body:
        if debug:
            print(row)
        if row == []: continue
        obj = {}
        for i in range(len(head)):
            try: obj[head[i]] = row[i]
            except:
                print(row)
        objects.append(obj)
    return objects
