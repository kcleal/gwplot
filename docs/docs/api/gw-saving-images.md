---
layout: default
title: Saving Images / Data
parent: API Reference
nav_order: 5
---

# Saving images
{: .no_toc }

- TOC
{:toc}

---

## save_png
`save_png(path)`

Save the current raster image to a PNG file.

**Parameters:**
- `path` (str): Path to save the PNG file

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
gw.save_png("visualisation.png")
```

---

## save_pdf
`save_pdf(path)`

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

## save_svg
`save_svg(path)`

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

## encode_as_png
`encode_as_png(compression_level=6)`

Encode the current canvas as PNG and return the binary data.

**Parameters:**
- `compression_level` (int): PNG compression level (0-9)

**Returns:**
- `bytes`: PNG encoded image data

## encode_as_jpeg
`encode_as_jpeg(quality=80)`

Encode the current canvas as JPEG and return the binary data.

**Parameters:**
- `quality` (int): JPEG quality (0-100)

**Returns:**
- `bytes`: JPEG encoded image data

---

## array
`array()`

Convert the raster image to a numpy array.

**Returns:**
- `numpy.ndarray` or `None`: RGBA image data as a 3D numpy array (height × width × 4) or None if the raster surface hasn't been created

**Example:**
```python
# Get the visualization as a numpy array
img_array = gw.draw().array()
```

---
