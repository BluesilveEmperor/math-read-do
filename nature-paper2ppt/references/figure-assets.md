# Figure assets reference

## When to use this file

Open this reference when you need to select, extract, crop, or quality-check figure or table assets from the source paper.

## Figure selection criteria

Select figures that directly support the paper's argument:

1. **Design / workflow** – shows what the authors did and in what order.
2. **Main evidence** – the central result the paper wants the reader to believe.
3. **Validation / robustness** – controls, orthogonal validation, replication.
4. **Mechanism / model / synthesis** – summary or mechanistic diagram.
5. **Practical / conceptual implication** – the "so what" panel.

Filter out figures that are:
- redundant with the selected main evidence,
- dense supplement-style panels that are not discussed in the main text,
- highly domain-specific technical quality checks.

## When the source paper's own architecture / framework figure is missing

Many slides need a **model architecture diagram**, **research framework diagram**, or **experiment pipeline diagram** that the original paper does not provide, or provides in an unusable form (raster only, missing labels, low-res). For those cases, do **not** redraw in python-pptx or matplotlib — instead:

- Use the sibling `nature-framework` sub-skill (`../../nature-framework/SKILL.md`).
- It takes a typed JSON spec (`diagram_type: model | framework | route | system | structure | experiment`) and produces a self-contained inline-SVG HTML figure with embedded CJK fonts.
- Embed the HTML in the PPTX as a web-viewer object, or render a screenshot at 300 dpi for static embedding.
- Always check the showcase 11-item receipt before locking the slide.

**Hard constraint — experiment pipeline figures**: `experiment` (实验流程图) is the only `diagram_type` whose **final version MUST be drawn AFTER the experiment runs**. PRISMA/CONSORT-style flow diagrams in particular record real numbers (initial n, exclusions, group sizes, dropouts, final analysis n, evaluation metrics) — none of which can be fabricated. A "predicted flow" can be drawn at the proposal stage, but the **final version must wait until the experimental record is curated** (`raw_metrics.csv` / `reproducibility_assessment.json` / Phase-5 statistical summary). The other five types — `framework`, `route`, `model` (provisional until code runs), `system`, `structure` — are not blocked on experimental data and can be authored at any stage. See [`../../nature-framework/SKILL.md` → "Hard rule: experiment-data dependency per type"](../../nature-framework/SKILL.md) for the full rule.

## Extraction rules

### From PDF (PyMuPDF)

- Render the page to 300 dpi, or higher for full-page figure panels.
- Crop to the figure bounding box using the page coordinates from the PDF layout.
- Save as PNG or JPEG, 300 dpi minimum, in `output/assets/figures/`.
- Name format: `fig{number}_{panel}.png` (e.g., `fig2_b.png`).
- Always include a small inset or trim for the crop boundary to be visually clear.

### From vector source (when available)

- Accept SVG or PDF source when the author provides it.
- Render at the highest resolution available; do not upsample or smooth.
- Save as PNG only for PPTX insertion; keep original SVG/PDF in archive if available.

### Dense multi-panel figures

For figures with 4+ panels arranged in a grid:
- Crop the full figure and insert it at full width only if all panels are readable.
- Otherwise, crop individual panels or rows and distribute them across multiple slides.
- Do not shrink a multi-panel figure to fit into a single upright slide; it will be illegible.

## Crop boundaries

- Include the panel label (a, b, c ...) in the crop when the label clearly indicates the panel.
- Do not crop too tightly — leave ~5px of padding around the panel boundary.
- When two panels share an axis label or legend, include them together.
- When a figure has a key callout (arrow, asterisk, bracket), include it in the crop.

## Quality checks

Before inserting the figure into the deck:
- Open the cropped file and verify: readable at 25% zoom (simulates projection legibility).
- Check for: text that is too small to read, compressed interpolation artifacts, missing panel labels, visible scan lines or moiré patterns.
- Re-crop or upgrade the extraction method if quality fails.

## Table assets

- For small tables (≤ 5 rows × 4 columns): recreate as native PPTX table for clarity.
- For large tables (more than 5 rows or 4 columns): render as high-resolution image.
- For benchmark tables: use native table with bold header row and alternating shading.
- Never insert raw table PDF screenshots.

## Asset manifest

Record every cropped or rendered asset in `output/asset_manifest.md`:

```markdown
| File | Source page | Panel label | Original size | Notes |
|---|---|---|---|---|
| fig2_b.png | p.4, PDF | Fig. 2b | 1200×800 px | Cropped from full page |
| table1.png | p.5 | Table 1 | 800×600 px | Rendered; too wide for native table |
```
