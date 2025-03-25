# gwplot

`gwplot` is a plotting library for genomics data and a Python interface to GW, a high-performance interactive genome browser.

Visit the documentation for more details:  https://kcleal.github.io/gwplot/

[![Build Status](https://github.com/kcleal/gwplot/actions/workflows/build.yml/badge.svg)](https://github.com/kcleal/gwplot/actions)

## Overview

`gwplot` can be used for rapid visualization of:

- Aligned sequencing reads (BAM files)
- Genomic data tracks (VCF, BED, etc.)
- Structural variants and complex rearrangements
- Entire chromosomes with minimal memory usage


## Installation

### From PyPI

```bash
pip install gwplot
```

### Building from Source (macOS)

```bash
# Install dependencies with Homebrew
brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz

git clone --recursive https://github.com/kcleal/gwplot
cd gwplot
pip install -r requirements.txt
pip install .
```

## Quick Start

```python
from gwplot import Gw

# Initialize with reference genome
gw = Gw("reference.fa")

# Add data sources
gw.add_bam("sample.bam")
gw.add_track("variants.vcf")

# Set region to view
gw.add_region("chr1", 1000000, 1100000)

# Render and save
gw.draw()
gw.save_png("output.png")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)