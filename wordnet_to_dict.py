'''
Parses the WordNet files and returns a dictionary of tokens for each line
'''
import json
import wordnet_metadata as META
import os

c = 0
max = 50

#Strips the new line character
def clean_line(line):
    line = line.strip('\n')
    return line

#Checks if line is WordNet comment
def is_comment(line):
    if line[0] == ' ' or line[0] == '#': #Comments start with empty space
        return True
    else:
        return False

def remove_whitespace_at_end(line):
    cleaner_line = line
    max = 5
    counter = 0
    while cleaner_line[len(cleaner_line)-1] == ' ':
        cleaner_line = cleaner_line[:-1]
        counter += 1
        if counter >= max:
            break
    return cleaner_line

#https://wordnet.princeton.edu/wordnet/man/wndb.5WN.html#toc2
class Index(object):
    """Container for static methods that deal with index.something files"""
    @staticmethod
    def parse(line):
        """Parses the line by breaking into tokens and returns a dictionary"""
        tokens = remove_whitespace_at_end(line).split(' ')
        lemma = tokens[0]
        pos = tokens[1]
        synset_cnt = int(tokens[2])
        p_cnt = int(tokens[3])
        ptr_symbols = ''
        synset_offsets = ''
        if p_cnt > 0:
            ptr_symbols = tokens[4:4+p_cnt]
        sense_cnt = tokens[4+p_cnt]
        tagsense_cnt = tokens[5+p_cnt]
        synset_offset_start = 6 + p_cnt
        if synset_cnt > 0:
            synset_offsets = tokens[synset_offset_start:synset_offset_start + synset_cnt]
        return {
            'lemma': lemma,
            'pos': pos,
            'synset_cnt': synset_cnt,
            'p_cnt': p_cnt,
            'pointers': ptr_symbols,
            'sense_cnt': sense_cnt,
            'tagsense_cnt': tagsense_cnt,
            'synset_offsets': synset_offsets
        }

#https://wordnet.princeton.edu/wordnet/man/wndb.5WN.html#toc3
class Data(object):
    """Container for static methods that deal with data.something files"""
    @staticmethod 
    def get_gloss(line):
        """Returns the gloss, which is the text after the pipe"""
        return line.split(' | ')[1]
    @staticmethod 
    def remove_gloss(line):
        """Removes the gloss"""
        return line.split(' | ')[0] + ' |' #Puts the pipe back in
    @staticmethod
    def parse(line):
        """Parses the line by breaking into tokens and returns a dictionary"""
        gloss = Data.get_gloss(line)
        tokens = Data.remove_gloss(remove_whitespace_at_end(line)).split(' ')
        synset_offset = tokens[0]
        lex_filenum = tokens[1]
        ss_type = tokens[2]
        w_cnt = tokens[3]
        #find the list [word1, lex_id1, word2, lex_id2, ...]
        words = tokens[4:4+2*int(w_cnt, 16)] #words come in pairs [word, lex_id], so we add 2*w_cnt
        #returns tuple [word, lex_id] from the list [word1, lex_id1, word2, lex_id2, ...]
        words = [{'word': words[0+n*2], 'lex_id': int(words[1+n*2], 16)} for n in range(int(len(words)/2))]
        p_cnt_index = 4+int(w_cnt, 16)*2
        p_cnt = tokens[p_cnt_index]
        #find the list [pointer1, pointer2, ...] where each pointer object is composed
        #of [pointer_symbol, synset_offset, pos, source_target]
        pointers = tokens[p_cnt_index+1:p_cnt_index+1+int(p_cnt)*4]
        #For all data.something we should have a pipe | now, but data.verb is an exception,
        #it has more data called frames
        possible_pipe_index = p_cnt_index +int(p_cnt)*4+1
        try:
            possible_pipe = tokens[possible_pipe_index]
        except Exception as e:
            print(str(e))
            print(line)
            print(tokens)
            print(possible_pipe_index)
            print(len(tokens))
        frames = []
        if not possible_pipe == '|':
            frame_counter = int(possible_pipe) #If it's not a pipe, it's a frame_counter
            frames = tokens[possible_pipe_index+1:possible_pipe_index+1+frame_counter*3]
            #removes the preceding '+' symbol in each new frame
            frames = [x for x in frames if x != "+"]
            #groups each frame in a list [f_num, w_num]
            frames = [{'f_num': frames[0+n*2], 'w_num': frames[1+n*2]} for n in range(int(len(frames)/2))]

        pointers = [
            {
                'pointer_symbol': pointers[0+n*4],
                'synset_offset': pointers[1+n*4],
                'pos': pointers[2+n*4],
                'source_target': pointers[3+n*4]
            }
            for n in range(int(len(pointers)/4))
        ]
        return {
            'synset_offset': synset_offset,
            'lex_filenum': lex_filenum,
            'ss_type': ss_type,
            'w_cnt': w_cnt,
            'words': words,
            'p_cnt': p_cnt,
            'ptrs': pointers,
            'frms': frames,
            'gloss': gloss
        }

#http://compling.hss.ntu.edu.sg/omw/
class MultilingualIndex(object):
    @staticmethod
    def parse(line):
        """Parses the line by breaking into tokens and returns a dictionary"""
        tokens = line.split("\t")
        synset_and_pos = tokens[0].split('-')
        synset_offset = synset_and_pos[0]
        pos = synset_and_pos[1]
        typ = tokens[1]
        word = tokens[2]
        return {
            'synset_offset': synset_offset,
            'pos': pos,
            'type': typ,
            'word': word
        }


class CallbackWrapper(object):
    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.kwargs = kwargs
    def execute(self, line, **extra):
        self.callback(line, self.kwargs, extra)


def get_file_name(path):
    return os.path.split(path)[1]

def for_each_line_of_file_do(file_path, wrapped_callback):
    """Executes function for each line of the file_path file"""
    c = 0
    first_line_never_reached = True
    with open(file_path) as fp:
        for line in fp:
            if not is_comment(line):
                line = clean_line(line)
                file_name = get_file_name(file_path)
                if file_name in META.index_files:
                    wrapped_callback.execute(Index.parse(line), is_first_line=first_line_never_reached)
                if file_name in META.data_files:
                    wrapped_callback.execute(Data.parse(line), is_first_line=first_line_never_reached)
                if file_name in META.multilingual_files:
                    wrapped_callback.execute(MultilingualIndex.parse(line), is_first_line=first_line_never_reached)
                first_line_never_reached = False
            c += 1
            if c > max:
                pass

