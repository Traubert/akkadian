import sys, os

from akkadian import *

html_string = '''
<!doctype html>
<html>
<head>
<title>Suggestions for completing absent or subset morpho fields</title>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<style>
div.examplebox {{ max-width:22cm; }}
</style>

</head>
<body>
<h2>Suggestions for completing absent or subset morpho fields:</h2>
<table class="table table-condensed table-bordered">
{TABLEROWS}
</table>
</body>
</html>
'''


rootdir = sys.argv[1]
filenames = os.listdir(rootdir)
outfilename = "suggestions.html"
if len(sys.argv) > 2:
    outfilename = sys.argv[2]
outfile = open(outfilename, "w")

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

row = '''
<tr>
<td>{WORDFORM}</td>
<td>
<button type="button" class="btn btn-link btn-xs" data-toggle="collapse" data-target="#{FROM_ID}">{FROM} occurs in the following {FROM_COUNT} locations:</button>
<div id="{FROM_ID}" class="collapse">
{FROM_LOCATION_LIST}
</div>
</td>
<td>
<button type="button" class="btn btn-link btn-xs" data-toggle="collapse" data-target="#{TO_ID}">{TO} occurs in the following {TO_COUNT} locations:</button>
<div id="{TO_ID}" class="collapse">
{TO_LOCATION_LIST}
</div>
</td>
</tr>
'''

tablerows = '''
<tr>
  <th>Word form</th>
  <th>From</th>
  <th>To</th>
</tr>
'''

id_count = 1
for _wordform in sorted(lemma2morpho):
    # if len(forms[form].keys()) < 2:
    #     continue
    tags = list(lemma2morpho[_wordform].keys())
    if len(tags) == 2:

        if ('_',) in tags:
            tags.remove(('_',))
            _from = ('_',)
            _to = tags[0]
        elif superset_relationship(tags):
            if len(tags[0]) > len(tags[1]):
                _to = tags[0]
                _from = tags[1]
            else:
                _to = tags[1]
                _from = tags[0]
        else:
            continue
        _from_str = '|'.join(_from)
        _to_str = '|'.join(_to)
        _to_count = len(morpho2loc[(_wordform, _to)])
        _from_count = len(morpho2loc[(_wordform, _from)])
        _from_list = '<br/>\n'.join(["{}, line number {}".format(location[0], location[1]) for location in morpho2loc[(_wordform, _from)]])
        _to_list = '<br/>\n'.join(["{}, line number {}".format(location[0], location[1]) for location in morpho2loc[(_wordform, _to)]])
        tablerows += row.format(WORDFORM=_wordform,
                                FROM=_from_str, TO=_to_str,
                                FROM_COUNT=_from_count,
                                TO_COUNT=_to_count,
                                FROM_LOCATION_LIST=_from_list,
                                TO_LOCATION_LIST=_to_list,
                                FROM_ID="{}_from_{}".format(_wordform, id_count),
                                TO_ID="{}_to_{}".format(_wordform, id_count))
        id_count += 1

    # elif superset_relationship(forms[form].keys()):
    #     continue
        # if ('_',) in forms[form].keys():
        #     continue
    # print(form)
    # for analysis in forms[form]:
    #     print("  " + str(forms[form][analysis]) + "  " + '|'.join(analysis))

outfile.write(html_string.format(TABLEROWS=tablerows))
