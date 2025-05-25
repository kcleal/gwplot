---
title: API Reference
layout: default
nav_order: 4
has_children: true
permalink: /api
---

# API Reference
{: .no_toc }
---

- TOC
{:toc}

---

# Gw class


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

## Gw.onlineGenomeTags

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

## Gw.apply_command

<div class="ml-6" markdown="1">

`apply_command(command: str) -> 'Gw`

Apply a GW command string.

**Parameters:**
- `command` (str): GW command to execute (e.g., "filter", "count", etc.)

</div>

---

# Loading data

Methods for adding data to Gw.


## Gw.add_bam

<div class="ml-6" markdown="1">

`add_bam(path: str) -> 'Gw'`

Add a BAM file to the visualisation.

**Parameters:**
- `path` (str): Path to the BAM file

**Returns:** 
- `Gw`: Self for method chaining

**Example:**
```python
gw.add_bam("sample.bam")
```

</div>

---

## Gw.remove_bam

<div class="ml-6" markdown="1">

`remove_bam(index: int) -> 'Gw'`

Remove a BAM file from the visualisation.

**Parameters:**
- `index` (int): Index of the BAM file to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.add_pysam_alignments

<div class="ml-6" markdown="1">

`add_pysam_alignments(self, pysam_alignments: List['AlignedSegment'],
                            region_index: int = -1,
                            bam_index: int = -1) -> 'Gw'`

Add a list of pysam alignments to Gw. Before using this function, you must add a
at least one region to Gw using `add_region` function, and a bam/cram file using `add_bam`.

Internally, the bam1_t data pointer is passed straight to Gw, so no copies are made during drawing.
However, this means input pysam_alignments must 'outlive' any drawing calls made by Gw.

If using multiple regions or bams, use the `region_index` and `bam_index` arguments to 
indicate which panel to use for drawing the pysam alignment.

Note, this function assumes alignments are in position sorted order. Also, 
pysam alignments can not be mixed with ‘normal’ Gw alignment tracks.

**Parameters:**
- `pysam_alignments` List['AlignedSegment']: List of alignments
- `region_index` (int): Region index to draw to (the column on the canvas)
- `bam_index` (int): Bam index to draw to (the row on the canvas)

**Returns:**
- `Gw`: Self for method chaining

**Raises**:

- `IndexError`: If the region_index or bam_index are out of range
- `RuntimeError`: If any normal collections are already present in the Gw object

**Example:**
```python
import pysam
from gwplot import Gw

# Open alignment file
bam = pysam.AlignmentFile("sample.bam")

# Define region of interest
region = ("chr1", 1000000, 1050000)

# Filter alignments based on custom criteria
filtered_reads = []
for read in bam.fetch(*region):
    # Only keep high-quality reads with specific characteristics
    if read.mapping_quality > 30 and not read.is_duplicate and not read.is_secondary:
        filtered_reads.append(read)

# Visualize only the filtered reads
gw = Gw("hg38")
gw.add_bam("sample.bam")  # Reference to original BAM still needed
gw.add_region(*region)
gw.add_pysam_alignments(filtered_reads)
gw.show()
```

</div>

---

## Gw.add_track

<div class="ml-6" markdown="1">

`add_track(path: str, vcf_as_track: bool = True, bed_as_track: bool = True) -> 'Gw'`

Add a genomic data track to the visualisation.

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

</div>

---

## Gw.remove_track

<div class="ml-6" markdown="1">

`remove_track(index: int) -> 'Gw'`

Remove a data track from the visualisation.

**Parameters:**
- `index` (int): Index of the track to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.clear

<div class="ml-6" markdown="1">

`clear() -> None`

Remove all data.

</div>

---

## Gw.clear_alignments

<div class="ml-6" markdown="1">

`clear_alignments() -> None`

Remove all loaded alignment data.

</div>

---

## Gw.clear_regions

<div class="ml-6" markdown="1">

`clear_regions() -> None`

Remove all defined genomic regions.

</div>

---

# Region management

Methods for adding data to Gw.


## Gw.add_region

<div class="ml-6" markdown="1">

`add_region(chrom: str, start: int, end: int, marker_start: int = -1, marker_end: int = -1) -> 'Gw'`

Add a genomic region for visualisation. Setting the markers will result in a small triangle being drawn at
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

Markers in regions allow you to highlight specific genomic positions within a larger region.
When you set marker positions using `add_region`, small triangular indicators will appear
at those positions in the visualisation.

**Example:**
```python
# Add a region with markers highlighting a gene of interest
gw.add_region("chr1", 1000000, 1100000, marker_start=1025000, marker_end=1075000)
```

This is particularly useful for:
- Highlighting the boundaries of a gene or feature within a larger context
- Marking specific variants or points of interest in your visualisation
- Creating visual references for discussing specific genomic locations

