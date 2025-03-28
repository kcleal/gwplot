from gwplot import Gw
import pysam
import os

root = os.path.abspath(os.path.dirname(__file__)).replace("/examples", "")
ref = root + "/tests/ref.fa"
bam = root + "/tests/small.bam"
roi = ("chr1", 1, 20000)

# Note, alignments must 'outlive' Gw
a = list(pysam.AlignmentFile(bam).fetch(*roi))

# Start Gw with a reference genome
with Gw(ref) as gw:
    gw.add_bam(bam).add_region(*roi)
    gw.add_pysam_alignments(a).show()
