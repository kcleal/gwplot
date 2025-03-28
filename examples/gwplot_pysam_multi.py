from gwplot import Gw
import pysam
import os
from PIL import Image

root = os.path.abspath(os.path.dirname(__file__)).replace("/examples", "")

# Bam files
bam_paths = [root + "/tests/small.bam", root + "/tests/small.bam"]
bams = [pysam.AlignmentFile(i) for i in bam_paths]

# Regions of interest
rois = [("chr1", 1, 20000), ("chr1", 10000, 11000)]

# First initialise Gw with data and regions
# This creates 4 panels on the image
gw = Gw(root + "/tests/ref.fa")
for bam in bam_paths:
    gw.add_bam(bam)
for region in rois:
    gw.add_region(*region)


# We need to collect reads and hold them in memory for Gw
# Also the panel index (row, column) is collected
collections = []
for region_idx, region in enumerate(rois):
    for bam_idx, bam in enumerate(bams):
        reads = list(bam.fetch(*region))
        collections.append((reads, region_idx, bam_idx))

# Now add them to Gw
for col in collections:
    gw.add_pysam_alignments(*col)

# Finally draw the screen
gw.draw()
img = Image.fromarray(gw.array())
img.show()
