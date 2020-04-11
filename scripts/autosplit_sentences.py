import sys, os

from akkadian import *

conservative = False

logfilename = "/dev/null"
readdirpath = sys.argv[1]
writedirpath = sys.argv[2]
if len(sys.argv) > 3:
    logfilename = sys.argv[3]
log_fobj = open(logfilename, "w")

def not_comment(line):
    return not line.lstrip().startswith("#")

def get_head(line):
    return line.split('\t')[6]
def get_id(line):
    return line.split('\t')[0]

def convert_file(name, read_fobj, write_fobj):
    log_fobj.write("Autosplitting {}\n".format(name))
    write_fobj.write(columns_comment)
    sent_num = 1
    lines = read_fobj.readlines()
#    non_comment_lines = list(filter(not_comment, lines))
    sentences = split(lines, "\n")
    for sentence in sentences:
        non_comment_line_parts = list(map(lambda x: x.split('\t'), filter(line_is_wordtoken, sentence)))
        if sentence[0].startswith("# sent_id = "):
            sentence_id = sentence[0]
        else:
            sentence_id = sentence[1]
        log_fobj.write("\n  Reading original sentence {}".format(sentence_id))
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
            if not line_is_wordtoken(line):
                continue
            if get_id(line) in head_ids and get_head(line) == '_':
                parts = line.split('\t')
                parts[6] = '0'
                parts[7] = 'root'
                parts[8] = '0:root'
                heads.append(get_id(line))
                sentence[i] = '\t'.join(parts)
        lastright = None
        assigned_ids = set()
        for head in heads:
            made_split = False
            children = list(map(int, collect_children(head)))
            leftmost = min(children + [int(head)])
            rightmost = max(children + [int(head)])
            log_fobj.write("    Apparent sentence root {}: leftmost node was {}, rightmost node was {}\n".format(head, leftmost, rightmost))
            if lastright != None:
                if not conservative or leftmost == lastright + 1:
                    log_fobj.write("      Trying to insert split at original id {}...".format(rightmost))
                    splits.append(lastright)
                    made_split = True
            this_range = set(range(leftmost, rightmost + 1))
            if made_split and not assigned_ids.isdisjoint(this_range):
#                print(non_comment_line_parts)
                this_tree_surfaces = filter(lambda x: ('-' not in x[0]) and (int(x[0]) in this_range), non_comment_line_parts)
                log_fobj.write(" OVERLAPPING TREE, so not splitting:\n")
                log_fobj.write("          ...{}...\n".format(' '.join(map(lambda x: x[1], this_tree_surfaces))))
                splits.pop()
                continue
            elif made_split:
                log_fobj.write(" ok\n")
            lastright = rightmost
            assigned_ids.update(this_range)
        log_fobj.write(f"{sorted(splits)}")
        for new_sentence, new_surface in apply_splits(list(map(lambda x: x.strip('\n'), filter(not_comment, sentence))), sorted(splits)):
            log_fobj.write('# sent_id = {}-{}\n'.format(name, sent_num))
            write_fobj.write('# sent_id = {}-{}\n'.format(name, sent_num))
            write_fobj.write('# text = {}\n'.format(new_surface))
            sent_num += 1
            write_fobj.write('\n'.join(new_sentence)+'\n\n')
    log_fobj.write("\n")
#            print(leftmost, rightmost)
            

#    print(sentences)
        
def apply_splits(lines, splits):
    new_sentences = []
    new_texts = []
    this_text = []
    skip_surfaces_until = 0
    this_sentence = []
    split = 0
    offset = 0
    for line in lines:
        # if line.startswith('#'):
        #     new_lines.append(line)
        #     continue
        parts = line.split('\t')
        assert(len(parts) == 10)
        if '-' in parts[0]:
            this_word_num = int(parts[0][:parts[0].index('-')])
        else:
            this_word_num = int(parts[0])
        if len(splits) > split and this_word_num > splits[split]:
            offset = splits[split]
            split += 1
            new_sentences.append(this_sentence)
            this_sentence = []
            new_texts.append(' '.join(this_text))
            this_text = []
        if '-' in parts[0]:
            start, stop = parts[0].split('-')
            part_0 = '{}-{}'.format(int(start) - offset, int(stop) - offset)
            this_text.append(parts[1])
            skip_surfaces_until = int(parts[0].split('-')[1]) + 1
        else:
            if int(parts[0]) >= skip_surfaces_until:
                this_text.append(parts[1])
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
        this_sentence.append('\t'.join(
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
    if this_sentence:
        new_sentences.append(this_sentence)
    assert(len(new_sentences) == len(splits) + 1)
    
    if this_text:
        new_texts.append(' '.join(this_text))
    return zip(new_sentences, new_texts)

for filename in os.listdir(readdirpath):
    if not filename.startswith("Q") or '_part_' in filename:
        continue
    name = filename[:7]
    readpath = os.path.realpath(os.path.join(readdirpath, filename))
    writepath = os.path.realpath(os.path.join(writedirpath, filename))
    convert_file(name, open(readpath), open(writepath, 'w'))
    print(writepath)
    
