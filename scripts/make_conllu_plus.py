import os, sys, string

columns_comment = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n"

def convert_file(readfilename, writefilename):
    writefile = open(writefilename, 'w')
    writefile.write(columns_comment)
    this_sentence_lines = []
    sentence_number = 1
    for line in open(readfilename):
        line = line.strip()
        basename = os.path.basename(readfilename)
        Q_number = basename[:7]
        if line == '':
            if len(this_sentence_lines) == 0:
                continue
            writefile.write('# sent_id = {}-{}\n'.format(Q_number, sentence_number))
            sentence_number += 1
            writefile.write('\n'.join(this_sentence_lines))
            writefile.write('\n\n')
            this_sentence_lines = []
        else:
            parts = line.split('\t')
            if len(parts) == 10:
                for index in [7, 8]:
                    if len(parts[index]) > 1:
                        parts[index] = parts[index].replace('_', ':')
                for index in [5]:
                    if len(parts[index]) > 1:
                        part_parts = parts[index].split('|')
                        new_part_parts = []
                        for part_part in part_parts:
                            tmp = string.capwords(part_part, '_').replace('_', '')
                            new_part_parts.append(string.capwords(tmp, '='))
                        parts[index] = '|'.join(new_part_parts)
                line = '\t'.join(parts)
            this_sentence_lines.append(line)

writedirpath = sys.argv[2]
readdirpath = sys.argv[1]

for filename in os.listdir(readdirpath):
    if not filename.startswith("Q"):
        continue
    readpath = os.path.realpath(os.path.join(readdirpath, filename))
    writepath = os.path.realpath(os.path.join(writedirpath, filename))
    convert_file(readpath, writepath)
    print(writepath)
    
