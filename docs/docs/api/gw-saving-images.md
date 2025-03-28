---
layout: default
title: Saving Images / Data
parent: API Reference
nav_order: 5
---

# Saving / Displaying Images
{: .no_toc }
---

- TOC
{:toc}

---


## draw

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

## draw_image

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

## show

<div class="ml-6" markdown="1">

`show() -> None`

Convenience method for showing the image on screen. Equivalent to gw.draw_image().show()

**Raises:**
- `ImportError`: If Pillow could not be imported

</div>

---

## save_png

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

## save_pdf

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

## save_svg

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

## encode_as_png

<div class="ml-6" markdown="1">

`encode_as_png(compression_level: int = 6) -> Optional[bytes]`

Encode the current canvas as PNG and return the binary data.

**Parameters:**
- `compression_level` (int): PNG compression level (0-9)

**Returns:**
- `bytes` or `None`: PNG encoded image data or None if the raster surface hasn't been created

</div>

---

## encode_as_jpeg

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

## array

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

## make_raster_surface

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

## clear_buffer

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

## set_clear_buffer

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

## redraw

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

## set_redraw

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