from gwplot import Gw
import os
root = os.path.abspath(os.path.dirname(__file__))


# Initialize with reference genome
gw = Gw(root + "../tests/ref.fa")

# Add data sources
gw.add_bam(root + "/../tests/small.bam")

# Set region to view
gw.add_region("chr1", 1, 20000)

# Render and save
gw.draw()
gw.save_png("output.png")
