# gwplot

`gwplot` is a plotting library for genomics data and a Python interface to GW, a high-performance interactive genome browser.

Visit the [documentation for more details](https://kcleal.github.io/gwplot/)

[![Build Status](https://github.com/kcleal/gwplot/actions/workflows/build.yml/badge.svg)](https://github.com/kcleal/gwplot/actions)


## Installation

```bash
pip install gwplot
```

## Quick Start

```python
from gwplot import Gw

# Initialise with reference genome
gw = Gw("reference.fa")

# Add data sources
gw.add_bam("sample.bam")
gw.add_track("variants.vcf")

# Set region to view
gw.add_region("chr1", 1000000, 1100000)

# Render and save
gw.save_png("output.png")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)