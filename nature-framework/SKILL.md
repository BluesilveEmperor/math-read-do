---
name: nature-framework
description: Create publication-grade research-paper diagrams as inline-SVG HTML figures and embedded-font vector PDF for LaTeX \includegraphics. Built for the whole research workflow — graduate students drafting thesis/proposal figures and group-meeting slides, supervisors preparing lecture notes, reviews and grant applications, and authors submitting to venues. Six diagram types share one typed IR — method/model architecture (transformer / CNN / diffusion with tensor shapes, residual skips, N× blocks), research framework (problem → content → outcome layers), technical route, system architecture, paper/chapter structure, and experiment pipeline (dataset → train → eval with baselines and ablations). White-first, print-friendly, serif/sans-serif typeset, ten visual presets including seven expressive styles. Use when the user asks to draw a research framework figure, technical route, model architecture, system architecture, paper structure diagram, or experiment pipeline for a thesis, dissertation, opening report (开题), group meeting, lecture, grant proposal, or NeurIPS / ICML / ICLR / CVPR / Nature / IEEE submission.
license: MIT
metadata:
  version: "0.1.0"
  author: nature-framework
  inspired_by: tt-a1i/archify (MIT, v2.17) — atomic delivery, typed JSON-IR, showcase artifact checks
---

# Paperfig

Create a self-contained, publication-grade ML/DL model architecture figure from a small typed JSON specification. Default output is a white-first, print-friendly HTML figure with inline SVG; an embedded-font vector PDF for LaTeX `\includegraphics` is produced alongside when `--pdf` is requested. Motion is opt-in and never enters canonical PDF export.

**Who it serves** — 研究生（学位论文插图、开题报告的技术路线与框架图、组会汇报）、导师（讲义与评审插图、基金申请的研究框架图、组内规范示范）、论文作者（期刊/会议投稿插图）。All audiences share one contract: a small typed JSON spec in, a geometry-checked, print-first figure out.

## Creative North Star: "The Figure Plate"

A paper figure is a print artifact first and an interactive object second. It must fit inside a single-column (~3.5in / 8.9cm) or double-column (~7in / 17.8cm) LaTeX float, survive grayscale printing, match the surrounding body type, and let a reader read the method's main path in one glance. Paperfig is a figure-making instrument, not a drawing suite, not a Mermaid beautifier, and not a dark-mode engineering console.

## Fast authoring path

Use this bounded path for ordinary generation.

1. Choose the diagram type from the question: `model`, `framework`, `route`, `system`, `structure`, or `experiment` (all six share one IR — same `modules` / `groups` / `connections` / `cards` fields; they differ in type vocabulary and layout conventions). When ambiguous, run `node bin/nature-framework.mjs guide "<scenario>" --json`.
2. Read `schemas/diagram.schema.json`, `schemas/common.schema.json`, and one matching example in `examples/`. Read only those files. Fresh authorship means new stable IDs, domain wording, and layout; use the example for field shape, not facts.
3. Artifact first: the next tool action must write the candidate. Write the candidate before inspecting renderer internals. Start with one clear forward main path (input → encoder → ... → output), short residual side branches, sparse tensor-shape annotations, and at most 14 primary modules. Set `meta.quality_profile` to `"showcase"` unless the user explicitly requests a denser `standard` map. Start with automatic routes and labels. Do not add `via`, `fromSide`, `toSide`, or `labelAt` before a diagnostic calls for one; apply at most one diagnosed geometry control per repair.
4. Validate after every candidate edit and immediately before handoff:

   ```bash
   node bin/nature-framework.mjs validate model <candidate.json> --quality showcase --json
   ```

   A receipt with only 4 artifact checks is basic validation, never showcase acceptance. A showcase pass must report all 11 artifact checks with 0 composition errors and 0 warnings. If the candidate omits or misspells the exact `meta.quality_profile` field, fix it before geometry.
5. For a delivered HTML, `deliver` is the final acceptance command. **Always ask the user which dataflow mode the figure should open in before delivering** — 静止 `off` / 悬停 `hover` / 流动 `flow` / 巡演 `tour` — and pass their choice as `--motion <mode>`. Never pick a mode silently on the user's behalf; if the user already stated a mode earlier in the conversation, reuse it without asking again. The same question applies to every figure in a batch (one shared answer may cover them all).

   ```bash
   node bin/nature-framework.mjs deliver model <candidate.json> <output.html> --quality showcase --motion flow --json
   ```

   Add `--pdf <output.pdf>` to produce an embedded-font vector PDF alongside the HTML. A non-zero exit can never be described as success. A failed delivery preserves any previous output, so do not run `visual-check` on that path. If validation fails, change only the diagnosed `subject`, verify `evidence`, choose from `supportedFixes`, and rerun. Continue focused correction while the objective error count reaches a new minimum. If two consecutive rounds do not improve that best count, stop and report the unresolved diagnostics truthfully.

