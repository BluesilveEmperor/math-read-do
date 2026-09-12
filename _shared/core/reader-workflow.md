# Reader workflow — shared reading protocol

This is the cross-skill workflow for extracting structured content from a scientific paper. It is referenced by `nature-reader`, `nature-figure`, and `nature-paper2ppt`.

## Steps

### 1. Metadata extraction

Capture: title, authors (first + last + corresponding), journal, year, volume, pages, DOI, PMID if available, publication type (Article, Review, Resource, etc.), and any data/code availability URLs.

### 2. Structure extraction

Identify: headings and subheadings, abstract (structured if available), section order (Introduction, Results, Discussion, Methods), main figures and figure legends, tables and captions, supplementary figure/table references.

### 3. Argument extraction

Identify: central problem or phenomenon, gap or unresolved question, main claim or thesis, key experimental design, main results in logical order, validation and control experiments, author interpretation, limitations and caveats, and the broader significance.

### 4. Evidence-log building

For each figure/table panel: panel label (a, b, c...), experimental type, data type, sample size / n / replicates, key values and statistics, and the claim it supports.

### 5. Cross-checking

Compare: text claim vs. corresponding figure values, sample sizes in text vs. figure legends, result order vs. figure numbering, and supplementary references for main-text claims.

### 6. Output

A structured .md file or a bullet summary with confidence flags and source references.

## Confidence flags

| Flag | Meaning |
|---|---|
| ✅ Confirmed | Statement matches the source text and figures. |
| ⚠️ Ambiguous | Statement is based on partial or unclear source text. |
| ❓ Uncertain | Statement is inferred from incomplete information. |
| 🚫 Extracted | Statement is extracted but could not be independently verified. |
