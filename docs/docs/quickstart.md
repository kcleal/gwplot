---
layout: default
title: Quickstart
nav_order: 3
permalink: /quickstart
---

# Quickstart

This guide will help you get started quickly with `gwplot` for genomic visualization.

## Basic Usage

Here's a simple example to create your first genomic visualization:

```python
from gwplot import Gw

# Initialize with a reference genome
gw = Gw("hg38")  # Can use reference path or built-in genome tag

# Add a BAM file
gw.add_bam("sample.bam")

# Add a region to visualize
gw.add_region("chr1", 1000000, 1100000)

# Generate and save an image
gw.draw().save_png("output.png")
```

## Using Built-in Reference Genomes

`gwplot` provides easy access to common reference genomes:

```python
from gwplot import Gw

# List available reference genomes
print(Gw.onlineGenomeTags())

# Use a built-in reference genome, fetch from online location
gw = Gw("hg38")
```

Available genome tags include: ce11, danrer11, dm6, hg19, hg38, grch37, grch38, t2t, mm39, pantro6, saccer3

## Working with Multiple Files

You can add multiple BAM files and other genomic data tracks:

```python
from gwplot import Gw

gw = Gw("hg38")

# Add multiple BAM files
gw.add_bam("normal.bam")
gw.add_bam("tumor.bam")

# Add a VCF file with variants
gw.add_track("variants.vcf")

# Add a BED file with annotations
gw.add_track("annotations.bed")

# Visualize a region
gw.add_region("chr1", 1000000, 1100000)
gw.draw().save_png("multi_track_visualization.png")
```

## Customizing the Visualization

You can customize the appearance of your visualization:

```python
from gwplot import Gw, GwPalette

gw = Gw("hg38")

# Set the theme
gw.set_theme("dark")  # Options: "dark", "slate", "igv"

# Customize specific colors
gw.set_paint_ARBG(GwPalette.DELETION, 255, 255, 0, 0)  # Red deletions
gw.set_paint_ARBG(GwPalette.INSERTION, 255, 0, 255, 0)  # Green insertions

# Set canvas size
gw.set_canvas_size(1200, 800)

# Adjust other visualization parameters
gw.set_font_size(18)
gw.set_ylim(100)  # Set y-axis limit for coverage

# Add data and visualize
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1100000)
gw.draw().save_png("customized_visualization.png")
```

## Using with Context Manager

You can use `gwplot` with a context manager for automatic resource cleanup:

```python
from gwplot import Gw

with Gw("hg38") as gw:
    gw.add_bam("sample.bam")
    gw.add_region("chr1", 1000000, 1100000)
    gw.draw().save_png("output.png")
# Resources automatically cleaned up when exiting the with block
```

## Multi-Region Comparison

Visualize multiple genomic regions at once:

```python
from gwplot import Gw

gw = Gw("hg38", canvas_width=1200, canvas_height=900)

# Add multiple regions
gw.add_region("chr1", 1000000, 1010000)
gw.add_region("chr2", 2000000, 2010000)

gw.add_bam("sample.bam")
```

## Using with Jupyter Notebooks

`gwplot` works seamlessly in Jupyter notebooks:

```python
from gwplot import Gw
from IPython.display import Image, display

gw = Gw("hg38", canvas_width=1000, canvas_height=400)
gw.add_bam(bam_file)
gw.add_region("chr1", 1000000, 1010000)

# Draw and get PNG data
gw.draw()
png_data = gw.encode_as_png()

# Display in the notebook
display(Image(data=png_data))
```

## Working with NumPy Arrays

You can convert visualizations to NumPy arrays for further processing:

```python
from gwplot import Gw
from PIL import Image

gw = Gw("hg38")
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1010000)
gw.draw()

# Get the visualization as a NumPy array
img_array = gw.array()  # Returns RGBA data as height x width x 4 array

# Process with NumPy/PIL
img = Image.fromarray(img_array)
img.save("processed_visualization.png")
```

### Commands

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

