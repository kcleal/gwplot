
---
layout: default
title: Gw Class
parent: API Reference
nav_order: 1
---

## Gw Class

`Gw(reference, **kwargs)`

The `Gw` class is the main interface to libgw (GW). Initialise the GW object 
with a reference genome and optional parameters.


**Parameters:**
- `reference` (str): Path to reference genome file or genome tag
- `**kwargs`: Additional parameters to configure the browser

**Example:**
```python
# Initialise with multiple options
gw = Gw("reference.fa", theme="dark", threads=4,
         sv_arcs=True, canvas_width=800, canvas_height=600)
```
---

## onlineGenomeTags

`onlineGenomeTags()`

Returns a dictionary of available online reference genome tags. Use a local genome 
for much better performance.

**Returns:**
- `dict`: Keys are genome tags, values are genome paths

**Example:**
```python
# List available genome tags
tags = Gw.onlineGenomeTags()
print(tags)
```
---
