'''
For each line of parsed WordNet files, save it as a new json element  
'''

import wordnet_to_dict as WN
import json
import os

#User defined area---------
DIR = "json_files"
WORDNET_DIR = "dict"
#--------------------------

'''
kwargs_from_file_reading are kwargs sent by the iterator that 
reads the file line per line, kwargs are from file constructor
kwargs_from_file_reading is mainly used to know in which line
we are 
'''

def to_json(line, kwargs, kwargs_from_file_reading):
    """Inserts a new line into kwargs['file_object'] file object"""
    original_file_name = kwargs['original_file_name']
    file_object = kwargs['file_object']
    is_first_line = kwargs_from_file_reading['is_first_line']
    if 'index' in original_file_name: #if it's an index file
    #We pop the counters as we don't need them in json
        line.pop('p_cnt', None)
        line.pop('synset_cnt', None)
        line.pop('sense_cnt', None)
        line.pop('tagsense_cnt', None)
    if 'data' in original_file_name and 'wn-' not in original_file_name:
    #if it's a data file but not a wn-lang-data... file
        line.pop('w_cnt', None)
        line.pop('p_cnt', None)
        line.pop('sense_cnt', None)
        line.pop('tagsense_cnt', None)
    comma = ''
    if not is_first_line: 
        comma = ','
    new_line = '\n'
    #if not firstLine, change comma
    file_object.write(comma + new_line + json.dumps(line))

print('working...\n')

#Takes care of index and data files
for file_name in list(set(WN.META.index_files) | set(WN.META.data_files)):
    original_file_name = file_name
    new_file_name = original_file_name + '.json'
    print('parsing ' + file_name + ' to ' + new_file_name + '...')
    path = DIR + '/' + new_file_name
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('[')
        WN.for_each_line_of_file_do(WORDNET_DIR + '/' + original_file_name,
            WN.CallbackWrapper(to_json,
                original_file_name = original_file_name,
                file_object = f
            )
        )
        f.write(']')

#Takes care of data files

'''
#Takes care of MultiLingual files
language = 'pt'
fileName = 'wn-data-por.tab'
collectionName = language + '_' + replacePointWithUnderscore(fileName)
client[databaseName].drop_collection(collectionName)
WN.forEachLineOfFileDo(fileName, WN.CallbackWrapper(to_json, fileName, collectionName))
'''
