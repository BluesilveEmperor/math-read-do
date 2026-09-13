# Math-Read-Do

数学文献阅读与实验复现工作流家族 / Mathematical Literature Reproduction Pipeline Family

**Math-Read-Do** 是一个面向数学文献的标准化"阅读→复现→验证"工作流（Skill）家族，专为 AI Agent 设计。输入一篇论文，即可自动完成从文献理解到结果验证的全流程。

本仓库包含多个分支，面向不同研究方向。请选择适合的分支开始使用。

| 分支 | 方向 | Phase 1 做什么 | 核心风险 |
|------|------|---------------|---------|
| [main](https://github.com/BluesilveEmperor/math-read-do/tree/main) | 通用数学文献 | PDF 解析 (MinerU) + 三视角审阅 | 公式理解偏差 |
| [routine](https://github.com/BluesilveEmperor/math-read-do/tree/routine) | 跨语言栈例行复现 | 论文解析与三方审阅 | 环境/语言栈 |
| [obj](https://github.com/BluesilveEmperor/math-read-do/tree/obj) | 图形学 / OBJ 几何 | 算法理解（无需 PDF 解析） | 几何退化 |
| [financial](https://github.com/BluesilveEmperor/math-read-do/tree/financial) | 量化金融 + 深度学习 | **数据可得性分诊** | 数据授权 + 环境冲突 |

---

## 分支导航 / Branch Navigation

### 🔄 [routine](https://github.com/BluesilveEmperor/math-read-do/tree/routine)

**跨语言栈例行复现** / Cross-Language Stack Batch Reproduction

面向需要**例行化、跨语言环境**跑的论文复现。与 main 同构，但环境重建支持多级 fallback（Conda/Mamba → Python venv → Julia → 系统级库），覆盖 Python/Julia/R 多语言栈。

**特色功能**：
- 多级环境 fallback：Conda 冲突→mamba clean → pip 超时→分批装 → Julia → 系统库
- 确定性配置：固定 torch/np/random/tf 种子 + 浮点确定性 + `PYTHONHASHSEED`
- 依赖扫描覆盖 `requirements.txt` / `environment.yml` / `Manifest.toml` / `renv.lock`
- 与 main 共享 9 种阅读模板 + 三视角审阅

---

### 🎨 [obj](https://github.com/BluesilveEmperor/math-read-do/tree/obj)

**QEM 网格简化 / 图形学 OBJ 复现** / QEM Mesh Simplification & Graphics OBJ Reproduction

面向图形学/几何处理方向，以 QEM 边收缩简化为范本，构建面向"任意输出 .obj 文件的图形学实验"的标准化复刻框架：

- **通用 .obj 实验复刻**：适配任意输出 .obj 的算法
- **多模型交叉验证**：cube / tetrahedron / sphere / bunny / 用户输入
- **Hausdorff 距离**：简化前后模型差异量化
- **退化面 / 重复面检测**：退化面率 < 0.1%
- **.obj 产物即契约**：输入 → 算法 → 输出自证正确性

适用论文：QEM (Garland & Heckbert, SIGGRAPH 1997)、Progressive Mesh、纹理简化等

**特色功能**：
- 完整的 .obj I/O 解析器 + QEM 简化引擎 + CLI
- 子实验命名 `<模型名>_<参数标记>`（如 `bunny_50pct`）
- 每图附带 Python + LaTeX 双版本生成代码

---

### 💹 [financial](https://github.com/BluesilveEmperor/math-read-do/tree/financial)

**量化金融论文复现** / Quantitative Finance Paper Reproduction

面向「量化金融 + 深度学习」方向，基于 10 篇顶刊论文（QF / Mathematical Finance / SIAM J. Financial Math / Frontiers Math Finance, 2022–2025）的真实复现经验构建：

- **深度对冲 / 超级对冲**：Robust Deep Hedging、Network Superhedging
- **签名方法**：Sig-Wasserstein GAN、Signature-Based Models、Signature Volatility
- **估值调整与定价**：Deep xVA Solver (CVA/BCVA/FVA)、Deep Weighted Monte Carlo
- **校准与最优停止**：SPX/VIX 联合校准、Randomized NN 最优停止
- **金融时间序列生成**：Fin-GAN

内建 10 个实验档案，含真实复现数值、阻塞原因与已验证修复补丁（完全复现 5 / 部分复现 3 / 无法复现 2）。

**特色功能**：
- Phase 1 **数据可得性分诊** — open（正常复现）/ licensed（合成替代，降级 `not_testable`）/ absent（标记 `blocked`）
- **五态判决**：`pass` / `approx` / `fail` / `not_testable` / `blocked`
- **双 conda 环境隔离**：signatory 只支持 torch 1.9，与 TF 2.15 依赖互斥
- 金融指标库：年化 Sharpe（252 交易日）/ Sortino / 最大回撤 / 对冲概率 + 确定性 bootstrap 95% CI

---

### 📐 [main](https://github.com/BluesilveEmperor/math-read-do/tree/main)

**通用数学文献复现** / General Mathematical Literature Reproduction

覆盖数学全领域：纯数学、应用数学、统计学、运筹学、计算数学、AI4Math 等。

**8 阶段全链路**：

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
| Phase 7 | 最终整理 | `实验复刻结果汇总/` |

**视角审阅**：研究生 / 导师 / 审稿人 / 三方全出（未指定时**必须先询问**，禁止默认）

---

## 快速开始 / Quick Start

```bash
# 克隆特定分支
git clone -b routine https://github.com/BluesilveEmperor/math-read-do.git
git clone -b obj     https://github.com/BluesilveEmperor/math-read-do.git
git clone -b financial https://github.com/BluesilveEmperor/math-read-do.git
git clone -b main    https://github.com/BluesilveEmperor/math-read-do.git
```

每个分支都有独立的 `SKILL.md`，包含该方向的完整使用说明。

## 自更新 / Auto-Update

所有分支内置自更新机制，每次调用前自动检查远程仓库是否有更新（`scripts/auto_update.sh`），无网络时静默跳过。

## 核心原则

1. **先问后做**：用户无指令时先主动提问，确认操作后再执行
2. **双语输出**：所有报告必有 `.md`（英文）+ `-CN.md`（中文）
3. **增量验证**：每添加一个模块即验证一次
4. **可审计**：每步产生结构化产物，溯源链完整
5. **.obj 产物即契约**（obj 分支）：输入 → 算法 → 输出自证正确性

## 子技能 / Sub-Skills

每个分支都集成四个 nature-* 子 Skill，可独立调用也可在主流程里协同：

| 子技能 | 角色 | 与谁互补 |
|--------|------|---------|
| `nature-reader/` | 科研论文智能阅读、结构化提取（PDF/HTML/DOI/arXiv） | — |
| `nature-figure/` | 科研数据可视化（matplotlib/seaborn/SciencePlots/plotly，8 步工作流 + 视觉自检闭环） | 跟 nature-framework 互补 |
| `nature-paper2ppt/` | 论文→中文 PPTX（6 类叙事弧 + 自审校） | — |
| `nature-framework/` | **科研架构图渲染器**（6 类图：model/framework/route/system/structure/experiment；10 视觉预设；11 项 showcase 校验；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体） | 跟 nature-figure 互补——本子技能专做架构/框架/流程图 |

### 询问规则（第 0 步必问）

各技能执行前必须先向用户询问，禁止默认：

| 技能 | 必问项 |
|------|--------|
| 主 SKILL.md | 操作菜单选择、G01 确认、G3/G4 门禁决策 |
| nature-figure | "这份数据主要想说服读者相信什么？"（组间差异/时间趋势/变量关系） |
| nature-framework | 主题、图类型、图语言（zh-CN/en）、数据流动形式（off/hover/flow/tour）、视觉风格、输出格式 |
| nature-reader | 输出模式、**审阅视角**（研究生/导师/审稿人/三方全出，禁止默认）、额外产物 |
| nature-paper2ppt | 场合听众、时长页数、讲者备注形式 |

### nature-framework 分阶段参与

nature-framework 参与文献阅读与实验复现全程：

- **阅读/理解期**：`structure` 论文结构图、`framework` 研究框架图、`route` 技术路线图（预计版）、`model` 方法/模型架构图主体
- **判决后**：`experiment` 实验流程图最终版（统计判决前仅 `"status": "draft"` predicted flow）
- **报告期**：报告中的架构/框架/流程图由 nature-framework 产出（inline-SVG HTML + 嵌入字体 PDF）

`nature-framework` 需要 Node.js ≥ 18，零外部依赖；Python 侧通过 `scripts/nature_framework_bridge.py`（obj/financial）或 `scripts/nature_architecture_bridge.py`（main/routine）调用。详见 [nature-framework/SKILL.md](nature-framework/SKILL.md)。

## 六类图实验依赖规则

| 图类型 | 是否需要实验复现后才能画最终版 |
|---|---|
| 研究框架图 | ❌ 不需要，开题/研究设计阶段就能画 |
| 技术路线图 | ❌ 不需要，计划阶段就能画；实验后补结果即可 |
| 方法/模型架构图 | ⚠️ 主体不需要，设计确定就能画；细节最好代码跑通后确认 |
| 系统架构图 | ❌ 不需要，设计阶段就能画 |
| 论文结构图 | ❌ 不需要，写作前就能画 |
| 实验流程图 | ✅ **需要**，最终版必须基于真实实验数据 |

实验流程图依赖实验的原因：需写清初始样本量、排除数量及原因、最终纳入量、分组方式、每组人数、失访/退出/剔除情况、最终进入分析的人数、评价指标。这些数字和分支不能靠想象编。医学领域的 PRISMA、CONSORT 流程图尤其如此——计划阶段只能画"预计流程图"，最终版必须实验后画。

## 许可 / License

MIT
