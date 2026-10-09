---
name: math-read-do-finance
description: >-
  量化金融论文实验复现标准化工作流 / Standardized Quantitative-Finance Paper Reproduction Pipeline

  以 10 篇顶刊量化金融论文的真实复现（Quantitative Finance / Mathematical Finance /
  SIAM J. Financial Mathematics / Frontiers of Mathematical Finance, 2022–2025）
  为设计范本，构建面向"深度学习 + 金融数值实验"的复现框架。

  集成四大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：科研数据可视化顾问（先思考后绘制，8 步工作流，视觉自检闭环）
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)
  - nature-archify/：系统架构图渲染器（5 类图 architecture/workflow/sequence/dataflow/lifecycle，13 视觉预设，9 项 showcase 校验，self-contained inline-SVG HTML）；与 nature-figure 形成互补——本子技能专做系统/流程/时序/数据流架构图，nature-figure 专做数据可视化图

  框架结构：
    Phase 0-2:  通用层 — 宿主检测、双环境构建（TF / torch+signatory）、数据可得性分诊
    Phase 3-4:  适配层 — 基线验证、按 DAG 拓扑序增量实现与修复
    Phase 5-6:  验证层 — 多种子统计验证（五态判决 + 95% bootstrap CI）、中英双语报告

  内建 10 个实验档案（fin_tool/registry.py），含真实复现数值、阻塞原因与已验证修复补丁。
  工具链：金融指标库（Sharpe/Sortino/最大回撤/对冲概率）+ 五态判决引擎 + CLI。

  Triggers / 触发词:
  量化金融复现, 金融论文复现, quantitative finance reproduction, finance paper reproduction,
  深度对冲, deep hedging, robust hedging, 稳健对冲, 超级对冲, superhedging,
  Fin-GAN, SigWGAN, Sig-Wasserstein GAN, 签名GAN, signature GAN, signature method, 签名方法,
  xVA, CVA, BCVA, FVA, 估值调整, 对手信用风险, counterparty credit risk,
  SPX VIX 联合校准, joint calibration, 波动率校准, volatility calibration,
  rough volatility, 粗糙波动率, Heston, local stochastic volatility,
  最优停止, optimal stopping, 美式期权定价, American option pricing, Bermudan,
  最小二乘蒙特卡洛, LSM, NLSM, randomized neural network, 随机神经网络,
  加权蒙特卡洛, weighted Monte Carlo, Deep WMC, 期权定价复现, option pricing reproduction,
  夏普比率, Sharpe ratio, PnL 回测, 金融时间序列生成, financial time series generation

compatibility:
  - conda 环境 A `financial`: Python 3.11.15, TensorFlow 2.15.0
  - conda 环境 B `sigtorch39`: Python 3.9.23, torch 1.9.1+cpu, signatory 1.2.6, numpy<2
  - fin_tool 本体: python >= 3.9, numpy >= 1.21（两个环境均可导入）
  - 可选: pytest（测试）, matplotlib（图表）, pandas/openpyxl（xlsx 产物）
  - nature-reader: python-pptx, Pillow (图提取), PyMuPDF (PDF渲染)
  - nature-figure: matplotlib + seaborn + SciencePlots (静态) + plotly (交互)，CJK 字体自动配置
  - nature-paper2ppt: python-pptx, PyMuPDF, Pillow, zipfile
  - nature-archify: Node.js >= 18（CLI: nature-archify/bin/archify.mjs；零外部依赖）；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体，离线可打印；Python 桥接：scripts/nature_archify_bridge.py
---

# Quantitative Finance Experiment Reproduction Framework
# 量化金融实验复现标准化框架

## 自动更新 / Auto-Update

**每次调用该 Skill 前，自动执行 `scripts/auto_update.sh`：**

1. 检测远程仓库 `https://github.com/BluesilveEmperor/math-read-do` 的 `financial` 分支
2. 未初始化 Git → `git init` + 添加 remote + fetch；已有 → fetch + `--ff-only`
3. 本地有未提交修改 → 自动 stash → 更新后 pop 恢复
4. 无网络降级：远程不可达 → 跳过更新，继续使用本地代码

> 该更新只同步框架（SKILL.md、fin_tool/、模板、脚本），不覆盖用户的 `results/`、`env/` 等产物目录。

---

## 设计理念 / Design Philosophy

