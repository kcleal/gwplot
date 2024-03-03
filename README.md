gwplot
======

Installation via a pip install. Check if the [build is passing here](https://github.com/kcleal/gwplot/actions)

If it is, download the artifact and install one of the wheel files using pip. Otherwise build from source

Building from source macOS only
-------------------------------

On mac use brew to get library dependencies:

    brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz
    pip install -r requirements

Make sure this is added to .bashrc, .bash_profile or .zshrc. (run source ~/.bashrc to refresh):

    export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$(brew --prefix)/lib

Then build gw:
    
    cd ./gw
    make prep -j8
    CPPFLAGS+="-I$(brew --prefix)/include" LDFLAGS+="-L$(brew --prefix)/lib" make shared -j3
    cp lib/libgw/out/* $(brew --prefix)/lib
    cd ..

Finally, install gwplot:

    pip install . --no-build-isolation 


Test using:
    
    pip install -e .
    python -m unittest discover -s ./tests


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

# Apply commands, same as when using GW
plot.apply_command("chr2")
plot.apply_command("theme dark")

plot.draw_buffer_reads()  # Reads are held in memory
print('Memory:', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)  # 304 Mb

print(plot.RGBA_array())  # Raw pixel array image

import matplotlib.pyplot as plt
from PIL import Image

img = Image.fromarray(plot.RGBA_array())
plt.figure()
plt.imshow(img)
plt.show()


# list of functions
# getters and setters for many of the properties
import pprint
pprint.pprint([i for i in dir(plot) if "__" not in i])

['RGBA_array',
 'add_bam',
 'add_bams_from_iter',
 'add_region',
 'add_regions_from_iter',
 'add_track',
 'add_tracks_from_iter',
 'apply_command',
 'canvas_height',
 'canvas_width',
 'draw',
 'draw_buffer_reads',
 'expand_tracks',
 'indel_length',
 'log2_cov',
 'low_memory',
 'make_raster_surface',
 'max_coverage',
 'max_tlen',
 'pad',
 'raster_to_png',
 'remove_bam',
 'remove_region',
 'remove_track',
 'scroll_speed',
 'set_expand_tracks',
 'set_image_number',
 'set_indel_length',
 'set_log2_cov',
 'set_low_memory',
 'set_max_coverage',
 'set_max_tlen',
 'set_pad',
 'set_paint_ARBG',
 'set_scroll_speed',
 'set_small_indel_threshold',
 'set_snp_threshold',
 'set_soft_clip_threshold',
 'set_split_view_size',
 'set_start_index',
 'set_sv_arcs',
 'set_tab_track_height',
 'set_theme',
 'set_threads',
 'set_tlen_yscale',
 'set_variant_distance',
 'set_vcf_as_tracks',
 'set_ylim',
 'small_indel_threshold',
 'snp_threshold',
 'soft_clip_threshold',
 'split_view_size',
 'start_index',
 'sv_arcs',
 'tab_track_height',
 'theme',
 'threads',
 'tlen_yscale',
 'variant_distance',
 'vcf_as_tracks',
 'ylim']
```

Functionality to add
---------------------

- Image grid view
- Toggle Image grid view and alignment-view
- Scroll and zoom in/out functions
- Simulate a mouse click (provide x, y pixel coordinates)