The markers appear as small triangles at the specified positions:
- A downward-pointing triangle at the marker_start position
- A downward-pointing triangle at the marker_end position

</div>

---

## Gw.remove_region

<div class="ml-6" markdown="1">

`remove_region(index: int) -> 'Gw'`

Remove a genomic region from the visualisation.

**Parameters:**
- `index` (int): Index of the region to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.view_region

<div class="ml-6" markdown="1">

`view_region(chrom: str, start: int, end: int) -> 'Gw'`

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

</div>

---

## Gw.draw_background

<div class="ml-6" markdown="1">

`draw_background() -> None`

Draws the background colour. Can be useful for clearing the canvas without removing 
the underlying data.

</div>

---

# Saving and displaying images

Methods for saving and displaying images.


## Gw.draw

<div class="ml-6" markdown="1">

`draw(clear_buffer: bool = False) -> 'Gw'`

Draw the visualisation to the raster surface. Caches state for using with interactive functions.

Creates the raster surface if it doesn't exist yet.

**Parameters:**
- `clear_buffer` (bool): Clears any buffered reads before re-drawing

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.draw_image

<div class="ml-6" markdown="1">

`draw_image() -> Image.Image`

Draw the visualisation and return it as a PIL Image.

**Returns:**
- `PIL.Image`: The visualisation as a PIL Image

**Raises:**
- `ImportError`: If Pillow could not be imported

**Example:**
```python
# Get the visualisation as a PIL Image
img = gw.draw_image()
img.save("output.png")
```

</div>

---

## Gw.show

<div class="ml-6" markdown="1">

`show() -> None`

Convenience method for showing the image on screen. Equivalent to gw.draw_image().show()

**Raises:**
- `ImportError`: If Pillow could not be imported

</div>

---

## Gw.save_png

<div class="ml-6" markdown="1">

`save_png(path: str) -> 'Gw'`

Draws and saves the raster canvas to a PNG file.

**Parameters:**
- `path` (str): Path to save the PNG file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_png("visualisation.png")
```

</div>

---

## Gw.save_pdf

<div class="ml-6" markdown="1">

`save_pdf(path: str) -> 'Gw'`

Draws and saves a PDF file using the current configuration.

**Parameters:**
- `path` (str): Path to save the PDF file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_pdf("visualization.pdf")
```

</div>

---

## Gw.save_svg

<div class="ml-6" markdown="1">

`save_svg(path: str) -> 'Gw'`

Saves an SVG file using the current configuration.

**Parameters:**
- `path` (str): Path to save the SVG file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_svg("visualization.svg")
```

</div>

---

## Gw.encode_as_png

<div class="ml-6" markdown="1">

`encode_as_png(compression_level: int = 6) -> Optional[bytes]`

Encode the current canvas as PNG and return the binary data.

**Parameters:**
- `compression_level` (int): PNG compression level (0-9)

**Returns:**
- `bytes` or `None`: PNG encoded image data or None if the raster surface hasn't been created

</div>

---

## Gw.encode_as_jpeg

<div class="ml-6" markdown="1">

`encode_as_jpeg(quality: int = 80) -> Optional[bytes]`

Encode the current canvas as JPEG and return the binary data.

**Parameters:**
- `quality` (int): JPEG quality (0-100)

**Returns:**
- `bytes` or `None`: JPEG encoded image data or None if the raster surface hasn't been created

**Raises:**
- `RuntimeError`: If image encoding failed

</div>

---

## Gw.array

<div class="ml-6" markdown="1">

`array() -> Optional[np.ndarray]`

Convert the pixel data to a numpy array using zero-copy interface.

**Returns:**
- `numpy.ndarray` or `None`: RGBA image data as a 3D numpy array (height × width × 4) or None if the raster surface hasn't been created

**Example:**
```python
# Get the visualization as a numpy array
img_array = gw.draw().array()
```

</div>

---

## Gw.make_raster_surface

<div class="ml-6" markdown="1">

`make_raster_surface(width: int = -1, height: int = -1) -> 'Gw'`

Create a raster surface for rendering. This is usually called automatically by drawing functions
if needed, but can be called explicitly to pre-allocate the rendering surface.

**Parameters:**
- `width` (int, optional): Width of the raster surface. If -1, uses the current canvas width.
- `height` (int, optional): Height of the raster surface. If -1, uses the current canvas height.

**Returns:**
- `Gw`: Self for method chaining

**Raises:**
- `RuntimeError`: If the raster surface could not be created

**Example:**
```python
# Explicitly create a raster surface
gw.make_raster_surface(1200, 800)
```

</div>

---

# Settings

Methods for setting/getting properties of Gw.


## Gw.canvas_width

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

## Gw.set_canvas_width

<div class="ml-6" markdown="1">

`set_canvas_width(width: int) -> 'Gw'`

Set the canvas width and recreate the raster surface.

**Parameters:**
- `width` (int): New canvas width in pixels

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.canvas_height

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

## Gw.set_canvas_height

<div class="ml-6" markdown="1">

`set_canvas_height(height: int) -> 'Gw'`

Set the canvas height and recreate the raster surface.

**Parameters:**
- `height` (int): New canvas height in pixels

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.canvas_size

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

## Gw.set_canvas_size

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

## Gw.theme

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

## Gw.set_theme

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

## Gw.set_paint_ARBG

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

## Gw.apply_theme

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

## Gw.load_theme_from_json

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

## Gw.save_theme_to_json

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

## Gw.font_size

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

## Gw.set_font_size

<div class="ml-6" markdown="1">

`set_font_size(size: int) -> 'Gw'`

Set the font size.

**Parameters:**
- `size` (int): Sets the font size

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.font_name

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

## Gw.set_font_name

<div class="ml-6" markdown="1">

`set_font_name(name: str) -> 'Gw'`

Set the font name.

**Parameters:**
- `name` (str): Sets the font name

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.set_image_number

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

## Gw.__array_interface__

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

# Interactive

Methods for interacting with Gw state.


## Gw.apply_command

<div class="ml-6" markdown="1">

`apply_command(command: str) -> 'Gw`

