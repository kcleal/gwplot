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

## add_pysam_alignments

<div class="ml-6" markdown="1">

`add_pysam_alignments(self, pysam_alignments: List['AlignedSegment'],
                            region_index: int = -1,
                            bam_index: int = -1) -> 'Gw'`

Add a list of pysam alignments to Gw. Before using this function, you must add a
at least one region to Gw using `add_region` function, and a bam/cram file using `add_bam`.

Internally, the bam1_t data pointer is passed straight to Gw, so no copies made during drawing.
However, this means input pysam_alignments must 'outlive' any drawing calls made by Gw.

If using multiple regions or bams, use the `region_index` and `bam_index` arguments to 
indicate which panel to use for drawing the pysam alignment.

Note, this function assumes alignments are in position sorted order.

**Parameters:**
- `pysam_alignments` List['AlignedSegment']: List of alignments
- `region_index` (int): Region index to draw to (the column on the canvas)
- `bam_index` (int): Bam index to draw to (the row on the canvas)

**Returns:**
- `Gw`: Self for method chaining

**Example:**
```python
from gwplot import Gw
import pysam

region1 = ("chr1", 1, 20000)
gw = Gw("ref.fa").add_bam("small.bam").add_region(*region1)

# Use pysam to fetch some alignments
af = pysam.AlignmentFile("small.bam")
aligns = list(af.fetch(*region1))

gw.add_pysam_alignments(aligns)
gw.show()
```

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

## draw_background

<div class="ml-6" markdown="1">

`draw_background() -> None`

Draws the background colour. Can be useful for clearing the canvas without removing 
the underlying data.

</div>

---