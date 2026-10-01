# Workflow

Run these nine steps for any paper-to-deck job. Steps 1–6 and 8–9 are unchanged
from the PPTX era; step 7 now produces a Beamer deck instead of a `.pptx`.

## Step 1. Read and extract source material

Extract, when available: title, authors, journal, year, DOI; field and subfield; paper type; central problem and knowledge gap; main claim; study design; key methods; main results; key figures, tables, and figure legends; validation analyses; limitations; broader meaning.

## Step 2. Classify the paper and choose the presentation logic

The router already detected the `paper_type` axis and loaded the matching arc fragment.

## Step 3. Build the Chinese presentation plan

Default length: 12-16 slides for a 15-20 minute report; prefer 10-14 for a quick request. Use the default slide structure from the loaded paper-type fragment.

## Step 4. Select figures as evidence, not decoration

Prioritize figures that carry the argument: design/workflow, main evidence, validation/robustness, mechanism/model/synthesis, then practical/conceptual implication.

## Step 5. Extract and prepare figure assets

Extract or render only selected figures, crop dense panels, keep original data visuals unchanged, save under `output/assets/figures/`, and record traceability in `output/asset_manifest.md`.

## Step 6. Write slide-by-slide content

For each slide write: Chinese title (conclusion-style where possible), slide purpose, suggested layout, 2-4 concise Chinese bullets, the selected figure/table asset if any, Chinese caption and interpretation, one core takeaway sentence, and a concise Chinese speaker note.

Map the layout to a macro from the theme family:

| Intended layout | Macro |
|---|---|
| Cover | `\naturetitlepage` |
| Story beat | `\naturesection{…}` |
| Figure callout | `\naturefigurepage{…}` |
| Two-panel comparison | `\naturetwocol{…}` |
| Data table | a `frame` with `booktabs` |
| Text / bullets | a plain `frame` |
| Closing | `\natureclosing{…}` |

## Step 7. Write and compile the Beamer deck

Pick one theme from `beamer/THEMES.md` (default `nature-slate`), write
`output/slides/slides.tex` using the macros above, and compile it:

```bash
bash build/build.sh <theme>
```

The deck's `\documentclass` must carry the `t` class option
(`\documentclass[aspectratio=169,10pt,t]{beamer}`): beamer vertically centres
frame content by default, and short slides then show a dead band between title
and body. The six layout macros already force `[t]` internally; the class
option covers the plain frames written in the deck.

Compile twice for the frame counter; `build.sh` handles this. Do not write speaker
notes as separate prose files — use Beamer's `\note{}` so they travel with the slides.

Require zero `!` errors and an aspect ratio of 1.778 before moving on.

## Step 8. Self-review and corrective revision loop

After the first draft, run at least one explicit self-review pass. Write a severity-graded defect list, fix every high-severity issue and every reasonable medium one, recompile, and update `output/qa_report.md`.

Check both the log and the rendered pages. Layout defects such as a takeaway panel
overlapping the footer do not appear in the log — measure them
(`beamer/README.md` has the snippet).

## Step 9. Final verification

Recompile and confirm: zero errors; aspect ratio 1.778; the expected slide count;
figures all present and legible; every `\note{}` retained; no page overflowing the
text block. Do not stop at "it compiles" if self-review found high-severity issues.

