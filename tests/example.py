
from gwplot import Gw
import pysam


region1 = ("chr1", 1, 20000)

gw = Gw("ref.fa")

# Add two 'rows' to the canvas
gw.add_bam("small.bam")
gw.add_bam("small.bam")

# Add the same region twice
gw.add_region(*region1)
gw.add_region(*region1)

# Open bam file using pysam
af = pysam.AlignmentFile("small.bam")

# Draw this top-left
aligns = list(af.fetch("chr1", 1, 20000))

# Draw this top-right
filt = [i for i in aligns if i.mapq > 20]

# Draw this bottom-right
filt2 = filt[:100]

# Drawing panels
gw.add_pysam_alignments(aligns, region_index=0, bam_index=0)
gw.add_pysam_alignments(filt, region_index=1, bam_index=0)
gw.add_pysam_alignments(filt2, region_index=1, bam_index=1)

gw.show()

