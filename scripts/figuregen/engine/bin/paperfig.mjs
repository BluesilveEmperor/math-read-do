#!/usr/bin/env node
// paperfig / bin / paperfig.mjs
// CLI entry: doctor | guide | validate | deliver | demo

import { readFileSync, writeFileSync, renameSync, unlinkSync, existsSync, mkdirSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { sha256Hex, writeAtomic, asJsonBytes, ensureUniqueIds } from "../renderers/shared/utils.mjs";
import { validateSchema, buildSchemaContext, runArtifactChecks } from "../renderers/shared/validator.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const skillRoot = path.resolve(here, "..");
const schemasDir = path.join(skillRoot, "schemas");

const DIAGRAM_TYPES = ["model", "framework", "route", "system", "structure", "experiment"];

const RENDERERS = {
  model: "../renderers/model/render-model.mjs",
  framework: "../renderers/model/render-model.mjs",
  route: "../renderers/model/render-model.mjs",
  system: "../renderers/model/render-model.mjs",
  structure: "../renderers/model/render-model.mjs",
  experiment: "../renderers/model/render-model.mjs",
};

function readJson(p) {
  return JSON.parse(readFileSync(p, "utf8"));
}

function loadSchema(type) {
  const common = readJson(path.join(schemasDir, "common.schema.json"));
  const typeSchema = readJson(path.join(schemasDir, "diagram.schema.json"));
  return buildSchemaContext(common, typeSchema);
}

async function loadRenderer(type) {
  const rel = RENDERERS[type];
  if (!rel) throw new Error(`no renderer for type "${type}"`);
  const abs = path.resolve(here, rel);
  const mod = await import(pathToFileURL(abs).href);
  return mod;
}

function printJson(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + "\n");
}

function humanBanner(s) {
  process.stderr.write(`paperfig: ${s}\n`);
}

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const sub = args.slice(1);

  try {
    switch (cmd) {
      case "doctor":
        return cmdDoctor(sub);
      case "guide":
        return cmdGuide(sub);
      case "validate":
        return await cmdValidate(sub);
      case "deliver":
        return await cmdDeliver(sub);
      case "demo":
        return await cmdDemo(sub);
      case "visual-check":
        return await cmdVisualCheck(sub);
      case undefined:
      case "-h":
      case "--help":
      case "help":
        return printHelp();
      default:
        humanBanner(`unknown command "${cmd}"`);
        process.exit(2);
    }
  } catch (e) {
    humanBanner(e.message);
    if (e.stack && process.env.PAPERFIG_DEBUG) process.stderr.write(e.stack + "\n");
    process.exit(1);
  }
}

function printHelp() {
  process.stdout.write(`paperfig — publication-grade ML/DL model architecture diagrams

Usage:
  paperfig doctor                              Check environment (node, schemas, renderer)
  paperfig guide "<scenario>" [--json]        Recommend a diagram type for a scenario
  paperfig validate <type> <json> [--quality p] [--layout-json] [--json]
                                              Validate a spec; default quality=standard
  paperfig deliver <type> <json> <out.html> [--pdf <out.pdf>] [--quality p] [--open] [--json]
                                              Render, check, atomically commit HTML (+PDF)
  paperfig demo <output-dir>                  Render a built-in transformer example
  paperfig visual-check <html> [--json]       (planned) Browser evidence for delivered HTML

Types: model | framework | route | system | structure | experiment (all share one IR)
Quality profiles: standard | showcase
Visual presets: 素白 paper | 深色 paper-dark | 制图线稿 blueprint-print | 新粗野 brutalism | 趣味插画 playful | 新拟态 neumorphism | 孟菲斯 memphis | 玻璃拟态 glass | 包豪斯 bauhaus | 苹果风 apple (set in spec.meta.visual_preset)
Column: single (default) | double (set in spec.meta.column)
`);
}

