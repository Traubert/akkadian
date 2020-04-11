import sys, os

rootdir = sys.argv[1]
filenames = os.listdir(rootdir)

def valid_filename(textname):
    q_num = os.path.basename(textname)[1:7]
    num = int(q_num)
    return 4455 <= num <= 4605 or 6013 <= num <= 6050

def superset_relationship(p):
    a, b = p
    a_set = set(a)
    b_set = set(b)
    return a_set.issuperset(b_set) or b_set.issuperset(a_set)

lemma2morpho = {}
lemma2pos = {}
pos2loc = {}
morpho2loc = {}

for f in filter(valid_filename, filenames):
    f_name = os.path.join(rootdir, f)
    for linenum, line in enumerate(open(f_name)):
        parts = line.strip().split('\t')
        if len(parts) != 10 or '-' in parts[0]:
            continue
        lemma = parts[1]
        pos = parts[4]
        loc = (f, linenum + 1)
        tag_parts = tuple(sorted(parts[5].split('|')))
        # if tag_parts == ('_',):
        #     continue
        
        if lemma not in lemma2morpho:
            lemma2morpho[lemma] = {tag_parts: 1}
        else:
            lemma2morpho[lemma][tag_parts] = lemma2morpho[lemma].get(tag_parts, 0) + 1
            
        if lemma not in lemma2pos:
            lemma2pos[lemma] = {pos: 1}
        else:
            lemma2pos[lemma][pos] = lemma2pos[lemma].get(pos, 0) + 1
            
        lemma_with_tags = (lemma, tag_parts)
        if lemma_with_tags not in morpho2loc:
            morpho2loc[lemma_with_tags] = [loc]
        else:
            morpho2loc[lemma_with_tags].append(loc)

        lemma_with_pos = (lemma, pos)
        if lemma_with_pos not in pos2loc:
            pos2loc[lemma_with_pos] = [loc]
        else:
            pos2loc[lemma_with_pos].append(loc)

# print("Suggestions for completing absent POS fields:")
            
# for lemma in sorted(lemma2pos):
#     # if len(forms[form].keys()) < 2:
#     #     continue
#     tags = list(lemma2pos[lemma].keys())
#     if len(tags) == 2 and '_' in tags:
#         tags.remove("_")
#         print()
#         print("{}: _ -> {}".format(lemma, tags[0]))
#         print("  _ occurs in following locations:")
#         for location in pos2loc[(lemma, "_")]:
#             print("    {}, line number {}".format(location[0], location[1]))
#     # elif superset_relationship(forms[form].keys()):
#     #     continue
#         # if ('_',) in forms[form].keys():
#         #     continue
#     # print(form)
#     # for analysis in forms[form]:
#     #     print("  " + str(forms[form][analysis]) + "  " + '|'.join(analysis))

print()
#print(morpho2loc)
print("Suggestions for completing absent or subset morpho fields:")
for lemma in sorted(lemma2morpho):
    # if len(forms[form].keys()) < 2:
    #     continue
    tags = list(lemma2morpho[lemma].keys())
    if len(tags) == 2:

        if ('_',) in tags:
            tags.remove(('_',))
            print()
            print("{}: _ -> {}".format(lemma, '|'.join(tags[0])))
            print("  _ occurs in following locations:")
            for location in morpho2loc[(lemma, ("_",))]:
                print("    {}, line number {}".format(location[0], location[1]))
        elif superset_relationship(tags):
            if len(tags[0]) > len(tags[1]):
                sup = tags[0]
                sub = tags[1]
            else:
                sup = tags[1]
                sub = tags[0]
            print()
            print("{}: {} -> {}".format(lemma, '|'.join(sub), '|'.join(sup)))
            print("  {} occurs in following locations:".format('|'.join(sub)))
            for location in morpho2loc[(lemma, sub)]:
                print("    {}, line number {}".format(location[0], location[1]))

    # elif superset_relationship(forms[form].keys()):
    #     continue
        # if ('_',) in forms[form].keys():
        #     continue
    # print(form)
    # for analysis in forms[form]:
    #     print("  " + str(forms[form][analysis]) + "  " + '|'.join(analysis))

