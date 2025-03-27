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

`add_bam(path)`

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
`remove_bam(index)`

Remove a BAM file from the visualisation.

**Parameters:**
- `index` (int): Index of the BAM file to remove

**Returns:**
- `Gw`: Self for method chaining

---

## add_track
`add_track(path, vcf_as_track=True, bed_as_track=True)`


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
---

## remove_track
`remove_track(index)`

Remove a data track from the visualisation.

**Parameters:**
- `index` (int): Index of the track to remove

**Returns:**
- `Gw`: Self for method chaining

---