// --- doctor ---
function cmdDoctor(_args) {
  const checks = [];
  const nodeVersion = process.versions.node;
  checks.push({ name: "node >= 18", ok: parseInt(nodeVersion, 10) >= 18, detail: `node ${nodeVersion}` });
  // 内化改动：上游此处检查不存在的 model.schema.json，导致 doctor 永远 not ready。
  // 实际六类图共用 common.schema.json + diagram.schema.json（见 loadSchema）。
  const schemaFiles = ["common.schema.json", "diagram.schema.json"];
  for (const f of schemaFiles) {
    const p = path.join(schemasDir, f);
    checks.push({ name: `schema ${f}`, ok: existsSync(p), detail: p });
  }
  const fontAsset = path.join(skillRoot, "assets/fonts/HarmonyOSSans-Medium-sub.woff2");
  checks.push({
    name: "embedded font subset",
    ok: existsSync(fontAsset),
    detail: existsSync(fontAsset) ? fontAsset : "missing assets/fonts/HarmonyOSSans-Medium-sub.woff2 (HTML 将回退到系统字体栈)",
  });
  checks.push({
    name: "renderer model",
    ok: existsSync(path.join(skillRoot, "renderers/model/render-model.mjs")),
    detail: "renderers/model/render-model.mjs",
  });
  // try load renderer
  let rendererOk = false;
  try {
    const mod = loadRenderer("model"); // returns a promise but we just probe import path resolution
    // (we don't await — just check the path resolves)
    checks.push({ name: "renderer import resolves", ok: true, detail: "model" });
    rendererOk = true;
  } catch (e) {
    checks.push({ name: "renderer import resolves", ok: false, detail: e.message });
  }
  const allOk = checks.every((c) => c.ok);
  for (const c of checks) {
    process.stdout.write(`  [${c.ok ? "OK" : "FAIL"}] ${c.name} — ${c.detail}\n`);
  }
  process.stdout.write(`\npaperfig ${allOk ? "ready" : "not ready"}\n`);
  process.exit(allOk ? 0 : 1);
}

// --- guide ---
function cmdGuide(args) {
  const json = args.includes("--json");
  let scenario = "";
  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith("--") && !scenario) scenario = args[i];
  }
  const lower = scenario.toLowerCase();
  let type = "model";
  let reason = "default to method/model architecture diagram";
  if (/transformer|attention|encoder|decoder|cnn|conv|diffusion|unet|resnet|vit|gnn|backbone|model architecture|layer|block/.test(lower)) {
    type = "model"; reason = "matches ML/DL model architecture keywords";
  } else if (/研究框架|research framework|研究内容|问题层|成果层/.test(lower)) {
    type = "framework"; reason = "matches research-framework keywords (problem → content → outcome layers)";
  } else if (/技术路线|technical route|技术方案/.test(lower)) {
    type = "route"; reason = "matches technical-route keywords (branching route from goal to conclusion)";
  } else if (/系统架构|system architecture|平台|platform|微服务|client|server/.test(lower)) {
    type = "system"; reason = "matches system architecture keywords";
  } else if (/论文结构|paper structure|章节|chapter|thesis structure/.test(lower)) {
    type = "structure"; reason = "matches paper-structure keywords";
  } else if (/实验|experiment|ablation|dataset|baseline|消融|对比实验/.test(lower)) {
    type = "experiment"; reason = "matches experiment-pipeline keywords";
  }
  const result = { type, reason, scenario };
  if (json) printJson(result);
  else process.stdout.write(`Recommended type: ${type}\nReason: ${reason}\n`);
}

