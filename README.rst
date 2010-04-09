NOTE: 

You can call any of the scripts with no options or with the -h option to get
help.


STEP 1: GFF db creation
-----------------------

Starting with a GFF file downloaded from FlyBase called data/dm3-r5.11.gff,
this command creates a GFF database in the current directory.  This step can
take upwards of 10 minutes, but you only have to do it once::

    ./makeGFFDB.py --gff data/dm3-r5.11.gff --gffdb dm3-r5.11.gff.db

The result is a sqlite3 database, dm3-r5.11.gff.db, which can be used by GFFutils.


STEP 2: Create a bed file of features of interest
-------------------------------------------------
Next, call the ``makeConstitutiveExons.py`` script on this newly created database
to get a BED file of exons that are found in all isoforms of a gene and that
do not overlap any other exons.  You only have to do this once::

    ./makeConstitutiveExons.py --gffdb dm3-r5.11.gff.db --bed const.exons.bed

The result is a BED file, ``const.exons.bed``, which contains the exons that are
found in all isoforms of a gene and that do not overlap any other exons in
other genes.

STEP 3: Count reads in features
-------------------------------
Next, for each SAM file or BAM file you have, call countReadsInFeatures.py
using the SAM/BAM file and the newly created const.exons.bed file.  You will
have to call this for as many files as you have.  If you provide a SAM file,
it will be automatically converted to a BAM. If you provide BAM files
directly to this script, it won't need to do that conversion and will run
more quickly::

    ./countReadsInFeatures.py --sam males_1.sam --bed const.exons.bed --prefix m1
    ./countReadsInFeatures.py --bam females_1.bam --bed const.exons.bed --prefix f1

Each of these runs will take a couple of minutes.  The output of each run is a .txt file, 
named with the prefix, then the basename of the BED file you provided as input, followed by
"-feature-counts.txt".  

So in the example above, you would end up with two files::

  m1-const.exons-feature-counts.txt
  f1-const.exons-feature-counts.txt

STEP 4: compile results
-------------------------
After you have many ``*-feature-counts.txt`` files, combine them with ``combineFeatureCounts.py``::

    ./combineFeatureCounts.py --out final-counts.txt m1-const.exons-feature-counts.txt f1-const.exons-feature-counts.txt

The result is a tab-delimited text file, final-counts.txt.  The first column
is the feature name, and the consecutive columns are the the counts in each
of the ``*-feature-counts.txt`` files you specified.  This can then be imported
into R or Python for further analysis.
