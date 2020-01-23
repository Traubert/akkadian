import sys

def find_splits(input_lines):
    lines = []
    splits = []
    for i, line in enumerate(input_lines):
        assert(line != '')
        if line.startswith("#") and line[1:].strip() == "cut":
            splits.append(int(input_lines[i-1].split('\t')[0]))
        else:
            lines.append(line)
    return lines, splits

def fix_deletions(sentence_lines):
    if not sentence_lines:
        return sentence_lines
    new_lines = []
    oldnum2newnum = {}
    word_num = 1
    for i, line in enumerate(sentence_lines):
        if line.startswith("#"):
            continue
        parts = line.split('\t')
        if '-' in parts[0]:
            continue
        else:
            if parts[0] not in oldnum2newnum:
                oldnum2newnum[parts[0]] = word_num
                word_num += 1
    for line in sentence_lines:
        if line.startswith('#'):
            new_lines.append(line)
            continue
        parts = line.split('\t')
        if len(parts) != 10:
            new_lines.append(line)
            continue
        if '-' in parts[0]:
            start, stop = parts[0].split('-')
            start = oldnum2newnum[start]
            stop = oldnum2newnum[stop]
            if start == stop:
                print(line, start, stop)
                assert(False)
            newnumber = '{}-{}'.format(start, stop)
        else:
            newnumber = str(oldnum2newnum[parts[0]])
        oldhead = parts[6]
        olddeps = parts[8]
        if oldhead in '_0':
            newhead = oldhead
            newdeps = olddeps
        else:
            newhead = str(oldnum2newnum[oldhead])
            if olddeps == '_':
                newdeps = '_'
            else:
                olddepsparts = olddeps.split('|')
                newdepsparts = []
                for dep in olddepsparts:
#                    print("#" + olddeps + "#")
#                    print(line)
                    target, label = dep.split(':')
                    newdepsparts.append('{}:{}'.format(oldnum2newnum[target], label))
                newdeps = '|'.join(newdepsparts)
        new_lines.append('\t'.join((
            newnumber,
            parts[1],
            parts[2],
            parts[3],
            parts[4],
            parts[5],
            newhead,
            parts[7],
            newdeps,
            parts[9])))
    return new_lines

def fix_additions(sentence_lines):
    if not sentence_lines:
        return sentence_lines
    new_lines = []
    oldnum2newnum = {}
    seen_words = {}
    word_num = 1
    for i, line in enumerate(sentence_lines):
        if line.startswith("#"):
            continue
        parts = line.split('\t')
        if '-' in parts[0]:
            continue
        else:
            if parts[0] not in seen_words:
                oldnum2newnum[parts[0]] = word_num
                word_num += 1
                seen_words[parts[0]] = parts[1]
            else:
                if parts[1] in seen_words[parts[0]]:
                    continue
                else:
                    parts[0] = str(word_num)
                    word_num += 1
                    sentence_lines[i] = '\t'.join(parts)
    for line in sentence_lines:
        if line.startswith('#'):
            new_lines.append(line)
            continue
        parts = line.split('\t')
        if len(parts) != 10:
            new_lines.append(line)
            continue
        if '-' in parts[0]:
            start, stop = parts[0].split('-')
            start = oldnum2newnum[start]
            stop = oldnum2newnum[stop]
            if start == stop:
                print(line, start, stop)
                assert(False)
            newnumber = '{}-{}'.format(start, stop)
        else:
            newnumber = str(oldnum2newnum[parts[0]])
        oldhead = parts[6]
        olddeps = parts[8]
        if oldhead in '_0':
            newhead = oldhead
            newdeps = olddeps
        else:
            newhead = str(oldnum2newnum[oldhead])
            if olddeps == '_':
                newdeps = '_'
            else:
                olddepsparts = olddeps.split('|')
                newdepsparts = []
                for dep in olddepsparts:
#                    print("#" + olddeps + "#")
#                    print(line)
                    target, label = dep.split(':')
                    newdepsparts.append('{}:{}'.format(oldnum2newnum[target], label))
                newdeps = '|'.join(newdepsparts)
        new_lines.append('\t'.join((
            newnumber,
            parts[1],
            parts[2],
            parts[3],
            parts[4],
            parts[5],
            newhead,
            parts[7],
            newdeps,
            parts[9])))
    return new_lines

def fix_new_multitokens(sentence_lines):
    if not sentence_lines:
        return sentence_lines
    new_lines = []
    new_multitoken_position2length = {}
    oldnum2newnum = {}
    word_num = 1
    for i, line in enumerate(sentence_lines):
#        print(line)
        if line.startswith("#"):
            continue
        parts = line.split('\t')
        if '-' in parts[0]:
#            print("fix_new_multitokens continuing #{}#".format(parts[0]))
            continue
        else:
            if parts[0] not in oldnum2newnum:
                oldnum2newnum[parts[0]] = word_num
#                print("fix_new_multitokens #{}#".format(parts[0]))
                word_num += 1
            else:
                if parts[0] in new_multitoken_position2length:
                    new_multitoken_position2length[parts[0]] += 1
                    word_num += 1
                else:
                    new_multitoken_position2length[parts[0]] = 1
    new_multitokens_written = {}
    for line in sentence_lines:
        if line.startswith('#'):
            new_lines.append(line)
            continue
        parts = line.split('\t')
        if '-' in parts[0]:
            start, stop = parts[0].split('-')
            start = oldnum2newnum[start]
            stop = oldnum2newnum[stop]
            assert(start != stop)
            newnumber = '{}-{}'.format(start, stop)
        else:
            newnum = oldnum2newnum[parts[0]]
            if parts[0] in new_multitoken_position2length:
                if parts[0] in new_multitokens_written:
                    offset = new_multitokens_written[parts[0]]
                    new_multitokens_written[parts[0]] += 1
                    newnumber = str(newnum + offset)
                else:
                    multitoken_length = new_multitoken_position2length[parts[0]]
                    newnumber = '{}-{}'.format(newnum, newnum + multitoken_length - 1)
                    new_multitokens_written[parts[0]] = 0
            else:
                newnumber = str(newnum)
        oldhead = parts[6]
        olddeps = parts[8]
        if oldhead in '_0':
            newhead = oldhead
            newdeps = olddeps
        else:
            newhead = str(oldnum2newnum[oldhead])
            if olddeps == '_':
                newdeps = '_'
            else:
                olddepsparts = olddeps.split('|')
                newdepsparts = []
                for dep in olddepsparts:
                    target, label = dep.split(':')
                    newdepsparts.append('{}:{}'.format(oldnum2newnum[target], label))
                newdeps = '|'.join(newdepsparts)
        new_lines.append('\t'.join((
            newnumber,
            parts[1],
            parts[2],
            parts[3],
            parts[4],
            parts[5],
            newhead,
            parts[7],
            newdeps,
            parts[9])))
    return new_lines

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
        if parts[6] == '_':
            part_6 = '_'
        else:
            part_6 = str(int(parts[6]) - offset)
        if parts[8] != '_':
            new_parts = []
            old_parts = parts[8].split('|')
            for part in old_parts:
                target, label = part.split(':')
                new_target = str(int(target) - offset)
                new_parts.append(new_target + ':' + label)
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

def tabbed_line_has_n_fields(line):
    return '\t' not in line or len(line.split('\t')) == 10

def multitoken_line_has_start_nequal_end(line):
    if '\t' not in line:
        return True
    n = line.split('\t')[0]
    if '-' not in n:
        return True
    start, stop = n.split('-')
    return start != stop

def process_lines(lines):
    lines = fix_deletions(lines)
    lines = fix_new_multitokens(lines)
    lines, splits = find_splits(lines)
    return apply_splits(lines, splits)

lines = []
for line in open(sys.argv[1]):
    line = line.strip()
    if line == "":
        print(process_lines(lines))
        lines = []
    else:
        lines.append(line.strip())
if lines:
    print(process_lines(lines))


        
