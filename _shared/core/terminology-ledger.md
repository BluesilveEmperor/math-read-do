# Terminology Ledger

Build and maintain a Terminology Ledger while reading any source paper. This ensures that model names, gene/protein names, dataset names, metrics, and abbreviations stay identical across every output (reading notes, figures, slides, speaker notes).

## Rule

Whenever a source paper introduces a technical term, abbreviation, model name, dataset identifier, metric name, or gene/protein symbol, record it here.

## Template

```markdown
# Terminology Ledger — [Paper short title]

| Term | Full name / definition | Keep as | Notes |
|---|---|---|---|
| scRNA-seq | single-cell RNA sequencing | scRNA-seq | Hyphenated, lowercase 'c' |
| M1 | Macrophage type 1 pro-inflammatory | M1 | Roman numeral |
| F1 | F1 score | F1 | Capital F, numeral |
| AD | Alzheimer's disease | AD | First occurrence: "Alzheimer's disease (AD)" |
| ... | ... | ... | ... |
```

## Usage across skills

- `nature-reader`: records all technical terms during extraction.
- `nature-figure`: uses the ledger to generate consistent axis labels, captions, and legend entries.
- `nature-paper2ppt`: uses the ledger to keep term forms identical across every slide and speaker note.

## Global glossary additions

If a term appears in the source with an unusual or ambiguous form, add a consensus rule for consistent rendering across all three skills:

```markdown
| Consensus rule | Applies to |
|---|---|
| "fold change (FC)", not "fold-change" or "Fold Change" | All |
| Single-letter gene symbols: italic (e.g., *RHOX2*) | figure text only |
```
