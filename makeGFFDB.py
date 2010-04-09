#!/usr/bin/python

usage = """
    
    Create a GFF database from a GFF file, e.g., downloaded from FlyBase.
    
    Ryan Dale 2010 (dalerr@niddk.nih.gov)
    """
import GFFutils
import optparse
import os
import sys

op = optparse.OptionParser(usage=usage)
op.add_option('--gff',dest='gff',help='Input GFF file')
op.add_option('--gffdb',dest='gffdb',help='Destination GFF database file')
options,args = op.parse_args()

if not options.gff or not options.gffdb:
    op.print_help()
    print '\nERROR: Please specify an input GFF file and an output GFF database file'
    sys.exit()


if not os.path.exists(options.gff):
    print 'GFF file %s does not exist!' % options.gff
    sys.exit()

GFFutils.create_gffdb(options.gff, options.gffdb)

