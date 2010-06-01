#!/usr/bin/python
usage="""
This script takes, as input, a 
"""
import optparse
import GFFutils

op = optparse.OptionParser()
op.add_option('--dbfn', help='GFF (or GTF) database as created by GFFutils')
op.add_option('-o', help='Output file to write exons to')
op.add_option('--level', help='Specify --level=exons or --level=genes to determine which ID '
                              'will be inserted in the gene_id attribute of the output GFF file.')
op.add_option('--type', default='GFF', help='Use --type=GTF for GTF files.')
options,args = op.parse_args()

if options.type == 'GFF':
    G = GFFutils.GFFDB(options.dbfn)
    exon_feature = 'exon'
if options.type == 'GTF':
    G = GFFutils.GTFDB(options.dbfn)
    exon_feature = 'CDS'

if __name__ == "__main__":

    fout = open(options.o,'w')

    # make a dictionary of each gene and the number of isoforms it has
    genes = {}
    for gene in G.features_of_type('gene'):
        genes[gene.id] = G.n_gene_isoforms(gene.id)

    # make a dictionary of each exon and the number of isoforms it has; 
    # also make a lookup dictionary of which exon goes to what gene
    exons = {}
    exon_genes = {}
    for exon in G.features_of_type(exon_feature):
        exons[exon.id] = G.n_exon_isoforms(exon.id)
        exon_genes[exon.id] = G.exons_gene(exon.id)

    # combine the dictionaries to determine if the exon's isoform count equals the gene's isoform count.
    # If so, it's a keeper...
    for exon,exon_isoforms in exons.iteritems():
        try:
            gene_isoforms = genes[exon_genes[exon]]
            if exon_isoforms == gene_isoforms:
                e = G[exon]
                e.add_attribute('gene_id',exon_genes[exon])
                
                # force it to be of type exon
                e.featuretype = 'exon'
                fout.write(e.tostring())
        except KeyError:
            pass
    fout.close()

