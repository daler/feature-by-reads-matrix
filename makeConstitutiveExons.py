#!/usr/bin/python

usage = """

    Script to generate a BED file of constitutive exons.

    Input is either a pre-compiled GFF database, or a GFF file which will be
    compiled into a GFF database. 
"""
import GFFutils
import os,sys,tempfile
import optparse
import logging

# Set up logger
format = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.DEBUG,format=format)

op = optparse.OptionParser(usage=usage)
op.add_option('--gff',dest='gff',help='GFF file to parse')
op.add_option('--gffdb',dest='gffdb',help='Pre-compiled GFF database, or'
                                          'database to create if -gff specified')
op.add_option('--bed',dest='bed',help='Output BED file to create')

options,args = op.parse_args()

if not options.gffdb:
    op.print_help()
    print '\nERROR: Please specify a GFF database filename with --gffdb'
    sys.exit()
if not options.bed:
    op.print_help()
    print '\nERROR: Please specify an output file with --bed'
    sys.exit()
if options.gff:
    GFFutils.create_gffdb(options.gff, options.gffdb)
G = GFFutils.GFFDB(options.gffdb)

logging.info('Finding exons found in all isoforms of a gene...')
tmp = tempfile.mktemp()
fout = open(tmp,'w')
ngenes = float(G.count_features_of_type('gene'))
c = 0
for gene in G.features_of_type('gene'):
    if 'mito' in gene.chr:
        continue
    if 'Het' in gene.chr:
        continue

    # print some feedback every 100 genes
    if c % 100 == 0:
        perc = c/ngenes*100
        print '\r%s genes done (%d%%)'% (c,perc),
        sys.stdout.flush()
    c+=1
    const_expr_exons = []

    # get the isoforms for this gene
    isoforms = [i for i in G.children(gene.id) if i.featuretype=='mRNA']
    n_isoforms = len(isoforms)
    #gene_isoform_ids = set([i.id for i in isoforms])
    # for each exon (child of level 2) for this gene...
    children = G.children(gene.id,level=2)
    for child in children:
        if child.featuretype != 'exon':
            continue
        #exon_id = child.id
        #...get the exon's parent mRNA
        n_parents = len(list(G.parents(child.id,level=1,featuretype='mRNA')))

        # if the number of exon mRNA parents is the same as the number of gene
        # mRNA children, this exon is found in all isoforms.
        if n_parents == n_isoforms:
            const_expr_exons.append(child)

    # decide what to write out to file...
    if len(const_expr_exons) > 0:
        #fout.write(gene.to_bed())
        pass
        for isoform in isoforms:
            #fout.write(isoform.to_bed())
            pass
        exon_count = 0
        for exon in const_expr_exons:
            exon_count += 1
            line = '%s\t%s\t%s\t%s\n' % ( exon.chr, exon.start, exon.stop, exon.id)
            fout.write(line)
fout.close()
print 

logging.info('Filtering out exons that overlap another exon...')
cmds = ['intersectBed',
        '-a',tmp,
        '-b',tmp,
        '-c',
        '| grep "\t1$"',
        '| cut -f1,2,3,4',
        '>',options.bed]
os.system(' '.join(cmds))
os.remove(tmp)
logging.info('Done.')

