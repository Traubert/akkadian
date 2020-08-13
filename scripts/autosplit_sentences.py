import sys, os

from akkadian import *

conservative = False

logfilename = "/dev/null"
readdirpath = sys.argv[1]
writedirpath = sys.argv[2]
if len(sys.argv) > 3:
    logfilename = sys.argv[3]
log_fobj = open(logfilename, "w")

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
        child2parent = {}
        multitokensets = {}
        roots = []
        splits = []

        def collect_children(root):
            collection = []
            if root not in parent2children:
                return collection
            for child in parent2children[root]:
                collection.append(child)
                if child in parent2children:
                    collection += collect_children(child)
            return collection
        def collect_parents(children):
            collection = set()
            for child in children:
                if child in child2parent:
                    this_child = child2parent[child]
                    this_child_parents = set()
                    this_child_parents.add(child2parent[child])
                    while this_child in child2parent:
                        this_child_parents.add(child2parent[this_child])
                        this_child = child2parent[this_child]
                        if child2parent[this_child] in this_child_parents:
                            exit("CYCLE")
                    collection.update(this_child_parents)
            return collection
        
        for line in filter(not_comment, sentence):
            head = get_head(line)
            this_id = get_id(line)
            if '-' in this_id:
                start, stop = this_id.split('-')
                members = list(map(str, range(int(start), int(stop)+1)))
                for member in members:
                    # log_fobj.write("    Recorded {} ({}) as multitokenset of {}\n".format(member, get_surface(line), members[:]))
                    multitokensets[member] = members[:]
            if head != '_' and head != '0':
                head_ids.add(head)
                child2parent[this_id] = head
                if head not in parent2children:
                    parent2children[head] = [this_id]
                else:
                    parent2children[head].append(this_id)
        
        for i, line in enumerate(sentence):
            this_id = get_id(line)
            if not line_is_wordtoken(line):
                continue
            if get_head(line) == '0':
                roots.append(this_id)
            elif get_head(line) == '_':
                parts = line.split('\t')
                if this_id in head_ids:
                    parts[6] = '0'
                    parts[7] = 'root'
                    parts[8] = '0:root'
                    roots.append(this_id)
                elif this_id in multitokensets:
                    for candidate in multitokensets[this_id]:
                        if candidate in roots or candidate in child2parent.keys():
                            parts[6] = candidate
                            parts[7] = 'dep'
                            parts[8] = '{}:dep'.format(candidate)
                            if candidate not in parent2children:
                                parent2children[candidate] = [this_id]
                            else:
                                parent2children[candidate].append(this_id)
                            child2parent[this_id] = candidate
                            log_fobj.write("    Automatically attached multitoken member {} to {}\n".format(this_id, candidate))
                            break
                sentence[i] = '\t'.join(parts)
            
        lastright = None
        assigned_ids = set()
        for head in roots:
            made_split = False
            children = list(map(int, collect_children(head)))
            # if not children:
            #     log_fobj.write("    Apparent sentence root {} but has no children, doing nothing\n".format(head))
            #     continue
            leftmost_wo_parents = min(children + [int(head)])
            rightmost_wo_parents = max(children + [int(head)])

            if lastright != None:
                if lastright + 1 < leftmost_wo_parents:
                    log_fobj.write("    Extended LHS by most recent RHS: was {}, now {}\n".format(leftmost_wo_parents, lastright + 1))
                children.append(lastright + 1)
            
            parents = list(map(int, collect_parents(range(leftmost_wo_parents, rightmost_wo_parents + 1))))
            leftmost = min(children + parents + [int(head)])
            rightmost = max(children + parents + [int(head)])
            log_fobj.write("    Apparent sentence root {}: leftmost node was {}, rightmost node was {}\n".format(head, leftmost_wo_parents, rightmost_wo_parents))
            if leftmost_wo_parents != leftmost:
                log_fobj.write("      Extended LHS by parents: was {}, now {}\n".format(leftmost_wo_parents, leftmost))
            if rightmost_wo_parents != rightmost:
                log_fobj.write("      Extended RHS by parents: was {}, now {}\n".format(rightmost_wo_parents, rightmost))
            if lastright != None:
                if not conservative or leftmost == lastright + 1:
                    log_fobj.write("      Trying to insert split at original id {}...".format(leftmost-1))
                    splits.append(leftmost-1)
                    made_split = True
            if made_split and str(leftmost-1) in multitokensets and str(leftmost) in multitokensets and str(leftmost) in multitokensets[str(leftmost-1)]:
                log_fobj.write(" BREAKS MULTITOKEN, so not splitting\n")
                splits.pop()
                continue
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
        for new_sentence, new_surface in apply_splits(list(map(lambda x: x.strip('\n'), filter(not_comment, sentence))), sorted(splits)):
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
    print(f"Processing {readpath}...")

    convert_file(name, open(readpath), open(writepath, 'w'))
    
