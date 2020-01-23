import os

filenames = os.listdir('merged_conllu_from_webanno')

forms = {}

for f in filenames:
    f_name = os.path.join('merged_conllu_from_webanno', f)
    for line in open(f_name):
        parts = line.strip().split('\t')
        if len(parts) != 10:
            continue
        lemma = parts[1]
        tag_parts = tuple(sorted(parts[5].split('|')))
        if lemma not in forms:
            forms[lemma] = {tag_parts: 1}
            continue
        forms[lemma][tag_parts] = forms[lemma].get(tag_parts, 0) + 1
for form in sorted(forms):
    # if len(forms[form].keys()) < 2:
    #     continue
    print(form)
    for analysis in forms[form]:
        print("  " + str(forms[form][analysis]) + "  " + '|'.join(analysis))

