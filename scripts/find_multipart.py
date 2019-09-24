import sys

current = []
limit = 0
start = 0
for filename in sys.argv[1:]:
#    print(filename)
    for line in open(filename):
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
            current.append(parts[1])
for form in current:
    print(form)
