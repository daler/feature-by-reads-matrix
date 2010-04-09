#!/usr/bin/python

import os
import sys
import optparse
import logging
import subprocess

# Set up logger
format = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.DEBUG,format=format)

def sam_to_bam(SAM):
    """Uses SAMtools to convert SAM to BAM format."""
    logging.info('Converting SAM file %s to BAM file, %s...'%(SAM,BAM))
    cmds = ['samtools',
            'view',
            '-S',SAM,
            '-b',
            '>',BAM]
    os.system(' '.join(cmds))
    logging.info('...new BAM file is %s'%BAM)

def bam_to_bed(BAM,READS):
    """Converts BAM file to BED format for use by BEDtools."""
    logging.info('Converting BAM file %s to BED...' % BAM)
    cmds = ['bamToBed',
            '-i',BAM,
            '>',READS]
    os.system(' '.join(cmds))
    logging.info('..."%s" now contains reads from SAM/BAM file.'%READS)

def count_reads_in_exons(READS,INBED,FEATURECOUNTS):
    """Counts the reads in each exon using intersectBed"""
    logging.info('Counting reads in "%s" per feature in "%s"...' % (READS,INBED))
    cmds = ['intersectBed',
            '-a', INBED,
            '-b', READS,
            '-c',
            '>',FEATURECOUNTS]
    os.system(' '.join(cmds))
    logging.info('"...%s" now has the read counts per exon.'%FEATURECOUNTS)

def make_table(FEATURECOUNTS,FEATURECOUNTSTXT):
    """Convert BED file into a table"""
    logging.info('Converting "%s" into a tab-delimited table...' % FEATURECOUNTS)
    cmds = ['cut -f4,5',
            FEATURECOUNTS,
            '>',FEATURECOUNTSTXT]
    os.system(' '.join(cmds))
    logging.info('DONE.  Results are in "%s".' % FEATURECOUNTSTXT)

if __name__ == "__main__":
    usage = '''

    For each feature in --bed, counts the number of reads in --sam/--bam that
    intersect that feature.

    Requires the following to be on the path:

        samtools (http://samtools.sourceforge.net/) 
        bedtools (http://code.google.com/p/bedtools/)

    Ryan Dale 2010 (dalerr@niddk.nih.gov)
    '''
    op = optparse.OptionParser(usage=usage)
    op.add_option('--sam',dest='sam',help='Input SAM file (if --bam not specified)')
    op.add_option('--bam',dest='bam',help='Input BAM file (if --sam not specified)')
    op.add_option('--bed',dest='bed',help='Input BED file containing regions of interest')
    op.add_option('--prefix',dest='prefix',help='Optional prefix to add to output files')
    options,args = op.parse_args()

    # Check for command line options
    if not options.sam and not options.bam:
        op.print_help()
        print '\nERROR: Please specifiy either a SAM or BAM file as input.\n'
        sys.exit()
    if not options.bed:
        op.print_help()
        print '\nERROR: Please specify a BED file.\n'
        sys.exit()

    # Check for 3rd-party tools
    try:
        p = subprocess.Popen(['samtools'],stderr=subprocess.PIPE)
    except OSError:
        print "samtools not found.  Please install and make sure it's on your path"
        sys.exit()
    try:
        p = subprocess.Popen(['intersectBed'],stderr=subprocess.PIPE)
    except OSError:
        print "BEDtools command \"intersectBed\" not found.  Please install and make sure it's on your path"
        sys.exit()
    try:
        p = subprocess.Popen(['bamToBed'],stderr=subprocess.PIPE)
    except OSError:
        print "BEDtools command \"bamToBed\" not found.  Please install and make sure it's on your path"
        sys.exit()

    # filenames that will be used throughout
    if options.sam:
        SAM = options.sam
        BAM = os.path.splitext(SAM)[0]+'.bam'
    if options.bam:
        BAM = options.bam

    if options.prefix:
        PREFIX = '%s-' % options.prefix
    else:
        PREFIX = ''

    READS = PREFIX + '%s-converted.bed' % os.path.splitext(BAM)[0]
    INBED = options.bed
    FEATURECOUNTS = PREFIX + '%s-feature-counts.bed' % os.path.splitext(INBED)[0]
    FEATURECOUNTSTXT = os.path.splitext(FEATURECOUNTS)[0]+'.txt'

    if options.sam:
        sam_to_bam(SAM)

    bam_to_bed(BAM,READS)
    count_reads_in_exons(READS,INBED,FEATURECOUNTS)
    make_table(FEATURECOUNTS,FEATURECOUNTSTXT)

