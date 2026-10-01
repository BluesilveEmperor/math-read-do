# Output files, citation, and quality rules

## Citation and attribution rules

Include source information:

- title slide: paper title, authors if useful, journal, year, DOI if available,
- figure slides: `\ntsource{}` with a short label such as `Source: Fig. 2b, Nature, 2024`,
- adapted or redrawn content: label as `整理自` or `改绘自`,
- `\cite` is optional; use it only when a `.bib` is present and compile with `--bib`.

## Output files

```text
output/
├── slides/
│   ├── slides.tex          the deck source (the primary editable deliverable)
│   ├── slides.pdf          compiled deck
│   └── ntsettings.tex      generated build parameters
├── qa_report.md            slide count, figures inserted, self-review defects
├── asset_manifest.md       figure asset traceability
└── assets/figures/         extracted or cropped figure assets
```

`slides.tex` and `slides.pdf` are both deliverables. The PDF is what the audience
sees; the `.tex` is what the next person edits.

Figure paths inside `slides.tex` are written **relative to the deck's figure root**,
e.g. `assets/fig1.pdf`, never with a leading `../`.

## Quality rules

- The deck must compile: zero `!` errors in the log.
- Page aspect ratio must be 1.778 (16:9). A different number means the paper size
  is wrong.
- Do not fabricate results, methods, numbers, or figure details.
- Do not overload slides: at most ~4 bullets, ~30 Chinese characters each.
- At most three distinct font sizes on one slide.
- Figures must be legible at 1/4 projection height.
- Run at least one self-review and corrective revision pass.
- Document uncertainty and missing source material clearly.

## Mechanical checks

A build that reports no errors can still have a broken page — an overlapping
caption panel or a figure pushed past the margin is invisible to the compiler.
After every build:

1. Confirm `errors=0` and `ratio=1.778` for the theme you built.
2. Look at the rendered pages in `build/preview/`, especially figure pages: the
   takeaway panel must clear the footer.
3. Verify the clearance numerically rather than by eye — `beamer/README.md` has a
   short PyMuPDF snippet that measures the gap between the takeaway panel and the
   footer text. `clearance > 0` is the pass condition.

## Fallback rules

If only partial content is available: still produce a compiling deck; mark uncertain
slides explicitly; write `output/qa_report.md` explaining what could not be verified.

If XeLaTeX is unavailable, do not silently fall back to python-pptx. Report the
missing toolchain and deliver `slides.tex` plus a `qa_report.md` note, so the deck
can be compiled later without redoing the content work.
