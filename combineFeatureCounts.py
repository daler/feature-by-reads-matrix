#!/usr/bin/python
usage = """

Combines multiple text files as output by countReadsInFeatures.py.  Reads entire files into memory.

    Example usage:
        combineFeatureCounts.py --out final-counts.txt FILE1-feature-counts.txt FILE2-feature-counts.txt

Ryan Dale 2010 (dalerr@niddk.nih.gov)
"""

import os,sys,optparse

op = optparse.OptionParser(usage=usage)
op.add_option('--out',dest='out',help='Combined tab-delimited txt file')
options,args = op.parse_args()
if not options.out:
    op.print_help()
    print '\nERROR: Please specify an output file with --out\n'
    sys.exit()

fns = args

d = {}
for i,f in enumerate(fns):
    for line in open(f):
        feature,count = line.strip().split('\t')
        value = d.setdefault(feature,{})
        value[f] = count
fout = open(options.out,'w')

header = ['feature']
header.extend(fns)
header = '\t'.join(header) + '\n'
fout.write(header)

for feature,value in d.iteritems():
    line = [feature]
    for fn in fns:
        line.append(value[fn])
    fout.write('\t'.join(line)+'\n')
fout.close()