## Type router

| Type | Use for | Vocabulary & conventions |
|---|---|---|
| `model` | ML/DL method/model architecture: layers, blocks, tensor shapes, residual skips, N× repeated blocks, encoder/decoder stages | operator types (`attention`, `ffn`, `linear`, `matmul`, `gelu`, …), `tensor_shape` annotations, `nested` containers, `backward-skip` residual edges |
| `framework` | Research framework: problem layer → research-content layer → outcome layer | types `problem` / `content` / `goal` / `outcome`; groups `kind: "layer"`, one per layer, laid out as vertical columns left-to-right (or horizontal bands top-to-bottom); one mapping edge per real correspondence, no invented links |
| `route` | Technical route: branching execution path from goal through methods to conclusion | types `goal` / `content` / `outcome` plus concrete method words; tree topology — branches leave their nearest main-path node and merge explicitly; every branch must rejoin or terminate at a named outcome |
| `system` | System architecture of a platform built or used in the thesis | types `client` / `service` / `storage` plus `custom`; groups `kind: "stage"` as tier boundaries (client tier / service tier / data tier); label real protocols on crossing edges (`HTTP`, `gRPC`, `SQL`) |
| `structure` | Paper/chapter organization and its mapping to research content | types `chapter` / `content` / `outcome`; one chapter node per chapter with `sublabel` of its title; edges only for genuine chapter-to-content mappings, dashed `data` variant for supporting relations |
| `experiment` | Experiment pipeline: data → train → evaluate → metrics, with comparisons | types `dataset` / `preprocess` / `train` / `eval` / `metric` / `baseline` / `ablation`; main line is the pipeline, `baseline`/`ablation` nodes feed the shared `eval` node from the side; `loss` variant for training-only feedback edges |

All six types share the same schema (`schemas/diagram.schema.json`); the type vocabulary is one enum — use the words listed for your diagram type and do not mix vocabularies inside one figure.

## Hard rule: experiment-data dependency per type

| diagram_type | 最终版是否需要实验数据 | 最早可画阶段 |
|---|---|---|
| `framework` | ❌ 不需要 | 开题/研究设计 |
| `route` | ❌ 不需要（实验后补结果节点即可） | 计划阶段 |
| `model` | ⚠️ 主体不需要，但维度/超参数/损失权重/模块细节最好代码跑通后确认 | 设计确定后可画主体 |
| `system` | ❌ 不需要（实现后微调） | 设计阶段 |
| `structure` | ❌ 不需要 | 写作前 |
| `experiment` | ✅ **必须**等实验跑完、数据整理完才能画最终版 | 仅可画"预计流程图" |

### experiment 类型为什么最依赖实验复现

实验流程图要写清楚：初始样本量、排除数与排除原因、最终纳入量、分组方式、各组样本量、失访/退出/剔除数、最终进入分析的数量、评价指标。这些数字和分支不能靠想象编，必须来自 `raw_metrics.csv` / `reproducibility_assessment.json` / Phase-5 统计摘要。医学 PRISMA/CONSORT 流程图尤甚——计划阶段只能画"预计流程图"，最终版一定要实验后画。

### 执行约束

- `experiment` 类型的 `deliver` 命令在 Phase 5 统计判决产出之前应拒绝执行最终版交付（可交付"predicted flow"草案，但 `meta` 必须标注 `"status": "draft"`）
- 其余 5 类不受此约束，可在任意阶段交付

## Authoring invariants

