#!/usr/bin/python
usage="""
This script takes, as input, a 
"""
import sys
import optparse
import GFFutils

op = optparse.OptionParser()
op.add_option('--dbfn', help='GFF (or GTF) database as created by GFFutils')
op.add_option('--gffout', help='Output file to write exons to')
op.add_option('--lengthsout', help='Output file containing the total length of each feature')
op.add_option('--level', help='Specify --level=exon or --level=gene to determine which ID '
                              'will be inserted in the gene_id attribute of the output GFF file.')
op.add_option('--ftype', default='GFF', help='Use --ftype=GTF for GTF files.')
options,args = op.parse_args()

required_args = ['dbfn','gffout','lengthsout','level']
for arg in required_args:
    if getattr(options,arg) is None:
        op.print_help()
        print '\nArgument "%s" required.\n'%arg
        sys.exit()

if options.type == 'GFF':
    G = GFFutils.GFFDB(options.dbfn)
    exon_feature = 'exon'
if options.type == 'GTF':
    G = GFFutils.GTFDB(options.dbfn)
    exon_feature = 'CDS'



if __name__ == "__main__":

    fout = open(options.gffout,'w')

    # make a dictionary of each gene and the number of isoforms it has
    gene_isoform_dict = {}
    lengths = {}
    print 'Getting gene isoforms...'
    sys.stdout.flush()
    for gene in G.features_of_type('gene'):
        gene_isoform_dict[gene.id] = G.n_gene_isoforms(gene.id)
        
    # make a dictionary of each exon and the number of isoforms it has; 
    # also make a lookup dictionary of which exon goes to what gene
    exons = {}
    exon_gene_parents = {}
    print 'Getting exon isoforms...'
    sys.stdout.flush()
    for exon in G.features_of_type(exon_feature):
        
        # which gene this exon belongs to
        try:
            exon_gene_parents[exon.id] = G.exons_gene(exon.id)
        except TypeError:
            print exon.id
            continue

        # how many isoforms this exon is found in
        exons[exon.id] = G.n_exon_isoforms(exon.id)


    # combine the dictionaries to determine if the exon's isoform count equals
    # the gene's isoform count.  If so, it's a keeper...
    print 'Comparing gene and exon isoforms; outputting keepers to file...'
    sys.stdout.flush()
    for exon_id,n_exon_isoforms in exons.iteritems():
        try:
            
            # See if we have a gene parent for this exon
            gene_id = exon_gene_parents[exon_id]

            # See if we have an isoform count for this gene
            n_gene_isoforms = gene_isoform_dict[gene_id]

        except KeyError:
            print exon_id, gene_id
            continue

        if n_exon_isoforms == n_gene_isoforms:
            
            # Decide which ID to use
            if options.level == 'gene':
                id_to_use = gene_id
            if options.level == 'exon':
                id_to_use = exon_id

            # Retrieve the GFFFeature for the exon from the database
            exon = G[exon_id]
            
            # Increment the length by the length of the exon.  If we're
            # using exon IDs, each time a new entry will be added.  If
            # we're using gene IDs, then it will be incremented, resulting
            # in a gene total.
            lengths[id_to_use] = lengths.setdefault(id_to_use,0) + len(exon)

            # Name it according to the options
            exon.add_attribute('gene_id',id_to_use)
            exon.value = 0
            
            # force it to be of type exon
            exon.featuretype = 'exon'
            
            # write out to file!
            fout.write(exon.tostring())
    
    fout.close()


    # Write the dictionary of lengths to file
    print 'Writing lengths to file...'
    sys.stdout.flush()
    lengthsout = open(options.lengthsout,'w')
    for item in lengths.iteritems():
        lengthsout.write('%s\t%s\n' % item)    
    lengthsout.close()

