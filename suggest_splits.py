import sys

examples = {}
suffixes = set()
suffixes = set()
prefixes = set()

for filename in sys.argv[1:]:
    current = []
    limit = 0
    start = 0
    this_parts = []
    multipart_line = ""
#    print(filename)
    lines = open(filename).readlines()
    for i, line in enumerate(lines):
        parts = line.split('\t')
        if '-' in parts[0]:
#            print(line)
            multipart_line = line.strip()
            this_parts = []
            num1, num2 = parts[0].split('-')
            limit = int(num2)
            start = int(num1)
            continue
        else:
            num = int(parts[0])
        if num >= start and num <= limit:
#            print(line)
            case = parts[1]
            this_parts.append(parts[1])
        else:
            if this_parts:
                if len(this_parts) == 2:
                    if len(this_parts[0]) < len(this_parts[1]):
                        prefixes.add(this_parts[0])
                    else:
                        suffixes.add(this_parts[1])
                else:
                    print(filename, multipart_line, this_parts)
            this_parts = []
for filename in sys.argv[1:]:
    current = []
    limit = 0
    start = 0
    this_parts = []
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
        if num >= start and num <= limit:
#            print(line)
            continue
        else:
            for suffix in suffixes:
                if len(suffix) > 1 and len(parts[1]) > len(suffix) and parts[1].endswith(suffix):
                    print(line.strip(), suffix)
                
# for part in affixes:
#     print(part)
            # if case not in examples:
            #     example_text = "  " + lines[i-2] + "  " + lines[i-1] + "  " + line
            #     examples[case] = example_text
#            current.append(parts[1])
#    for form in current:
#        pass
 #       print(form)

# for example in examples:
#     print(example + ":")
#     print(examples[example])
