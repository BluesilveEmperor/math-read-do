# Authoring Contract

This document owns the field enums, spacing math, geometry repair rules, and mode-specific placement for paperfig model architecture diagrams. Read it only when `SKILL.md`'s fast authoring path does not cover your case.

## Module type → shape default

When `shape` is omitted, the renderer chooses by `type`:

| type | default shape | rationale |
|---|---|---|
| `input` / `output` | `parallelogram` | I/O convention |
| `embedding` | `rect` | dense matrix |
| `encoder` / `decoder` | `rounded` | container block |
| `attention` | `trapezoid` | QKV projection |
| `ffn` | `rect` | dense stack |
| `norm` / `activation` | `circle` | pointwise op |
| `pooling` | `trapezoid` | reduction |
| `residual` / `concat` | `circle` | junction |
| `custom` | `rect` | default |

Authors may override `shape` explicitly. A `repeated` variant must use `rounded` or `rect` (never `circle` / `diamond` — those cannot host a `×N` sigil legibly).

## Variant semantics

- `default`: solid 1.25px stroke, light fill.
- `emphasis`: solid 1.75px stroke, accent fill (used for the main forward path's primary blocks).
- `dashed`: 1.25px dashed stroke, no fill — for optional / conditional branches.
- `repeated`: solid 1.25px stroke with a `×N` sigil in the upper-right and an interior divider line — for stacked transformer blocks, ResNet stages, etc.

## Tensor-shape annotation

`tensor_shape` is a string like `[B, C, H, W]` or `[B, S, D]`. The renderer renders it as a small monospace label adjacent to the module's right or bottom edge (controlled by `tensor_pos`). When `tensor_pos` is omitted, the renderer chooses the side with the most free space.

**Clearance rule**: a tensor-shape annotation must keep ≥4px clear gap from any connection route in `showcase`. In `standard`, sub-2px clearance is a warning.

**Repair order when a tensor-shape annotation collides**:
1. Move `tensor_pos` to the opposite side.
2. Shift the offending connection's `labelAt`.
3. Increase module `size` (width preferred) to give the annotation room.
4. Shorten the shape wording while preserving meaning (`[B, C, H, W]` → `[B,C,H,W]` is fine; dropping a dimension is not, unless fully implied by both endpoints).

## N× repeated block

A module with `variant: "repeated"` and `repeat: 6` renders as one block with a `×6` sigil. The block visually represents the entire stack; inner modules are not drawn separately unless `nested` is provided (in which case the inner modules are drawn inside the block and the `×6` sigil applies to the whole stack).

A residual skip that wraps a `repeated` block must connect from before the block to after the block, not to an inner module. Connecting to an inner module of a `repeated` block fails showcase.

## Stage group

A `groups[]` entry with `kind: "stage"` and `wraps: ["a", "b", "c"]` draws a labeled rectangular boundary around the bounding box of the wrapped modules, padded by `pad` (default 14). Stages must form a contiguous rectangular region; overlapping or non-contiguous stage groups fail showcase.

`kind: "ablation"` draws a dashed boundary and is used to mark a sub-stack that is removed in an ablation experiment. `kind: "branch"` draws a labeled boundary around a parallel branch (e.g., a two-tower encoder).

## Connection variants

- `forward`: solid arrow, 1.25px stroke — the main data flow.
- `loss`: dashed arrow, 1.25px — loss gradient backprop (rendered in red accent).
- `data`: solid arrow, 1.25px, gray — auxiliary data flow (e.g., attention mask, positional encoding injection).
- `backward-skip`: solid curved arrow, 1.25px — residual skip connection, curves around the modules it bypasses.
- `label-only`: no arrow, just a label — for annotations like "shared weights".

## Route contracts

- `straight`: a single line segment from `from` to `to`.
- `orthogonal-h`: horizontal-first L-shape.
- `orthogonal-v`: vertical-first L-shape.
- `curved`: a cubic Bezier — required for `backward-skip` that must wrap a `repeated` block.

When `fromSide` / `toSide` are omitted, the renderer chooses the facing sides automatically based on relative positions. An explicit side is a direction contract: the first and final segment must leave/enter perpendicular to that side.

## Geometry repair rules

When a `validate` diagnostic reports a composition error, apply **at most one** of the listed `supportedFixes` per repair round, then re-validate:

1. Move the offending module's `pos`.
2. Adjust the offending connection's `route` or add `via`.
3. Move the offending label's `labelAt` / `tensor_pos`.
4. Increase a stage group's `pad`.
5. Shorten a label's wording (preserve meaning).

Never rewrite topology to silence a geometry error. If two consecutive rounds do not reduce the error count, stop and report the unresolved diagnostics truthfully.

## Showcase artifact checks (11)

A `showcase` delivery must pass all 11:

1. **Schema valid** — JSON Schema passes.
2. **No module overlap** — no two module rectangles overlap by more than 1px.
3. **No edge-module overlap** — no connection segment crosses an unrelated opaque module by more than 1px.
4. **No edge-edge overlap** — no two connection segments share more than 8px of collinear lane (parallel fan-out from a shared endpoint is exempt).
5. **Label clearance** — every connection label and tensor-shape annotation has an on-canvas text box (computed at the renderer's font metrics, padded 1.5px) that no foreign route crosses.
6. **Stage contiguity** — every stage group's wrapped modules form a single contiguous rectangular region.
7. **Skip wraps block** — every `backward-skip` connection that originates from a module before a `repeated` block terminates after that block, not at an inner module.
8. **Repeat sigil legible** — every `repeated` module has `repeat ≥ 2` and a `×N` sigil that does not overlap the module's label or any connection.
9. **No viewBox overflow** — every module, group boundary, and connection endpoint lies inside `meta.viewBox` with ≥4px margin.
10. **Text fits module** — every module label/sublabel, after renderer-side auto-wrapping, fits the shape's interior height (circles and diamonds are measured against their rendered diameter `min(w,h)`, with the text block capped at 75% of the diameter); tensor annotations are not covered by another opaque module and stay inside the viewBox; container label zones and connection labels are never crossed by routes and never sit on top of an opaque module.
11. **Chinese-first language (`text-language`)** — active when `meta.locale` is `zh-CN` (or `meta.language.mode` is `zh-CN`): every human-facing string must contain Chinese, unless all of its alphabetic words are whitelisted professional terms / reserved words / identifiers (built-in whitelist, extendable via `meta.language.allow`) or the string has no English word longer than 3 letters. Descriptive everyday English must be translated.

`standard` records checks 2–11 as warnings instead of errors.
