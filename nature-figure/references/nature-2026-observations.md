# 2026 Nature Sample Observations

This note captures page-level figure patterns observed from a local 2026 sample of `Nature`
papers, plus one `Nature Biomedical Engineering` paper used as a clinical / ML-adjacent
cross-check.

Sampled figure sources:

- `s41586-026-10408-8` — wide schematic-led materials figure with supporting quant panels
- `s41586-026-10426-6` — dark whole-brain image plate with repeated views
- `s41586-026-10393-y` — clinical triptych: longitudinal lines, forest plots, summary bars
- `s41586-026-10257-5` — dense categorical stacked-area panels with direct labels
- `s41586-026-10439-1` — asymmetric genomics figure with one dominant circular panel
- `Expert-level detection of pathologies...` — compact medical / ML figure conventions

## Archetype 1: Schematic-led composite

- Let the schematic occupy roughly 45–60% of figure height.
- Use the same palette in the supporting plots; do not switch to generic method colors below the schematic.
- Supporting quantitative panels should be smaller, cleaner and less saturated than the schematic.

## Archetype 2: Dark image plate

- Use a black facecolor only for the image plate region, not for the whole page.
- Pair grayscale context with one or two fluorescent channels.
- Keep crops, scale bars and view boxes geometrically consistent across rows and columns.

   ```python
   CYAN = "#22D7E6"
   MAGENTA = "#FF2AD4"
   GREY_CONTEXT = "#B8B8B8"
   ```

## Archetype 3: Clinical triptych

- Top row: line plots or longitudinal summaries, sharing one legend strip above the row.
- Middle row: forest-plot style effects with a dashed vertical reference line and light category bands.
- Bottom row: compact summary bars, often binary or stacked-percentage bars.
- Keep columns semantically parallel.

## Archetype 4: Asymmetric mixed-modality figure

- Do not force equal panel sizes. Let the biologically central panel dominate.
- Use small supporting plots around the hero panel to answer narrower questions.

## Cross-cutting Nature rules

- Panel labels are small bold lowercase letters near the top-left corner.
- Figure pages are narrative, not dashboard-like.
- Legends are often omitted if direct labeling is possible.
- Background discipline matters more than ornament. White for charts, black only for image plates.
- Saturated colors are used sparingly.
