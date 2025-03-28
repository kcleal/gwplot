---
layout: default
title: Managing Data
parent: API Reference
nav_order: 2
---

# Managing Data
{: .no_toc }
---

- TOC
{:toc}

---

## add_bam

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

## remove_bam

<div class="ml-6" markdown="1">

`remove_bam(index: int) -> 'Gw'`

Remove a BAM file from the visualisation.

**Parameters:**
- `index` (int): Index of the BAM file to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---

## add_pysam_alignments

<div class="ml-6" markdown="1">

`add_pysam_alignments(pysam_alignments: List['AlignedSegment'], region_index: int = -1, bam_index: int = -1) -> 'Gw'`

Adds alignments from a pysam list to a region. Creates a raster surface if needed. Calls clear_alignments if non-pysam collections in use.

**Parameters:**
- `pysam_alignments` (List[AlignedSegment]): List of pysam AlignedSegments
- `region_index` (int, optional): The region index to draw to for multi-region support. If -1, the last added region will be used
- `bam_index` (int, optional): The bam index to draw to for multi-region support. If -1, the last added bam will be used

**Returns:**
- `Gw`: Self for method chaining

**Raises:**
- `IndexError`: If the region_index or bam_index are out of range
- `UserWarning`: If any normal collections are already present in the Gw object

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
- If a region_index and bam_index are not provided, data is added to the most-recently-added region and bam.

</div>

---

## clear_alignments

<div class="ml-6" markdown="1">

`clear_alignments() -> None`

Remove all loaded alignment data.

</div>

---

## add_track

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

## remove_track

<div class="ml-6" markdown="1">

`remove_track(index: int) -> 'Gw'`

Remove a data track from the visualisation.

**Parameters:**
- `index` (int): Index of the track to remove

**Returns:**
- `Gw`: Self for method chaining

</div>

---