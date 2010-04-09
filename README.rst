Generating a feature-by-reads matrix
====================================

This is a collection of Python scripts that wrap ``samtools`` and ``bedtools``
programs to summarize short-read data on a feature-by-feature basis.  The first
steps describe the creation of a non-trivial feature set (constitutive exons
that do not overlap any other exons) and is a rather specific example, but the
last steps are quite generic and should be applicable to a wide range of
problems.

.. note:: 

    You can call any of the scripts with no options or with the -h option to
    get help.

STEP 0: Setup and installation
------------------------------
You will need these programs installed on your path:

    * samtools (http://samtools.sourceforge.net/)
    * bedtools (http://code.google.com/p/bedtools/)

For manipulating the GFF file (steps 1 and 2 below), you will also need to
install the ``GFFutils`` module (http://github.com/daler/GFFutils).  However,
if you already have a file containing the features you want counts for, then
skip right to Step 3 . . .

STEP 1: GFF db creation
-----------------------
Let's assume you're starting with a GFF file downloaded from FlyBase called
``data/dm3-r5.11.gff``.

If your mapped reads have chromosome names starting with "chr", then you may
need to add "chr" to the chromosome names in the GFF file with the following::

    awk '{print "chr"$0}' data/dm3-r5.11.gff > data/dm3-r5.11-with-chr.gff

Create a GFF database in the current directory.  This step can take upwards of
10 minutes, but you only have to do it once.::

    ./makeGFFDB.py --gff data/dm3-r5.11-with-chr.gff --gffdb dm3-r5.11-with-chr.gff.db

The result is a sqlite3 database, ``dm3-r5.11.gff.db``, which can be used by
``GFFutils``. You can read more about this database and what you can do with it
at http://github.com/daler/GFFutils. But for now . . .


STEP 2: Create a bed file of features of interest
-------------------------------------------------
Call the ``makeConstitutiveExons.py`` script on this newly created database to
get a BED file of exons that are found in all isoforms of a gene and that do
not overlap any other exons.  You only have to do this once.  If you want to
make other feature sets you can write your own script, perhaps using this one
as a template, and use that new BED file as input for the next step.

::

    ./makeConstitutiveExons.py --gffdb dm3-r5.11-with-chr.gff.db --bed const.exons.bed

The result is a BED file, ``const.exons.bed``, which contains the exons that are
found in all isoforms of a gene and that do not overlap any other exons in
other genes.  It's a BED4 file, something like this::

    chr3R	7784	8649	CG12581:3
    chr3R	9439	10200	CG12581:4
    chr2L	7529	8116	CG11023:1
    chr2L	8229	8589	CG11023:2
    chr2L	8668	9491	CG11023:3
    ....
    ....

STEP 3: Count reads in features
-------------------------------
Next, for each SAM file or BAM file you have, call ``countReadsInFeatures.py``
with a SAM/BAM file and the newly created ``const.exons.bed`` file.  This
script is essentially just a wrapper around ``samtools`` and ``bedtools``.

You will have to call this for as many files as you have.  Note that if you
provide a SAM file, it will be automatically converted to a BAM (for use with
``bamToBed``). This means if you provide a BAM file instead, it won't need to
do that conversion and this step will run much more quickly.  It's also
probably a good idea to add a prefix so you can keep track of the files
downstream::

    ./countReadsInFeatures.py --sam males_1.sam --bed const.exons.bed --prefix m1
    ./countReadsInFeatures.py --bam females_1.bam --bed const.exons.bed --prefix f1

Note that you can parallelize this step, but the advantage may depend on your
disk access speed.

Each of these runs will take a couple of minutes.  The output of each run is a
``.txt`` file, named with the prefix you provided, then the basename of the BED
file you provided as input, followed by ``-feature-counts.txt``.  

So in the example above, you would end up with these two files::

  m1-const.exons-feature-counts.txt
  f1-const.exons-feature-counts.txt

Each of these files has the following form (exon name, read count)::

    exon1   30
    exon2   900
    exon3   0

STEP 4: compile results
-----------------------
After you have many ``*-feature-counts.txt`` files, combine them with ``combineFeatureCounts.py``::

    ./combineFeatureCounts.py --out final-counts.txt m1-const.exons-feature-counts.txt f1-const.exons-feature-counts.txt

The result is a tab-delimited text file, ``final-counts.txt``.  The first column
is the feature name, and the consecutive columns are the the counts in each
of the ``*-feature-counts.txt`` files you specified.  This file will have the
form::

    exon1   30  29
    exon2   900 3
    exon3   0   10

This can now be imported into R or Python for further analysis.
