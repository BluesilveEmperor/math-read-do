// paperfig / renderers / model / render-model.mjs
// Compile a model spec into inline-SVG + HTML wrapper (white-first, print-friendly).

import { readFileSync } from "node:fs";
import { bbox, buildConnectionPath, spreadEndpoints, round, sidePoint } from "../shared/geometry.mjs";
import { escapeXml, wrapText } from "../shared/utils.mjs";
import { SHAPE_DEFAULTS, TEXT_METRICS } from "../shared/shapes.mjs";

// --- embedded brand font (HarmonyOS Sans Medium, subset) ---
// The subset woff2 lives in assets/fonts and is inlined as a base64 data URI so
// every delivered HTML is fully self-contained (offline, print, archive-safe).
let FONT_FACE_CSS = null;
function fontFaceCss() {
  if (FONT_FACE_CSS !== null) return FONT_FACE_CSS;
  try {
    const fontPath = new URL("../../assets/fonts/HarmonyOSSans-Medium-sub.woff2", import.meta.url);
    const bytes = readFileSync(fontPath);
    FONT_FACE_CSS =
      `@font-face { font-family: "HarmonyOS Sans"; src: url(data:font/woff2;base64,${bytes.toString("base64")}) format("woff2"); font-weight: 100 900; font-style: normal; font-display: swap; }`;
  } catch {
    FONT_FACE_CSS = ""; // font asset missing → silently fall back to system stacks
  }
  return FONT_FACE_CSS;
}

const FILL_BY_TYPE = {
  input: "var(--fill-input)",
  output: "var(--fill-output)",
  embedding: "var(--fill-input)",
  encoder: "var(--fill-encoder)",
  decoder: "var(--fill-encoder)",
  attention: "var(--fill-attention)",
  ffn: "var(--fill-ffn)",
  norm: "var(--fill-norm)",
  activation: "var(--fill-norm)",
  pooling: "var(--fill-attention)",
  residual: "var(--fill-residual)",
  concat: "var(--fill-concat)",
  custom: "var(--fill-custom)",
  linear: "var(--fill-linear)",
  matmul: "var(--fill-matmul)",
  scale: "var(--fill-scale)",
  softmax_op: "var(--fill-softmax)",
  add: "var(--fill-add)",
  layernorm: "var(--fill-layernorm)",
  gelu: "var(--fill-gelu)",
  scaled_dot_product_attention: "var(--fill-sdpa)",
  // research-framework / structure vocabulary
  problem: "var(--fill-input)",
  content: "var(--fill-encoder)",
  goal: "var(--fill-output)",
  outcome: "var(--fill-output)",
  chapter: "var(--fill-encoder)",
  // experiment vocabulary
  dataset: "var(--fill-input)",
  preprocess: "var(--fill-ffn)",
  train: "var(--fill-encoder)",
  eval: "var(--fill-attention)",
  metric: "var(--fill-norm)",
  baseline: "var(--fill-concat)",
  ablation: "var(--fill-concat)",
  // system vocabulary
  client: "var(--fill-encoder)",
  service: "var(--fill-ffn)",
  storage: "var(--fill-norm)",
};

const STROKE_VARIANT = {
  default: { stroke: "var(--paper-ink)", "stroke-width": 1.25 },
  emphasis: { stroke: "var(--accent-blue)", "stroke-width": 1.75 },
  dashed: { stroke: "var(--paper-muted)", "stroke-width": 1.25, "stroke-dasharray": "4 3" },
  repeated: { stroke: "var(--paper-ink)", "stroke-width": 1.25 },
};

const CONN_VARIANT = {
  forward: { stroke: "var(--paper-ink)", "stroke-width": 1.25, dash: null, color: "var(--paper-ink)" },
  loss: { stroke: "var(--accent-red)", "stroke-width": 1.25, dash: "4 3", color: "var(--accent-red)" },
  data: { stroke: "var(--accent-gray)", "stroke-width": 1.25, dash: null, color: "var(--accent-gray)" },
  "backward-skip": { stroke: "var(--paper-ink)", "stroke-width": 1.25, dash: null, color: "var(--paper-ink)" },
  "label-only": { stroke: "transparent", "stroke-width": 0, dash: null, color: "var(--paper-muted)" },
};

// dataflow dash color per connection semantics, all via theme accent
// variables so the marching line always matches the active visual preset
// (paper blue / brutalism cobalt / apple system blue / glass lavender / …).
const FLOW_STROKE = {
  forward: "var(--accent-blue)",
  loss: "var(--accent-red)",
  data: "var(--accent-gray)",
  "backward-skip": "var(--accent-blue)",
};

// Order the forward/data main path for tour mode: modules and edges in walk
// order from the roots (no incoming forward/data edge) downstream, so a guided
// playback can light up the figure the way a presenter would narrate it.
function buildTourSeq(modules, connections) {
  const ids = new Set(modules.map((m) => m.id));
  const fwd = connections
    .map((c, i) => ({ from: c.from, to: c.to, variant: c.variant || "forward", i }))
    .filter((c) => c.variant === "forward" || c.variant === "data");
  const hasIncoming = new Set(fwd.map((c) => c.to));
  let roots = modules.map((m) => m.id).filter((id) => !hasIncoming.has(id));
  if (!roots.length) roots = [modules[0]?.id].filter(Boolean);
  // visit roots top-to-bottom, left-to-right so playback reads naturally
  const posOf = new Map(modules.map((m) => [m.id, m.pos]));
  roots.sort((a, b) => (posOf.get(a)[1] - posOf.get(b)[1]) || (posOf.get(a)[0] - posOf.get(b)[0]));
  const seq = [];
  const seenM = new Set();
  const seenE = new Set();
  const queue = [...roots];
  while (queue.length) {
    const id = queue.shift();
    if (seenM.has(id) || !ids.has(id)) continue;
    seenM.add(id);
    seq.push(["m", id]);
    for (const e of fwd) {
      if (e.from !== id || seenE.has(e.i)) continue;
      seenE.add(e.i);
      seq.push(["c", e.i]);
      queue.push(e.to);
    }
  }
  return seq;
}

