'''
For each line of parsed WordNet files, send it to MongoDB
'''

import wordnet_to_dict as WN
from pymongo import MongoClient

CLIENT = MongoClient()

#User defined area---------
WORDNET_DIR = "dict"
DATABASE_NAME = 'wordnet'
#--------------------------
'''
kwargs_from_file_reading are kwargs sent by the iterator that 
reads the file line per line, kwargs are from file constructor
kwargs_from_file_reading is mainly used to know in which line
we are 
'''
def to_mongo(line, kwargs, kwargs_from_file_reading):
    """Inserts a new object into kwargs['collection_name'] database"""
    file_name = kwargs['original_file_name']
    collection_name = kwargs['collection_name']
    if 'index' in file_name: #if it's an index file
    #We pop the counters as we don't need them in json
        line.pop('p_cnt', None)
        line.pop('synset_cnt', None)
        line.pop('sense_cnt', None)
        line.pop('tagsense_cnt', None)
    if 'data' in file_name and 'wn-' not in file_name:
    #if it's a data file but not a wn-lang-data... file
        line.pop('w_cnt', None)
        line.pop('p_cnt', None)
        line.pop('sense_cnt', None)
        line.pop('tagsense_cnt', None)
    CLIENT[DATABASE_NAME][collection_name].insert_one(line)

def replace_point_with_underline(string):
    return string.replace('.', '_')

print('working...\n')

#Takes care of index and data files

#erases collection in case you have written something there before
file_name = 'index.verb'
collection_name = replace_point_with_underline(file_name)
CLIENT[DATABASE_NAME].drop_collection(collection_name)
WN.for_each_line_of_file_do(WORDNET_DIR + '/' + file_name,
    WN.CallbackWrapper(to_mongo,
        original_file_name = file_name,
        collection_name = collection_name
    )
)


'''
#Takes care of MultiLingual files
language = 'pt'
file_name = 'wn-data-por.tab'
collection_name = language + '_' + replace_point_with_underline(file_name)
CLIENT[DATABASE_NAME].drop_collection(collection_name)
#WN.forEachLineOfFileDo(file_name, WN.CallbackWrapper(to_mongo, file_name, collection_name))
WN.forEachLineOfFileDo(file_name, 
    WN.CallbackWrapper(toMongo, 
        original_file_name = file_name, 
        collection_name = collection_name
    )
)
'''
