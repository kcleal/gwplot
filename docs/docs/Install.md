---
title: Install
layout: default
has_children: false
nav_order: 2
---

# Installation
---

### From PyPI

Base installation:

```bash
pip install gwplot
```

`gwplot` also has `pillow` as an optional runtime dependency.

### Building from Source 

#### MacOS

Install dependencies using homebrew (shown), or conda.
```bash
brew install fontconfig freetype glfw htslib jpeg-turbo libpng xz
```

Clone repository with GW submodule, install using pip.
```bash
git clone --recursive https://github.com/kcleal/gwplot
cd gwplot
pip install -e . -v  # Use editable mode for development

# Run tests, need -e option when using pip install
python -m unittest discover -s ./tests
```

The prefix path (i.e. homebrew or conda environments) is usually
auto-detected, but this can be manually set using:
```bash
pip install . --config-settings=setup-args=-Dprefix_path=~/miniconda3
```

#### Linux

For linux users, building is more convoluted. You will need to install htslib, glfw and freetype. An
example build script can be found in `ci/manylinux-build-deps`
