# Toolchain policy and fast path

## Toolchain policy

Decks are built with **XeLaTeX + Beamer**, not python-pptx. A `.tex` source plus a
compiled `.pdf` is the deliverable: the source diffs cleanly in git, the layout is
reproducible, and formulas and Chinese typography are handled natively.

Build layer: the `beamer/` directory inside this skill (see `beamer/README.md`).

- **XeLaTeX** compiles the deck. Two passes are required for the frame counter.
- **latexmk + biber** when the deck needs `\cite` against a `.bib`.
- **PyMuPDF** for page count, aspect-ratio checks, and rendered previews.
- **Pillow** only for contact sheets when figure locations in the source are unclear.

Fonts, fixed so a deck renders identically anywhere:

- Chinese: **HarmonyOS Sans SC** (Regular / Medium / Bold files).
- Latin and math: **Source Sans Pro** / **Source Serif Pro** from TeX Live.

Do not substitute fonts per deck. A deck that renders differently on another machine
is not a reproducible deck.

## Default fast path

For a normal selectable-text paper PDF, run the shortest complete path:

1. Extract metadata, abstract, headings, figure legends, and table captions with PyMuPDF.
2. Classify the paper type and fix the argument before rendering any full pages.
3. Render low-resolution contact sheets only when figure locations are unclear.
4. Render and crop only the figures that will actually appear in the deck, into
   `output/assets/figures/`.
5. Choose one of the four themes (`beamer/THEMES.md`) and write `output/slides/slides.tex`.
6. Compile; require zero `!` errors and an aspect ratio of 1.778.
7. Run the self-review and revision loop, then re-verify the rendered pages.

OCR, full supplementary extraction, all-page high-resolution rendering, all-slide
rendered QA, and long script files are opt-in or justified exceptions, not defaults.

## Compile commands

```bash
# from this skill's beamer/ directory
bash build/build.sh slate          # XeLaTeX, two passes
bash build/build.sh all            # all four themes
bash build/build.sh deck.tex --bib # latexmk + biber
```

When compiling by hand, the deck needs an absolute figure root: a relative path
containing `../` is rejected by kpathsea as soon as an output directory is in use.
Generate the parameter file the deck reads, then:

```bash
xelatex -output-directory=build -jobname=slides slides.tex
```

Do **not** use `-usepretex` to pass parameters. XeLaTeX applies it after the
preamble, so it cannot override anything the document defines for itself — the
theme would silently stay at its default. Reading a generated file is the only
reliable channel. Details and the full list of known traps are in
`beamer/README.md`.
