---
layout: default
title: GwPalette
parent: API Reference
nav_order: 8
---


# GwPalette Class
{: .no_toc .text-delta }

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

---

The `GwPalette` class provides constants for all color and paint types used in GW visualisations. Use these constants with the `set_paint_ARBG` method to customise the appearance of GW.

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