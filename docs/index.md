---
layout: default
title: Home
nav_order: 1
description: "gwplot: a python library for plotting genomic sequencing data"
---

# gwplot

`gwplot` is a plotting library for genomics data and a Python interface to GW, a high-performance interactive genome browser.

Install using:

```bash
pip install gwplot
```

<br>

![Alt text](/assets/images/splash1.png "Gwplot")


## Features

- **High-performance visualization** of genomic data including BAM files, VCF, BED, and other formats
- **Customizable themes and colors** for creating high-quality visualizations
- **Multi-regions and data tracks** for comparative genomics
- **Interactive mode** for dynamic exploration of genomic regions
- **Flexible output formats** including PNG, PDF, SVG, JPEG, and NumPy arrays for further processing
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
gw.save_pdf("region.pdf")
```
