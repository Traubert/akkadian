import sys, os

columns_comment = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n"

conservative = False

logfilename = "/dev/null"
readdirpath = sys.argv[1]
writedirpath = sys.argv[2]
if len(sys.argv) > 3:
    logfilename = sys.argv[3]
log_fobj = open(logfilename, "w")

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
    log_fobj.write("Converting {}\n".format(name))
#    write_fobj.write(columns_comment)
    sent_num = 1
#    lines = list(filter(not_comment, read_fobj.readlines()))
    lines = read_fobj.readlines()
    sentences = split(lines, "\n")
    for sentence in sentences:
        log_fobj.write("Reading sentence {}".format(sentence[0]))
        head_ids = set()
        parent2children = {}
        heads = []
        splits = []

        def collect_children(root):
            collection = []
            for child in parent2children[root]:
                collection.append(child)
                if child in parent2children:
                    collection += collect_children(child)
            return collection
        
        for line in filter(not_comment, sentence):
            head = get_head(line)
            this_id = get_id(line)
            head_ids.add(head)
            if head not in parent2children:
                parent2children[head] = [this_id]
            else:
                parent2children[head].append(this_id)
        for i, line in enumerate(sentence):
            if not not_comment(line):
                continue
            if get_id(line) in head_ids and get_head(line) == '_':
                parts = line.split('\t')
                parts[6] = '0'
                parts[7] = 'root'
                parts[8] = '0:root'
                heads.append(get_id(line))
                sentence[i] = '\t'.join(parts)
        lastright = None
        for head in heads:
            children = list(map(int, collect_children(head)))
            leftmost = min(children + [int(head)])
            if lastright != None:
                if not conservative or leftmost == lastright + 1:
                    log_fobj.write("Inserting split at original id {}\n".format(lastright))
                    splits.append(lastright)
            lastright = max(children + [int(head)])
        write_fobj.write(apply_splits(list(map(lambda x: x.strip('\n'), sentence)), splits))
    log_fobj.write("\n")
#            print(leftmost, rightmost)
            

#    print(sentences)
        
def apply_splits(lines, splits):
    new_lines = []
    split = 0
    offset = 0
    for line in lines:
        if line.startswith('#'):
            new_lines.append(line)
            continue
        parts = line.split('\t')
        if len(parts) < 10:
            new_lines.append(line)
            continue
        if '-' in parts[0]:
            this_word_num = int(parts[0][:parts[0].index('-')])
        else:
            this_word_num = int(parts[0])
        if len(splits) > split and this_word_num > splits[split]:
            offset = splits[split]
            split += 1
            new_lines.append('')
        if '-' in parts[0]:
            start, stop = parts[0].split('-')
            part_0 = '{}-{}'.format(int(start) - offset, int(stop) - offset)
        else:
            part_0 = str(int(parts[0]) - offset)
        part_6 = parts[6]
        if part_6 != '_' and part_6 != '0':
            part_6 = str(int(parts[6]) - offset)
        if parts[8] != '_':
            new_parts = []
            old_parts = parts[8].split('|')
            for part in old_parts:
                firstcolon = part.index(':')
                target = part[:firstcolon]
                new_target = target
                if new_target != '0':
                    new_target = str(int(target) - offset)
                new_parts.append(new_target + part[firstcolon:])
            part_8 = '|'.join(new_parts)
        else:
            part_8 = '_'
        assert(part_0 and parts[1] and parts[3] and parts[4] and parts[5] and part_6 and parts[7] and part_8 and parts[9])
        new_lines.append('\t'.join(
            (part_0,
             parts[1],
             '_',
             parts[3],
             parts[4],
             parts[5],
             part_6,
             parts[7],
             part_8,
             parts[9]
            )))
    return '\n'.join(new_lines)

for filename in os.listdir(readdirpath):
    if not filename.startswith("Q"):# or '_part_' in filename:
        continue
    name = filename[:7]
    readpath = os.path.realpath(os.path.join(readdirpath, filename))
    writepath = os.path.realpath(os.path.join(writedirpath, filename))
    convert_file(name, open(readpath), open(writepath, 'w'))
    print(writepath)
    
