gwplot
======

Installation will eventually be via a pip install. Check if the [build is passing here](https://github.com/kcleal/gwplot/actions)

If it is, download the artifact and install one of the wheel files using pip. Otherwise build from source

Building from source
--------------------

On mac use brew to get library dependencies:

        brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz

Then use:
    
    bash ci/osx-deps
    pip install -r requirements
    pip install -e . ; install_name_tool -change libgw.dylib @loader_path/libgw.dylib gwplot/interface.cpython-310-darwin.so; pip install . --no-build-isolation -v;
    

Test using:

   python -m unittest discover -s ./tests 

Continuous integration
----------------------

Build GW the prerequisites (htslib, glfw3, libgw) using either:
    
    bash ci/osx-deps
    bash ci/manylinux-deps


Demo
----

```python
from gwplot import Gw
import time
import resource

t0 = time.time()
plot = Gw('/Users/sbi8kc2/Documents/data/db/hg19/ucsc.hg19.fa')
plot.add_bam('/Users/sbi8kc2/Desktop/HG002.bam')
plot.add_region('chr1', 1, 1000000)
plot.draw()  # Reads are streamed
plot.raster_to_png("out.png")

print('Time (s):', time.time() - t0)  # 0.21 seconds
print('Memory:', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)  # 94 Mb

plot.draw_buffer_reads()  # Reads are held in memory
print('Memory:', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)  # 304 Mb

print(plot.RGBA_array())  # Raw pixel array image

import matplotlib.pyplot as plt
from PIL import Image

img = Image.fromarray(plot.RGBA_array())
plt.figure()
plt.imshow(img)
plt.show()
```

Functionality to add
---------------------

- Remove bam
- Remove region
- Add track BED, GFF3, GTF, VCF/BCF
- Image grid view
- Toggle Image grid view and alignment-view
- Scroll and zoom in/out functions
- Simulate a mouse click (provide x, y pixel coordinates)
- Apply commands
