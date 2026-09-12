# NOTICE — 第三方代码归属

本目录（`scripts/figuregen/engine/`）中的渲染内核**源自 [paperfig](https://github.com/BluesilveEmperor/paperfig)
（MIT License）**，按 math-read-do《论文插图功能方案 v2》（`docs/figures-feature-plan.md` §3、§9）
整体内化，用于「论文插图（六类图）」功能的实现。

## 内嵌基线

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/BluesilveEmperor/paperfig |
| 内嵌基线 commit | `3d092689e12f5e630ada0d31550a53436875b6b7` |
| 内嵌时间 | 2026-09-12 |
| 运行时依赖 | Node ≥ 18（内部依赖，用户无需安装 paperfig 本体） |
| 内嵌后分叉 | 接受分叉：`bin/paperfig.mjs` 的 `doctor` 检查修正为
  `common.schema.json + diagram.schema.json`（上游检查不存在的 `model.schema.json`，
  导致 `doctor` 永远 not ready），并新增字体子集资源检查。
  详见 `figures/manifest.json` 的 `engine.upstream_commit` |

## MIT License

Copyright (c) paperfig contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 字体资源说明

`engine/assets/fonts/HarmonyOSSans-Medium-sub.woff2`（约 496KB）是 HarmonyOS Sans Medium
的**子集**，随渲染结果以 base64 内嵌进交付 HTML，使每张图自包含、可离线、可打印、可归档。
**全量字体（8.2MB ttf）不进仓库**（见 `.gitignore`）。字体仅作为图内文字渲染使用，
不构成对 HarmonyOS 商标的任何权利主张。
