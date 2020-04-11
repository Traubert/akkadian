import os

columns_comment = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n"

def split(l, val):
    retval = []
    curlist = []
    for item in l:
        if item == val:
            retval.append(curlist)
            curlist = []
        else:
            curlist.append(item)
    if len(curlist) > 0:
        retval.append(curlist)
    return retval

def not_comment(line):
    return not line.lstrip().startswith("#")

def line_is_wordtoken(line):
    parts = line.split('\t')
    return len(parts) == 10 and ('-' not in parts[0]) and (not line.lstrip().startswith("#"))

def valid_filename(textname):
    textname = os.path.basename(textname)
    if (not textname.startswith("Q")) or '_part_' in textname:
        return False
    q_num = os.path.basename(textname)[1:7]
    num = int(q_num)
    return 4455 <= num <= 4605 or 6013 <= num <= 6050