Apply a GW command string.

**Parameters:**
- `command` (str): GW command to execute (e.g., "filter", "count", etc.)

</div>

---

## Gw.key_press

<div class="ml-6" markdown="1">

`key_press(key: int, scancode: int, action: int, mods: int) -> None`

Process a key press event.

**Parameters:**
- `key` (int): Key code
- `scancode` (int): Scan code
- `action` (int): Key action code
- `mods` (int): Modifier keys

</div>

---

## Gw.mouse_event

<div class="ml-6" markdown="1">

`mouse_event(x_pos: float, y_pos: float, button: int, action: int) -> None`

Process a mouse event.

**Parameters:**
- `x_pos` (float): Mouse x-position
- `y_pos` (float): Mouse y-position
- `button` (int): Mouse button code (can be "left", "right")
- `action` (int): Mouse action code

</div>

---

## Gw.flush_log

<div class="ml-6" markdown="1">

`flush_log() -> str`

Returns and clears the GW log. This is useful for retrieving messages
generated by GW during operation.

**Returns:**
- `str`: GW log as a python string

**Example:**
```python
# Get any messages from GW
log_messages = gw.flush_log()
print(log_messages)
```

</div>

---

## Gw.set_active_region_index

<div class="ml-6" markdown="1">

`set_active_region_index(index: int) -> 'Gw'`

Set the currently active region for visualisation. Subsequent mouse/key interactions will
affect this region index.

**Parameters:**
- `index` (int): Index of the region to activate

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## Gw.clear_buffer

<div class="ml-6" markdown="1">

`clear_buffer -> bool`

Property that indicates whether the read buffer should be cleared on the next draw.

**Returns:**
- `bool`: Read buffer needs clearing

**Example:**
```python
# Check if buffer needs clearing
if gw.clear_buffer:
    print("Buffer will be cleared on next draw")
```

</div>

---

## Gw.set_clear_buffer

<div class="ml-6" markdown="1">

`set_clear_buffer(state: bool) -> None`

Set the clear_buffer status.

**Parameters:**
- `state` (bool): If True, buffer will be cleared on next draw

**Example:**
```python
# Force buffer clearing on next draw
gw.set_clear_buffer(True)
```

</div>

---

## Gw.redraw

<div class="ml-6" markdown="1">

`redraw -> bool`

Property that indicates whether a re-draw needs to occur. Check this after
some event e.g. command or mouse button.

**Returns:**
- `bool`: Image needs to be re-drawn

**Example:**
```python
# Check if a redraw is needed
if gw.redraw:
    gw.draw()
```

</div>

---

## Gw.set_redraw

<div class="ml-6" markdown="1">

`set_redraw(state: bool) -> None`

Set the redraw status. For dynamic applications, set this to False after
a drawing call to avoid unnecessary redraws.

**Parameters:**
- `state` (bool): If True, a redraw will be triggered

**Example:**
```python
# Set redraw status
gw.set_redraw(False)  # Prevent automatic redraw
```

</div>

---

# GwPalette class

The `GwPalette` class provides constants for all color and paint types used in GW visualisations. 
Use these constants with the `set_paint_ARBG` method to customise the appearance of GW, or
the `apply_theme` method of Gw.

### Background Colors

- `BACKGROUND`: Main background color for the visualisation
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