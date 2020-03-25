import sys, os

rootdir = sys.argv[1]
filenames = os.listdir(rootdir)

def superset_relationship(p):
    a, b = p
    a_parts = set(a)
    b_parts = set(b)
    return a_parts.issuperset(b_parts) or b_parts.issuperset(a_parts)

forms = {}

for f in filenames:
    f_name = os.path.join(rootdir, f)
    for line in open(f_name):
        parts = line.strip().split('\t')
        if len(parts) != 10:
            continue
        lemma = parts[1]
        tag_parts = tuple(sorted(parts[5].split('|')))
        # if tag_parts == ('_',):
        #     continue
        if lemma not in forms:
            forms[lemma] = {tag_parts: 1}
            continue
        forms[lemma][tag_parts] = forms[lemma].get(tag_parts, 0) + 1
for form in sorted(forms):
    # if len(forms[form].keys()) < 2:
    #     continue
    if len(forms[form].keys()) <= 2:
        continue
        # if ('_',) in forms[form].keys():
        #     continue
    # if superset_relationship(forms[form].keys()):
    #     continue
    print(form)
    for analysis in forms[form]:
        print("  " + str(forms[form][analysis]) + "  " + '|'.join(analysis))

