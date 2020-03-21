import sys, os

columns_comment = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n"

readdirpath = sys.argv[1]
writedirpath = sys.argv[2]

def split(l, val):
    retval = []
    curlist = []
    for item in l:
        if item == val:
            retval.append(curlist)
            curlist = []
        else:
            curlist.append(item)
    if len(curlist) > 0:
        retval.append(curlist)
    return retval

def not_comment(line):
    return not line.lstrip().startswith("#")

def get_head(line):
    return line.split('\t')[6]
def get_id(line):
    return line.split('\t')[0]

def convert_file(name, read_fobj, write_fobj):
    write_fobj.write(columns_comment)
    sent_num = 1
    lines = list(filter(not_comment, read_fobj.readlines()))
    sentences = split(lines, "\n")
    for sentence in sentences:
        head_ids = set()
        parent2children = {}
        heads = []
        for line in sentence:
            head = get_head(line)
            this_id = get_id(line)
            head_ids.add(head)
            if head not in parent2children:
                parent2children[head] = [this_id]
            else:
                parent2children[head].append(this_id)
        for i, line in enumerate(sentence):
            if get_id(line) in head_ids and get_head(line) == '_':
                parts = line.split('\t')
                parts[6] = '0'
                parts[7] = 'root'
                parts[8] = '0:root'
                heads.append(get_id(line))
            sentence[i] = parts.join('\t')
            
            
    print(sentences)
        

for filename in os.listdir(readdirpath):
    if not filename.startswith("Q"):# or '_part_' in filename:
        continue
    name = filename[:7]
    readpath = os.path.realpath(os.path.join(readdirpath, filename))
    writepath = os.path.realpath(os.path.join(writedirpath, filename))
    convert_file(name, open(readpath), open(writepath, 'w'))
    print(writepath)
    
