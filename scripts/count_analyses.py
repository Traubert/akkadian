import sys, os

filenames = sys.argv[1:]

forms = {}
total_words = 0
max_analyses = 0

for f in filenames:
    for line in open(f):
        parts = line.strip().split('\t')
        if len(parts) != 10:
            continue
        total_words += 1
        lemma = parts[1]
        tag_parts = (parts[4],) + tuple(sorted(parts[5].split('|')))
        if lemma not in forms:
            forms[lemma] = {tag_parts: 1}
            continue
        forms[lemma][tag_parts] = forms[lemma].get(tag_parts, 0) + 1
        max_analyses = max(max_analyses, len(forms[lemma]))

print("Total words: {}  Total forms: {}".format(total_words, len(forms)))
print()        
for n in range(1, max_analyses + 1):
    n_words = 0
    n_forms = 0
    for form in filter(lambda x: len(forms[x]) == n, forms.keys()):
        n_forms += 1
        for analysis in forms[form]:
            n_words += forms[form][analysis]
    print("{words} words with {n} analyses ({words_rel:.1f}%), {forms} forms with {n} analyses ({forms_rel:.1f}%)".format(words = n_words, forms = n_forms, n = n, words_rel = 100*n_words/total_words, forms_rel = 100*n_forms/len(forms)))
