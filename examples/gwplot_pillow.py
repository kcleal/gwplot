from gwplot import Gw
import os
from PIL import Image
import numpy as np

root = os.path.abspath(os.path.dirname(__file__)).replace("/examples", "")

# Initialize with reference genome
gw = Gw(root + "/tests/ref.fa")

# Add data sources
gw.add_bam(root + "/tests/small.bam")

# Set region to view
gw.add_region("chr1", 1, 20000)

# Render
gw.draw()

# Convert to Image
img = Image.fromarray(gw.array())

# Display to screen
img.show()
