// paperfig / renderers / shared / validator.mjs
// Lightweight JSON-schema-like validator + 11 showcase artifact checks.
// We avoid pulling ajv to keep the skill zero-dependency (matches archify's no-install contract).

import {
  bbox,
  bboxesOverlap,
  segmentIntersectsRect,
  buildConnectionPath,
  spreadEndpoints,
  rectFromPoints,
  collinearRunLen,
} from "./geometry.mjs";
import { ensureUniqueIds, isValidId, estTextWidth, wrapText } from "./utils.mjs";
import { SHAPE_DEFAULTS, TEXT_METRICS } from "./shapes.mjs";

// --- minimal schema validators ---

const TYPE_CHECKS = {
  string: (v) => typeof v === "string",
  number: (v) => typeof v === "number" && Number.isFinite(v),
  integer: (v) => typeof v === "number" && Number.isInteger(v),
  boolean: (v) => typeof v === "boolean",
  array: (v) => Array.isArray(v),
  object: (v) => typeof v === "object" && v !== null && !Array.isArray(v),
};

export function validateSchema(json, schema, defs = {}) {
  const errors = [];
  validateNode(json, schema, "$", defs, errors);
  return { ok: errors.length === 0, errors };
}

function validateNode(value, schema, path, defs, errors) {
  if (!schema) return;
  if (schema.$ref) {
    const refSchema = resolveRef(schema.$ref, defs);
    validateNode(value, refSchema, path, defs, errors);
    return;
  }
  if (schema.const !== undefined) {
    if (!Object.is(value, schema.const)) {
      errors.push({ path, msg: `expected const ${JSON.stringify(schema.const)}, got ${JSON.stringify(value)}` });
    }
    return;
  }
  if (schema.enum) {
    if (!schema.enum.includes(value)) {
      errors.push({ path, msg: `${JSON.stringify(value)} not in enum [${schema.enum.join(", ")}]` });
    }
    return;
  }
  if (schema.type) {
    const ok = TYPE_CHECKS[schema.type]?.(value);
    if (!ok) {
      errors.push({ path, msg: `expected type ${schema.type}, got ${typeof value}` });
      return;
    }
  }
  if (schema.type === "string") {
    if (schema.minLength !== undefined && value.length < schema.minLength)
      errors.push({ path, msg: `string too short (min ${schema.minLength})` });
    if (schema.pattern && !new RegExp(schema.pattern).test(value))
      errors.push({ path, msg: `string does not match pattern ${schema.pattern}` });
    return;
  }
  if (schema.type === "number" || schema.type === "integer") {
    if (schema.minimum !== undefined && value < schema.minimum)
      errors.push({ path, msg: `${value} < minimum ${schema.minimum}` });
    if (schema.maximum !== undefined && value > schema.maximum)
      errors.push({ path, msg: `${value} > maximum ${schema.maximum}` });
    return;
  }
  if (schema.type === "array") {
    if (schema.minItems !== undefined && value.length < schema.minItems)
      errors.push({ path, msg: `array too short (min ${schema.minItems})` });
    if (schema.maxItems !== undefined && value.length > schema.maxItems)
      errors.push({ path, msg: `array too long (max ${schema.maxItems})` });
    if (schema.prefixItems) {
      for (let i = 0; i < Math.min(schema.prefixItems.length, value.length); i++) {
        validateNode(value[i], schema.prefixItems[i], `${path}[${i}]`, defs, errors);
      }
    }
    if (schema.items && !Array.isArray(schema.items)) {
      for (let i = 0; i < value.length; i++) {
        validateNode(value[i], schema.items, `${path}[${i}]`, defs, errors);
      }
    }
    return;
  }
  if (schema.type === "object") {
    if (schema.required) {
      for (const r of schema.required) {
        if (!Object.prototype.hasOwnProperty.call(value, r))
          errors.push({ path, msg: `missing required property "${r}"` });
      }
    }
    if (schema.properties) {
      for (const [k, sub] of Object.entries(schema.properties)) {
        if (Object.prototype.hasOwnProperty.call(value, k)) {
          validateNode(value[k], sub, `${path}.${k}`, defs, errors);
        }
      }
    }
    if (schema.additionalProperties === false) {
      for (const k of Object.keys(value)) {
        if (!schema.properties || !Object.prototype.hasOwnProperty.call(schema.properties, k)) {
          errors.push({ path, msg: `unknown property "${k}" (additionalProperties: false)` });
        }
      }
    }
  }
}

