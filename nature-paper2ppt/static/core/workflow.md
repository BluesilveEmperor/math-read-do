# Workflow

Run these nine steps for any paper-to-deck job.

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

## Step 7. Build the actual PPTX deck

Create a real `.pptx` as the primary deliverable with `python-pptx` using 16:9 by default, Chinese titles/bullets/captions/notes, source labels on figure slides, and consistent typography.

## Step 8. Self-review and corrective revision loop

After the first draft, run at least one explicit self-review pass. Write a severity-graded defect list, fix every high-severity issue and every reasonable medium one, regenerate, and update `output/qa_report.md`.

## Step 9. Final verification

Reopen the PPTX, check slide count, embedded media count, and speaker-notes presence. Do not stop at "PPTX opens" if self-review found high-severity issues.
