---
layout: default
title: Home
nav_order: 1
description: "gwplot: a python library for plotting genomic sequencing data"
---

# gwplot: Python library for plotting genomics data

`gwplot` is a high-performance interactive genome browser for Python. It provides a Cython wrapper around 
the `libgw` C++ library, enabling rapid visualization of aligned sequencing reads, data tracks, 
and genome-variation datasets.

<br>

![Alt text](/assets/images/splash.png "Gwplot")


## Features

- **High-performance visualization** of genomic data including BAM files, VCF, BED, and other formats
- **Customizable themes and colors** for creating publication-quality visualizations
- **Multi-region support** for comparative genomics
- **Interactive mode** for dynamic exploration of genomic regions
- **Flexible output formats** including PNG, JPEG, and NumPy arrays for further processing
- **Built-in access** to common reference genomes

## Example Visualization

```python
from gwplot import Gw

# Initialize with a reference genome
gw = Gw("hg38")  # Can use reference path or built-in genome tag

# Add a BAM file and a region to visualize
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1100000)

# Draw and save an image
gw.draw().save_png("visualization.png")
```