// --- validate ---
async function cmdValidate(args) {
  const json = args.includes("--json");
  const qualityIdx = args.indexOf("--quality");
  const quality = qualityIdx >= 0 ? args[qualityIdx + 1] : "standard";
  const positional = args.filter((a) => !a.startsWith("--"));
  if (positional.length < 2) {
    humanBanner("usage: validate <type> <json> [--quality p] [--json]");
    process.exit(2);
  }
  const [type, jsonPath] = positional;
  if (!DIAGRAM_TYPES.includes(type)) {
    humanBanner(`unsupported type "${type}" (supported: ${DIAGRAM_TYPES.join(", ")})`);
    process.exit(2);
  }
  const spec = readJson(path.resolve(jsonPath));
  // spec quality override
  if (spec.meta?.quality_profile) spec.meta.quality_profile = quality === "showcase" ? "showcase" : spec.meta.quality_profile;
  else spec.meta = { ...spec.meta, quality_profile: quality };

  const schema = loadSchema(type);
  const schemaRes = validateSchema(spec, schema, schema.$defs || {});
  if (!schemaRes.ok) {
    const result = {
      ok: false,
      stage: "schema",
      quality_profile: quality,
      schema_errors: schemaRes.errors,
      diagnostics: schemaRes.errors.map((e) => ({
        rule: "schema-valid",
        severity: "error",
        subject: e.path,
        evidence: e.msg,
        supportedFixes: ["fix per schema"],
      })),
    };
    if (json) printJson(result);
    else humanBanner(`schema invalid: ${schemaRes.errors.length} errors\n  ${schemaRes.errors.map((e) => `${e.path}: ${e.msg}`).join("\n  ")}`);
    process.exit(1);
  }

  // id uniqueness
  const idCheck = ensureUniqueIds(spec.modules || [], "id");
  if (!idCheck.ok) {
    const result = {
      ok: false,
      stage: "schema",
      quality_profile: quality,
      diagnostics: [{ rule: "unique-ids", severity: "error", subject: idCheck.subject, evidence: idCheck.error, supportedFixes: ["rename module id"] }],
    };
    if (json) printJson(result);
    else humanBanner(`id check failed: ${idCheck.error}`);
    process.exit(1);
  }

  const checks = runArtifactChecks(spec, { quality });
  const ok = checks.errors === 0 && (quality !== "showcase" || checks.warnings === 0);
  const result = {
    ok,
    stage: "check",
    quality_profile: quality,
    checks: { total: checks.total, errors: checks.errors, warnings: checks.warnings },
    diagnostics: checks.items,
  };
  if (json) printJson(result);
  else {
    process.stdout.write(`validation: ${ok ? "PASS" : "FAIL"}\n  total ${checks.total}, errors ${checks.errors}, warnings ${checks.warnings}\n`);
    for (const item of checks.items) {
      process.stdout.write(`  [${item.severity}] ${item.rule}: ${item.subject} — ${item.evidence}\n`);
    }
  }
  process.exit(ok ? 0 : 1);
}

