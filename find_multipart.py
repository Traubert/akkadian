import sys

examples = {}

for filename in sys.argv[1:]:
    current = []
    limit = 0
    start = 0
#    print(filename)
    lines = open(filename).readlines()
    for i, line in enumerate(lines):
        parts = line.split('\t')
        if '-' in parts[0]:
#            print(line)
            num1, num2 = parts[0].split('-')
            limit = int(num2)
            start = int(num1)
            continue
        else:
            num = int(parts[0])
        if num > start and num <= limit:
#            print(line)
            case = parts[1]
            if case not in examples:
                example_text = "  " + lines[i-2] + "  " + lines[i-1] + "  " + line
                examples[case] = example_text
            current.append(parts[1])
#    for form in current:
#        pass
#        print(form)

for example in examples:
    print(example + ":")
    print(examples[example])
