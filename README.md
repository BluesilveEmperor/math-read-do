# Math-Read-Do：数学文献阅读与实验复现工作流

## 概述

**Math-Read-Do** 是一个面向数学文献的标准化"阅读→复现→验证"工作流（Skill），专为 AI Agent 设计。输入一篇数学论文 PDF，即可自动完成从文献理解到结果验证的全流程。

核心价值在于将数学论文的**阅读理解**（Read）与**实验复现**（Do）有机结合，避免只读不练或盲目复现。

## 8 阶段全链路

| 阶段 | 名称 | 核心产出 |
|------|------|----------|
| Phase 0 | 基础设施检测 | `infra_manifest.json` |
| Phase 0.5 | 版本管理 | `version_spec.json` |
| Phase 1 | 论文解析 & 视角审阅 | `reproducibility_assessment.json` |
| Phase 2 | 环境重建 | `conda-lock.yml` |
| Phase 3 | 基线验证 | `baseline_metrics.json` |
| Phase 4 | 增量实现（按需） | `delta_report.json` |
| Phase 5 | 统计判决 & 图表导出 | `判决结果.json` |
| Phase 6 | 双语报告生成 | `复现报告.md / -CN.md` |
| Phase 7 | 最终整理与完整性确认 | `实验复刻结果汇总/` |

## 视角审阅

按用户指定视角输出审阅报告，用户未指定时主动询问：

- **研究生视角** — 深度理解论文方法、公式、实验设计
- **导师视角** — 可复现性评级与教学建议
- **审稿人视角** — 批判性审查，发现论文弱点

## 支持的领域

覆盖数学全领域：纯数学 · 应用数学 · 统计学 · 运筹学 · 计算数学 · AI4Math 等

## 快速开始

```bash
# 1. 配置 MinerU Token（用于 PDF 解析）
mkdir -p ~/.mineru
echo "token: 'your-api-key'" > ~/.mineru/config.yaml
# 获取 Token：https://mineru.net/apiManage/token

# 2. 安装依赖
pip install mineru-open-sdk pyyaml

# 3. 运行复现
python scripts/math_pdf_extract.py paper.pdf --output-dir analysis/
python scripts/three_perspective_review.py analysis/parsed_text.md --output-dir analysis/
```

## 项目结构

```
reproduction/
├── SKILL.md              # 工作流定义
├── infra/                # 基础设施配置
├── provisioning/         # 环境配置脚本
├── env/                  # 环境锁定文件
├── analysis/             # 论文分析与三方审阅
├── code/                 # 复现代码
├── logs/                 # 运行日志
├── results/              # 实验结果与图表
├── reports/              # 双语报告
├── implementation/       # 增量实现记录
└── dist/                 # 发布制品
```

## 输出规范

- 所有报告**中英双语**（`.md` + `.zh.md`）
- 图表附带独立可运行生成代码（`results/figures/code/plot_*.py`）
- 判决结果使用五态分类：OK / approx / FAIL / WARN / FAIL
- 统计验证使用 95% 置信区间，至少 N=5 随机种子

## 依赖

| 包 | 用途 |
|---|------|
| mineru-open-sdk | PDF → Markdown（含公式、表格、图表） |
| pyyaml | MinerU 配置解析 |

## 子技能 / Sub-Skills

本分支集成四个 nature-* 子 Skill，可独立调用也可在主流程里协同：

| 子技能 | 角色 | 与谁互补 |
|--------|------|---------|
| `nature-reader/` | 科研论文智能阅读、结构化提取 (PDF/HTML/DOI/arXiv) | — |
| `nature-figure/` | 科研数据可视化（matplotlib/seaborn，8 步工作流 + 视觉自检闭环） | 跟 nature-framework 互补 |
| `nature-paper2ppt/` | 论文→中文 PPTX（6 类叙事弧 + 自审校） | — |
| `nature-framework/` | 科研架构图渲染器（6 类图：model/framework/route/system/structure/experiment；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体） | 跟 nature-figure 互补——本子技能专做架构/框架/流程图 |

`nature-framework` 需要 Node.js ≥ 18，零外部依赖；Python 侧通过 `scripts/nature_architecture_bridge.py` 调用。

## 许可

MIT