function resolveRef(ref, defs) {
  // refs look like "common.schema.json#/$defs/locale"
  const parts = ref.split("#/");
  if (parts.length < 2) return null;
  const segs = parts[1].split("/");
  let node = defs;
  for (const s of segs) {
    node = node?.[s];
    if (!node) return null;
  }
  return node;
}

// Load a schema with its $defs inlined so $ref can resolve.
export function buildSchemaContext(commonSchema, typeSchema) {
  return {
    ...typeSchema,
    $defs: commonSchema?.$defs || {},
  };
}

// --- 11 showcase artifact checks ---

// Returns { total, errors, warnings, items: [{rule, severity, subject, evidence, supportedFixes}] }
export function runArtifactChecks(spec, opts = {}) {
  const quality = spec?.meta?.quality_profile || "standard";
  const items = [];
  const error = (rule, subject, evidence, supportedFixes = []) => items.push({
    rule, subject, evidence, severity: "error", supportedFixes,
  });
  const warn = (rule, subject, evidence, supportedFixes = []) => items.push({
    rule, subject, evidence, severity: "warning", supportedFixes,
  });
  const record = quality === "showcase" ? error : warn;

  // Build module lookup + bboxes
  const modules = spec.modules || [];
  const modById = new Map();
  const modBbox = new Map();
  for (const m of modules) {
    modById.set(m.id, m);
    modBbox.set(m.id, bbox(m.pos, m.size));
  }
  // Build the set of nested-child ids: a module that appears in another module's
  // `nested[]` belongs to its parent for contiguity purposes and is skipped by the
  // stage-contiguity check (the parent, if listed in wraps[], carries it).
  // We also stamp `__parent` on each child so the no-overlap check can skip
  // parent↔child pairs (a child overlapping its own container is intended nesting).
  const nestedChildIds = new Set();
  for (const m of modules) {
    if (Array.isArray(m.nested)) {
      for (const id of m.nested) {
        if (modById.has(id)) {
          nestedChildIds.add(id);
          modById.get(id).__parent = m.id;
        }
      }
    }
  }

  // 1. schema valid is checked outside; here we add a structural sanity check
  // (check that every group/connection references existing module ids)
  for (const g of spec.groups || []) {
    for (const id of g.wraps) {
      if (!modById.has(id)) {
        error("group-wraps-existing", g.label, `group references unknown module "${id}"`, ["fix wraps list"]);
      }
    }
  }
  for (const c of spec.connections || []) {
    if (!modById.has(c.from)) error("conn-from-existing", c.id || `${c.from}->${c.to}`, `from "${c.from}" not found`, ["fix from"]);
    if (!modById.has(c.to)) error("conn-to-existing", c.id || `${c.from}->${c.to}`, `to "${c.to}" not found`, ["fix to"]);
  }

  // 2. no module overlap (tolerance 1px)
  // A nested child overlapping its own container parent is the intended nesting
  // behavior, not an overlap error: skip parent↔child pairs.
  for (let i = 0; i < modules.length; i++) {
    for (let j = i + 1; j < modules.length; j++) {
      const idA = modules[i].id, idB = modules[j].id;
      const aIsChildOfB = nestedChildIds.has(idA) && (modById.get(idA)?.__parent === idB);
      const bIsChildOfA = nestedChildIds.has(idB) && (modById.get(idB)?.__parent === idA);
      if (aIsChildOfB || bIsChildOfA) continue;
      const a = modBbox.get(idA);
      const b = modBbox.get(idB);
      if (bboxesOverlap(a, b, 1)) {
        record("no-module-overlap", `${idA} vs ${idB}`,
          `rects overlap (${(Math.min(a.x2, b.x2) - Math.max(a.x, b.x)).toFixed(1)} × ${(Math.min(a.y2, b.y2) - Math.max(a.y, b.y)).toFixed(1)}px)`,
          ["move one module pos", "shrink one module size"]);
      }
    }
  }

  // 3. no edge-module overlap (a connection must not cross an unrelated opaque module)
  // build path samples for each connection first — must mirror the renderer's
  // fan-in/fan-out endpoint spreading so checks test the rendered geometry
  const endpointOverrides = spreadEndpoints(spec.connections || [], (id) => modBbox.get(id));
  const connPaths = [];
  for (const c of spec.connections || []) {
    if (!modById.has(c.from) || !modById.has(c.to)) continue;
    const path = buildConnectionPath(c, modBbox.get(c.from), modBbox.get(c.to), endpointOverrides.get(c));
    connPaths.push({ conn: c, path });
  }

  for (const { conn, path } of connPaths) {
    for (const m of modules) {
      if (m.id === conn.from || m.id === conn.to) continue;
      // Nested containers are dashed frames with a translucent fill, not opaque
      // blocks: a connection may legitimately cross its border. Skip them.
      if (Array.isArray(m.nested) && m.nested.length > 0) continue;
      const mb = modBbox.get(m.id);
      for (let i = 0; i < path.samples.length - 1; i++) {
        if (segmentIntersectsRect(path.samples[i], path.samples[i + 1], mb, 0.5)) {
          record("no-edge-module-overlap", `${conn.from}->${conn.to} crosses ${m.id}`,
            `segment (${path.samples[i][0].toFixed(0)},${path.samples[i][1].toFixed(0)})→(${path.samples[i+1][0].toFixed(0)},${path.samples[i+1][1].toFixed(0)}) crosses ${m.id}`,
            ["adjust route", "add via", "move blocking module"]);
          break;
        }
      }
    }
  }

  // 4. no edge-edge overlap (collinear run > 8px, except shared endpoint fan-out)
  for (let i = 0; i < connPaths.length; i++) {
    for (let j = i + 1; j < connPaths.length; j++) {
      const a = connPaths[i], b = connPaths[j];
      // skip shared-endpoint fan-out (both share an endpoint)
      if (a.conn.from === b.conn.from || a.conn.from === b.conn.to ||
          a.conn.to === b.conn.from || a.conn.to === b.conn.to) continue;
      const run = collinearRunLen(a.path.samples, b.path.samples);
      if (run > 8) {
        record("no-edge-edge-overlap", `${a.conn.from}->${a.conn.to} vs ${b.conn.from}->${b.conn.to}`,
          `collinear run ${run.toFixed(1)}px`,
          ["adjust route on one edge", "add via to one edge"]);
      }
    }
  }

  // 5. label / tensor-shape clearance — the actual text rect (padded by 1.5px)
  // must not be crossed by any foreign route. Rect-intersection at the same
  // coordinates the renderer uses, not a center-point approximation.
  const textRects = [];
  for (const { conn, path } of connPaths) {
    if (conn.label) {
      const at = conn.labelAt || pathMidpoint(path.samples);
      if (at) {
        textRects.push({
          kind: "conn-label",
          owner: conn,
          rect: textRectAt(conn.label, [at[0], at[1] - 4], TEXT_METRICS.connLabel.font, "middle"),
        });
      }
    }
    if (conn.tensor_anno) {
      const at = conn.tensor_anno_at || path.samples[Math.floor(path.samples.length / 4)];
      if (at) {
        textRects.push({
          kind: "conn-tensor",
          owner: conn,
          rect: textRectAt(conn.tensor_anno, [at[0], at[1] - 4], TEXT_METRICS.tensor.font, "middle"),
        });
      }
    }
  }
  for (const m of modules) {
    if (!m.tensor_shape) continue;
    const mb = modBbox.get(m.id);
    // Mirror the renderer: nested containers draw their tensor annotation at the
    // bottom-right corner INSIDE the frame (text-anchor: end); regular modules
    // honor tensor_pos or default to the right side, vertically centered.
    const isContainer = Array.isArray(m.nested) && m.nested.length > 0;
    let at, anchor;
    if (isContainer) {
      at = [mb.x2 - 6, mb.y2 - 6];
      anchor = "end";
    } else {
      at = m.tensor_pos || [mb.x2 + 6, mb.cy + 4];
      anchor = "start";
    }
    textRects.push({
      kind: "tensor",
      owner: m.id,
      rect: textRectAt(m.tensor_shape, at, TEXT_METRICS.tensor.font, anchor),
    });
  }
  // Container (nested) label/sublabel sit at the top-left INSIDE the frame — a
  // route is allowed to cross the translucent frame itself, but never the label
  // text. Mirror the renderer's top-inside wrap layout.
  for (const m of modules) {
    if (!(Array.isArray(m.nested) && m.nested.length > 0)) continue;
    const mb = modBbox.get(m.id);
    const gFont = TEXT_METRICS.groupLabel.font;
    const gLH = TEXT_METRICS.groupLabel.lineHeight;
    const labelW = m.variant === "repeated" ? mb.w - 44 : mb.w - 16;
    const lines = wrapText(m.label || "", labelW, gFont);
    lines.forEach((ln, i) => {
      textRects.push({
        kind: "container-label",
        owner: m.id,
        rect: textRectAt(ln, [mb.x + 8, mb.y + 14 + i * gLH], gFont, "start"),
      });
    });
    if (m.sublabel) {
      const subY = mb.y + 14 + lines.length * gLH + 1;
      textRects.push({
        kind: "container-label",
        owner: m.id,
        rect: textRectAt(m.sublabel, [mb.x + 8, subY], TEXT_METRICS.sub.font, "start"),
      });
    }
  }
  const padRect = (r, p) => ({ x: r.x - p, y: r.y - p, x2: r.x2 + p, y2: r.y2 + p });
  const CLEAR_PAD = 1.5;
  for (const tr of textRects) {
    const rb = padRect(tr.rect, CLEAR_PAD);
    for (const { conn, path } of connPaths) {
      if (tr.owner === conn) continue;
      for (let i = 0; i < path.samples.length - 1; i++) {
        if (segmentIntersectsRect(path.samples[i], path.samples[i + 1], rb, 0.25)) {
          const subj = tr.kind === "tensor" ? `${tr.owner}.tensor_shape`
            : tr.kind === "container-label" ? `${tr.owner} label`
            : `${tr.owner.from}->${tr.owner.to} label`;
          record("label-clearance", subj,
            `route ${conn.from}->${conn.to} crosses the text box (segment (${path.samples[i][0].toFixed(0)},${path.samples[i][1].toFixed(0)})→(${path.samples[i+1][0].toFixed(0)},${path.samples[i+1][1].toFixed(0)}))`,
            ["move label / tensor_pos", "adjust route", "add via"]);
          break;
        }
      }
    }
    // text on top of an opaque module is unreadable: conn labels and tensor
    // annotations must not sit inside any non-container module
    if (tr.kind !== "container-label") {
      for (const other of modules) {
        if (Array.isArray(other.nested) && other.nested.length > 0) continue;
        const ob = modBbox.get(other.id);
        if (tr.kind === "tensor" && tr.owner === other.id) continue;
        if (tr.kind !== "tensor" && (other.id === tr.owner.from || other.id === tr.owner.to)) continue;
        if (bboxesOverlap(padRect(tr.rect, 0.5), ob, 0)) {
          record("label-clearance",
            tr.kind === "tensor" ? `${tr.owner}.tensor_shape` : `${tr.owner.from}->${tr.owner.to} label`,
            `text box sits on top of module ${other.id}`,
            ["move label / tensor_pos", "enlarge the gap around the module"]);
          break;
        }
      }
    }
  }

  // 6. stage contiguity (every group wraps a contiguous rectangular region)
  for (const g of spec.groups || []) {
    if (g.kind !== "stage" && g.kind !== "block" && g.kind !== "ablation" && g.kind !== "branch") continue;
    const boxes = g.wraps.map((id) => modBbox.get(id)).filter(Boolean);
    if (!boxes.length) continue;
    const union = rectFromPoints(boxes.flatMap((b) => [[b.x, b.y], [b.x2, b.y2]]));
    const pad = g.pad ?? 14;
    const stageBbox = { x: union.x - pad, y: union.y - pad, x2: union.x2 + pad, y2: union.y2 + pad, w: union.w + 2 * pad, h: union.h + 2 * pad };
    // any module INSIDE the stage's bbox but NOT listed in wraps → non-contiguous
    // (nested children are exempt: they belong to their parent, which carries them)
    for (const m of modules) {
      if (g.wraps.includes(m.id)) continue;
      if (nestedChildIds.has(m.id)) continue;
      const mb = modBbox.get(m.id);
      if (bboxesOverlap(stageBbox, mb, 0)) {
        record("stage-contiguity", `stage "${g.label}"`,
          `module ${m.id} lies inside stage bbox but is not in wraps[]`,
          ["add module to wraps", "move module out of stage", "shrink stage pad"]);
        break;
      }
    }
  }

  // 7. skip wraps block (a backward-skip originating before a repeated block must terminate after it)
  for (const c of spec.connections || []) {
    if (c.variant !== "backward-skip") continue;
    // find the nearest repeated block between from and to on the main path
    const fromB = modBbox.get(c.from);
    const toB = modBbox.get(c.to);
    if (!fromB || !toB) continue;
    for (const m of modules) {
      if (m.variant !== "repeated") continue;
      const mb = modBbox.get(m.id);
      // is the repeated block spatially between from and to?
      const between =
        (fromB.cy < mb.y && toB.cy > mb.y2) || (fromB.cy > mb.y2 && toB.cy < mb.y);
      if (!between) continue;
      // is either endpoint an inner module of the repeated block (nested)?
      if (m.nested && (m.nested.includes(c.from) || m.nested.includes(c.to))) {
        record("skip-wraps-block", `${c.from}->${c.to}`,
          `skip touches inner module of repeated block ${m.id} instead of wrapping it`,
          ["connect skip to before/after the repeated block"]);
        break;
      }
    }
  }

  // 8. repeat sigil legible (×N must not overlap module label or any connection)
  for (const m of modules) {
    if (m.variant !== "repeated") continue;
    if (!Number.isInteger(m.repeat) || m.repeat < 2) {
      record("repeat-sigil-legible", m.id, `repeat=${m.repeat} (must be ≥2)`, ["set repeat ≥ 2"]);
      continue;
    }
    // sigil sits in upper-right corner inside the module
    const mb = modBbox.get(m.id);
    const sigil = bboxOfPointAt([mb.x2 - 18, mb.y + 4], 14, 10);
    // check the sigil doesn't overlap any connection
    for (const { conn, path } of connPaths) {
      if (conn.from === m.id || conn.to === m.id) continue;
      for (let i = 0; i < path.samples.length - 1; i++) {
        if (segmentIntersectsRect(path.samples[i], path.samples[i + 1], sigil, 0.5)) {
          record("repeat-sigil-legible", m.id,
            `×N sigil at (${mb.x2 - 18},${mb.y + 4}) crossed by ${conn.from}->${conn.to}`,
            ["move connection", "enlarge module"]);
          break;
        }
      }
    }
  }

  // 9. no viewBox overflow (every module/group/endpoint inside viewBox with ≥4px margin)
  if (spec.meta?.viewBox) {
    const [vw, vh] = spec.meta.viewBox;
    const vb = { x: 4, y: 4, x2: vw - 4, y2: vh - 4, w: vw, h: vh };
    for (const m of modules) {
      const mb = modBbox.get(m.id);
      if (mb.x < 4 || mb.y < 4 || mb.x2 > vw - 4 || mb.y2 > vh - 4) {
        record("no-viewbox-overflow", m.id,
          `module bbox (${mb.x},${mb.y})-(${mb.x2},${mb.y2}) outside viewBox (${vw}×${vh}) margin`,
          ["shrink viewBox", "move module inside", "enlarge viewBox"]);
      }
    }
  }

  // 10. text fits its module — wrapped label/sublabel height stays inside the
  // shape; tensor annotations are not covered by another module and stay in-view.
  const isContainerMod = (m) => Array.isArray(m.nested) && m.nested.length > 0;
  for (const m of modules) {
    const mb = modBbox.get(m.id);
    if (isContainerMod(m)) {
      const gLH = TEXT_METRICS.groupLabel.lineHeight;
      const gFont = TEXT_METRICS.groupLabel.font;
      const labelW = m.variant === "repeated" ? mb.w - 44 : mb.w - 16;
      const lines = wrapText(m.label || "", labelW, gFont);
      const need = 14 + lines.length * gLH + (m.sublabel ? TEXT_METRICS.sub.lineHeight + 1 : 0);
      if (need > mb.h) {
        record("text-fits-module", m.id,
          `container label needs ~${need.toFixed(0)}px height but the frame is ${mb.h}px`,
          ["enlarge frame", "shorten label"]);
      }
      continue;
    }
    const shape = m.shape || SHAPE_DEFAULTS[m.type] || "rect";
    // Mirror the renderer: a circle's rendered diameter is min(w,h); a diamond's
    // inscribed text width is even narrower. Rect-like shapes use w - 10.
    const minDim = Math.min(mb.w, mb.h);
    const usableW = shape === "circle" ? minDim * 0.68
      : shape === "diamond" ? minDim * 0.55
      : mb.w - 10;
    const { font: lf, lineHeight: llh } = TEXT_METRICS.label;
    const { lineHeight: slh } = TEXT_METRICS.sub;
    const labelLines = wrapText(m.label || "", usableW, lf);
    const subLines = m.sublabel ? wrapText(m.sublabel, usableW, TEXT_METRICS.sub.font) : [];
    const need = labelLines.length * llh + subLines.length * slh;
    // circles/diamonds: lines must also stay inside the chord band — cap the
    // total text-block height at 75% of the diameter
    const heightCap = (shape === "circle" || shape === "diamond") ? minDim * 0.75 : mb.h - 6;
    if (need > heightCap) {
      record("text-fits-module", m.id,
        `label "${m.label}" needs ${need}px of text height but the module allows ${(heightCap).toFixed(0)}px`,
        ["enlarge module", "shorten label", "move sublabel to a caption card"]);
    }
    if (m.tensor_shape) {
      const at = m.tensor_pos || [mb.x2 + 6, mb.cy + 4];
      const tr = textRectAt(m.tensor_shape, at, TEXT_METRICS.tensor.font, "start");
      for (const other of modules) {
        if (other.id === m.id) continue;
        if (isContainerMod(other)) continue; // translucent background frames don't hide text
        const ob = modBbox.get(other.id);
        if (bboxesOverlap(tr, ob, 0)) {
          record("text-fits-module", `${m.id}.tensor_shape`,
            `tensor annotation box overlaps module ${other.id}`,
            ["move tensor_pos", "enlarge the gap around the module"]);
          break;
        }
      }
      if (spec.meta?.viewBox) {
        const [vw, vh] = spec.meta.viewBox;
        if (tr.x < 0 || tr.y < 0 || tr.x2 > vw || tr.y2 > vh) {
          record("text-fits-module", `${m.id}.tensor_shape`,
            `tensor annotation box extends outside viewBox (${vw}×${vh})`,
            ["move tensor_pos", "enlarge viewBox"]);
        }
      }
    }
  }

  // 11. language rule (zh-CN hard rule) — every human-facing text must contain
  // Chinese, except professional terms, programming reserved words / identifiers,
  // math symbols, and spec-level `meta.language.allow` extras.
  const langMode = spec.meta?.language?.mode || (spec.meta?.locale === "zh-CN" ? "zh-CN" : "off");
  if (langMode === "zh-CN") {
    const allow = new Set((spec.meta?.language?.allow || []).map((w) => String(w).toLowerCase()));
    const texts = [];
    const push = (s, where) => { if (typeof s === "string" && s.trim()) texts.push({ s, where }); };
    push(spec.meta?.title, "meta.title");
    push(spec.meta?.subtitle, "meta.subtitle");
    for (const m of modules) {
      push(m.label, `${m.id}.label`);
      push(m.sublabel, `${m.id}.sublabel`);
      push(m.repeat_label, `${m.id}.repeat_label`);
    }
    for (const g of spec.groups || []) push(g.label, `group "${g.label}".label`);
    for (const c of spec.connections || []) {
      push(c.label, `${c.from}->${c.to}.label`);
      push(c.tensor_anno, `${c.from}->${c.to}.tensor_anno`);
    }
    for (const card of spec.cards || []) {
      push(card.title, `card "${card.title}".title`);
      for (const it of card.items || []) push(it, `card "${card.title}".item`);
    }
    const legendEntries = spec.meta?.legend?.entries;
    if (legendEntries) {
      for (const [k, v] of Object.entries(legendEntries)) {
        if (v && typeof v === "object" && typeof v.label === "string") push(v.label, `legend.${k}.label`);
      }
    }
    for (const { s, where } of texts) {
      const offender = findNonChineseOffender(s, allow);
      if (offender) {
        record("text-language", where,
          `"${s}" contains non-Chinese word "${offender}" that is not a whitelisted term`,
          ["translate the descriptive words to Chinese", "add the term to meta.language.allow"]);
      }
    }
  }

  const errors = items.filter((i) => i.severity === "error").length;
  const warnings = items.filter((i) => i.severity === "warning").length;
  return { total: 11, errors, warnings, items };
}

