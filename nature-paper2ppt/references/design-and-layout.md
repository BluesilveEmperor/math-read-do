# Design and layout reference

## Slide layout principles

Every slide should have a clear visual hierarchy: one main message, one (or rarely two) evidence element, and minimal text.

### Layout modes and their macros

Layouts are expressed through the theme family rather than assembled by hand, so
all four themes stay consistent. Map intent to macro, then write the copy.

| Slide content | Macro | Notes |
|---|---|---|
| Cover | `\naturetitlepage` | Title, author, institute, venue, date |
| Story beat | `\naturesection{…}` | 5–7 characters, no body copy |
| Full-width figure | `\naturefigurepage[t]{标题}{图}{来源}{takeaway}` | Default layout for main evidence |
| 2-panel comparison | `\naturetwocol{标题}{左头}{左体}{右头}{右体}` | Same kind of data, direct comparison |
| Data table / benchmark | plain `frame` + `booktabs` | Reads left to right; avoid dense matrices |
| Text / bullets | plain `frame` | ≤ 4 bullets |
| Closing | `\natureclosing{…}` | One short phrase |

Hand-built layouts are allowed when the deck genuinely needs one, but they bypass
the vertical budget the theme maintains, so check the rendered page afterwards.

### Text capacity limits

- Slide title: ≤ 25 characters (Chinese equivalent), one line preferred, never wrap to three.
- Bullet item: ≤ 30 characters, never more than 4 bullets per slide.
- Figure caption: ≤ 2 lines below the figure.
- Speaker note: no limit, but keep each paragraph short.

### Typography

Fonts are fixed by the theme family so output is reproducible:

- Chinese: HarmonyOS Sans SC (Regular / Medium / Bold).
- Latin and math: Source Sans Pro / Source Serif Pro.
- Title 14–17pt depending on theme; body 9.2pt / 11.4pt leading; caption 5.6pt;
  takeaway 8.2pt; footer 6.2pt.

Do not change font size inside a single frame to make text fit. Rewrite the copy
shorter, or move detail into `\note{}`. At most three distinct font sizes per slide.

### Visual rhythm rules

- Vary layouts across slides — avoid the same pattern twice in a row.
- Alternate between figure-heavy and text-light slides.
- Use section dividers (5–7 words only) between major story beats.
- Never more than two bullet-list slides in a row.

### Anti-template design

Do not replicate Nature-branded layouts, green/red/blue color blocks, publisher footers, or journal-specific header styles. The deck should look clean and self-consistent, not "like a Nature template."

Acceptable: a simple footer with slide number and short talk section. Never add journal logos, page numbers, or "Nature 2024" watermarks.

Good slide design: intentional negative space, varied evidence layouts, readable figures at 1/4 projection height, and a single visible trim mark per figure crop for clarity.

### Figure pages specifically

The figure page already reserves space for a source line and a takeaway panel. Keep
to one figure and one sentence: the panel holds a single conclusion, not a paragraph.
If a figure needs more explanation than that, give it its own following slide.

Portrait figures work but waste the horizontal field. Crop square where the data
allows.

## Slide archetypes (evidence-led)

Distribute these across the deck; avoid more than two "bullet-list" slides in a row.

1. **Figure callout** – one full-width evidence figure centered, with a short callout text at bottom.
2. **Comparison** – two related panels side-by-side (e.g., wild-type vs. knockout, baseline vs. treatment).
3. **Workflow / pipeline** – a process figure with numbered steps or labeled boxes.
4. **Data table / benchmark** – a clean, minimal table reading from left to right.
5. **Annotated zoom** – one zoomed panel with numbered or arrow annotations, with short explanations below.
6. **Concept diagram** – an illustrative graphic (mechanism model, summary scheme, or graphical abstract). Use simple geometric shapes, thin arrows, and small text labels.
7. **Section divider** – a transition slide with a short phrase.

## On-slide text budget

- A slide should contain no more words than can be read in 60 seconds at a normal pace.
- Bullets should not copy-paste from the manuscript. Rewrite each point as a short telegraphic phrase: "Method A outperformed B by 12% in F1", not a full sentence.
- Each bullet should be one idea, one line. If you need more than one line, split into two bullets or move detail to `\note{}`.

