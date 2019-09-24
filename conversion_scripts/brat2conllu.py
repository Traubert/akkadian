import sys, re

UPOS_tags = ["ADJ",
             "ADP",
             "ADV",
             "AUX",
             "CCONJ",
             "DET",
             "INTJ",
             "NOUN",
             "NUM",
             "PART",
             "PRON",
             "PROPN",
             "PUNCT",
             "SCONJ",
             "SYM",
             "VERB",
             "X"]

arg1_re = re.compile(r'Arg1:(\S+)')
arg2_re = re.compile(r'Arg2:(\S+)')
token_re = re.compile(r'^T(\d+)')
token_anywhere_re = re.compile(r'T(\d+)')

first = lambda x: x[0]
second = lambda x: x[1]
third = lambda x: x[2]
fourth = lambda x: x[3]
fifth = lambda x: x[4]

def first_token(text):
    return int(first(token_re.search(text).groups()))

def token_line_to_token(line):
    token_num, token_info, token = line.strip().split('\t')
    pos, start, end = token_info.split(' ')
    assert(start != end)
    return (token, pos, token_num, int(start)-1, int(end)-1)

def attrib_line_to_attrib(line):
    attrib_num, attrib_info = line.strip().split('\t')
    key, token_num, value = attrib_info.split(' ')
    return (token_num, key, value)

def relation_line_to_relation(line):
    relation_num, relation_info = line.strip().split('\t')
    relation, arg1, arg2 = relation_info.split(' ')
    arg1 = arg1[5:]
    arg2 = arg2[5:]
    return (relation, arg1, arg2)

def comment_line_to_comment(line):
    comment_num, comment_info, comment = line.strip().split('\t')
    comment_type, token_num = comment_info.split(' ')
    return (token_num, comment)

def conllu_multitoken(i, tokens):
    ID = str(i+1) + '-' + str(i+len(tokens))
    FORM = ''.join(map(first, tokens))
    LEMMA = '_'
    UPOS = '_'
    XPOS = '_'
    FEATS = '_'
    HEAD = '_'
    DEPREL = '_'
    DEPS = '_'
    MISC = '_'
    return '\t'.join((ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC)) + '\n'

def line_is_token_line(line):
    return line.startswith('T') and len(line.strip().split('\t')) == 3

filename = sys.argv[1]
lines = open(filename).readlines()
name_prefix = filename[:filename.index('.ann')]
filename = name_prefix + '.txt'
try:
    running_text = open(filename, "r", encoding="utf-8").read()
except:
    exit()
breakpoints = [0]
for i, line in enumerate(lines):
    if line.startswith("BREAK"):
        nextline_tabparts = lines[i+1].split('\t')
        breakpoint = int(nextline_tabparts[1].split(' ')[1])
        breakpoints.append(breakpoint)
relations = list(map(relation_line_to_relation, filter(lambda x: x.startswith('R'), lines)))
tokens = list(map(token_line_to_token, filter(line_is_token_line, lines)))
attributes = list(map(attrib_line_to_attrib, filter(lambda x: x.startswith('A'), lines)))
comments = list(map(comment_line_to_comment, filter(lambda x: x.startswith('#'), lines)))
    
tokens.sort(key = fourth)
added_tokens = []
for i, token in enumerate(tokens):
    if i == 0:
        continue
    gap = fourth(token) - fifth(tokens[i-1])
    if gap > 1:
        # if running_text[fourth(token) - 1] != ' ':
        #     continue
#        print(running_text[fifth(tokens[i-1]):fourth(token)-1])
        start = fifth(tokens[i-1]) + 1
        stop = fourth(token) - 1
        new_tokens = running_text[start:stop].split(" ")
#        print("#" + running_text[start:stop] + "#")
#        print(new_tokens)
        for j, new_token in enumerate(new_tokens):
            added_tokens.append((new_token, "_", "T-1", start, start + len(new_token)))
            start += len(new_token) + 1
tokens = sorted(tokens + added_tokens, key = fourth)
token_nums = list(map(third, tokens))
queued_tokens = []
queued_token_lines = ""
i_ = 0

#print(breakpoints)

for part, breakpoint in enumerate(breakpoints):
    if len(breakpoints) == 1:
        write_file = open(name_prefix + "_conllu.txt", 'w', encoding = 'utf-8')
        print(name_prefix + "_conllu.txt")
    else:
        write_file = open(name_prefix + "_part_" + str(1 + part) + "_conllu.txt", "w", encoding = 'utf-8')
    for i, token in enumerate(tokens):
        if fourth(token) < breakpoint:
            continue
        if part + 1 != len(breakpoints) and fourth(token) > breakpoints[part+1]:
            continue
#        if first(token) != running_text[fourth(token)-1:fifth(token)-1]:
#            print(first(token) + "#" + running_text[fourth(token)-1:fifth(token)-1])
        if first(token) == '':
            continue
        if i == 0:
            queued_tokens = [token]
        else:
            if fourth(token) == fifth(tokens[i-1]):
                # this begins where previous ended
                queued_tokens.append(token)
            else:
                if len(queued_tokens) > 1:
                    write_file.write(conllu_multitoken(i_, queued_tokens))
                write_file.write(queued_token_lines)
                queued_tokens = [token]
                i_ = i
                queued_token_lines = ""
        token_num = third(token)
        ID = str(i+1)
        FORM = first(token)
        LEMMA = '_'#first(token)
        pos = second(token)
        XPOS = pos
        # if pos in UPOS_tags or pos == '_':
        #     UPOS = pos
        # else:
        #     UPOS = "X"
        UPOS = '_'
        FEATS = "|".join(map(lambda y: second(y) + '=' + third(y), filter(lambda x: token_num == first(x), attributes)))
        if len(FEATS) == 0:
            FEATS = "_"
        this_as_child = list(filter(lambda x: third(x) == token_num, relations))
        if len(this_as_child) == 0:
            HEAD = "_"
        else:
            headrelation = this_as_child[0]
            HEAD = str(token_nums.index(second(headrelation)) + 1)
        DEPS = '_'
        if HEAD == '_':
            DEPREL = '_'
        else:
            DEPREL = first(headrelation)
            if len(this_as_child) > 1:
                DEPS = '|'.join(map(lambda x: str(token_nums.index(second(x)) + 1) + ':' + first(x), this_as_child))
        this_comments = list(filter(lambda x: first(x) == token_num, comments))
        if len(this_comments) == 0:
            MISC = '_'
        else:
            MISC = this_comments[0][1]
        queued_token_lines += '\t'.join((ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC)) + '\n'
        if i == len(tokens) - 1:
            if len(queued_tokens) > 1:
                write_file.write(conllu_multitoken(i_, queued_tokens))
            write_file.write(queued_token_lines)
    write_file.close()

