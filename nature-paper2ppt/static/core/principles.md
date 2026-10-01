# Core principles (paper2ppt)

## Purpose

Transform a scientific paper or paper-derived notes into a complete Chinese, figure-integrated presentation package with a Nature-style reporting logic.

The expected end product is a real, compiling Beamer deck: `slides.tex` plus the PDF it produces. The skill must not stop at an outline or a script.

## Core principle

Use the paper's scientific argument as the presentation spine. The default slide logic should help the audience answer, in order:

1. Why does this problem matter?
2. What gap or bottleneck does the paper address?
3. What did the authors do?
4. What is the key evidence?
5. Why should we trust the result?
6. What is new, reusable, or broadly meaningful?
7. Where are the boundaries and open questions?

## Lean operating mode

Default to the lowest-overhead workflow that still produces a usable deck.

Do:
- read only the source material needed to understand the paper's argument,
- extract only figures/tables that will actually appear in the deck,
- produce a compiling `.tex` and `.pdf` as the deliverable,
- design slides with varied, evidence-led composition,
- prevent text overflow by writing shorter on-slide copy,
- run at least one self-audit and correction pass on the compiled deck.

Avoid by default:
- exhaustive extraction of every figure,
- full OCR unless normal text extraction fails,
- launching GUI apps just to render previews,
- per-slide font-size hacks; change the theme instead.

## Accepted inputs

Full paper PDF; supplementary figures or tables; abstract + results + figure legends; structured reading notes; pasted article content.

Default output language is simplified Chinese. Preserve important technical terms, abbreviations, gene/protein names, model names, dataset names, and equations in English.
