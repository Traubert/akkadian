import sys, os

rootdir = sys.argv[1]

# conlludir = os.path.join(rootdir, 'conllu')
# annotationdir = os.path.join(rootdir, 'annotation')
# sourcedir = os.path.join(rootdir, 'source')

sections = {}

for filename in os.listdir(rootdir):
    if "_part_" not in filename:
        continue
    lastperiod = filename.rindex('.')
    lastunderscore = filename.rindex('_')
    part_number = int(filename[lastunderscore+1:lastperiod])
    Q_number = filename[:7]
    if Q_number not in sections:
        sections[Q_number] = []
    while len(sections[Q_number]) < part_number:
        sections[Q_number].append(None)
    sections[Q_number][part_number - 1] = open(os.path.join(rootdir, filename)).read()


for q_num in sections:
    writefile = open(os.path.join(rootdir, q_num + '.txt'), 'w')
    writefile.write(''.join(sections[q_num]))

