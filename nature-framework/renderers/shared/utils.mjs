// nature-framework / renderers / shared / utils.mjs
// Pure utility helpers — no DOM, no fs, safe to import anywhere.

import { createHash } from "node:crypto";

export function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

export function isPlainObject(v) {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

export function clampNumber(n, min, max) {
  if (!Number.isFinite(n)) return min;
  return Math.max(min, Math.min(max, n));
}

export function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

const ID_RE = /^[a-z][a-z0-9_]*$/;
export function isValidId(s) {
  return typeof s === "string" && ID_RE.test(s);
}

// --- text metrics (shared by renderer wrapping and validator fit checks) ---

export function estTextWidth(text, fontSize) {
  let wpx = 0;
  for (const ch of String(text)) {
    const code = ch.codePointAt(0);
    // CJK / fullwidth ranges take a full em
    if ((code >= 0x2e80 && code <= 0x9fff) || (code >= 0xf900 && code <= 0xfaff) || (code >= 0xff00 && code <= 0xffef)) {
      wpx += fontSize;
    } else if (/[A-Z@#%&WM]/.test(ch)) {
      wpx += fontSize * 0.78;
    } else if (/[a-z0-9]/.test(ch)) {
      wpx += fontSize * 0.56;
    } else if (ch === " ") {
      wpx += fontSize * 0.3;
    } else {
      wpx += fontSize * 0.45;
    }
  }
  return wpx;
}

// Wrap text into lines that each fit maxWidth at the given font size.
// Word-based wrap when spaces exist, character-based fallback for CJK/long tokens.
export function wrapText(text, maxWidth, fontSize) {
  const words = String(text).split(/\s+/).filter(Boolean);
  const fits = (s) => estTextWidth(s, fontSize) <= maxWidth;
  const lines = [];
  if (words.length > 1) {
    let cur = "";
    for (const w of words) {
      const cand = cur ? cur + " " + w : w;
      if (fits(cand) || !cur) cur = cand;
      else { lines.push(cur); cur = w; }
    }
    if (cur) lines.push(cur);
    // if a single word is itself too wide, re-wrap that word per-character below
    if (lines.every(fits)) return lines;
  }
  const chars = Array.from(String(text));
  const charLines = [];
  let line = "";
  for (const ch of chars) {
    const cand = line + ch;
    if (fits(cand) || !line) line = cand;
    else { charLines.push(line); line = ch; }
  }
  if (line) charLines.push(line);
  return charLines;
}

export function ensureUniqueIds(items, key = "id") {
  const seen = new Set();
  const dups = [];
  for (const it of items) {
    const id = it?.[key];
    if (!isValidId(id)) return { ok: false, error: `invalid id: "${id}"`, subject: id };
    if (seen.has(id)) dups.push(id);
    seen.add(id);
  }
  if (dups.length) return { ok: false, error: `duplicate id: ${dups.join(", ")}`, subject: dups[0] };
  return { ok: true, ids: seen };
}

const VIEWS_RE = /^[a-z][a-z0-9-]*$/;
export function isValidViewId(s) {
  return typeof s === "string" && VIEWS_RE.test(s);
}

export function pickByMap(obj, map, fallback) {
  if (!isPlainObject(obj)) return fallback;
  for (const key of Object.keys(map)) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) return map[key];
  }
  return fallback;
}

export function deepFreeze(o) {
  if (Array.isArray(o)) return o.map(deepFreeze);
  if (isPlainObject(o)) {
    for (const k of Object.keys(o)) o[k] = deepFreeze(o[k]);
    return Object.freeze(o);
  }
  return o;
}

export function asJsonBytes(value) {
  return Buffer.from(JSON.stringify(value, null, 2), "utf8");
}

export function readJsonFile(fs, path) {
  const txt = fs.readFileSync(path, "utf8");
  return JSON.parse(txt);
}

export function writeAtomic(fs, targetPath, bytes) {
  const dir = pathDir(targetPath);
  const tmp = `${targetPath}.${process.pid}.${Date.now()}.tmp`;
  fs.writeFileSync(tmp, bytes);
  try {
    fs.renameSync(tmp, targetPath);
  } catch (e) {
    try { fs.unlinkSync(tmp); } catch (_) { /* swallow */ }
    throw e;
  }
}

// Minimal path utilities so we don't pull in node:path in the browser bundle.
export function pathDir(p) {
  const i = p.lastIndexOf("/");
  if (i < 0) return ".";
  if (i === 0) return "/";
  return p.slice(0, i);
}

export function pathBasename(p) {
  const i = p.lastIndexOf("/");
  return i < 0 ? p : p.slice(i + 1);
}

export function pathExt(p) {
  const b = pathBasename(p);
  const i = b.lastIndexOf(".");
  return i <= 0 ? "" : b.slice(i);
}

export function pathStem(p) {
  const b = pathBasename(p);
  const i = b.lastIndexOf(".");
  return i <= 0 ? b : b.slice(0, i);
}
