# Delivery Contract

`nature-architecture deliver` is the canonical acceptance command. It freezes the exact specification bytes into a private same-directory snapshot, renders and checks that snapshot, atomically commits the HTML (and the optional PDF), and reports SHA-256 plus byte counts for specification and artifact(s).

## Receipt fields

A successful `deliver --json` receipt contains:

```json
{
  "ok": true,
  "stage": "commit",
  "spec": { "sha256": "...", "bytes": N, "path": "..." },
  "html": { "sha256": "...", "bytes": N, "path": "..." },
  "pdf": { "sha256": "...", "bytes": N, "path": "...", "fonts_embedded": true, "page_size": "single" },
  "checks": { "total": 9, "errors": 0, "warnings": 0, "items": [...] },
  "quality_profile": "showcase"
}
```

A failed delivery returns:

```json
{
  "ok": false,
  "stage": "render" | "check" | "commit",
  "diagnostics": [
    { "rule": "no-module-overlap", "severity": "error", "subject": "attn1 vs ffn1", "evidence": "...", "supportedFixes": [...] }
  ]
}
```

## Stage guarantees

1. **Snapshot**: the input bytes are copied to a private same-directory staging file with a stable name. The original input is never modified.
2. **Render**: the renderer reads the snapshot and produces the HTML (and PDF if `--pdf`).
3. **Check**: the artifact checker runs all 9 showcase checks against the rendered SVG primitives.
4. **Commit**: only if all checks pass, the candidate is atomically renamed to the final output path. A failed commit preserves any previous artifact byte-for-byte.

A non-zero exit at any stage can never be described as success.

## PDF contract

When `--pdf <path>` is supplied:

- The PDF is generated from the same SVG primitives as the HTML, not from a screenshot.
- All fonts (serif title + sans-serif body + monospace tensor annotations) must be embedded.
- Page size matches `meta.column`: `single` → 3.5in × auto-height; `double` → 7in × auto-height.
- The PDF contains no animation, no theme toggle, no viewer chrome. It is print-only.
- The receipt reports `fonts_embedded: true` and `page_size`. A PDF with un-embedded fonts fails the check stage.

## EPS contract

When `--eps <path>` is supplied, the figure is rendered in `blueprint-print` preset (pure line-art, no fills beyond gray hatching) and exported as EPS. The receipt reports the EPS path and SHA-256.

## LaTeX snippet

After a successful `--pdf` delivery, a LaTeX usage snippet is printed to stderr (not stdout, to keep `--json` clean):

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{<basename>.pdf}
  \caption{<authored title>}
  \label{fig:<stable-id>}
\end{figure}
```

## visual-check

`nature-architecture visual-check <output.html> --json` collects automated browser evidence from the exact delivered HTML without modifying or rerendering it. It opens the HTML at single-column (~336px) and double-column (~672px) widths plus 1440×900 desktop, captures screenshots, and reports scroll overflow checks.

`visual-check` measurements do not approve perceptual polish. Perceptual review requires an actual human or image-capable reviewer. Report browser evidence and perceptual review independently.

## Anti-counterfeit

Never counterfeit a pass with:
- `overflow: hidden` on the figure container.
- Clipped SVG content.
- An internal figure scroller.
- Stretched SVG height to fill a viewport.
- Smaller typography to fit content.
- A PDF that is a rasterized screenshot rather than vector SVG.

A receipt that reports `ok: true` while any of these are present is a contract violation.
