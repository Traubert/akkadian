import sys

prevline = ""
prevmorpho = ""
while True:
    try:
        line = input().strip()
    except EOFError:
        break
    if line.startswith('"'):
        if line.startswith('"<'):
            continue
        prevline_parts = prevline.split('\t')
        curr_morpho = line[line.rindex('"') + 2:]
        prev_pos = prevline_parts[3]
        prev_morpho = prevline_parts[5].replace('|', ' ')
        if prev_pos + ' ' + prev_morpho != curr_morpho:
            addition = curr_morpho[len(prev_pos) + 1 + len(prev_morpho) + 1:].strip()
        else:
            print('\t'.join(prevline_parts))
            prevline = ''
            continue
        this_wordnum = int(prevline_parts[0])
        if addition.endswith('<'):
            target = this_wordnum - 1
            addition = addition[:-1]
        elif addition.endswith('>'):
            target = this_wordnum + 1
            addition = addition[:-1]
        elif '>' in addition:
            count = int(addition[addition.rindex('>')+1:])
            target = this_wordnum + count
            addition = addition[:-2]
        elif '<' in addition:
            count = int(addition[addition.rindex('<')+1:])
            target = this_wordnum - count
            addition = addition[:-2]
        else:
            sys.stderr.write(addition + '\n')
        prevline_parts[6] = str(target)
        prevline_parts[7] = addition
        if prevline_parts[8] == '_':
            prevline_parts[8] = prevline_parts[6] + ':' + prevline_parts[7]
        else:
            prevline_parts += '|' + prevline_parts[6] + ':' + prevline_parts[7]
        prevline_parts[8] = '_'
        print('\t'.join(prevline_parts))
        prevline = ''
    else:
        if prevline != '':
            print(prevline)
            prevline = ''
        prevline = line
