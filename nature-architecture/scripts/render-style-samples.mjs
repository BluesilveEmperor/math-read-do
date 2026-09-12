#!/usr/bin/env node
// nature-architecture / scripts / render-style-samples.mjs
// Render one example spec in every visual preset for side-by-side comparison.
// Usage: node scripts/render-style-samples.mjs <example.json> [out-dir]

import { readFileSync, mkdirSync, writeFileSync, renameSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const skillRoot = path.resolve(here, "..");

const [, , jsonPath, outDirArg] = process.argv;
if (!jsonPath) {
  console.error("usage: node scripts/render-style-samples.mjs <example.json> [out-dir] [--motion off|hover|flow|tour]");
  process.exit(2);
}
const motionIdx = process.argv.indexOf("--motion");
const motion = motionIdx >= 0 ? process.argv[motionIdx + 1] : null;
const outDir = path.resolve(outDirArg || path.join(skillRoot, "..", "demo-out", "styles"));
mkdirSync(outDir, { recursive: true });

const mod = await import(pathToFileURL(path.join(skillRoot, "renderers/model/render-model.mjs")).href);
const PRESETS = ["paper", "paper-dark", "blueprint-print", "brutalism", "playful", "neumorphism", "memphis", "glass", "bauhaus", "apple"];
const PRESET_NAMES = {
  paper: "素白",
  "paper-dark": "深色",
  "blueprint-print": "制图线稿",
  brutalism: "新粗野",
  playful: "趣味插画",
  neumorphism: "新拟态",
  memphis: "孟菲斯",
  glass: "玻璃拟态",
  bauhaus: "包豪斯",
  apple: "苹果风",
};
const PRESET_NOTES = {
  paper: "默认 — 印刷优先，白底",
  "paper-dark": "深色 — 幻灯片 / 博客夜间模式",
  "blueprint-print": "纯线稿 — 供 EPS 导出",
  brutalism: "新粗野主义（Gumroad 正典）— 粗黑描边、每块硬投影、超大标题，钴蓝/信号黄/正红/紫/绿扁平撞色，钴蓝模块白字",
  playful: "趣味插画 — 暖米色底、软圆角、珊瑚/薄荷",
  neumorphism: "新拟态 — 同色凸起表面，双向柔影，无描边",
  memphis: "孟菲斯 — 80 年代撞色，2px 黑描边",
  glass: "玻璃拟态 — 紫罗兰渐变底，半透明白填充，磨砂卡片",
  bauhaus: "包豪斯 — 形式即功能：红/蓝/黄只标结构角色，直角，蓝底白字",
  apple: "苹果设计 — 磨砂材质，柔和景深，单一系统蓝强调，连续圆角",
};

const raw = readFileSync(path.resolve(jsonPath), "utf8");
const stem = path.basename(jsonPath, ".json");
const written = [];

for (const preset of PRESETS) {
  const spec = JSON.parse(raw);
  spec.meta = spec.meta || {};
  spec.meta.quality_profile = "showcase";
  spec.meta.visual_preset = preset;
  const rendered = mod.renderModel(spec, { quality: "showcase", ...(motion ? { motion } : {}) });
  const file = `${stem}.${preset}.html`;
  const out = path.join(outDir, file);
  const tmp = `${out}.${process.pid}.tmp`;
  writeFileSync(tmp, Buffer.from(rendered.html, "utf8"));
  renameSync(tmp, out);
  written.push({ preset, file, bytes: rendered.bytes });
  console.log(`${preset}: ${out} (${rendered.bytes} bytes)`);
}

const indexHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>nature-architecture 风格样张 — ${stem}</title>
<style>
  body { margin: 0; padding: 24px; font-family: "HarmonyOS Sans", "PingFang SC", "Microsoft YaHei", sans-serif; background: #f2f2f2; color: #1a1a1a; }
  h1 { font-size: 18px; margin: 0 0 4px; }
  p.note { font-size: 12px; color: #666; margin: 0 0 20px; }
  section { margin-bottom: 28px; }
  h2 { font-size: 14px; margin: 0 0 2px; }
  h2 code { font-size: 11px; color: #999; font-weight: 400; font-family: Consolas, monospace; margin-left: 4px; }
  .note { font-size: 12px; color: #666; margin: 0 0 8px; }
  iframe { width: 100%; height: 900px; border: 1px solid #ccc; border-radius: 8px; background: white; }
</style>
</head>
<body>
<h1>nature-architecture 风格样张 — ${stem}</h1>
<p class="note">同一规格、同一几何，十种视觉预设。表现系风格需显式指定，默认始终为 paper。</p>
${written.map((w) => `<section><h2>${PRESET_NAMES[w.preset] || w.preset} <code>${w.preset}</code></h2><p class="note">${PRESET_NOTES[w.preset] || ""} · ${w.bytes} 字节</p><iframe src="${w.file}" loading="lazy"></iframe></section>`).join("\n")}
</body>
</html>`;

const indexPath = path.join(outDir, "index.html");
writeFileSync(indexPath, indexHtml, "utf8");
console.log(`index: ${indexPath}`);
