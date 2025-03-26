---
layout: default
title: Managing Regions
parent: API Reference
nav_order: 3
---

## Managing Regions
{: .no_toc .text-delta }

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

---

### add_region
`add_region(chrom, start, end, marker_start=-1, marker_end=-1)`

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

---

### remove_region
`remove_region(index)`

Remove a genomic region from the visualisation.

**Parameters:**
- `index` (int): Index of the region to remove

**Returns:**
- `Gw`: Self for method chaining

---

### view_region
`view_region(chrom, start, end)`

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

### set_active_region_index
`set_active_region_index(index)`

Set the currently active region for dynamic visualisation.

**Parameters:**
- `index` (int): Index of the region to activate

**Returns:**
- `Gw`: Self for method chaining

---

### clear
`clear()`

Remove all data.

---

### clear_regions
`clear_regions()`

Remove all defined genomic regions.

---

### clear_alignments
`clear_alignments()`

Remove all loaded alignment data.

---
