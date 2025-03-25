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