export function renderModel(spec, opts = {}) {
  const visualPreset = opts.visual_preset || spec.meta?.visual_preset || "paper";
  const column = opts.column || spec.meta?.column || "single";
  const locale = spec.meta?.locale || "en";
  const langAttr = locale === "zh-CN" ? "zh-CN" : "en";

  const modules = spec.modules || [];
  const groups = spec.groups || [];
  const connections = spec.connections || [];
  const cards = spec.cards || [];

  // motion: opt-in dataflow layer, off by default so canonical output stays
  // purely static for print. meta.motion (or opts.motion, e.g. the CLI
  // --motion override) selects the default mode: "off" | "hover" ("on" is a
  // legacy alias) | "flow" | "tour". Every non-off mode renders the same
  // per-connection marching-dash flow layer ("------" style, no particles —
  // the user picked the pure dashed-line look) plus a small viewer switcher
  // (流动/悬停/巡演/静止) so readers can change modes live;
  // reduced-motion users, print media, and non-JS viewers always get the
  // static figure. Motion never changes geometry, so all artifact checks run
  // identically with motion on or off.
  const motionRaw = opts.motion ?? spec.meta?.motion ?? "off";
  const motionMode = motionRaw === "on" ? "hover" : ["hover", "flow", "tour"].includes(motionRaw) ? motionRaw : "off";
  const motion = motionMode !== "off";
  const moduleIds = modules.map((m) => m.id);
  const tourSeq = motion ? buildTourSeq(modules, connections) : [];

  // viewBox: from spec.meta.viewBox, or derive from modules
  let vb = spec.meta?.viewBox;
  if (!vb) {
    let maxX = 0, maxY = 0;
    for (const m of modules) {
      maxX = Math.max(maxX, m.pos[0] + m.size[0]);
      maxY = Math.max(maxY, m.pos[1] + m.size[1]);
    }
    vb = [Math.max(240, maxX + 24), Math.max(200, maxY + 24)];
  }
  const [vw, vh] = vb;

  // build module bbox lookup
  const modBbox = new Map();
  for (const m of modules) modBbox.set(m.id, bbox(m.pos, m.size));

  // build connection paths — fan-in/fan-out endpoints on a shared side are
  // spread apart so arrowheads never stack on the same point
  const endpointOverrides = spreadEndpoints(connections, (id) => modBbox.get(id));
  const connPaths = connections.map((c) => ({
    conn: c,
    path: buildConnectionPath(c, modBbox.get(c.from), modBbox.get(c.to), endpointOverrides.get(c)),
  }));

  // --- SVG body ---
  const svgParts = [];

  // defs: arrow markers
  svgParts.push(`<defs>`);
  for (const variant of ["forward", "loss", "data", "backward-skip"]) {
    const v = CONN_VARIANT[variant];
    svgParts.push(
      `<marker id="arrow-${variant}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">` +
      `<path d="M 0 0 L 10 5 L 0 10 z" fill="${v.color}"/>` +
      `</marker>`
    );
  }
  if (motion) {
    // flow-mode arrowheads in the same theme accent as the marching dash,
    // so the dashed edge keeps a color-matched direction cue
    for (const variant of ["forward", "loss", "data", "backward-skip"]) {
      svgParts.push(
        `<marker id="arrow-flow-${variant}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">` +
        `<path d="M 0 0 L 10 5 L 0 10 z" fill="${FLOW_STROKE[variant]}"/>` +
        `</marker>`
      );
    }
  }
  svgParts.push(`</defs>`);

  // groups (drawn first so they sit behind modules)
  for (const g of groups) {
    const boxes = g.wraps.map((id) => modBbox.get(id)).filter(Boolean);
    if (!boxes.length) continue;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const b of boxes) {
      if (b.x < minX) minX = b.x;
      if (b.y < minY) minY = b.y;
      if (b.x2 > maxX) maxX = b.x2;
      if (b.y2 > maxY) maxY = b.y2;
    }
    const pad = g.pad ?? 14;
    const gx = minX - pad, gy = minY - pad, gw = (maxX - minX) + 2 * pad, gh = (maxY - minY) + 2 * pad;
    const isDashed = g.kind === "ablation" || g.variant === "dashed";
    const stroke = g.variant === "emphasis" ? "var(--accent-blue)" : "var(--paper-border)";
    const dashAttr = isDashed ? ` stroke-dasharray="6 3"` : "";
    svgParts.push(
      `<rect class="pf-group pf-group-${g.kind}" x="${round(gx)}" y="${round(gy)}" width="${round(gw)}" height="${round(gh)}" ` +
      `rx="6" ry="6" fill="none" stroke="${stroke}" stroke-width="1"${dashAttr}/>`
    );
    // label in the top-left corner
    svgParts.push(
      `<text x="${round(gx + 8)}" y="${round(gy + 14)}" class="pf-group-label" fill="var(--paper-muted)">${escapeXml(g.label)}</text>`
    );
  }

  // connections (drawn before modules so module shapes overlay any endpoint stub)
  for (const [ci, { conn, path }] of connPaths.entries()) {
    const v = CONN_VARIANT[conn.variant || "forward"];
    if (conn.variant === "label-only") {
      // only the label, no path
      if (conn.label) {
        const at = conn.labelAt || path.p0;
        svgParts.push(
          `<text x="${round(at[0])}" y="${round(at[1])}" class="pf-conn-label" fill="${v.color}" text-anchor="middle">${escapeXml(conn.label)}</text>`
        );
      }
      continue;
    }
    const markerEnd = `marker-end="url(#arrow-${conn.variant || "forward"})"`;
    const dashAttr = v.dash ? ` stroke-dasharray="${v.dash}"` : "";
    // pair the static route with its flow dash via a shared connection index,
    // so each mode can swap solid ↔ dashed instead of overlaying them
    const ciAttr = motion ? ` data-pf-ci="${ci}"` : "";
    svgParts.push(
      `<path class="pf-conn pf-conn-${conn.variant || "forward"}"${ciAttr} d="${path.d}" fill="none" ` +
      `stroke="${v.stroke}" stroke-width="${v["stroke-width"]}"${dashAttr} ${markerEnd}/>`
    );
    if (motion) {
      // dataflow layer per connection: a marching-dash path ("------" style,
      // long segments with short gaps) in the theme accent color of its edge
      // semantics. While an edge flows, the static solid line steps aside —
      // the dash carries the arrowhead so direction stays readable.
      svgParts.push(
        `<path class="pf-flow pf-conn-${conn.variant || "forward"}" data-pf-from="${conn.from}" data-pf-to="${conn.to}" data-pf-ci="${ci}" d="${path.d}" fill="none" ` +
        `stroke="${FLOW_STROKE[conn.variant || "forward"]}" stroke-width="${v["stroke-width"]}" stroke-dasharray="9 5" ` +
        `stroke-linecap="round" marker-end="url(#arrow-flow-${conn.variant || "forward"})"/>`
      );
    }
    // connection label
    if (conn.label) {
      const at = conn.labelAt || path.samples[Math.floor(path.samples.length / 2)];
      svgParts.push(
        `<text x="${round(at[0])}" y="${round(at[1] - 4)}" class="pf-conn-label" fill="${v.color}" text-anchor="middle">${escapeXml(conn.label)}</text>`
      );
    }
    // tensor annotation on the connection
    if (conn.tensor_anno) {
      const at = conn.tensor_anno_at || path.samples[Math.floor(path.samples.length / 4)];
      svgParts.push(
        `<text x="${round(at[0])}" y="${round(at[1] - 4)}" class="pf-tensor-anno" fill="var(--paper-muted)">${escapeXml(conn.tensor_anno)}</text>`
      );
    }
  }

  // modules — two passes: nested containers (background frames) first, then regular modules on top
  const isContainer = (m) => Array.isArray(m.nested) && m.nested.length > 0;
  const containers = modules.filter(isContainer);
  const regular = modules.filter((m) => !isContainer(m));

  // pass 1: nested containers — dashed frame + light fill + label at top-inside
  for (const m of containers) {
    const variant = m.variant || "default";
    const sv = STROKE_VARIANT[variant];
    const fill = FILL_BY_TYPE[m.type] || "var(--fill-sdpa)";
    const x = m.pos[0], y = m.pos[1], w = m.size[0], h = m.size[1];
    const strokeAttrs = Object.entries(sv).map(([k, val]) => `${k}="${val}"`).join(" ");
    const dashAttr = ' stroke-dasharray="3 2"';
    const contDataAttr = motion ? ` data-pf-id="${m.id}"` : "";
    svgParts.push(`<g class="pf-mod pf-mod-${m.type} pf-container"${contDataAttr}>`);
    svgParts.push(`<rect x="${round(x)}" y="${round(y)}" width="${round(w)}" height="${round(h)}" rx="6" ry="6" fill="${fill}" fill-opacity="0.35" ${strokeAttrs}${dashAttr}/>`);
    if (variant === "repeated" && Number.isInteger(m.repeat) && m.repeat >= 2) {
      const repeatLabel = m.repeat_label || `×${m.repeat}`;
      svgParts.push(`<text x="${round(x + w - 6)}" y="${round(y + 14)}" class="pf-repeat-sigil" text-anchor="end" fill="var(--paper-muted)">${escapeXml(repeatLabel)}</text>`);
    }
    // container label at top-inside, auto-wrapped (repeated blocks leave room for the ×N sigil)
    const contLH = TEXT_METRICS.groupLabel.lineHeight;
    const contFont = TEXT_METRICS.groupLabel.font;
    const contLabelW = variant === "repeated" ? w - 44 : w - 16;
    const contLines = wrapText(m.label || "", contLabelW, contFont);
    svgParts.push(
      `<text class="pf-group-label" fill="var(--paper-muted)">` +
      contLines.map((ln, i) => `<tspan x="${round(x + 8)}" y="${round(y + 14 + i * contLH)}">${escapeXml(ln)}</tspan>`).join("") +
      `</text>`
    );
    if (m.sublabel) {
      const subY = y + 14 + contLines.length * contLH + 1;
      svgParts.push(`<text x="${round(x + 8)}" y="${round(subY)}" class="pf-mod-sublabel" fill="var(--paper-dim)">${escapeXml(m.sublabel)}</text>`);
    }
    if (m.tensor_shape) {
      svgParts.push(`<text x="${round(x + w - 6)}" y="${round(y + h - 6)}" class="pf-tensor-anno" text-anchor="end" fill="var(--paper-dim)">${escapeXml(m.tensor_shape)}</text>`);
    }
    svgParts.push(`</g>`);
  }

  // pass 2: regular modules (including nested children, drawn on top of their containers)
  for (const m of regular) {
    const shape = m.shape || SHAPE_DEFAULTS[m.type] || "rect";
    const variant = m.variant || "default";
    const sv = STROKE_VARIANT[variant];
    const fill = FILL_BY_TYPE[m.type] || "var(--fill-custom)";
    const x = m.pos[0], y = m.pos[1], w = m.size[0], h = m.size[1];
    const cx = x + w / 2, cy = y + h / 2;
    const strokeAttrs = Object.entries(sv).map(([k, val]) => `${k}="${val}"`).join(" ");
    const modDataAttr = motion ? ` data-pf-id="${m.id}"` : "";
    svgParts.push(`<g class="pf-mod pf-mod-${m.type}"${modDataAttr}>`);

    // shape
    if (shape === "rect") {
      svgParts.push(`<rect x="${round(x)}" y="${round(y)}" width="${round(w)}" height="${round(h)}" fill="${fill}" ${strokeAttrs}/>`);
    } else if (shape === "rounded") {
      svgParts.push(`<rect x="${round(x)}" y="${round(y)}" width="${round(w)}" height="${round(h)}" rx="6" ry="6" fill="${fill}" ${strokeAttrs}/>`);
    } else if (shape === "trapezoid") {
      const tinset = Math.min(8, w / 5);
      const pts = [
        [x + tinset, y], [x + w - tinset, y],
        [x + w, y + h], [x, y + h],
      ];
      svgParts.push(`<polygon points="${pts.map((p) => `${round(p[0])},${round(p[1])}`).join(" ")}" fill="${fill}" ${strokeAttrs}/>`);
    } else if (shape === "parallelogram") {
      const tinset = Math.min(8, w / 5);
      const pts = [
        [x + tinset, y], [x + w, y],
        [x + w - tinset, y + h], [x, y + h],
      ];
      svgParts.push(`<polygon points="${pts.map((p) => `${round(p[0])},${round(p[1])}`).join(" ")}" fill="${fill}" ${strokeAttrs}/>`);
    } else if (shape === "circle") {
      const r = Math.min(w, h) / 2;
      svgParts.push(`<circle cx="${round(cx)}" cy="${round(cy)}" r="${round(r)}" fill="${fill}" ${strokeAttrs}/>`);
    } else if (shape === "diamond") {
      const pts = [[cx, y], [x + w, cy], [cx, y + h], [x, cy]];
      svgParts.push(`<polygon points="${pts.map((p) => `${round(p[0])},${round(p[1])}`).join(" ")}" fill="${fill}" ${strokeAttrs}/>`);
    }

    // repeated block: interior divider line + ×N sigil
    if (variant === "repeated" && Number.isInteger(m.repeat) && m.repeat >= 2) {
      svgParts.push(`<line x1="${round(x + 4)}" y1="${round(y + 8)}" x2="${round(x + w - 4)}" y2="${round(y + 8)}" stroke="var(--fill-repeated-divider)" stroke-width="0.75"/>`);
      const repeatLabel = m.repeat_label || `×${m.repeat}`;
      svgParts.push(`<text x="${round(x + w - 5)}" y="${round(y + 7)}" class="pf-repeat-sigil" text-anchor="end" fill="var(--paper-muted)">${escapeXml(repeatLabel)}</text>`);
    }

    // label + sublabel: measure, auto-wrap into the shape, and center vertically
    // so text never spills outside the module boundary.
    const { font: labelFont, lineHeight: labelLH } = TEXT_METRICS.label;
    const { font: subFont, lineHeight: subLH } = TEXT_METRICS.sub;
    // circles/diamonds: the rendered diameter is min(w,h), not w — size the
    // text to the actual inscribed area near the vertical middle
    const usableW = shape === "circle" ? Math.min(w, h) * 0.68
      : shape === "diamond" ? Math.min(w, h) * 0.55
      : w - 10;
    const labelLines = wrapText(m.label, usableW, labelFont);
    const subLines = m.sublabel ? wrapText(m.sublabel, usableW, subFont) : [];
    const textH = labelLines.length * labelLH + subLines.length * subLH;
    let lineTop = cy - textH / 2;
    svgParts.push(
      `<text class="pf-mod-label" text-anchor="middle" fill="var(--paper-ink)">` +
      labelLines.map((ln) => {
        lineTop += labelLH;
        const baseline = lineTop - labelLH / 2 + labelFont * 0.35;
        return `<tspan x="${round(cx)}" y="${round(baseline)}">${escapeXml(ln)}</tspan>`;
      }).join("") +
      `</text>`
    );
    if (subLines.length) {
      svgParts.push(
        `<text class="pf-mod-sublabel" text-anchor="middle" fill="var(--paper-muted)">` +
        subLines.map((ln) => {
          lineTop += subLH;
          const baseline = lineTop - subLH / 2 + subFont * 0.35;
          return `<tspan x="${round(cx)}" y="${round(baseline)}">${escapeXml(ln)}</tspan>`;
        }).join("") +
        `</text>`
      );
    }
    // tensor shape annotation (next to the module)
    if (m.tensor_shape) {
      let tx, ty;
      if (m.tensor_pos) {
        tx = m.tensor_pos[0]; ty = m.tensor_pos[1];
      } else {
        // default: right side, vertically centered
        tx = x + w + 6; ty = cy + 4;
      }
      svgParts.push(
        `<text x="${round(tx)}" y="${round(ty)}" class="pf-tensor-anno" fill="var(--paper-muted)">${escapeXml(m.tensor_shape)}</text>`
      );
    }

    svgParts.push(`</g>`);
  }

  const svgBody = svgParts.join("\n  ");

  const svg = `<svg class="pf-canvas" viewBox="0 0 ${vw} ${vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="pf-title">` +
    `<title id="pf-title">${escapeXml(spec.meta.title)}</title>\n  ${svgBody}\n</svg>`;

  // --- HTML wrapper ---
  const columnClass = column === "double" ? "double" : "single";
  const subtitleHtml = spec.meta.subtitle ? `<div class="pf-subtitle">${escapeXml(spec.meta.subtitle)}</div>` : "";

  // viewer mode switcher (hidden in print / for reduced-motion users via CSS)
  const switchLabels = locale === "zh-CN"
    ? { flow: "流动", hover: "悬停", tour: "巡演", off: "静止" }
    : { flow: "Flow", hover: "Hover", tour: "Tour", off: "Still" };
  const switchHtml = motion
    ? `<div class="pf-switch" role="group" aria-label="dataflow mode">` +
      ["flow", "hover", "tour", "off"].map((m) =>
        `<button type="button" data-m="${m}" aria-pressed="${m === motionMode}">${switchLabels[m]}</button>`
      ).join("") +
      `</div>`
    : "";

  const cardsHtml = cards.length
    ? `<div class="pf-cards">` + cards.map((c) => {
        const dotClass = c.dot ? ` ${c.dot}` : "";
        const itemsHtml = (c.items || []).map((i) => `<li>${escapeXml(i)}</li>`).join("");
        return `<div class="pf-card"><div class="pf-card-title"><span class="pf-card-dot${dotClass}"></span>${escapeXml(c.title)}</div>` +
               `<ul class="pf-card-items">${itemsHtml}</ul></div>`;
      }).join("") + `</div>`
    : "";

  const legendEntries = spec.meta?.legend?.entries;
  const legendMode = spec.meta?.legend?.mode || "auto";
  let legendHtml = "";
  if (legendMode !== "hidden" && legendEntries) {
    const visibleTypes = Object.entries(legendEntries).filter(([_, v]) => v?.visible !== false).map(([k]) => k);
    const usedTypes = new Set(modules.map((m) => m.type));
    const showTypes = legendMode === "all" ? visibleTypes : visibleTypes.filter((t) => usedTypes.has(t));
    if (showTypes.length) {
      legendHtml = `<div class="pf-legend">` + showTypes.map((t) => {
        const label = legendEntries[t]?.label || t;
        return `<span class="pf-legend-item"><span class="pf-legend-swatch" style="background:${FILL_BY_TYPE[t] || "var(--fill-custom)"}"></span>${escapeXml(label)}</span>`;
      }).join("") + `</div>`;
    }
  }

  const html = `<!DOCTYPE html>
<html lang="${langAttr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeXml(spec.meta.title)}</title>
<style>${paperfigCss(visualPreset, motion, moduleIds)}</style>
</head>
<body>
<figure class="pf-figure${motion ? ` pf-motion pf-m-${motionMode}` : ""} ${columnClass}">
  ${switchHtml}
  <figcaption>
    <div class="pf-title">${escapeXml(spec.meta.title)}</div>
    ${subtitleHtml}
  </figcaption>
  ${svg}
  ${cardsHtml}
  ${legendHtml}
</figure>
${motion ? `<script>
(() => {
  const fig = document.querySelector('.pf-motion');
  if (!fig) return;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const flows = Array.from(fig.querySelectorAll('.pf-flow'));
  const connByCi = new Map(Array.from(fig.querySelectorAll('.pf-conn[data-pf-ci]')).map((c) => [c.getAttribute('data-pf-ci'), c]));
  const MODES = ['flow', 'hover', 'tour', 'off'];
  const tourSeq = ${JSON.stringify(tourSeq)};
  let mode = '${motionMode}';
  let ti = 0, tourTimer = null;
  const clearLive = () => {
    flows.forEach((p) => p.classList.remove('pf-live'));
    connByCi.forEach((c) => c.classList.remove('pf-live'));
  };
  const clearTour = () => {
    if (tourTimer) { clearTimeout(tourTimer); tourTimer = null; }
    flows.forEach((p) => p.classList.remove('pf-tour-on'));
    connByCi.forEach((c) => c.classList.remove('pf-tour-on'));
    fig.querySelectorAll('.pf-mod.pf-tour-on').forEach((m) => m.classList.remove('pf-tour-on'));
  };
  const stepTour = () => {
    if (mode !== 'tour' || !tourSeq.length) return;
    flows.forEach((p) => p.classList.remove('pf-tour-on'));
    connByCi.forEach((c) => c.classList.remove('pf-tour-on'));
    fig.querySelectorAll('.pf-mod.pf-tour-on').forEach((m) => m.classList.remove('pf-tour-on'));
    const step = tourSeq[ti % tourSeq.length]; ti++;
    let dwell = 700;
    if (step[0] === 'm') {
      const modEl = fig.querySelector('.pf-mod[data-pf-id="' + step[1] + '"]');
      if (modEl) modEl.classList.add('pf-tour-on');
    } else {
      const path = fig.querySelector('.pf-flow[data-pf-ci="' + step[1] + '"]');
      if (path) {
        path.classList.add('pf-tour-on');
        const c = connByCi.get(String(step[1]));
        if (c) c.classList.add('pf-tour-on');
        dwell = 1100;
      }
    }
    tourTimer = setTimeout(stepTour, dwell);
  };
  const setMode = (m) => {
    mode = m;
    MODES.forEach((x) => fig.classList.toggle('pf-m-' + x, x === m));
    fig.querySelectorAll('.pf-switch button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.m === m ? 'true' : 'false'));
    clearLive();
    clearTour();
    if (m === 'tour' && !reduce && tourSeq.length) { ti = 0; stepTour(); }
  };
  fig.querySelectorAll('.pf-switch button').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.m)));
  if (!reduce) {
    fig.querySelectorAll('.pf-mod[data-pf-id]').forEach((m) => {
      const id = m.getAttribute('data-pf-id');
      m.addEventListener('mouseenter', () => {
        if (mode !== 'hover' && mode !== 'flow') return;
        clearLive();
        flows.forEach((p) => {
          if (p.getAttribute('data-pf-from') === id || p.getAttribute('data-pf-to') === id) {
            p.classList.add('pf-live');
            const c = connByCi.get(p.getAttribute('data-pf-ci'));
            if (c) c.classList.add('pf-live');
          }
        });
      });
      m.addEventListener('mouseleave', clearLive);
    });
    fig.addEventListener('mouseleave', clearLive);
    if (mode === 'tour' && tourSeq.length) stepTour();
  }
})();
</script>` : ""}
</body>
</html>`;

  return { html, svg, viewBox: [vw, vh], bytes: Buffer.byteLength(html, "utf8") };
}

