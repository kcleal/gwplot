---
layout: default
title: Visualisation
parent: API Reference
nav_order: 4
---

## Visualisation

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

---

### `draw()`

Draw the visualisation to the raster surface. Suitable for non-interactive visualisations.

**Returns:**
- `Gw`: Self for method chaining

---

### `draw_interactive(clear_buffer=False)`

Draw the visualisation to the raster surface. Caches state for using with interactive functions.

**Parameters:**
- `clear_buffer` (bool): Clears any buffered reads before re-drawing

**Returns:**
- `Gw`: Self for method chaining

---

### `draw_image()`

Draw the visualisation and return it as a PIL Image.

**Returns:**
- `PIL.Image`: The visualisation as a PIL Image

**Example:**
```python
# Get the visualisation as a PIL Image
img = gw.draw_image()
img.save("output.png")
```

---
