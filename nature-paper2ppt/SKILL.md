# Paper-to-Slides — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (core principles, toolchain policy, the 9-step workflow, output/quality rules, and per-paper-type presentation arcs).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the paper type and loads only the fragments needed for the current job. Deep design, figure, and self-review material lives in on-demand references.

Decks are built with **XeLaTeX + Beamer**, not python-pptx. A `.tex` source and the
PDF it compiles to are the deliverables; the build layer lives in `beamer/`.

Do not try to apply the deck-building logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Run **step 0 (ask before building)** first, then follow these five steps every time the skill is invoked.

### 0. Ask before building

Before loading any fragment, ask the user to confirm:

1. **汇报场合与听众 / Venue & audience** — journal club / group meeting / thesis seminar / lab meeting / department report / conference presentation; the intended audience shapes depth and pacing.
2. **时长 / 页数 / Duration & length** — total time or slide count budget (e.g. 10 min / 12 slides); drives how many figures and how much detail per slide.
3. **讲者备注形式 / Speaker notes** — full speaker notes (display script), bullet talking points, or none.

Wait for the user's answers before continuing. If the user already stated these in the request, confirm them in one line instead of asking again.

Also confirm the **theme** in the same breath — `slate` (default), `navy`, `ink`, or
`paper`. See `beamer/THEMES.md`; one line of description is usually enough for the
user to choose.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the `paper_type` axis, the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load`. These hold the purpose and core principle, the lean operating mode and toolchain policy, the 9-step workflow spine, and the output/quality rules that apply to every deck, plus the shared Terminology Ledger used to keep technical terms consistent across slides.

### 2. Classify the paper type

Decide the `paper_type` value using the manifest's `detect:` hint and the source:

- `discovery` — discovery / mechanism papers (question-to-evidence arc). Default.
- `methods` — methods / AI / tool / algorithm papers (problem-to-solution arc).
- `resource` — resource / dataset / atlas / omics / benchmark papers (workflow-to-validation arc).
- `clinical` — clinical / population / intervention studies (design-to-inference arc).
- `materials` — materials / chemistry / physics / engineering papers (property-to-mechanism / design-to-performance arc).
- `review` — reviews / perspectives / commentaries / meta-analyses (evidence-map arc).

State the detected value in one short line to the user before designing slides, so they can correct you cheaply.

### 3. Load the matching fragment

Read the file mapped for the detected `paper_type`. It gives the presentation arc and how to adapt the default slide structure for this type. Do **not** read every fragment in `static/`.

### 4. Build the deck using the loaded material

Apply the loaded fragments in this priority order:

1. Core principles (`core/principles.md`) — the argument is the spine; lean operating mode; accepted inputs; Chinese-by-default language rule.
2. Toolchain policy and fast path (`core/toolchain.md`) — XeLaTeX/Beamer build, fixed fonts, the compile commands.
3. Paper-type arc (the loaded `paper_type` fragment) — narrative order and slide structure for this paper.
4. Workflow (`core/workflow.md`) — run the 9 steps end to end, mapping each slide to a theme macro.
5. Output and quality rules (`core/output-and-quality.md`) — deliverables, quality gates, mechanical checks, fallbacks.

Build the Terminology Ledger (`../_shared/core/terminology-ledger.md`) while reading the source, so model names, gene/protein names, datasets, metrics, and abbreviations stay identical across every slide and speaker note.

The end product is a compiling Beamer deck — `slides.tex` plus `slides.pdf` — not an outline or a script. Do not fabricate results, numbers, or figure details.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest:

- composing/auditing slide layout, visual rhythm, typography, anti-template design, archetypes, on-slide text budget → `references/design-and-layout.md`.
- theme internals, the shared layout macros, the build script, or a compile/toolchain failure → `beamer/README.md` (it lists every XeLaTeX and kpathsea trap already hit on this project).
- choosing or comparing themes → `beamer/THEMES.md`.
- selecting, extracting, cropping, and quality-checking figure/table assets → `references/figure-assets.md`.
- running the self-review/corrective revision loop, severity grading, compile and rendered-page checks, final verification → `references/self-review.md`.

## Why this split

- The static layer is versioned and reviewable. Adding a new paper-type arc is one new fragment plus one manifest line; adding a theme is one `.sty` plus one line.
- The dynamic layer keeps each invocation cheap: only the arc for this paper enters context up front; heavy design and QA material loads only when that step runs.
- The router itself is short on purpose. Update fragments, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, and `nature-reader` so shared content lives in `_shared/`.
