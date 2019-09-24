while True:
    try:
        line = input()
    except EOFError:
        break
    parts = line.split('\t')
    if len(parts) < 10:
        continue
    if '-' in parts[0]:
        # Hide multitoken lines from cg
        print(line)
        continue
    surface = parts[1]
    lemma = parts[2]
    POS = parts[3]
    othertags = parts[5].replace('|', ' ')
    print(line)
    print('"<{}>"'.format(surface))
    print('  "{}" {} {}'.format(lemma, POS, othertags))
print('"<$.>"')
        