// Per-preset material overrides: these CSS rules override the SVG presentation
// attributes (CSS class rules win over presentation attributes), so each style
// can express its signature stroke weight, shadow language, and material feel
// without changing geometry or renderer code.
const PRESET_EXTRA = {
  brutalism: `
  .pf-title { font-family: var(--sans); font-size: 21px; font-weight: 900; letter-spacing: -0.02em; text-transform: uppercase; }
  .pf-mod-label { font-weight: 800; }
  .pf-mod:not(.pf-container) rect, .pf-mod:not(.pf-container) polygon, .pf-mod:not(.pf-container) circle {
    stroke-width: 2.5px;
    filter: drop-shadow(3px 3px 0 #111111);
  }
  .pf-conn { stroke-width: 2px; }
  .pf-group { stroke-width: 2px; }
  .pf-figure { border: 3px solid #111; box-shadow: 8px 8px 0 #111; }
  .pf-card { border: 2px solid #111; box-shadow: 4px 4px 0 #111; border-radius: 0; }
  .pf-card-title { font-family: var(--mono); }
  .pf-mod-encoder .pf-mod-label, .pf-mod-decoder .pf-mod-label, .pf-mod-linear .pf-mod-label, .pf-mod-scaled_dot_product_attention .pf-mod-label { fill: #ffffff; }
  .pf-mod-encoder .pf-mod-sublabel, .pf-mod-decoder .pf-mod-sublabel, .pf-mod-linear .pf-mod-sublabel, .pf-mod-scaled_dot_product_attention .pf-mod-sublabel { fill: rgba(255, 255, 255, 0.85); }
  `,
  playful: `
  .pf-mod rect { rx: 10px; ry: 10px; }
  .pf-figure { border-radius: 20px; }
  .pf-card { border-radius: 14px; border-width: 1.5px; }
  .pf-title { letter-spacing: 0.01em; }
  `,
  neumorphism: `
  .pf-mod rect, .pf-mod polygon, .pf-mod circle {
    stroke: none;
    filter: drop-shadow(-3px -3px 4px rgba(255, 255, 255, 0.9)) drop-shadow(4px 4px 6px rgba(140, 155, 180, 0.45));
  }
  .pf-conn { filter: drop-shadow(1px 1px 2px rgba(140, 155, 180, 0.35)); }
  .pf-card { border: none; box-shadow: -4px -4px 8px rgba(255,255,255,0.85), 5px 5px 10px rgba(140,155,180,0.4); }
  `,
  memphis: `
  .pf-mod rect, .pf-mod polygon, .pf-mod circle { stroke-width: 2px; }
  .pf-conn { stroke-width: 1.75px; }
  .pf-figure { border: 2.5px solid #212121; }
  .pf-card { border: 2px solid #212121; border-radius: 0; }
  .pf-title { text-transform: uppercase; letter-spacing: 0.04em; }
  `,
  bauhaus: `
  .pf-mod rect, .pf-mod polygon, .pf-mod circle { stroke-width: 1.75px; }
  .pf-conn { stroke-width: 1.5px; }
  .pf-mod rect { rx: 0px; ry: 0px; }
  .pf-mod-encoder .pf-mod-label, .pf-mod-decoder .pf-mod-label { fill: #ffffff; }
  .pf-mod-encoder .pf-mod-sublabel, .pf-mod-decoder .pf-mod-sublabel { fill: rgba(255, 255, 255, 0.8); }
  .pf-figure { border: 2px solid #1a1a1a; }
  .pf-card { border: 1.5px solid #1a1a1a; border-radius: 0; }
  .pf-title { font-weight: 800; letter-spacing: 0.02em; }
  `,
  glass: `
  body { background: linear-gradient(135deg, #667eea 0%, #764ba2 55%, #6b8dd6 100%); background-attachment: fixed; }
  .pf-figure { background: rgba(255, 255, 255, 0.08); border-radius: 18px; }
  .pf-card { background: rgba(255, 255, 255, 0.16); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.4); }
  .pf-legend-swatch { border-color: rgba(255, 255, 255, 0.5); }
  `,
  apple: `
  :root {
    --serif: "HarmonyOS Sans", -apple-system, "SF Pro Display", "Segoe UI", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
    --sans: "HarmonyOS Sans", -apple-system, "SF Pro Text", "Segoe UI", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
    --mono: "HarmonyOS Sans", "SF Mono", ui-monospace, "JetBrains Mono", "Consolas", monospace;
  }
  .pf-figure { background: #ffffff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); }
  .pf-title { letter-spacing: -0.02em; }
  .pf-subtitle { letter-spacing: -0.01em; }
  .pf-mod rect, .pf-mod polygon, .pf-mod circle {
    stroke-width: 1px;
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.10));
  }
  .pf-mod rect { rx: 10px; ry: 10px; }
  .pf-group { stroke-width: 1px; }
  .pf-conn { stroke-width: 1.5px; }
  .pf-card {
    background: rgba(245, 245, 247, 0.72);
    backdrop-filter: blur(14px) saturate(180%);
    -webkit-backdrop-filter: blur(14px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
  }
  .pf-legend-swatch { border-radius: 4px; border-color: rgba(0, 0, 0, 0.10); }
  `,
};