与 `math-read-do`（通用数学复现）和 `math-read-do-obj`（图形学 .obj 复现）不同，
量化金融论文复现的**主要失败模式不是算法实现错误，而是数据与环境**：

| 特点 | 含义 | 框架对策 |
|------|------|---------|
| **数据常为商业授权** | CRSP/WRDS、Bloomberg、ICAP 数据不可公开获取 | Phase 1 数据分诊：先判可得性，再决定合成替代或标记 `skip` |
| **环境高度分裂** | signatory 只支持 torch 1.9，与 TF 2.15 不可共存 | 强制双 conda 环境（`financial` / `sigtorch39`），每个实验声明所属环境 |
| **结果是随机量** | GAN、蒙特卡洛的输出天然带方差 | 多种子 + bootstrap 95% CI，而非单点比对 |
| **上游代码常残缺** | 论文仓库漏提交核心模块 | 五态判决含 `skip`，允许诚实地"复现不了" |
| **内存是硬约束** | 3.7 GB RAM 下 notebook 会 kernel died | Phase 0 记录内存上限，串行化重实验 |

因此本框架的核心不是"跑通"，而是 **"分清跑不通的三种原因"**：
数据缺失（`skip`）／上游代码缺失（`skip`）／实现有偏差（`fail`）。

---

## 交互规则 / Interaction Rules

### Pre-flight：自动更新
执行任何操作前先跑 `scripts/auto_update.sh`，完成后进入用户交互。

### 用户交互规则

用户未输入具体操作指令时，**不允许默认执行任何操作**。必须主动提问，列出可执行选项，等待选择。

**标准提问模板**:
```
请选择操作类型：

=== 框架通用操作 ===
1️⃣ 查看状态 — 显示 10 个内建实验的复现状态总表
2️⃣ 实验详情 — 查看某个实验的复现数值、阻塞原因、已验证修复
3️⃣ 数据分诊 — 判定目标论文的数据可得性，给出合成替代方案
4️⃣ 指标计算 — 对 PnL/收益序列算 Sharpe/Sortino/回撤/对冲概率 + 95% CI
5️⃣ 判决比对 — 复现值 vs 论文值，输出五态判决

=== 完整复现流程 ===
6️⃣ 完整复现 — 启动完整实验复现流水线（Phase 0→6）

=== 当前内建档案 ===
  10 篇量化金融顶刊论文（2022–2025）
  完全复现 5 / 部分复现 3 / 无法复现 2
```

---

## 核心原则 / Core Principles

0. **自动更新**: 每次使用前拉取最新框架代码
1. **双语输出**: 所有报告必有中英双版本（`.md` + `-CN.md`）
2. **数据先行**: 未确认数据可得性之前不启动训练——这是本领域最大的时间陷阱
3. **环境隔离**: 每个实验显式声明 `financial` 或 `sigtorch39`，绝不混装
4. **诚实判决**: 复现不了要说清是缺数据、缺代码还是算错了，不用合成数据冒充原始结果
5. **可审计**: 每步产生结构化产物（日志 + json），溯源链完整
6. **先问后做**: 用户无指令时先主动提问

---

## 反模式 / Anti-Patterns & Blacklist

12 条量化金融复现常见反模式（合成数据对比/单次运行/环境混装/signatory 编译/numpy 版本/plt.show 挂起/SavedModel 兼容/内存并行/n_lags/种子记录/年化天数/日志落盘）及对应正确做法。

> 完整 12 条反模式表格见 [`references/anti_patterns.md`](references/anti_patterns.md)。

---

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| **Δ-1** | 自动更新 | `git log -1` | **GΔ**: 网络可达时同步最新 |
| 0 | 宿主检测 + 资源上限 | `infra/infra_manifest.json` | G0: CPU/RAM/磁盘记录在案 |
| 0.5 | 双环境构建 + 版本锁定 | `env/version_spec.json` | G1: 两环境导入测试通过 |
| 1 | **数据可得性分诊** | `analysis/data_triage.json` | G01: 每个数据源标记 open/licensed/absent |
| 2 | 论文理解 + 指标提取 | `analysis/paper_summary.json` | G02: 目标数值清单确认 |
| 3 | 基线验证 | `results/baseline_metrics.json` | G4: 基线对齐或记录灰区 |
| 4 | 增量实现 + 修复 | `implementation/delta_report.json` | G5: 每模块 delta 验证 |
| 5 | 多种子统计验证 | `results/statistical_summary.json` | G6: 五态判决 + 95% CI |
| 6 | 中英双语报告 | `实验复现结果汇总/` | G7: 各子实验目录完整 |

