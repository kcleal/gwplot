---
layout: default
title: Loading Data
parent: API Reference
nav_order: 2
---

# Loading Data
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
- `ImportError`: If pysam could not be imported
- `IndexError`: If the region_index or bam_index are out of range
- `UserWarning`: If any normal collections are already present in the Gw object

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