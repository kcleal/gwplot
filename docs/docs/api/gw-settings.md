---
layout: default
title: Settings and properties
parent: API Reference
nav_order: 6
---

# Settings and properties
{: .no_toc }
---


- TOC
{:toc}

---

## canvas_width

<div class="ml-6" markdown="1">

`canvas_width -> int`

Property that returns the current canvas width in pixels.

**Returns:**
- `int`: Current canvas width

**Example:**
```python
# Get current canvas width
width = gw.canvas_width
print(f"Canvas width: {width}px")
```

</div>

---

## set_canvas_width

<div class="ml-6" markdown="1">

`set_canvas_width(width: int) -> 'Gw'`

Set the canvas width and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## canvas_height

<div class="ml-6" markdown="1">

`canvas_height -> int`

Property that returns the current canvas height in pixels.

**Returns:**
- `int`: Current canvas height

**Example:**
```python
# Get current canvas height
height = gw.canvas_height
print(f"Canvas height: {height}px")
```

</div>

---

## set_canvas_height

<div class="ml-6" markdown="1">

`set_canvas_height(height: int) -> 'Gw'`

Set the canvas height and recreate the raster surface.

**Parameters:**
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## canvas_size

<div class="ml-6" markdown="1">

`canvas_size -> Tuple[int, int]`

Property that returns the current canvas dimensions.

**Returns:**
- `tuple`: (width, height) in pixels

**Example:**
```python
# Get current canvas dimensions
width, height = gw.canvas_size
print(f"Canvas dimensions: {width}x{height}px")
```

</div>

---

## set_canvas_size

<div class="ml-6" markdown="1">

`set_canvas_size(width: int, height: int) -> 'Gw'`

Set both canvas width and height and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## theme

<div class="ml-6" markdown="1">

`theme -> str`

Property that returns the current theme name.

**Returns:**
- `str`: Current theme name ("slate", "dark", or "igv")

**Example:**
```python
# Get current theme
theme = gw.theme
print(f"Current theme: {theme}")
```

</div>

---

## set_theme

<div class="ml-6" markdown="1">

`set_theme(theme_name: str) -> 'Gw'`

Set a predefined visualisation theme.

**Parameters:**
- `theme_name` (str): Theme name, must be one of "slate", "dark", or "igv"

**Returns:**
- `Gw`: Self for method chaining

**Raises:**
- `ValueError`: If theme_name is not one of the supported themes

**Example:**
```python
# Set the dark theme
gw.set_theme("dark")
```

</div>

---

## set_paint_ARBG

<div class="ml-6" markdown="1">

`set_paint_ARBG(paint_enum: int, a: int, r: int, g: int, b: int) -> 'Gw'`

Set the ARGB color for a specific paint type.

**Parameters:**
- `paint_enum` (int): Paint type enumeration value from GwPalette enum or Paint class
  (e.g., GwPalette.NORMAL_READ, GwPalette.DELETION)
- `a` (int): Alpha channel value (0-255)
- `r` (int): Red channel value (0-255)
- `g` (int): Green channel value (0-255)
- `b` (int): Blue channel value (0-255)

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Set normal read color to dark blue
gw.set_paint_ARBG(GwPalette.NORMAL_READ, 255, 0, 0, 128)
```

</div>

---

## apply_theme

<div class="ml-6" markdown="1">

`apply_theme(theme_dict: Dict[int, Tuple[int, int, int, int]]) -> 'Gw'`

Apply a custom theme using a dictionary of paint types and colors.

**Parameters:**
- `theme_dict` (dict): Dictionary mapping Paint constants to ARGB tuples (alpha, red, green, blue)

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
custom_theme = {
    GwPalette.BACKGROUND: (255, 240, 240, 240),
    GwPalette.NORMAL_READ: (255, 100, 100, 100),
    GwPalette.DELETION: (255, 255, 0, 0)
}
gw.apply_theme(custom_theme)
```

</div>

---

## load_theme_from_json

<div class="ml-6" markdown="1">

`load_theme_from_json(filepath: str) -> 'Gw'`

Load and apply a theme from a JSON file.

**Parameters:**
- `filepath` (str): Path to the JSON theme file

**Returns:**
- `Gw`: Self for method chaining

**Raises:**
- `ValueError`: If the color name is not recognised

**Example:**
```python
gw.load_theme_from_json("custom_theme.json")
```

</div>

---

## save_theme_to_json

<div class="ml-6" markdown="1">

`save_theme_to_json(filepath: str) -> 'Gw'`

Save the current theme settings to a JSON file.