---

## 门禁总表 / Gate Map

> **说明**：financial 分支门禁编号已与 routine/main/obj 分支统一。原 G3→G4, G4→G5, G5→G6, G6→G7；原 G2（目标数值清单确认）重编号为 G02（financial 特有，论文理解阶段）。

| Gate | 所属阶段 | 检查项摘要 | 失败动作 |
|------|---------|-----------|---------|
| GΔ | Phase Δ-1 自动更新 | 网络可达时同步至最新 | 静默跳过，不阻塞流程 |
| G0 | Phase 0 宿主检测 | CPU/RAM/磁盘记录在案 | 返回修复 manifest/环境 |
| G1 | Phase 0.5 版本检测 | 两环境导入测试通过 | 修复版本冲突后继续 |
| G01 | Phase 1 数据分诊 | 每个数据源标记 open/licensed/absent | 用户介入决策处置方式 |
| G02 | Phase 2 论文理解 | 目标数值清单确认 | 用户介入确认目标数值 |
| G4 | Phase 3 基线验证 | 基线对齐或灰区记录完整 | 用户决策是否继续 |
| G5 | Phase 4 增量实现 | 每模块 delta 验证通过 | 排查修复后重跑 |
| G6 | Phase 5 统计判决 | 五态判决 + 95% CI 产出 | 补跑统计验证 |
| G7 | Phase 6 双语报告 | 各子实验目录完整 | 补缺文件/补译 |

---

## 阶段详述 / Phase Detail

### Phase Δ-1: 自动更新
见上文「自动更新」。失败静默跳过，不阻塞流程。

---

### Phase 0.0: 环境选择 / Environment Selection

**目的**: 检测用户是否已有 WSL 且 Linux 环境已配置好，据此选择实验复现的执行平台。

**流程**:
0.0.1 **WSL 环境检测**: 运行 `scripts/detect_wsl.sh` → 输出 `infra/wsl_detection.json`
    - 检测 `wsl` 命令是否可用
    - 若可用，检测默认 WSL 发行版中 Python3 + numpy + scipy 是否就绪
    - 输出 `recommend` 字段: `"wsl"` 或 `"native"`

0.0.2 **平台选择**:
    - `recommend == "wsl"` → 后续所有实验复现命令通过 `wsl -d <distro> --` 执行，Windows 路径用 `wslpath` 自动转换
    - `recommend == "native"` → 在用户当前所在系统直接执行（Windows/macOS/Linux 原生）
    - **不强制安装 WSL**——仅检测已有环境并选择，未配置则在当前系统运行

0.0.3 **Linux 环境配置策略**（当 recommend == "wsl" 时适用）:
    - **优先使用 UV** (`uv venv` + `uv pip install`) 进行 Python 环境配置——UV 极快且兼容 pip 生态
    - **UV 不好处理的情况** → 启用 conda 配置：
      - 需要特定 conda 频道（如 `conda-forge`）的二进制包
      - 依赖非 Python 的系统级库（如 CUDA toolkit、MKL、特定 BLAS）
      - UV 安装失败的包（如需要编译且缺少系统头文件的 C 扩展）
    - 检测顺序: `detect_wsl.sh` 先检测 `uv` → 再检测 `conda`，输出 `env_manager` 字段
    - 环境创建: `uv venv .venv && source .venv/bin/activate && uv pip install -r requirements.txt`
    - conda 兜底: `conda env create -f environment.yml`

**设计原则**: 优先使用已配置好的 Linux 环境（WSL）进行复现，以保证与论文原始实验环境的一致性；若用户未配置 WSL，则在当前系统直接运行，降低使用门槛。

**实现文件**: `scripts/detect_wsl.sh`

---

### Phase 0: 基础设施检测 / Infrastructure Detection

**输出**: `infra/infra_manifest.json`

0.1 **宿主检测**: CPU 核数、**可用内存**（本领域关键）、磁盘余量、是否有 GPU
0.2 **资源策略**: 内存 < 8 GB → 标记 `serial_only`，禁止并行重实验
0.3 记录到 manifest，后续所有阶段读取该文件决定并行度

**G0**: manifest 生成，并行度策略确定

---

### Phase 0.5: 双环境构建 / Dual Environment Setup

