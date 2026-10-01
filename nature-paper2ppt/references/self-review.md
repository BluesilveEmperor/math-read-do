# Self-review and corrective revision loop

## When to use this file

Open this reference during Step 8 (self-review and corrective revision loop) to systematically identify and fix defects in the generated Beamer deck.

## Self-review checklist

Review every slide for these categories of defects:

### Severity grading

| Severity | Label | Definition | Mandatory to fix |
|---|---|---|---|
| High | CRITICAL | Factual error, illegible figure, wrong figure, missing slide, deck fails to compile | Yes |
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

Run the built-in build layer; it already gates on the mechanical checks:

```bash
bash beamer/build/build.sh all      # 编译四主题，逐主题报 errors / pages / ratio
```

`pdf_tools.py` 会从日志与 PDF 里核对：

- 编译日志中 `!` 开头的错误数为 0（含 `Unable to load` 一类静默失败）。
- 页面宽高比为 1.778（16:9）；不是这个数说明纸张设错了。
- 页数与预期一致（默认 8 页 demo；成品按 slide plan 核对）。

随后 `check_clearance.py` 量化图表页「结论条下沿」到「页脚文字上沿」的净空，
四个主题都必须为正。

这些之外还需人工核对（脚本测不出）：

- 每一页都有非空标题。
- 至少一页含图片。
- 讲者备注按选定的形式（全稿 / 要点 / 无）齐备。
- 术语与 Terminology Ledger 一致。

Log failures in `output/qa_report.md`。

## Rendered preview policy

Do not require a visual rendered preview for routine passes; the clearance table above
is the fast path. When layout changed, render pages to PNG and look at them —
`build/pdf_tools.py` writes `build/preview/demo-<theme>-NN.png`. Some defects
(panel overlapping the footer) are only visible in the rendered image, never in the log.

## Final verification

Before delivering, confirm on the compiled PDF:

- The deck compiles with zero `!` errors and opens without error.
- Page ratio is 1.778 and page count matches the slide plan.
- Every theme used clears the footer (clearance > 0).
- Speaker note count matches the expected count.
- Slide sequence matches the slide plan.
