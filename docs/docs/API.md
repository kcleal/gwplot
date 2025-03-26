---
title: API Reference
layout: home
nav_order: 4
has_children: true
permalink: /api
---

# API Reference
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

# Gw Class

The `Gw` class is the main interface to libgw (GW).

## `Gw(reference, **kwargs)`

Initialize the GW object with a reference genome and optional parameters.

**Parameters:**
- `reference` (str): Path to reference genome file or genome tag
- `**kwargs`: Additional parameters to configure the browser

**Example:**
```python
# Initialize with multiple options
gw = Gw("reference.fa", theme="dark", threads=4,
         sv_arcs=True, canvas_width=800, canvas_height=600)
```
---

## Gw Class Methods

## `onlineGenomeTags()`

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

## Loading Data

## `add_bam(path)`

Add a BAM file to the visualization.

**Parameters:**
- `path` (str): Path to the BAM file

**Returns:** 
- `Gw`: Self for method chaining

**Example:**
```python
gw.add_bam("sample.bam")
```
---

## `remove_bam(index)`

Remove a BAM file from the visualization.

**Parameters:**
- `index` (int): Index of the BAM file to remove

**Returns:**
- `Gw`: Self for method chaining

---

## `add_track(path, vcf_as_track=True, bed_as_track=True)`

Add a genomic data track to the visualization.

**Parameters:**
- `path` (str): Path to the track file (VCF, BED, etc.)
- `vcf_as_track` (bool, optional): Whether to display VCF files as tracks
- `bed_as_track` (bool, optional): Whether to display BED files as tracks

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Add a VCF file as a track
gw.add_track("variants.vcf")

# Add a BED file
gw.add_track("features.bed")
```
---

## `remove_track(index)`

Remove a data track from the visualization.

**Parameters:**
- `index` (int): Index of the track to remove

**Returns:**
- `Gw`: Self for method chaining

---

## Managing Regions

## `add_region(chrom, start, end, marker_start=-1, marker_end=-1)`

Add a genomic region for visualization. Setting the markers will result in a small triangle being drawn at
the genomic position.

**Parameters:**
- `chrom` (str): Chromosome name
- `start` (int): Start position
- `end` (int): End position
- `marker_start` (int, optional): Start position for a marker, -1 for no marker
- `marker_end` (int, optional): End position for a marker, -1 for no marker

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Add a region with markers
gw.add_region("chr1", 1000000, 1100000, 1050000, 1060000)
```

---

## `remove_region(index)`

Remove a genomic region from the visualization.

**Parameters:**
- `index` (int): Index of the region to remove

**Returns:**
- `Gw`: Self for method chaining

---

## `view_region(chrom, start, end)`

Clear existing regions and view a specific genomic region.

**Parameters:**
- `chrom` (str): Chromosome
- `start` (int): Region start
- `end` (int): Region end

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
# Clear existing regions and view a new one
gw.view_region("chr1", 1000000, 1100000)
```

---

## `set_active_region_index(index)`

Set the currently active region for dynamic visualization.

**Parameters:**
- `index` (int): Index of the region to activate

**Returns:**
- `Gw`: Self for method chaining

---

## `clear()`

Remove all data.

---

## `clear_regions()`

Remove all defined genomic regions.

---

## `clear_alignments()`

Remove all loaded alignment data.

---

## Visualisation

## `draw()`

Draw the visualization to the raster surface. Suitable for non-interactive visualizations.

**Returns:**
- `Gw`: Self for method chaining

---

## `draw_interactive(clear_buffer=False)`

Draw the visualization to the raster surface. Caches state for using with interactive functions.

**Parameters:**
- `clear_buffer` (bool): Clears any buffered reads before re-drawing

**Returns:**
- `Gw`: Self for method chaining

---

## `draw_image()`

Draw the visualization and return it as a PIL Image.

**Returns:**
- `PIL.Image`: The visualization as a PIL Image

**Example:**
```python
# Get the visualization as a PIL Image
img = gw.draw_image()
img.save("output.png")
```

---

## Saving images

## `save_png(path)`

Save the current raster image to a PNG file.

**Parameters:**
- `path` (str): Path to save the PNG file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_png("visualization.png")
```

---

## `save_pdf(path)`

Save the plot to a PDF file.

**Parameters:**
- `path` (str): Path to save the PDF file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_pdf("visualization.pdf")
```

---

## `save_svg(path)`

Save the plot to a SVG file.

**Parameters:**
- `path` (str): Path to save the SVG file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_svg("visualization.svg")
```

---

## `encode_as_png(compression_level=6)`

Encode the current canvas as PNG and return the binary data.

**Parameters:**
- `compression_level` (int): PNG compression level (0-9)

**Returns:**
- `bytes`: PNG encoded image data

## `encode_as_jpeg(quality=80)`

Encode the current canvas as JPEG and return the binary data.

**Parameters:**
- `quality` (int): JPEG quality (0-100)

**Returns:**
- `bytes`: JPEG encoded image data

---

## `array()`

Convert the raster image to a numpy array.

**Returns:**
- `numpy.ndarray` or `None`: RGBA image data as a 3D numpy array (height × width × 4) or None if the raster surface hasn't been created

**Example:**
```python
# Get the visualization as a numpy array
img_array = gw.draw().array()
```

