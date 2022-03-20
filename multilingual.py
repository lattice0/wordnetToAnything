import urllib.request
import zipfile
import os

#User defined area---------
DIR = "multilingual_wordnets"
#--------------------------

languages = [
    'als', 'arb', 'bul', 'cmn', 'qcn', 'dan', 'ell',
    'eng', 'fas', 'fin', 'fra', 'heb', 'hrv', 'isl',
    'ita', 'ita', 'jpn' 'cat', 'eus', 'glg', 'spa',
    'ind', 'zsm', 'nld', 'nno', 'nob', 'pol', 'por',
    'ron', 'lit', 'slk', 'slv', 'swe', 'tha'
]

baseUrl = 'http://compling.hss.ntu.edu.sg/omw/wns/'

language = 'por'
fileName = language + '.zip'
file_path = DIR + "/" + fileName 
os.makedirs(os.path.dirname(file_path), exist_ok=True)
print('downloading '+fileName)
urllib.request.urlretrieve(baseUrl + language + '.zip', file_path)
print('extracting '+fileName)
with zipfile.ZipFile(file_path,"r") as zip_ref:
    zip_ref.extractall(DIR)