**输出**: `env/version_spec.json`

```json
{
  "environments": {
    "financial":  {"python": "3.11.15", "tensorflow": "2.15.0"},
    "sigtorch39": {"python": "3.9.23", "torch": "1.9.1+cpu",
                   "signatory": "1.2.6", "numpy": "<2"}
  }
}
```

0.5.1 `conda create -n financial python=3.11 && pip install tensorflow==2.15.0`
0.5.2 `conda create -n sigtorch39 python=3.9 && pip install torch==1.9.1 "numpy<2"`
0.5.3 signatory 从源码编译（需 g++；`pip install signatory` 必失败）
0.5.4 验证: `conda run -n <env> python -c "import ..."`

**G1**: 两环境导入测试均通过

---

### Phase 1: 数据可得性分诊 / Data Availability Triage

**本框架最重要的阶段。** 在这一步砍掉不可能完成的实验，避免浪费算力。

**输出**: `analysis/data_triage.json`

每个数据源归入三类之一：

| 类别 | 判定 | 处置 |
|------|------|------|
| `open` | 公开可下载（Yahoo Finance、Stanford 数据集等） | 正常复现，可与论文数值直接比对 |
| `licensed` | 商业授权（CRSP/WRDS、Bloomberg、ICAP） | 生成合成替代（GBM/Heston），**判决降级为 `skip`** |
| `absent` | 论文和仓库均未提供，也无法合成 | 标记 `skip`，不启动训练 |

**合成替代规范**：
- 必须与原数据同维度、同频率（否则出现实验 06 的 7 vs 9 维度不匹配）
- 生成脚本落盘并记录种子
- 报告中显著标注"合成数据，不构成对论文数值的验证"

**分诊脚本**（`scripts/data_triage.py`，将上述流程代码化，可执行可回归）:

```bash
# 输入论文元数据 JSON，输出 results/triage_report.json
python scripts/data_triage.py --paper paper.json
python scripts/data_triage.py --paper paper.json --output results/triage_report.json
```

`paper.json` 格式：
```json
{
  "title": "Robust Deep Hedging",
  "url": "https://arxiv.org/abs/...",
  "data_sources": [
    {"name": "Yahoo Finance", "type": "url", "location": "https://..."},
    {"name": "CRSP", "type": "licensed", "location": "WRDS"},
    {"name": "local.csv", "type": "file", "location": "data/local.csv"},
    {"name": "Bloomberg SPX", "type": "absent", "location": ""}
  ]
}
```

输出 `results/triage_report.json`：每个数据源标记 `available` / `needs_auth` / `missing` + 处置建议 + 汇总计数。URL 探测超时 5 秒，网络不可达时降级为 `missing`，不阻塞流程。

**G01**: 每个数据源均已分类；`licensed`/`absent` 的实验已确定处置方式

---

### Phase 2: 论文理解 / Paper Understanding

**输出**: `analysis/paper_summary.json`

2.1 提取**目标数值清单**：论文中每个待复现的表格数值/图表数值 + 其容差
2.2 提取模型架构规格（层数、单元数、激活、参数总量）——参数总量是最快的架构校验
2.3 提取训练超参（epochs、lr、batch、种子）
2.4 标记论文中未交代的细节 → `analysis/gray_areas.md`

**G02**: 目标数值清单确认

**nature-archify 参与（论文理解阶段）**: 理解确认后可用 nature-archify 绘制不依赖实验数据的系统与流程图——`architecture` 系统架构图、`workflow` 技术流程图、`sequence` 调用时序图、`dataflow` 数据流图、`lifecycle` 状态机图（预计版；五类图都不承载实验数值）；`experiment` 实验流程图此阶段仅允许 `"status": "draft"` 的 predicted flow 草案，最终版必须等 G6 判决后（硬规则见 nature-archify/SKILL.md）。执行前遵守 nature-archify 第 0 步必问。

### 1.5 辅助架构图征询（可选但必须询问） / Auxiliary Architecture Diagram Offer

论文理解阶段完成后须主动征询用户是否制作系统/流程架构图（nature-archify），同意后强制 6 项逐项询问（主题/图类型/图语言/动画/视觉预设/输出格式）。五类图（architecture/workflow/sequence/dataflow/lifecycle）均不承载实验数值，Phase 1-6 均可交付终版。

