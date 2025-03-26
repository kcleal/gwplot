---
layout: default
title: Config
parent: API Reference
nav_order: 6
---

# Display Settings
{: .no_toc .text-delta }
---

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

---

## set_canvas_width
`set_canvas_width(width)`

Set the canvas width and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels

**Returns:**
- `Gw`: Self for method chaining

---

# set_canvas_height
`set_canvas_height(height)`

Set the canvas height and recreate the raster surface.

**Parameters:**
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

---

# set_canvas_size
`set_canvas_size(width, height)`

Set both canvas width and height and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

---

# set_theme
`set_theme(theme_name)`

Set a predefined visualisation theme.

**Parameters:**
- `theme_name` (str): Theme name, must be one of "slate", "dark", or "igv"

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Set the dark theme
gw.set_theme("dark")
```

---

# set_paint_ARBG
`set_paint_ARBG(paint_enum, a, r, g, b)`

Set the ARGB color for a specific paint type.

**Parameters:**
- `paint_enum` (int): Paint type enumeration value from GwPalette
- `a` (int): Alpha channel value (0-255)
- `r` (int): Red channel value (0-255)
- `g` (int): Green channel value (0-255)
- `b` (int): Blue channel value (0-255)

**Example:**
```python
# Set normal read color to dark blue
gw.set_paint_ARBG(GwPalette.NORMAL_READ, 255, 0, 0, 128)
```

---

# apply_theme
`apply_theme(theme_dict)`

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

---

# load_theme_from_json
`load_theme_from_json(filepath)`

Load and apply a theme from a JSON file.

**Parameters:**
- `filepath` (str): Path to the JSON theme file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.load_theme_from_json("custom_theme.json")
```

---

# save_theme_to_json
`save_theme_to_json(filepath)`

Save the current theme settings to a JSON file.

**Parameters:**
- `filepath` (str): Path where the JSON theme file should be saved

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Save the current theme for future use
gw.save_theme_to_json("my_theme.json")
```

---

# set_font_size
`set_font_size(size)`

Set the font size.

**Parameters:**
- `size` (int): Sets the font size

**Returns:**
- `Gw`: Self for method chaining

## set_font_name
`set_font_name(name)`

Set the font name.

**Parameters:**
- `name` (str): Sets the font name

**Returns:**
- `Gw`: Self for method chaining

---

# Configuration Properties

`gwplot` provides numerous properties that can be accessed or modified to configure the visualisation:

## Thread and Memory Settings

- `threads` / `set_threads(num)`: Get/set the number of processing threads
- `low_memory` / `set_low_memory(size)`: Get/set low memory mode threshold in base-pairs

## Visualisation Parameters

- `indel_length` / `set_indel_length(length)`: Get/set indel length threshold for labeling
- `ylim` / `set_ylim(limit)`: Get/set the y-axis limit
- `split_view_size` / `set_split_view_size(size)`: Get/set the split view size
- `pad` / `set_pad(padding)`: Get/set the padding between elements
- `max_coverage` / `set_max_coverage(coverage)`: Get/set maximum coverage value
- `max_tlen` / `set_max_tlen(length)`: Get/set maximum template length
- `log2_cov` / `set_log2_cov(enabled)`: Get/set log2 coverage display
- `tlen_yscale` / `set_tlen_yscale(scale)`: Get/set template length y-scale
- `expand_tracks` / `set_expand_tracks(expand)`: Get/set track expansion
- `vcf_as_tracks` / `set_vcf_as_tracks(as_tracks)`: Get/set VCF display as tracks
- `sv_arcs` / `set_sv_arcs(arcs)`: Get/set structural variant arcs display
- `scroll_speed` / `set_scroll_speed(speed)`: Get/set the scroll speed
- `tab_track_height` / `set_tab_track_height(height)`: Get/set track tab height
- `start_index` / `set_start_index(index)`: Get/set coordinate start index (0 or 1)
- `soft_clip_threshold` / `set_soft_clip_threshold(threshold)`: Get/set soft clip threshold
- `small_indel_threshold` / `set_small_indel_threshold(threshold)`: Get/set small indel threshold
- `snp_threshold` / `set_snp_threshold(threshold)`: Get/set SNP threshold
- `variant_distance` / `set_variant_distance(distance)`: Get/set variant distance threshold

---