---

## Display Settings

## `set_canvas_width(width)`

Set the canvas width and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels

**Returns:**
- `Gw`: Self for method chaining

---

## `set_canvas_height(height)`

Set the canvas height and recreate the raster surface.

**Parameters:**
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

---

## `set_canvas_size(width, height)`

Set both canvas width and height and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

---

## `set_theme(theme_name)`

Set a predefined visualization theme.

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

## `set_paint_ARBG(paint_enum, a, r, g, b)`

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

## `apply_theme(theme_dict)`

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

## `load_theme_from_json(filepath)`

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

## `save_theme_to_json(filepath)`

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

## `set_font_size(size)`

Set the font size.

**Parameters:**
- `size` (int): Sets the font size

**Returns:**
- `Gw`: Self for method chaining

## `set_font_name(name)`

Set the font name.

**Parameters:**
- `name` (str): Sets the font name

**Returns:**
- `Gw`: Self for method chaining

---

# Configuration Properties

`gwplot` provides numerous properties that can be accessed or modified to configure the visualization:

## Thread and Memory Settings

- `threads` / `set_threads(num)`: Get/set the number of processing threads
- `low_memory` / `set_low_memory(size)`: Get/set low memory mode threshold in base-pairs

## Visualization Parameters

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

# Interactive Controls

## `apply_command(command)`

Apply a GW command string.

**Parameters:**
- `command` (str): GW command to execute (e.g., "filter", "count", etc.)

---

## `key_press(key, scancode, action, mods)`

Process a key press event.

**Parameters:**
- `key` (int): Key code
- `scancode` (int): Scan code
- `action` (int): Key action code
- `mods` (int): Modifier keys

---

## `mouse_event(x_pos, y_pos, button, action)`

Process a mouse event.

**Parameters:**
- `x_pos` (float): Mouse x-position
- `y_pos` (float): Mouse y-position
- `button` (int): Mouse button code
- `action` (int): Mouse action code

---

# GwPalette Class

The `GwPalette` class provides constants for all color and paint types used in GW visualizations. Use these constants with the `set_paint_ARBG` method to customize the appearance of GW.

### Background Colors

- `BACKGROUND`: Main background color for the visualization
- `BACKGROUND_TILED`: Tiled background color
- `BACKGROUND_MENU`: Menu background color

### Primary Read Feature Colors

- `NORMAL_READ`: Normal read color
- `DELETION`: Deletion color
- `DUPLICATION`: Duplication color
- `INVERSION_FORWARD`: Forward inversion color
- `INVERSION_REVERSE`: Reverse inversion color
- `TRANSLOCATION`: Translocation color
- `INSERTION`: Insertion color
- `SOFT_CLIP`: Soft clip color

### Nucleotide Colors

- `NUCLEOTIDE_A`: Adenine (A) nucleotide color
- `NUCLEOTIDE_T`: Thymine (T) nucleotide color
- `NUCLEOTIDE_C`: Cytosine (C) nucleotide color
- `NUCLEOTIDE_G`: Guanine (G) nucleotide color
- `NUCLEOTIDE_N`: N (any/unknown) nucleotide color

### Coverage and Track Colors

- `COVERAGE`: Coverage plot color
- `TRACK`: Generic data track color
- `NORMAL_READ_MQ0`: Map-quality=0 normal read color
- `DELETION_MQ0`: Map-quality=0 deletion color
- `DUPLICATION_MQ0`: Map-quality=0 duplication color
- `INVERSION_FORWARD_MQ0`: Map-quality=0 forward inversion color
- `INVERSION_REVERSE_MQ0`: Map-quality=0 reverse inversion color
- `TRANSLOCATION_MQ0`: Map-quality=0 translocation color
- `SOFT_CLIP_MQ0`: Map-quality=0 soft clip color

### BigWig and Special Features

- `BIGWIG`: BigWig track display color
- `REGION_OF_INTEREST`: Region of interest highlight color

### Mate-Related Colors

- `MATE_PRIMARY`: Primary mate pair color
- `MATE_SECONDARY`: Secondary mate pair color
- `MATE_UNMAPPED`: Unmapped mate color

### Edge and Line Colors

- `SPLIT_READ`: Split read edge color
- `SELECTED_ELEMENT`: Selected element highlight color
- `LINE_JOINS`: Line color for join connections
- `LINE_COVERAGE`: Line color for coverage plots
- `LINE_LIGHT_JOINS`: Light line color for join connections
- `LINE_GTF_JOINS`: Line color for GTF feature joins
- `LINE_LABEL`: Line color for labels
- `LINE_BRIGHT`: Bright line color for emphasis

### Text Colors

- `TEXT_DELETION`: Text color for deletion annotations
- `TEXT_INSERTION`: Text color for insertion annotations
- `TEXT_LABELS`: Text color for general labels
- `TEXT_BACKGROUND`: Text background color

### Markers and Modifications

- `MARKERS`: Color for genomic markers
- `METHYLATED_C`: 5-methylcytosine (5mC) color for epigenetic modification
- `HYDROXYMETHYLATED_C`: 5-hydroxymethylcytosine (5hmC) color for epigenetic modification
- `OTHER_MODIFICATION`: Color for other base modifications