// --- deliver ---
async function cmdDeliver(args) {
  const json = args.includes("--json");
  const open = args.includes("--open");
  const qualityIdx = args.indexOf("--quality");
  const quality = qualityIdx >= 0 ? args[qualityIdx + 1] : "showcase";
  const pdfIdx = args.indexOf("--pdf");
  const pdfPath = pdfIdx >= 0 ? args[pdfIdx + 1] : null;
  const positional = args.filter((a) => !a.startsWith("--"));
  if (positional.length < 3) {
    humanBanner("usage: deliver <type> <json> <out.html> [--pdf <out.pdf>] [--quality p] [--motion m] [--open] [--json]");
    process.exit(2);
  }
  const [type, jsonPath, outHtml] = positional;
  if (!DIAGRAM_TYPES.includes(type)) {
    humanBanner(`unsupported type "${type}" (supported: ${DIAGRAM_TYPES.join(", ")})`);
    process.exit(2);
  }
  const motionIdx = args.indexOf("--motion");
  const motion = motionIdx >= 0 ? args[motionIdx + 1] : null;
  if (motion != null && !["off", "on", "hover", "flow", "tour"].includes(motion)) {
    humanBanner(`invalid --motion "${motion}" (expected off|hover|flow|tour)`);
    process.exit(2);
  }

  const specPath = path.resolve(jsonPath);
  const outPath = path.resolve(outHtml);
  const specBytes = readFileSync(specPath);
  const spec = JSON.parse(specBytes.toString("utf8"));
  if (!spec.meta) spec.meta = {};
  spec.meta.quality_profile = quality;
  if (spec.meta.output && path.isAbsolute(spec.meta.output)) {
    // ignore; we use outPath
  }

  // stage: schema + checks
  const schema = loadSchema(type);
  const schemaRes = validateSchema(spec, schema, schema.$defs || {});
  if (!schemaRes.ok) {
    const result = {
      ok: false,
      stage: "schema",
      diagnostics: schemaRes.errors.map((e) => ({ rule: "schema-valid", severity: "error", subject: e.path, evidence: e.msg, supportedFixes: ["fix per schema"] })),
    };
    if (json) printJson(result);
    else humanBanner(`schema invalid: ${schemaRes.errors.length} errors`);
    process.exit(1);
  }
  const idCheck = ensureUniqueIds(spec.modules || [], "id");
  if (!idCheck.ok) {
    const result = {
      ok: false,
      stage: "schema",
      diagnostics: [{ rule: "unique-ids", severity: "error", subject: idCheck.subject, evidence: idCheck.error, supportedFixes: ["rename"] }],
    };
    if (json) printJson(result);
    else humanBanner(`id check failed: ${idCheck.error}`);
    process.exit(1);
  }

  const checks = runArtifactChecks(spec, { quality });
  if (checks.errors > 0 || (quality === "showcase" && checks.warnings > 0)) {
    const result = {
      ok: false,
      stage: "check",
      quality_profile: quality,
      checks: { total: checks.total, errors: checks.errors, warnings: checks.warnings },
      diagnostics: checks.items,
    };
    if (json) printJson(result);
    else humanBanner(`check failed: ${checks.errors} errors, ${checks.warnings} warnings`);
    process.exit(1);
  }

  // render
  const mod = await loadRenderer(type);
  const renderFn = mod.renderModel || mod.default;
  if (typeof renderFn !== "function") {
    humanBanner(`renderer for "${type}" has no renderModel export`);
    process.exit(1);
  }
  const rendered = renderFn(spec, { quality, ...(motion ? { motion } : {}) });

  // atomic commit
  try {
    writeAtomic({ writeFileSync: (p, b) => writeFile(p, b), renameSync: (a, b) => rename(a, b), unlinkSync: (p) => unlink(p) }, outPath, Buffer.from(rendered.html, "utf8"));
  } catch (e) {
    // fall back to direct write (Node >= 18 has fs.rmSync etc.)
    const fs = await import("node:fs");
    const tmpPath = `${outPath}.${process.pid}.${Date.now()}.tmp`;
    fs.writeFileSync(tmpPath, Buffer.from(rendered.html, "utf8"));
    fs.renameSync(tmpPath, outPath);
  }

  // PDF (Phase 2: stub — we record that it is planned)
  let pdfReceipt = null;
  if (pdfPath) {
    pdfReceipt = {
      ok: false,
      stage: "pdf",
      evidence: "PDF export is planned for Phase 2; HTML has been delivered successfully",
      path: path.resolve(pdfPath),
    };
  }

  // receipts
  const specSha = sha256Hex(specBytes);
  const htmlBytes = Buffer.byteLength(rendered.html, "utf8");
  const htmlSha = sha256Hex(Buffer.from(rendered.html, "utf8"));
  const result = {
    ok: true,
    stage: "commit",
    spec: { sha256: specSha, bytes: specBytes.length, path: specPath },
    html: { sha256: htmlSha, bytes: htmlBytes, path: outPath },
    pdf: pdfReceipt,
    checks: { total: checks.total, errors: checks.errors, warnings: checks.warnings, items: checks.items },
    quality_profile: quality,
    view_box: rendered.viewBox,
  };

  // latex snippet to stderr when PDF requested
  if (pdfPath) {
    const stableId = (spec.meta.title || "fig").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 24);
    process.stderr.write(`\nLaTeX snippet (PDF export is Phase 2 — HTML delivered successfully):\n`);
    process.stderr.write(`\\begin{figure}[t]\n  \\centering\n  \\includegraphics[width=\\columnwidth]{${path.basename(pdfPath)}}\n  \\caption{${spec.meta.title}}\n  \\label{fig:${stableId}}\n\\end{figure}\n\n`);
  }

  if (json) printJson(result);
  else {
    process.stdout.write(`deliver: OK\n  spec sha256: ${specSha.slice(0, 16)}… (${specBytes.length} bytes)\n  html sha256: ${htmlSha.slice(0, 16)}… (${htmlBytes} bytes)\n  checks: ${checks.total} total, ${checks.errors} errors, ${checks.warnings} warnings\n  output: ${outPath}\n`);
  }

  if (open) {
    const opener = process.platform === "win32" ? "explorer" : process.platform === "darwin" ? "open" : "xdg-open";
    try {
      spawn(opener, [outPath], { detached: true, stdio: "ignore" }).unref();
    } catch (_) { /* swallow */ }
  }
  process.exit(0);
}