> 完整流程、6 项询问表与图类型可用矩阵见 [`references/auxiliary_diagram_offer.md`](references/auxiliary_diagram_offer.md)。

---

### Phase 3: 基线验证 / Baseline Verification

**输出**: `results/baseline_metrics.json`

3.1 先跑上游仓库原始代码（不改一行），记录是否能跑通
3.2 架构校验：参数总量是否与论文一致（如实验 07 的 11,191）
3.3 单点数值比对，容差取论文精度位数（确定性实验可用 1e-4）
3.4 跑不通 → 定位是环境、数据还是代码缺失，写入 `analysis/gray_areas.md`

**G4**: 基线对齐，或灰区记录完整

---

### Phase 4: 增量实现与修复 / Incremental Implementation

**输出**: `implementation/delta_report.json`

4.1 按 DAG 拓扑序修复：数据加载 → 模型构建 → 训练循环 → 评估
4.2 每个修复独立 commit，注明论文 Eq. 编号或 bug 现象
4.3 每次修复后重跑最小规模验证，delta 超容差则回退

**已验证的修复补丁**：具体修复内容见 `fin_tool/registry.py` 中各实验的 `fixes` 字段（当前含实验 02/04/10）。查看完整修复详情：

```bash
python -m fin_tool.cli show 02    # WGAN discriminator shape mismatch
python -m fin_tool.cli show 04    # BCVA 第二阶段 0% CPU 挂起
python -m fin_tool.cli show 10    # keras_metadata.pb 与 TF 2.15 不兼容
```

**G5**: 所有模块通过 delta 验证

---

### Phase 5: 统计验证 / Statistical Verification

**输出**: `results/statistical_summary.json`

5.1 **多种子**: N ≥ 5（GAN/MC 类实验必须；确定性实验可 N=1 并注明）
5.2 **指标**（`fin_tool.metrics`）:
    年化 Sharpe（252 交易日）、Sortino、最大回撤、对冲概率、相对误差
5.3 **区间估计**: `bootstrap_ci()` 给出均值的 95% 置信区间
5.4 **五态判决**（`fin_tool.metrics.verdict`，统一枚举）:

| 判决 | 条件 |
|------|------|
| `pass` | 相对误差 ≤ tol |
| `approx` | tol < 相对误差 ≤ 3·tol |
| `within_ci` | 论文值落在复现 95% CI 内 |
| `fail` | 相对误差 > 3·tol |
| `skip` | 跳过（无参考值/实验不可运行；旧 not_testable, blocked → skip） |

**G6**: 每个目标数值均有判决 + CI

**nature-archify 参与（报告插图）**: G6 判决产出后，系统架构/技术流程/调用时序/数据流/状态机图一律经 nature-archify 渲染，数据可视化图走 nature-figure。注意：`experiment` 实验流程图（PRISMA/CONSORT 等，需真实样本量与排除数）**不在 nature-archify 的五类图内**，需要时另行接入 paperfig 类渲染器。

---

### Phase 6: 报告生成 / Report Generation

**输出**: `实验复刻结果汇总/` 中英双语文档

**nature-archify 参与（报告插图）**: 报告中的系统架构图/技术流程图/时序图/数据流图/状态机图由 nature-archify 产出（self-contained inline-SVG HTML，可加 trace 动效；13 种视觉预设）；实验流程图不在其图类型内，另行接入 paperfig 类渲染器。

```
实验复现结果汇总/
│
├── <编号>_<实验名>/                  # 每篇论文一个子实验目录
│   ├── 实验报告/
│   │   ├── 复现报告.md               # 英文
│   │   ├── 复现报告-CN.md            # 中文
│   │   ├── 诊断分析.md               # 英文
│   │   ├── 诊断分析-CN.md            # 中文
│   │   ├── 运行摘要.md / 运行摘要-CN.md
│   │   └── 判决结果.json             # 双语 JSON，含五态判决
│   ├── 实验结果对比表/
│   │   ├── 实验结果对比表.md         # 英文
│   │   └── 实验结果对比表-CN.md      # 中文
│   ├── 训练结果/                     # 权重、PnL csv、npy
│   ├── 日志/                         # 完整训练日志
│   └── 实验图表（含代码）/
│       ├── *.png
│       └── code/ plot_*.py + plot_*.tex
│
└── 总览/
    ├── 汇总报告.md / 汇总报告-CN.md
    ├── 对比总表.md
    └── 总判决结果.json
```

