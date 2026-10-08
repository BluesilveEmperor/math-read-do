# 集成 Nature 子技能 / Integrated Nature Skills

> 本文档从 SKILL.md 外移的低频道参考内容（子技能路由、协同、调用方式）。

## 集成 Nature 子技能 / Integrated Nature Skills

本 skill 集成了四个独立的 Nature 子技能 (`nature-reader`, `nature-figure`, `nature-paper2ppt`, `nature-archify`) 和一个共享层 (`_shared/`)，它们位于 `math-read-do/` 目录下，可作为独立 skill 被调用，也可作为 Phase 1-6 的增强工具。

### 子技能路由

| 子技能 | 目录 | 入口文件 | 主要用途 |
|--------|------|---------|---------|
| nature-reader | `nature-reader/` | `SKILL.md` + `manifest.yaml` | 科研论文智能阅读、结构化提取、6种来源格式路由 |
| nature-figure | `nature-figure/` | `SKILL.md` | 科研数据可视化顾问：8 步工作流，matplotlib+seaborn+SciencePlots+plotly，视觉自检闭环 |
| nature-paper2ppt | `nature-paper2ppt/` | `SKILL.md` + `manifest.yaml` | 论文→中文 PPTX，6类论文叙事弧，自审校循环 |
| nature-archify | `nature-archify/` | `SKILL.md` | 系统架构图渲染器：5 类图 architecture/workflow/sequence/dataflow/lifecycle，13 视觉预设，9 项 showcase 校验 |
| _shared | `_shared/` | 无入口，被子技能引用 | 术语账本、论文类型分类法、伦理规范、Nat Communs 格式 |

### 与主流程的协同

- **nature-reader** 可增强 Phase 1 (论文解析与视角审阅)，提供替代 PDF 解析策略和结构化输出格式。用户未指定审阅视角时，主动询问。
- **nature-figure** 可增强 Phase 5 (图表导出)，作为"可视化顾问"：先剖析数据→推荐图型→拦截错误→绘制→视觉自检闭环，提供出版级图表样式和质量门禁。
- **nature-archify** 参与文献阅读与实验复现全程：Phase 1（系统架构/流程预计版）、Phase 4（系统架构图主体）、Phase 6（报告插图），作为"系统架构 / 技术流程 / 调用时序 / 数据流 / 状态机渲染器"：从 JSON 规格产出 self-contained inline-SVG HTML，内嵌中文字体、几何自证，13 种视觉预设、深/浅双主题；适用于论文 float / 开题报告 / 组会汇报里的系统与流程图。Node CLI（`nature-archify/bin/archify.mjs`）零外部依赖，Python 侧通过 `scripts/nature_archify_bridge.py` 调用。论文的**方法/模型架构图**与**实验流程图**不在本模块图类型内，需要时另行接入 paperfig 类渲染器。
- **nature-paper2ppt** 在 Phase 6 之后生成汇报 PPTX，将复现结果呈现为学术演示。

### 调用方式

每个子技能有独立的 `SKILL.md` + `manifest.yaml`，通过 load_skill 加载后自动读取对应的 static/fragments/references。子技能之间的共享内容通过 `_shared/` 目录引用，无需重复加载。
