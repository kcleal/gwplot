---
title: Install
layout: default
has_children: false
nav_order: 2
---

# Installation

### From PyPI

```bash
pip install gwplot
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

## Building from Source

First install dependencies. 

On macOS, you can install the required dependencies using Homebrew:

```bash
brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz
```

Then:

```bash
git clone https://github.com/kcleal/gwplot.git
cd gwplot
pip install -r requirements.txt
pip install .
# Run tests
python -m unittest discover -s ./tests
```