**G7**: 每个子实验目录结构完整，`总览/` 提供跨实验汇总

---

## 内建实验档案 / Built-in Experiment Registry

10 篇论文的真实复现结果（WSL2 Ubuntu, 8 核 CPU, 3.7 GB RAM, 无 GPU）：完全复现 5 / 部分复现 3 / 无法复现 2。实验 07 是唯一达到 0.01% 容差内逐项匹配的实验，可作为框架正确性基准。

> 实验档案的**单一真相源**为 `fin_tool/registry.py`（`REGISTRY` 字典）。完整状态表、阻塞原因与实验 07 基准数值见 [`references/experiment_registry_detail.md`](references/experiment_registry_detail.md)（人类可读视图，数据与 registry.py 同步）。
---

## 快速开始 / Quick Start

```bash
# 10 个实验的复现状态总表
python -m fin_tool.cli status

# 某个实验的完整档案（数值、产物、阻塞、修复）
python -m fin_tool.cli show 07
python -m fin_tool.cli show 02 --json

# 五态判决：复现值 vs 论文值
python -m fin_tool.cli verdict --value 1.3274 --ref 1.3274 --tol 1e-4

# PnL 序列的风险指标 + 95% bootstrap CI
python -m fin_tool.cli metrics --pnl results/AMZN-FinGAN-PnL.csv

# 测试套件
python -m pytest tests/ -v
```

```python
from fin_tool import metrics as M, registry as R

M.sharpe_ratio(returns)                  # 年化 Sharpe（252 交易日）
M.hedge_probability(pnl)                 # 对冲概率
M.bootstrap_ci(sample, seed=42)          # 95% CI，确定性
M.verdict(1.02, 1.0, tol=0.01)           # -> 'approx'

R.get("07").metrics                      # 实验 07 的复现数值
R.by_status(R.BLOCKED)                   # 哪些实验跑不了、为什么
```

---

## 适配新论文 / Adapting to a New Paper

| 步骤 | 动作 |
|------|------|
| 1 | 在 `fin_tool/registry.py` 追加一条 `Experiment`，先只填 `status=BLOCKED` |
| 2 | 跑 Phase 1 数据分诊，把数据源写进 `blockers` 或确认 `open` |
| 3 | Phase 2 提取目标数值清单 → 用 `M.verdict_table()` 生成判决表 |
| 4 | 复现推进过程中把 `status` 逐步升级为 `partial` / `done`，`fixes` 记录每个补丁 |

框架层（`fin_tool/metrics.py`、`scripts/`、`templates/`）无需修改。

---

## 集成 Nature 子技能 / Integrated Nature Skills

本 skill 集成四个独立 Nature 子技能（`nature-reader`/`nature-figure`/`nature-paper2ppt`/`nature-archify`）和共享层 `_shared/`，位于 `math-read-do/` 目录下，可独立调用，也可增强 Phase 1-6。nature-archify 参与 Phase 2（系统/流程/时序/数据流/状态机图）与 Phase 6（报告插图）；nature-figure 增强 Phase 5 图表导出；nature-paper2ppt 在 Phase 6 后生成汇报 PPTX。

> 子技能路由表、入口文件与主流程协同详情见 [`references/nature_skills_integration.md`](references/nature_skills_integration.md)。

---

## 与其它 math-read-do 分支的关系

| 维度 | math-read-do (main) | math-read-do-obj | **math-read-do-finance** |
|------|--------------------|------------------|--------------------------|
| 目标 | 任意数学论文复现 | 输出 .obj 的图形学算法 | 量化金融 + 深度学习实验 |
| Phase 1 | PDF 解析 (MinerU) | 算法理解 | **数据可得性分诊** |
| 输入 | PDF / arXiv | .obj + 算法规格 | 论文 + 金融时间序列/期权面 |
| 关键风险 | 公式理解偏差 | 几何退化 | **数据授权 + 环境冲突** |
| Phase 5 | 多种子统计验证 | 多模型交叉验证 | 多种子 + bootstrap CI + 五态判决 |
| 核心依赖 | mineru-open-sdk | numpy | numpy (+ TF 2.15 / torch 1.9 双环境) |
| 典型用户 | 数学研究者 | 图形学开发者 | 量化研究员 / 金融工程 |

---

## 参考文献 / References

> 10 篇量化金融顶刊论文完整列表见 [`references/references.md`](references/references.md)。