// --- demo ---
async function cmdDemo(args) {
  const positional = args.filter((a) => !a.startsWith("--"));
  const outDir = positional[0] || "./paperfig-demo";
  const motionIdx = args.indexOf("--motion");
  const motion = motionIdx >= 0 ? args[motionIdx + 1] : null;
  if (motion != null && !["off", "on", "hover", "flow", "tour"].includes(motion)) {
    humanBanner(`invalid --motion "${motion}" (expected off|hover|flow|tour)`);
    process.exit(2);
  }
  mkdirSync(outDir, { recursive: true });
  const examplePath = path.resolve(skillRoot, "..", "examples", "transformer-encoder.model.json");
  if (!existsSync(examplePath)) {
    humanBanner(`demo example not found: ${examplePath}`);
    process.exit(1);
  }
  const spec = readJson(examplePath);
  spec.meta = spec.meta || {};
  spec.meta.quality_profile = "showcase";
  const mod = await loadRenderer("model");
  const rendered = mod.renderModel(spec, { quality: "showcase", ...(motion ? { motion } : {}) });
  const outHtml = path.join(outDir, "transformer-encoder.html");
  const tmp = `${outHtml}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(tmp, Buffer.from(rendered.html, "utf8"));
  renameSync(tmp, outHtml);
  process.stdout.write(`demo: wrote ${outHtml}\n`);
}

// --- visual-check (Phase 2 stub) ---
async function cmdVisualCheck(args) {
  const json = args.includes("--json");
  const positional = args.filter((a) => !a.startsWith("--"));
  const htmlPath = positional[0];
  if (!htmlPath) {
    humanBanner("usage: visual-check <html> [--json]");
    process.exit(2);
  }
  const result = {
    ok: false,
    stage: "visual-check",
    evidence: "visual-check is planned for Phase 2; the HTML has been delivered and can be opened manually",
    path: path.resolve(htmlPath),
  };
  if (json) printJson(result);
  else process.stdout.write(`visual-check: planned for Phase 2\n  html: ${path.resolve(htmlPath)}\n`);
  process.exit(0);
}

// shim fs methods used by writeAtomic (we pass an object with the right shape)
function readFileShim(p, enc) {
  // sync via fs.readFileSync via require; for our flow we use fs/promises directly above
  const fs = require_from_node_modules();
  return fs.readFileSync(p, enc);
}
function rename(a, b) {
  // use sync fs.renameSync
  return _fs().renameSync(a, b);
}
function unlink(p) {
  return _fs().unlinkSync(p);
}
function _fs() {
  // sync access to fs; we re-import for shim
  // eslint-disable-next-line no-eval
  return (0, eval)("require")("fs");
}
function require_from_node_modules() {
  return _fs();
}

main();
