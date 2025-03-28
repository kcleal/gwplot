---
layout: default
title: Managing Regions
parent: API Reference
nav_order: 3
---

# Managing Regions
{: .no_toc }
---

- TOC
{:toc}

---

## add_region

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

</div>

---

## Using Markers in Regions

<div class="ml-6" markdown="1">

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

## remove_region

<div class="ml-6" markdown="1">

`remove_region(index: int) -> 'Gw'`

Remove a genomic region from the visualisation.

**Parameters:**
- `index` (int): Index of the region to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## view_region

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

## set_active_region_index

<div class="ml-6" markdown="1">

`set_active_region_index(index: int) -> 'Gw'`

Set the currently active region for visualisation.

**Parameters:**
- `index` (int): Index of the region to activate

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## clear

<div class="ml-6" markdown="1">

`clear() -> None`

Remove all data.

</div>

---

## clear_regions

<div class="ml-6" markdown="1">

`clear_regions() -> None`

Remove all defined genomic regions.

</div>

---

## clear_alignments

<div class="ml-6" markdown="1">

`clear_alignments() -> None`

Remove all loaded alignment data.

</div>

---

## Using PyPSAM Alignments (Advanced)

<div class="ml-6" markdown="1">

The `add_pysam_alignments` method allows for integration with the Pysam library,
enabling you to filter and manipulate alignments before visualisation.

**Complex Example:**
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
gw.save_png("filtered_high_quality_reads.png")
```
Notes:
- Pysam alignments must not be freed before Gw, otherwise you will have a dangling pointer!
- Pysam alignments can not be mixed with 'normal' Gw alignment tracks.
- `add_pysam_alignments` can take a region_index and bam_index for multi-panel images. If these are not provided, data is added to the most-recently-added bam and region.

</div>

---