function paperfigCss(preset, motion, moduleIds) {
  // preset only changes color tokens; layout is identical
  const presetVars = preset === "paper-dark"
    ? `
    --paper-bg: #1c1c1c;
    --paper-ink: #f0f0f0;
    --paper-muted: #b0b0b0;
    --paper-dim: #808080;
    --paper-border: #444444;
    --paper-rule: #2a2a2a;
    --accent-blue: #60a5fa;
    --accent-red: #f87171;
    --accent-gray: #9ca3af;
    --fill-input: #2a2a2a;
    --fill-encoder: #2a2f44;
    --fill-attention: #3d3522;
    --fill-ffn: #1f2e26;
    --fill-norm: #2c2c2c;
    --fill-output: #2a2a2a;
    --fill-residual: #3a2a1f;
    --fill-concat: #2c2c2c;
    --fill-custom: #1f1f1f;
    --fill-repeated-divider: #4a4a4a;
    --fill-linear: #1f2940;
    --fill-matmul: #2a2a2a;
    --fill-scale: #3d3522;
    --fill-softmax: #3a1f1f;
    --fill-add: #3a2a1f;
    --fill-layernorm: #2a2a2a;
    --fill-gelu: #1f2e26;
    --fill-sdpa: #1f2a3a;
  `
    : preset === "brutalism"
    ? `
    --paper-bg: #fffdf5;
    --paper-ink: #111111;
    --paper-muted: #333333;
    --paper-dim: #555555;
    --paper-border: #111111;
    --paper-rule: #111111;
    --accent-blue: #0047ab;
    --accent-red: #f04438;
    --accent-gray: #6f6f6f;
    --fill-input: #ffd60a;
    --fill-encoder: #0047ab;
    --fill-attention: #f04438;
    --fill-ffn: #0ec463;
    --fill-norm: #ffffff;
    --fill-output: #ffd60a;
    --fill-residual: #a259ff;
    --fill-concat: #ffffff;
    --fill-custom: #ffffff;
    --fill-repeated-divider: #111111;
    --fill-linear: #0047ab;
    --fill-matmul: #ffffff;
    --fill-scale: #ffd60a;
    --fill-softmax: #f04438;
    --fill-add: #a259ff;
    --fill-layernorm: #ffffff;
    --fill-gelu: #0ec463;
    --fill-sdpa: #0047ab;
  `
    : preset === "playful"
    ? `
    --paper-bg: #fff9f0;
    --paper-ink: #4a3b32;
    --paper-muted: #8a7a6d;
    --paper-dim: #b0a295;
    --paper-border: #e8d5c4;
    --paper-rule: #f0e4d8;
    --accent-blue: #4db6ac;
    --accent-red: #ff8a65;
    --accent-gray: #a1887f;
    --fill-input: #ffe0b2;
    --fill-encoder: #b2dfdb;
    --fill-attention: #ffccbc;
    --fill-ffn: #c8e6c9;
    --fill-norm: #efebe9;
    --fill-output: #ffe0b2;
    --fill-residual: #ffccbc;
    --fill-concat: #efebe9;
    --fill-custom: #fffdf9;
    --fill-repeated-divider: #d7ccc8;
    --fill-linear: #ffe9c7;
    --fill-matmul: #efebe9;
    --fill-scale: #fff3c4;
    --fill-softmax: #ffd9cf;
    --fill-add: #ffe5d3;
    --fill-layernorm: #efebe9;
    --fill-gelu: #d5efd5;
    --fill-sdpa: #d6f0ee;
  `
    : preset === "neumorphism"
    ? `
    --paper-bg: #e3e9f2;
    --paper-ink: #4a5568;
    --paper-muted: #718096;
    --paper-dim: #a0aec0;
    --paper-border: #c5cdd9;
    --paper-rule: #d5dbe6;
    --accent-blue: #6b8dd6;
    --accent-red: #d67b7b;
    --accent-gray: #8a97a8;
    --fill-input: #dde3ec;
    --fill-encoder: #dbe4f0;
    --fill-attention: #e6e3ee;
    --fill-ffn: #dce8e4;
    --fill-norm: #e0e5ee;
    --fill-output: #dde3ec;
    --fill-residual: #e8e2e0;
    --fill-concat: #e0e5ee;
    --fill-custom: #e6ebf3;
    --fill-repeated-divider: #c5cdd9;
    --fill-linear: #dbe4f0;
    --fill-matmul: #e0e5ee;
    --fill-scale: #e6e3ee;
    --fill-softmax: #e8e2e0;
    --fill-add: #e8e5e0;
    --fill-layernorm: #e0e5ee;
    --fill-gelu: #dce8e4;
    --fill-sdpa: #dde6f0;
  `
    : preset === "memphis"
    ? `
    --paper-bg: #fdf6ec;
    --paper-ink: #212121;
    --paper-muted: #424242;
    --paper-dim: #757575;
    --paper-border: #212121;
    --paper-rule: #212121;
    --accent-blue: #3742fa;
    --accent-red: #ff4757;
    --accent-gray: #747d8c;
    --fill-input: #ffc312;
    --fill-encoder: #70a1ff;
    --fill-attention: #ff6b81;
    --fill-ffn: #7bed9f;
    --fill-norm: #f1f2f6;
    --fill-output: #ffc312;
    --fill-residual: #ff9f43;
    --fill-concat: #f1f2f6;
    --fill-custom: #ffffff;
    --fill-repeated-divider: #212121;
    --fill-linear: #9c88ff;
    --fill-matmul: #f1f2f6;
    --fill-scale: #ffd32a;
    --fill-softmax: #ff6b81;
    --fill-add: #ff9f43;
    --fill-layernorm: #f1f2f6;
    --fill-gelu: #7bed9f;
    --fill-sdpa: #70a1ff;
  `
    : preset === "bauhaus"
    ? `
    --paper-bg: #f7f5f0;
    --paper-ink: #1a1a1a;
    --paper-muted: #4a4a44;
    --paper-dim: #8a887f;
    --paper-border: #1a1a1a;
    --paper-rule: #1a1a1a;
    --accent-blue: #2255a4;
    --accent-red: #d64141;
    --accent-gray: #6a6860;
    --fill-input: #f2c230;
    --fill-encoder: #2255a4;
    --fill-attention: #d64141;
    --fill-ffn: #f2c230;
    --fill-norm: #e8e6e1;
    --fill-output: #ffffff;
    --fill-residual: #e8e6e1;
    --fill-concat: #e8e6e1;
    --fill-custom: #ffffff;
    --fill-repeated-divider: #1a1a1a;
    --fill-linear: #ffffff;
    --fill-matmul: #e8e6e1;
    --fill-scale: #e8e6e1;
    --fill-softmax: #e8e6e1;
    --fill-add: #e8e6e1;
    --fill-layernorm: #e8e6e1;
    --fill-gelu: #e8e6e1;
    --fill-sdpa: #d7e0f0;
  `
    : preset === "glass"
    ? `
    --paper-bg: #5b6ee8;
    --paper-ink: #ffffff;
    --paper-muted: rgba(255, 255, 255, 0.85);
    --paper-dim: rgba(255, 255, 255, 0.6);
    --paper-border: rgba(255, 255, 255, 0.55);
    --paper-rule: rgba(255, 255, 255, 0.3);
    --accent-blue: #a5b4fc;
    --accent-red: #fda4af;
    --accent-gray: rgba(255, 255, 255, 0.7);
    --fill-input: rgba(255, 255, 255, 0.35);
    --fill-encoder: rgba(255, 255, 255, 0.30);
    --fill-attention: rgba(255, 255, 255, 0.28);
    --fill-ffn: rgba(255, 255, 255, 0.30);
    --fill-norm: rgba(255, 255, 255, 0.22);
    --fill-output: rgba(255, 255, 255, 0.35);
    --fill-residual: rgba(255, 255, 255, 0.28);
    --fill-concat: rgba(255, 255, 255, 0.22);
    --fill-custom: rgba(255, 255, 255, 0.32);
    --fill-repeated-divider: rgba(255, 255, 255, 0.5);
    --fill-linear: rgba(255, 255, 255, 0.34);
    --fill-matmul: rgba(255, 255, 255, 0.22);
    --fill-scale: rgba(255, 255, 255, 0.30);
    --fill-softmax: rgba(255, 255, 255, 0.28);
    --fill-add: rgba(255, 255, 255, 0.30);
    --fill-layernorm: rgba(255, 255, 255, 0.22);
    --fill-gelu: rgba(255, 255, 255, 0.30);
    --fill-sdpa: rgba(255, 255, 255, 0.26);
  `
    : preset === "blueprint-print"
    ? `
    --paper-bg: #ffffff;
    --paper-ink: #000000;
    --paper-muted: #333333;
    --paper-dim: #666666;
    --paper-border: #000000;
    --paper-rule: #cccccc;
    --accent-blue: #000000;
    --accent-red: #333333;
    --accent-gray: #555555;
    --fill-input: #ffffff;
    --fill-encoder: #ffffff;
    --fill-attention: #ffffff;
    --fill-ffn: #ffffff;
    --fill-norm: #ffffff;
    --fill-output: #ffffff;
    --fill-residual: #ffffff;
    --fill-concat: #ffffff;
    --fill-custom: #ffffff;
    --fill-repeated-divider: #000000;
    --fill-linear: #ffffff;
    --fill-matmul: #ffffff;
    --fill-scale: #ffffff;
    --fill-softmax: #ffffff;
    --fill-add: #ffffff;
    --fill-layernorm: #ffffff;
    --fill-gelu: #ffffff;
    --fill-sdpa: #ffffff;
  `
    : preset === "apple"
    ? `
    --paper-bg: #f5f5f7;
    --paper-ink: #1d1d1f;
    --paper-muted: #6e6e73;
    --paper-dim: #86868b;
    --paper-border: rgba(0, 0, 0, 0.10);
    --paper-rule: rgba(0, 0, 0, 0.06);
    --accent-blue: #0071e3;
    --accent-red: #ff3b30;
    --accent-gray: #8e8e93;
    --fill-input: #eef4fb;
    --fill-encoder: #e8f0fe;
    --fill-attention: #fef4e8;
    --fill-ffn: #e9f7ef;
    --fill-norm: #f2f2f4;
    --fill-output: #eef4fb;
    --fill-residual: #fff3e6;
    --fill-concat: #f2f2f4;
    --fill-custom: #fafafc;
    --fill-repeated-divider: #d2d2d7;
    --fill-linear: #e8f0fe;
    --fill-matmul: #f2f2f4;
    --fill-scale: #fef4e8;
    --fill-softmax: #fdecec;
    --fill-add: #fff3e6;
    --fill-layernorm: #f2f2f4;
    --fill-gelu: #e9f7ef;
    --fill-sdpa: #e8f0fe;
  `
    : `
    --paper-bg: #ffffff;
    --paper-ink: #1a1a1a;
    --paper-muted: #5a5a5a;
    --paper-dim: #8a8a8a;
    --paper-border: #c8c8c8;
    --paper-rule: #e0e0e0;
    --accent-blue: #2563eb;
    --accent-red: #b91c1c;
    --accent-gray: #6b7280;
    --fill-input: #f5f5f5;
    --fill-encoder: #eef2ff;
    --fill-attention: #fef3c7;
    --fill-ffn: #ecfdf5;
    --fill-norm: #f3f4f6;
    --fill-output: #f5f5f5;
    --fill-residual: #fff7ed;
    --fill-concat: #f3f4f6;
    --fill-custom: #fafafa;
    --fill-repeated-divider: #d4d4d4;
    --fill-linear: #e6f0ff;
    --fill-matmul: #f0f0f0;
    --fill-scale: #fff5e0;
    --fill-softmax: #ffe6e6;
    --fill-add: #fff0e0;
    --fill-layernorm: #f0f0f0;
    --fill-gelu: #e6ffe6;
    --fill-sdpa: #e6f7ff;
  `;

  const presetExtra = PRESET_EXTRA[preset] || "";

  return `${fontFaceCss()}
  :root {${presetVars}
    --serif: "HarmonyOS Sans", "Cambria", "Georgia", "Times New Roman", "Noto Serif CJK SC", "SimSun", serif;
    --sans: "HarmonyOS Sans", -apple-system, "Segoe UI", "Arial", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    --mono: "HarmonyOS Sans", "SF Mono", "JetBrains Mono", "Consolas", monospace;
  }
  html, body { margin: 0; padding: 0; background: var(--paper-bg); color: var(--paper-ink); }
  body { font-family: var(--sans); font-size: 14px; line-height: 1.55; }
  .pf-figure { max-width: 100%; margin: 0 auto; padding: 24px; box-sizing: border-box; }
  .pf-figure.single { max-width: 336px; }
  .pf-figure.double { max-width: 672px; }
  .pf-title { font-family: var(--serif); font-size: 16px; font-weight: 700; margin: 0 0 4px; }
  .pf-subtitle { font-family: var(--sans); font-size: 12px; color: var(--paper-muted); margin: 0 0 16px; }
  .pf-canvas { display: block; width: 100%; height: auto; }
  ${motion ? `
  .pf-motion .pf-flow { stroke-dasharray: 9 5; opacity: 0; transition: opacity 180ms ease; }
  .pf-motion .pf-conn { transition: opacity 180ms ease; }
  .pf-motion .pf-mod[data-pf-id] { cursor: pointer; }
  .pf-m-flow .pf-flow { opacity: 0.6; animation: pf-flow 1s linear infinite; }
  .pf-m-flow .pf-conn { opacity: 0; }
  .pf-m-hover .pf-conn.pf-live, .pf-m-tour .pf-conn.pf-tour-on { opacity: 0; }
  .pf-m-hover .pf-flow.pf-live, .pf-m-flow .pf-flow.pf-live { opacity: 0.95; animation: pf-flow 1s linear infinite; }
  ${moduleIds.map((id) => `.pf-m-hover:has([data-pf-id="${id}"]:hover) .pf-flow[data-pf-from="${id}"],
  .pf-m-hover:has([data-pf-id="${id}"]:hover) .pf-flow[data-pf-to="${id}"],
  .pf-m-flow:has([data-pf-id="${id}"]:hover) .pf-flow[data-pf-from="${id}"],
  .pf-m-flow:has([data-pf-id="${id}"]:hover) .pf-flow[data-pf-to="${id}"] { opacity: 0.95; animation: pf-flow 1s linear infinite; }
  .pf-m-hover:has([data-pf-id="${id}"]:hover) .pf-conn[data-pf-from="${id}"],
  .pf-m-hover:has([data-pf-id="${id}"]:hover) .pf-conn[data-pf-to="${id}"] { opacity: 0; }`).join("\n  ")}
  .pf-m-tour .pf-flow.pf-tour-on { opacity: 0.95; animation: pf-flow 1s linear infinite; }
  .pf-m-tour .pf-mod.pf-tour-on rect, .pf-m-tour .pf-mod.pf-tour-on polygon, .pf-m-tour .pf-mod.pf-tour-on circle { stroke: var(--accent-blue); stroke-width: 2.25px; }
  .pf-switch { display: flex; gap: 4px; justify-content: flex-end; margin: 0 0 8px; }
  .pf-switch button { font-family: var(--sans); font-size: 11px; line-height: 1.6; padding: 1px 10px; border-radius: 999px; border: 1px solid var(--paper-border); background: transparent; color: var(--paper-muted); cursor: pointer; }
  .pf-switch button[aria-pressed="true"] { background: color-mix(in srgb, var(--accent-blue) 72%, #000000); border-color: var(--accent-blue); color: #ffffff; }
  @keyframes pf-flow { to { stroke-dashoffset: -14; } }
  @media (prefers-reduced-motion: reduce) {
    .pf-motion .pf-flow { opacity: 0 !important; animation: none !important; }
    .pf-switch { display: none; }
  }
  @media print {
    .pf-motion .pf-flow { display: none; }
    .pf-switch { display: none; }
  }
  ` : ""}
  .pf-mod-label { font-family: var(--sans); font-size: 12px; font-weight: 600; }
  .pf-mod-sublabel { font-family: var(--sans); font-size: 10px; font-weight: 400; }
  .pf-tensor-anno { font-family: var(--mono); font-size: 9px; font-weight: 400; }
  .pf-repeat-sigil { font-family: var(--mono); font-size: 9px; font-weight: 700; }
  .pf-conn-label { font-family: var(--sans); font-size: 10px; font-weight: 500; }
  .pf-group-label { font-family: var(--sans); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
  .pf-cards { display: grid; grid-template-columns: 1fr; gap: 8px; margin-top: 16px; }
  @media (min-width: 480px) { .pf-cards { grid-template-columns: 1fr 1fr; } }
  .pf-card { border: 1px solid var(--paper-border); border-radius: 4px; padding: 8px 10px; background: color-mix(in srgb, var(--paper-bg) 96%, var(--paper-ink) 4%); }
  .pf-card-title { font-family: var(--sans); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 4px; display: flex; align-items: center; gap: 6px; }
  .pf-card-dot { display: inline-block; width: 8px; height: 8px; border-radius: 999px; background: var(--paper-ink); }
  .pf-card-dot.blue { background: var(--accent-blue); }
  .pf-card-dot.red { background: var(--accent-red); }
  .pf-card-dot.gray { background: var(--accent-gray); }
  .pf-card-items { margin: 0; padding-left: 14px; font-size: 11px; color: var(--paper-muted); }
  .pf-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; font-size: 11px; color: var(--paper-muted); }
  .pf-legend-item { display: flex; align-items: center; gap: 4px; }
  .pf-legend-swatch { display: inline-block; width: 14px; height: 10px; border: 1px solid var(--paper-border); }
  ${presetExtra}
  @media print {
    .pf-figure { max-width: none !important; padding: 0 !important; }
    body { background: white; }
  }
  `;
}