- One obvious forward main path; residual / skip / branch edges leave the nearest main-path module. Remove low-value edges before adding routing controls.
- Omit `meta.visual_preset` by default so every figure opens in `paper` (white-first). Switching presets must preserve the current layout. Ten presets ship: `paper` (default, print-first), `paper-dark` (slide/blog dark), `blueprint-print` (pure line-art for EPS), and seven expressive styles learned from VibeHub design topics plus Apple's design language — `brutalism` (Neubrutalism after the Gumroad canon: 2.5px black strokes, hard offset drop shadows on every block, oversized uppercase headline, flat high-saturation candy picks from cobalt blue / signal yellow / flat red / purple / green on off-white, white labels on cobalt modules, monospace-flavored card titles, no gradients — anti-polish but structurally strict), `playful` (Playful Illustration: warm cream ground, soft rounded corners, coral/mint fills), `neumorphism` (same-color raised surfaces with dual light/dark soft shadows, no strokes), `memphis` (80s clash colors with 2px dark outlines), `glass` (violet gradient backdrop, translucent white module fills, frosted cards), `bauhaus` (shape-as-function: primary red/blue/yellow mark only structural roles — blue structure modules carry white labels, square corners, no shadows), and `apple` (Apple design language: frosted translucent cards with backdrop blur + saturate, soft depth shadows, iOS system-palette tints with one restrained system-blue accent `#0071e3`, continuous corners, system-font typography with size-specific negative tracking). The expressive styles are explicit opt-in only: set one when the user names the style or asks for that look; never let a style's decoration reduce figure legibility — labels, tensor shapes, and routes must stay readable.
- Omit `meta.subtitle` by default. Never invent a subtitle that restates the title, modules, or cards; include one short supporting line only when the user explicitly asks for it.
- Treat the figure as a single-column print artifact by default. Generate one responsive HTML that adapts the outer reading width from the live viewport; it must preserve the authored SVG/viewBox, proportions, tensor-shape labels, and stage boundaries. Before handoff, open the real HTML at single-column width (~8.9cm / ~336px at 96dpi) and double-column width (~17.8cm / ~672px) and additionally check 1440×900 desktop. Require `document.documentElement.scrollWidth <= window.innerWidth` at every checked width, while visually checking that layer blocks, tensor annotations, and residual skips remain comfortably readable. Repair overflow by removing only genuinely redundant content or compacting spacing before shrinking modules, labels, or the main panel. Never counterfeit a pass with `overflow: hidden`, clipped content, an internal figure scroller, stretched SVG height, or smaller typography.
- Choose one primary authored language from an explicit user choice; otherwise follow the request or conversation's dominant language. `meta.locale` controls only viewer-owned UI: use `"en"` or `"zh-CN"` for the corresponding supported primary language. The renderer never translates authored content.
- **Chinese-first hard rule (zh-CN figures)**: when the figure language is Chinese (`meta.locale: "zh-CN"`, mandatory for Chinese theses/papers), ALL human-facing text — titles, subtitles, module labels/sublabels, group labels, connection labels, card titles/items, legend labels — MUST be Chinese. The only exceptions are professional terms (e.g. `Transformer`, `Softmax`, `GELU`, `Token`, `d_model`), programming reserved words / identifiers, math notation (`[B, S, D]`, `QKᵀ`, `γ, β`, `×6`), and citations. Ordinary descriptive English words (`input`, `output`, `source sequence`, `probabilities`, `cosine schedule`) are forbidden — translate them (输入、输出、源序列、概率分布、余弦调度). Artifact check 11 `text-language` enforces this with a built-in term whitelist; extend it per-spec via `meta.language.allow` when a legitimate term is missing.
- All text renders in **HarmonyOS Sans Medium**. The renderer auto-embeds the subset font (`assets/fonts/HarmonyOSSans-Medium-sub.woff2`, ~3750 chars: 3600 common Chinese + ASCII + math/CJK symbols) as a base64 `@font-face` into every HTML, so figures stay self-contained offline and in print. Do not reference external/web fonts. Characters outside the subset fall back to PingFang SC / Microsoft YaHei. Re-subset with the full font (`assets/fonts/HarmonyOS_Sans_SC_Medium-full.ttf`) when shipped figures need rarer glyphs.
- Preserve exact layer names, tensor-shape notation, operator names (e.g., `Softmax`, `GELU`, `LayerNorm`), and quantifier wording (`×6`, `×12`, `N ×`). They may remain English inside localized copy.
- Module types are `input`, `embedding`, `encoder`, `decoder`, `attention`, `ffn`, `norm`, `activation`, `pooling`, `output`, `residual`, `concat`, and `custom`; shapes are `rect`, `rounded`, `trapezoid`, `parallelogram`, `circle`, and `diamond`; variants are `default`, `emphasis`, `dashed`, and `repeated`. A `repeated` block carries an integer `repeat` (e.g., `6`) and renders a `×6` sigil; nested repeated blocks must use distinct IDs.
- Tensor-shape annotations are semantic data. When one collides, move the annotation, adjust the route or spacing, then shorten the wording while preserving meaning (e.g., `[B,C,H,W]` → `[B,C,H,W]` stays; a redundant dimension may drop only when fully implied by both endpoints and contains no batch / channel / sequence-length meaning). Preserve every meaningful shape; deleting it is not a geometry repair.
- Residual skip connections use `variant: "backward-skip"` and must not cross an unrelated opaque module or mask a forward `variant: "forward"` edge. A skip that wraps an N× repeated block must clearly enclose the repeated group, not just one inner module.
- Stage groups (`groups[]` with `kind: "stage"`) carry an authored `label` and `wraps[]` of module IDs; they must form a contiguous rectangular region. Overlapping or non-contiguous stage groups fail showcase.
- Spacing means clear gap, not center distance. For a tensor-shape annotation, clear gap must exceed its measured mask width.
- Fan-in / fan-out endpoints are auto-spread by the renderer: when several `via`-free connections share the same (module, side) attachment point, each head lands on its own slot (70% of the side length, ordered by the opposite endpoint so lines never cross). Connections carrying `via` keep their authored endpoints — do not add vias just to dodge a shared side; let the spread do it.
- Automatic routes own their endpoint sides. A side is a direction contract: the first and final segment must leave/enter perpendicular to that side.
- **Motion is opt-in and user-chosen** — ask which mode the user wants before delivering (fast path step 5); never default to one silently. `meta.motion` (or the CLI `--motion` override) then selects: `"off"` (default, purely static for print), `"hover"` (legacy alias `"on"`; the flows of a module's incoming and outgoing edges light up while the pointer rests on it), `"flow"` (always-on: a marching dashed line ("------" style, long segments with short gaps) riding every connection — pure dashes, no particles, per the author's choice — colored by edge semantics from the active preset's accent palette: forward and backward-skip in `accent-blue`, loss in `accent-red`, data in `accent-gray`, so the flow always matches the theme. While an edge flows, its static solid line steps aside — an edge is either solid or flowing, never both at once; the dash carries a color-matched arrowhead so direction stays readable. In flow mode hovering a module boosts its edges), and `"tour"` (guided playback that walks the forward/data main path from the roots downstream, lighting modules and flowing edges in narration order). Every non-off mode ships a small viewer switcher (流动/悬停/巡演/静止, or Flow/Hover/Tour/Still when `meta.locale` is `"en"`) so readers change modes live. `prefers-reduced-motion` users, print media, and non-JS viewers always get the static figure, and the switcher is hidden for them. Motion never enters canonical PDF/EPS export, and it never changes geometry — all artifact checks run identically with motion on or off.
- Never accept an edge crossing an unrelated opaque module, an ambiguous shared corridor, or a tensor-shape annotation masking another route.

Read `references/authoring-contract.md` only when you need field enums, spacing math, geometry repair rules, or mode-specific placement.

## Delivery

Use `validate` during repair and `deliver` once for final acceptance. Delivery freezes the exact specification bytes into a private same-directory snapshot, renders and checks that snapshot, atomically commits the HTML (and the optional PDF), and reports SHA-256 plus byte counts for specification and artifact(s). This is deterministic artifact evidence; it does not exercise the Viewer in a browser.

After delivery, collect bounded desktop evidence without modifying or rerendering the trusted HTML:

```bash
node bin/nature-framework.mjs visual-check <output.html> --json
```

`visual-check` collects automated browser evidence from the exact delivered HTML without modifying or rerendering it. Its machine-readable measurements and screenshots do not approve perceptual polish. Follow `references/delivery-contract.md` for the canonical receipt fields, coverage, sidecars, exit behavior, and supplementary manual-record requirements.

Keep the three claims separate: `deliver` proves deterministic artifact checks, `visual-check` proves bounded behavior in a real browser, and perceptual visual review requires an actual human or image-capable reviewer. Report browser evidence and perceptual review independently.

For PDF, the deliver receipt reports the embedded-font vector PDF separately: exact page size (single-column ~3.5in or double-column ~7in), byte count, SHA-256, and font-embedding status. PDF is print-only: no animation, no theme toggle, no viewer chrome.

Add `--open` only when the user wants an immediate local preview.

Never start preview by default. Read `references/delivery-contract.md` when using preview, export receipts, visual review, or post-commit opening.

## Print and export contract

- HTML is the canonical interactive artifact. PDF is the canonical print artifact.
- PDF embeds all fonts (serif title + sans-serif body) and matches the HTML's geometry 1:1; no rasterization fallback inside the SVG.
- Single-column width is the default (`meta.column = "single"`); double-column (`"double"`) is opt-in.
- LaTeX usage snippet is printed to stderr after a successful `--pdf` delivery:

  ```latex
  \begin{figure}[t]
    \centering
    \includegraphics[width=\columnwidth]{<output.pdf>}
    \caption{<authored title>}
    \label{fig:<stable-id>}
  \end{figure}
  ```

- EPS export is supported via `--eps` and is pure line-art (blueprint-print preset forced, no fills beyond gray hatching).

## Setup and fallback

No install is required inside the skill package. Verify with:

```bash
node bin/nature-framework.mjs doctor
node bin/nature-framework.mjs demo <output-directory>
```

When shell access is unavailable, hand-place architecture SVG into `assets/template.html`, use CSS semantic classes rather than inline colors, and follow the visual review contract in `references/delivery-contract.md`.

## Output

Return the checked HTML path (and PDF path when produced), diagram type, validation summary, specification/artifact receipt, browser-evidence status, and truthful visual-review status. Do not claim success for a non-zero command or claim visual inspection you did not perform.
