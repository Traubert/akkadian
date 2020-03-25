import sys, os

rootdir = sys.argv[1]
conlludir = os.path.join(rootdir, 'conllu')
annotationdir = os.path.join(rootdir, 'annotation')
sourcedir = os.path.join(rootdir, 'source')
suffix = '.txt'

try:
    os.mkdir(conlludir)
except FileExistsError:
    pass

for dirname in os.listdir(annotationdir):
    prefix = dirname[:dirname.index(suffix)]
    f_bytes = open(os.path.join(annotationdir, dirname, 'miluukko@helsinki.fi.conll')).read()
    open(os.path.join(conlludir, '{}.txt'.format(prefix)), 'w').write(f_bytes)
