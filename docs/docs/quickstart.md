---
layout: default
title: Quickstart
nav_order: 3
permalink: /quickstart
---

# Quickstart
---

`Gw` is intialised with a reference genome path or tag (a tag is used below). Next, add
data tracks (bam files etc), and add a genomic region. Images can then be saved to common file
formats such as PNG, SVG and PDF:

```python
from gwplot import Gw

# Initialise with a reference genome
gw = Gw("hg38")  # Can use reference path or built-in genome tag

# Add a BAM file
gw.add_bam("sample.bam")

# Add a region to visualise
gw.add_region("chr1", 1000000, 1100000)

# Generate and save an image
gw.save_png("output.png")
```
---

## Using Built-in Reference Genomes

`gwplot` provides easy access to common reference genomes:

```python
from gwplot import Gw

# List available reference genomes
print(Gw.onlineGenomeTags())

# Use a built-in reference genome, fetch from online location
gw = Gw("t2t")
```

Available genome tags include: ce11, danrer11, dm6, hg19, hg38, grch37, grch38, t2t, mm39, pantro6, saccer3

---

## Working with Multiple Files and Regions

You can add multiple BAM files and other genomic data tracks:

```python
from gwplot import Gw

gw = Gw("hg38")

# Add multiple BAM files
gw.add_bam("normal.bam")
gw.add_bam("tumor.bam")

# Add a VCF file with variants and a BED file
gw.add_track("variants.vcf")
gw.add_track("annotations.bed")

# Visualise a region
gw.add_region("chr1", 1000000, 1100000)
gw.add_region("chr2", 1000000, 1100000)
gw.save_png("multi_track_visualisation.png")
```
---

## Customising the Visualisation

You can customise the appearance of your visualisation:

```python
from gwplot import Gw, GwPalette

gw = Gw("hg38")

# Set the theme
gw.set_theme("dark")  # Options: "dark", "slate", "igv"

# Customise specific colors
gw.set_paint_ARBG(GwPalette.DELETION, 255, 255, 0, 0)  # Red deletions
gw.set_paint_ARBG(GwPalette.INSERTION, 255, 0, 255, 0)  # Green insertions

# Set canvas size
gw.set_canvas_size(1200, 800)

# Adjust other visualisation parameters
gw.set_font_size(18)
gw.set_ylim(100)  # Set y-axis limit for coverage

# Add data and visualise
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1100000)
gw.save_png("customised_visualisation.png")
```

### Custom Themes

Themes and be created, saved and loaded using json file.

```python
from gw import GwPalette

custom_theme = {
    GwPalette.BACKGROUND: (255, 240, 240, 240),
    GwPalette.NORMAL_READ: (255, 100, 100, 100),
    GwPalette.DELETION: (255, 255, 0, 0)
}
gw.apply_theme(custom_theme)
gw.save_theme_to_json("custom_theme.json")
gw.load_theme_from_json("custom_theme.json")
```

---

## Using with Context Manager

You can use `gwplot` with a context manager for automatic resource cleanup:

```python
from gwplot import Gw

with Gw("hg38") as gw:
    gw.add_bam("sample.bam")
    gw.add_region("chr1", 1000000, 1100000)
    gw.save_png("output.png")
# Resources automatically cleaned up when exiting the with block
```
---

## Using with Jupyter Notebooks

`gwplot` works seamlessly in Jupyter notebooks:

```python
from gwplot import Gw
from IPython.display import display
bam_file = "https://github.com/kcleal/gw/releases/download/v1.0.0/demo1.bam"

with Gw("hg19", canvas_width=1000, canvas_height=400, theme="slate") as gw:
    gw.add_bam(bam_file)
    gw.add_region("chr8", 37047270, 37055161)
    display(gw.draw_image())
```

---

## Working with NumPy Arrays

You can convert visualisations to NumPy arrays for further processing:

```python
from gwplot import Gw
from PIL import Image

gw = Gw("hg38")
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1010000)
gw.draw()

# Get the visualisation as a NumPy array
img_array = gw.array()  # Returns RGBA data as height x width x 4 array

# Process with NumPy/PIL
img = Image.fromarray(img_array)
img.save("processed_visualisation.png")
```

---

## Commands

Access GW's command interface for advanced functionality:

```python
# Filter reads
gw.apply_command("filter mapq > 30")

# Count reads with specific properties
gw.apply_command("count seq contains TTAGGG")

# Go to a new location
gw.apply_command("chr8:1000000-2000000")

# Change theme
gw.apply_command("theme dark")
```

See GW documentation for more details https://kcleal.github.io/gw/docs/guide/Commands.html

---

## Interactive plots

`Gw` can support interactivity through mouse buttons and keyboard events, allowing 
interacive apps to be built. 

```python
from gwplot import Gw, GLFW

plot = Gw("hg19", canvas_width=1900, canvas_height=600).\
    add_bam("small.bam").\
    add_region("chr1", 1, 20000)

        
# Gw will cache state between drawing calls and interactions
plot.draw_interactive()

# Mouse-click event at canvas co-ordinates 
plot.mouse_event(x_pos=100, y_pos=200, button=GLFW.MOUSE_BUTTON_LEFT, action=GLFW.PRESS)
# Print any output messages from Gw
print(plot.flush_log())

# Re-draw
plot.draw_interactive()

img_data = plot.encode_as_png()  # For display to screen
```

See the `flask_server.py` demo in the `examples` directory.
