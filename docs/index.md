---
layout: default
title: Home
nav_order: 1
description: "gwplot: a python library for plotting genomic sequencing data"
---

# gwplot
---

`gwplot` is a plotting library for genomics data and a Python interface to [GW](https://github.com/kcleal/gw), 
a high-performance interactive genome browser.

Features of `gwplot`:

- **Very fast visualisation** of genomics data (BAM/CRAM, VCF, BED, and other formats)
- **Customisable themes and colors** for creating high-quality visualisations
- **Multi-regions and data tracks** for comparative genomics
- **Flexible output formats** including PNG, PDF, SVG, JPEG, and NumPy arrays for further processing
- **Built-in access** to common reference genomes
- **Interactive mode** for dynamic creating dynamic apps

Install from PyPI:

```bash
pip install gwplot
```

Quick example:

```python
from gwplot import Gw

# Initialise with a reference genome
gw = Gw("hg38")

# Add a BAM file and a region to visualise
gw.add_bam("sample.bam")
gw.add_region("chr1", 1000000, 1100000)

# Draw and save an image
gw.save_pdf("region.pdf")
```

![Alt text](/assets/images/splash1.png "Gwplot")


