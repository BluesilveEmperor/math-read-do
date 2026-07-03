# Output files, citation, and quality rules

## Citation and attribution rules

Include source information:

- title slide: paper title, authors if useful, journal, year, DOI if available,
- figure slides: small labels such as `Source: Fig. 2b, Nature, 2024`,
- adapted or redrawn content: label as `整理自` or `改绘自`.

## Output files

### 1. `output/final_presentation_cn.pptx`
The main deliverable: a complete Chinese PPTX deck.

### 2. `output/qa_report.md`
Short quality report: PPTX creation status; slide count; figures inserted; self-review defects.

### 3. `output/assets/figures/`
Extracted or cropped figure assets.

### 4. `output/asset_manifest.md`
Figure asset traceability file.

## Quality rules

- Build the `.pptx` whenever tooling is available.
- Do not fabricate results, methods, numbers, or figure details.
- Do not overload slides with text.
- Ensure figures are readable at presentation scale.
- Run at least one self-review and corrective revision pass.
- Document uncertainty and missing source material clearly.

## Fallback rules

If only partial content is available: still create a useful PPTX structure when possible; clearly mark uncertain slides or missing details; write `output/qa_report.md` explaining what could not be verified.