// Professional terms / reserved words allowed to appear without Chinese in a
// zh-CN figure. Descriptive everyday English (input, output, source, sequence,
// probabilities, ...) is deliberately NOT whitelisted — those must be translated.
const TERM_WHITELIST = new Set((
  "softmax gelu relu prelu sigmoid tanh elu selu swish glu layernorm batchnorm rmsnorm " +
  "token embedding embeddings attention encoder decoder transformer ffn mlp cnn rnn lstm " +
  "gru bilstm bert gpt vit detr resnet vgg mobilenet efficientnet unet gan vae clip t5 " +
  "llama qwen deepseek adamw adam sgd momentum cosine annealing warmup epoch epochs " +
  "diffusion clip unet clip vit api sdk gpu cpu tpu cuda webhook http https json yaml csv " +
  "parquet onnx tensorrt openvino vocab concat pooling pool upscale downsample logits " +
  "positional encoding self scaled dot product multi head feed forward cross shortcut " +
  "skip residual norm rope alibi sinusoidal kv cache rotary quantize prune distill " +
  "train val test eval acc f1 map ap iou nms auc roc precision recall baseline ablation " +
  "metric loss argmax topk topp beam greedy inference deploy serve prompt rag id ids url uri"
).split(/\s+/));

// Returns the first offending English word, or null if the string is compliant:
// contains CJK, or every alphabetic token is whitelisted / an identifier
// (contains "_" or a digit) / an acronym of ≤3 letters.
function findNonChineseOffender(s, allow) {
  const str = String(s);
  if (/[\u2e80-\u9fff\uF900-\uFAFF]/.test(str)) return null; // has Chinese → mixed text is fine
  const words = str.match(/[A-Za-z][A-Za-z0-9_]*/g) || [];
  for (const w of words) {
    const lw = w.toLowerCase();
    if (allow.has(lw) || TERM_WHITELIST.has(lw)) continue;
    if (w.includes("_") || /\d/.test(w)) continue; // identifier-like: d_model, resnet50
    if (w.length <= 3) continue; // acronym: FFN, mAP, QK, ViT(broken by case? no—see below)
    return w;
  }
  return null;
}

function pathMidpoint(samples) {
  if (!samples || !samples.length) return null;
  return samples[Math.floor(samples.length / 2)];
}

function bboxOfPointAt(at, w, h) {
  return { x: at[0], y: at[1], w, h, x2: at[0] + w, y2: at[1] + h, cx: at[0] + w / 2, cy: at[1] + h / 2 };
}

// Build the on-canvas rect a text occupies, given its anchor point.
// `at[1]` is the SVG text baseline (matches how the renderer emits <text y=...>).
// Mirrors the renderer's CSS font sizes — see shared/shapes.mjs TEXT_METRICS.
function textRectAt(text, at, font, anchor) {
  const w = estTextWidth(text, font);
  const h = font * 1.25;
  const x = anchor === "middle" ? at[0] - w / 2 : anchor === "end" ? at[0] - w : at[0];
  const y = at[1] - font * 0.85;
  return { x, y, w, h, x2: x + w, y2: y + h };
}