This function exports all paint colors from the current theme
to a JSON file that can later be loaded with load_theme_from_json.

**Parameters:**
- `filepath` (str): Path where the JSON theme file should be saved

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Save the current theme for future use
gw.save_theme_to_json("my_theme.json")
```

</div>

---

## font_size

<div class="ml-6" markdown="1">

`font_size -> int`

Property that returns the current font size.

**Returns:**
- `int`: Current font size

**Example:**
```python
# Get current font size
size = gw.font_size
print(f"Current font size: {size}")
```

</div>

---

## set_font_size

<div class="ml-6" markdown="1">

`set_font_size(size: int) -> 'Gw'`

Set the font size.

**Parameters:**
- `size` (int): Sets the font size

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## font_name

<div class="ml-6" markdown="1">

`font_name -> str`

Property that returns the current font name.

**Returns:**
- `str`: Current font name

**Example:**
```python
# Get current font name
font = gw.font_name
print(f"Current font: {font}")
```

</div>

---

## set_font_name

<div class="ml-6" markdown="1">

`set_font_name(name: str) -> 'Gw'`

Set the font name.

**Parameters:**
- `name` (str): Sets the font name

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## set_image_number

<div class="ml-6" markdown="1">

`set_image_number(x: int, y: int) -> 'Gw'`

Set the grid dimensions for image view when using tiled display.

**Parameters:**
- `x` (int): Number of columns in the grid
- `y` (int): Number of rows in the grid

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Set up a 2x3 grid layout
gw.set_image_number(2, 3)
```

</div>

---

## __ array_interface __

<div class="ml-6" markdown="1">

The `Gw` object implements the NumPy array interface protocol, allowing it to be directly
converted to a NumPy array without copying the underlying data.

**Returns:**
- `dict` or `None`: Describes the underlying image buffer if the raster surface exists, otherwise None

**Example:**
```python
import numpy as np

# Convert to numpy array with zero-copy
gw.draw()  # Ensure the image is rendered
arr = np.asarray(gw)  # Uses __array_interface__ automatically
```

</div>

---

# Configuration Properties

`gwplot` provides numerous properties that can be accessed or modified to configure the visualisation:

## Thread and Memory Settings

- `threads` / `set_threads(num: int) -> 'Gw'`: Get/set the number of processing threads
- `low_memory` / `set_low_memory(size: int) -> 'Gw'`: Get/set low memory mode threshold in base-pairs

## Visualisation Parameters

- `indel_length` / `set_indel_length(length: int) -> 'Gw'`: Get/set indel length threshold for labeling
- `ylim` / `set_ylim(limit: int) -> 'Gw'`: Get/set the y-axis limit
- `split_view_size` / `set_split_view_size(size: int) -> 'Gw'`: Get/set the split view size
- `pad` / `set_pad(padding: int) -> 'Gw'`: Get/set the padding between elements
- `max_coverage` / `set_max_coverage(coverage: int) -> 'Gw'`: Get/set maximum coverage value
- `max_tlen` / `set_max_tlen(length: int) -> 'Gw'`: Get/set maximum template length
- `log2_cov` / `set_log2_cov(enabled: bool) -> 'Gw'`: Get/set log2 coverage display
- `tlen_yscale` / `set_tlen_yscale(scale: bool) -> 'Gw'`: Get/set template length y-scale
- `expand_tracks` / `set_expand_tracks(expand: bool) -> 'Gw'`: Get/set track expansion
- `vcf_as_tracks` / `set_vcf_as_tracks(as_tracks: bool) -> 'Gw'`: Get/set VCF display as tracks
- `sv_arcs` / `set_sv_arcs(arcs: bool) -> 'Gw'`: Get/set structural variant arcs display
- `scroll_speed` / `set_scroll_speed(speed: float) -> 'Gw'`: Get/set the scroll speed
- `tab_track_height` / `set_tab_track_height(height: float) -> 'Gw'`: Get/set track tab height
- `start_index` / `set_start_index(index: int) -> 'Gw'`: Get/set coordinate start index (0 or 1)
- `soft_clip_threshold` / `set_soft_clip_threshold(threshold: int) -> 'Gw'`: Get/set soft clip threshold
- `small_indel_threshold` / `set_small_indel_threshold(threshold: int) -> 'Gw'`: Get/set small indel threshold
- `snp_threshold` / `set_snp_threshold(threshold: int) -> 'Gw'`: Get/set SNP threshold
- `variant_distance` / `set_variant_distance(distance: int) -> 'Gw'`: Get/set variant distance threshold

---