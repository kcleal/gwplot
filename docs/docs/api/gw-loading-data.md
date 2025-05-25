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

## clear

<div class="ml-6" markdown="1">

`clear() -> None`

Remove all data.

</div>

---

## clear_alignments

<div class="ml-6" markdown="1">

`clear_alignments() -> None`

Remove all loaded alignment data.

</div>

---

## clear_regions

<div class="ml-6" markdown="1">

`clear_regions() -> None`

Remove all defined genomic regions.

</div>

---
