# Self-review and corrective revision loop

## When to use this file

Open this reference during Step 8 (self-review and corrective revision loop) to systematically identify and fix defects in the generated PPTX deck.

## Self-review checklist

Review every slide for these categories of defects:

### Severity grading

| Severity | Label | Definition | Mandatory to fix |
|---|---|---|---|
| High | CRITICAL | Factual error, illegible figure, wrong figure, missing slide, broken PPTX | Yes |
| Medium | MAJOR | Text overflow, overcrowded layout, wrong caption, inconsistent terminology, missing source label, speaker note missing or empty | Yes |
| Low | MINOR | Aesthetic: font mismatch, alignment drift, uneven figure sizing, uneven spacing, duplicate slide patterns | Fix if time permits |

### Checklist (review each slide)

1. **Factual accuracy** — Are numbers, methods, and claims correct relative to the source?
2. **Figure quality** — Is the figure readable? Is it the right figure? Is the crop good? Is the source label present?
3. **Text fit** — Does the text exceed the on-slide budget? Are bullets one line each?
4. **Terminology consistency** — Do model names, gene names, dataset names, abbreviations match the Terminology Ledger?
5. **Speaker notes** — Are notes present and useful? Do they reflect the slide content?
6. **Slide completeness** — Is the deck complete? Are any slides missing?

## Corrective revision rules

1. Fix every CRITICAL defect before marking the deck as ready.
2. Fix every MAJOR defect, unless fixing one would introduce a CRITICAL or another MAJOR.
3. For MAJOR text overflow: split the slide, move detail to speaker notes, or rewrite bullets.
4. For MAJOR figure problems: re-extract, re-crop, or remove the figure and replace with a descriptive placeholder.
5. After fixing, re-run only the affected slides through the self-review checklist.
6. Keep the defect list in `output/qa_report.md` with a fixed/resolved column.

## Programmatic checks

When python-pptx is available, run these checks programmatically:

- Slide count ≥ 10.
- Every slide has a title (non-empty).
- At least one slide has an embedded image.
- At least half the slides have speaker notes.
- No slide has more than 5 text runs (text overflow signal).

Log failures in `output/qa_report.md`.

## Rendered preview policy

Do not require a visual rendered preview for routine passes. Use programmatic checks as the fast path. If rendering is needed, use LibreOffice CLI when available to render each slide as PNG or PDF.

## Final verification

Before delivering, reopen the PPTX, confirm:
- The file is readable by python-pptx and opens without error.
- Embedded image count is correct.
- Speaker note count matches the expected count.
- Slide sequence matches the slide plan.
