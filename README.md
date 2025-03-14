# gwplot

Python interface to GW, a high-performance interactive genome browser.

[![Build Status](https://github.com/kcleal/gwplot/actions/workflows/build.yml/badge.svg)](https://github.com/kcleal/gwplot/actions)

## Overview

`gwplot` provides a Python wrapper for the GW genome browser, enabling rapid visualization of:

- Aligned sequencing reads (BAM files)
- Genomic data tracks (VCF, BED, etc.)
- Structural variants and complex rearrangements
- Entire chromosomes with minimal memory usage

GW's high-performance design enables visualization of large genomic regions at speeds significantly faster than other genome browsers, while maintaining a small memory footprint.

## Installation

### From PyPI

```bash
pip install gwplot
```

### From Pre-built Wheels

Check the [latest successful build](https://github.com/kcleal/gwplot/actions) on GitHub Actions, download the artifact, and install the appropriate wheel file:

```bash
pip install gwplot-X.Y.Z-cpXX-cpXX-PLATFORM.whl
```

### Building from Source (macOS)

```bash
# Install dependencies with Homebrew
brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz

# Clone repository with submodules
git clone --recursive https://github.com/kcleal/gwplot
cd gwplot

# Install development version
pip install -r requirements.txt
pip install -e . -v

# Run tests
python -m unittest discover -s ./tests
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

## Key Features

### Fluent Interface

All setter methods return `self`, enabling method chaining for a more concise API:

```python
gw = (Gw("reference.fa")
      .set_theme("dark")
      .set_threads(4)
      .add_bam("sample.bam")
      .add_region("chr1", 1000000, 1100000)
      .draw())
```

### Context Manager Support

Use with the `with` statement for automatic resource cleanup:

```python
with Gw("reference.fa") as gw:
    gw.add_bam("sample.bam")
    gw.add_region("chr8", 10000000, 20000000)
    gw.draw_image()
# Resources automatically cleaned up
```

### Customizable Visualization

Create custom themes or modify individual color elements:

```python
# Set individual colors
gw.set_paint_ARBG(Paint.DELETION, 255, 255, 0, 0)  # Bright red for deletions
gw.set_paint_ARBG(Paint.NUCLEOTIDE_A, 255, 0, 200, 0)  # Green for adenine

# Save custom theme
gw.save_theme_to_json("my_theme.json")

# Load theme in another session
gw = Gw("reference.fa").load_theme_from_json("my_theme.json")
```

### Memory-Efficient Visualization

GW provides two rendering modes for different use cases:

```python
# Standard mode: loads reads into memory
gw.draw()

# Streaming mode: processes reads on-the-fly for lower memory usage
gw.draw_stream()
```

### Integration with Python Visualization Tools

Easily integrate with matplotlib, PIL, or other Python libraries:

```python
import matplotlib.pyplot as plt
from PIL import Image

# Get visualization as a PIL Image
img = gw.draw_image()

# Display with matplotlib
plt.figure(figsize=(12, 8))
plt.imshow(img)
plt.show()

# Or convert to numpy array
array_data = gw.array()
```

## Key Concepts

- **Regions**: Genomic intervals to visualize
- **Themes**: Color schemes for visualization ("slate", "dark", or "igv")
- **Paint Types**: Individual color elements that can be customized

## Main Methods

### Initialization

```python
# Basic initialization
gw = Gw("reference.fa")

# With options
gw = Gw("reference.fa", 
         theme="dark",           # Visual theme
         threads=4,              # Processing threads
         canvas_width=1200,      # Image width
         canvas_height=800,      # Image height
         sv_arcs=True,           # Show SV arcs
         max_coverage=100)       # Max coverage display
```

### Data Loading

```python
# Add BAM files
gw.add_bam("sample.bam")

# Add tracks (VCF, BED, etc.)
gw.add_track("variants.vcf")
gw.add_track("features.bed", bed_as_track=True)

# Define regions to view
gw.add_region("chr1", 1000000, 1100000)
gw.add_region("chr2", 2000000, 2100000)  # Multiple regions supported
```

### Rendering

```python
# Draw with reads in memory
gw.draw()

# Draw with streaming (lower memory usage)
gw.draw_stream()

# Get as PIL Image
img = gw.draw_image()

# Save to file
gw.save_png("output.png")
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)