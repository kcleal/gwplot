gwplot
======

Installation will eventually be via a pip install. Check if the [build is passing here](https://github.com/kcleal/gwplot/actions)

If it is, download the artifact and install one of the wheel files using pip. Otherwise build from source

Building from source
--------------------

Install the prerequisites (htslib, glfw3) using either:
    
    bash ci/osx-deps
    bash ci/manylinux-deps

Then use:

    pip install -r requirements
    pip install .

If you want to do development, use this, which will prevent skia being downloaded every time:

    SKIP_PREP=1 pip install . --no-build-isolation -v

Test using:

    python -m unittest

Demo
----

Depends on numpy. Recommended to have Pillow and matplotlib

```python
from gwplot import Gw
import time

t0 = time.time()
plot = Gw('/Users/sbi8kc2/Documents/data/db/hg19/ucsc.hg19.fa')
plot.add_bam('/Users/sbi8kc2/Desktop/HG002.bam')
plot.add_region('chr1', 1, 1000000)
plot.draw()
plot.raster_to_png("out.png")

print(time.time() - t0)  # 0.255 seconds

print(plot.RGBA_array())  # Raw pixel array image

import matplotlib.pyplot as plt
from PIL import Image

img = Image.fromarray(plot.RGBA_array())
plt.figure()
plt.imshow(img)
plt.show()
```

