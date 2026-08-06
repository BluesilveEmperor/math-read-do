---
name: math-read-do-finance
description: >-
  量化金融论文实验复现标准化工作流 / Standardized Quantitative-Finance Paper Reproduction Pipeline

  以 10 篇顶刊量化金融论文的真实复现（Quantitative Finance / Mathematical Finance /
  SIAM J. Financial Mathematics / Frontiers of Mathematical Finance, 2022–2025）
  为设计范本，构建面向"深度学习 + 金融数值实验"的复现框架。

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
| **数据常为商业授权** | CRSP/WRDS、Bloomberg、ICAP 数据不可公开获取 | Phase 1 数据分诊：先判可得性，再决定合成替代或标记 `not_testable` |
| **环境高度分裂** | signatory 只支持 torch 1.9，与 TF 2.15 不可共存 | 强制双 conda 环境（`financial` / `sigtorch39`），每个实验声明所属环境 |
| **结果是随机量** | GAN、蒙特卡洛的输出天然带方差 | 多种子 + bootstrap 95% CI，而非单点比对 |
| **上游代码常残缺** | 论文仓库漏提交核心模块 | 五态判决含 `blocked`，允许诚实地"复现不了" |
| **内存是硬约束** | 3.7 GB RAM 下 notebook 会 kernel died | Phase 0 记录内存上限，串行化重实验 |

因此本框架的核心不是"跑通"，而是 **"分清跑不通的三种原因"**：
数据缺失（`not_testable`）／上游代码缺失（`blocked`）／实现有偏差（`fail`）。

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

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 合成数据结果直接与论文数值对比 | 结论无效 | 标记 `not_testable`，只做"方法可运行性"验证 |
| 2 | 单次运行结果与论文比对 | GAN/MC 方差被当成偏差 | N≥5 种子 + bootstrap 95% CI |
| 3 | 在一个 conda 环境里同时装 TF 2.15 和 signatory | 依赖地狱，numpy 版本互斥 | 双环境，`conda run -n <env>` 调用 |
| 4 | `pip install signatory` | 必然失败 | 从源码编译（需 g++），且只支持 torch 1.9 |
| 5 | torch 1.9 环境装 numpy>=2 | 导入即崩 | 锁 `numpy<2`；esig 需 0.9.8.3 |
| 6 | notebook 里留 `plt.show()` 跑批处理 | 进程 0% CPU 永久挂起（实验 04 原因） | 批处理一律 `matplotlib.use("Agg")` + `savefig` |
| 7 | 直接 load TF1 时代的 SavedModel | `keras_metadata.pb` 与 TF 2.15 不兼容 | 代码里重建架构 + 逐层拷权重（实验 10 修复） |
| 8 | 3.7 GB RAM 下并行 6 个训练 | kernel died，全部白跑 | 最多并行 4–5 个轻量任务，重实验串行 |
| 9 | 假定 `n_lags` 等于真实时间步数 | discriminator 维度不匹配（实验 02 bug） | 用 `x_real.shape[1]` 取真实步数 |
| 10 | 不记录随机种子与超参 | 结果不可重现 | 每次运行落 `results/<exp>/run_config.json` |
| 11 | 年化 Sharpe 时用 365 天 | 数值系统性偏高 | 交易日 252（`fin_tool.metrics.TRADING_DAYS`） |
| 12 | 训练日志只打屏不落盘 | 挂起后无法定位 | 一律 `> logs/<exp>/<run>.log 2>&1` |

---

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| **Δ-1** | 自动更新 | `git log -1` | **GΔ**: 网络可达时同步最新 |
| 0 | 宿主检测 + 资源上限 | `infra/infra_manifest.json` | G0: CPU/RAM/磁盘记录在案 |
| 0.5 | 双环境构建 + 版本锁定 | `env/version_spec.json` | G1: 两环境导入测试通过 |
| 1 | **数据可得性分诊** | `analysis/data_triage.json` | G01: 每个数据源标记 open/licensed/absent |
| 2 | 论文理解 + 指标提取 | `analysis/paper_summary.json` | G2: 目标数值清单确认 |
| 3 | 基线验证 | `results/baseline_metrics.json` | G3: 基线对齐或记录灰区 |
| 4 | 增量实现 + 修复 | `implementation/delta_report.json` | G4: 每模块 delta 验证 |
| 5 | 多种子统计验证 | `results/statistical_summary.json` | G5: 五态判决 + 95% CI |
| 6 | 中英双语报告 | `实验复现结果汇总/` | G6: 各子实验目录完整 |

---

## 阶段详述 / Phase Detail

### Phase Δ-1: 自动更新
见上文「自动更新」。失败静默跳过，不阻塞流程。

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
| `licensed` | 商业授权（CRSP/WRDS、Bloomberg、ICAP） | 生成合成替代（GBM/Heston），**判决降级为 `not_testable`** |
| `absent` | 论文和仓库均未提供，也无法合成 | 标记 `blocked`，不启动训练 |

**合成替代规范**：
- 必须与原数据同维度、同频率（否则出现实验 06 的 7 vs 9 维度不匹配）
- 生成脚本落盘并记录种子
- 报告中显著标注"合成数据，不构成对论文数值的验证"

**G01**: 每个数据源均已分类；`licensed`/`absent` 的实验已确定处置方式

---

### Phase 2: 论文理解 / Paper Understanding

**输出**: `analysis/paper_summary.json`

2.1 提取**目标数值清单**：论文中每个待复现的表格数值/图表数值 + 其容差
2.2 提取模型架构规格（层数、单元数、激活、参数总量）——参数总量是最快的架构校验
2.3 提取训练超参（epochs、lr、batch、种子）
2.4 标记论文中未交代的细节 → `analysis/gray_areas.md`

**G2**: 目标数值清单确认

---

### Phase 3: 基线验证 / Baseline Verification

**输出**: `results/baseline_metrics.json`

3.1 先跑上游仓库原始代码（不改一行），记录是否能跑通
3.2 架构校验：参数总量是否与论文一致（如实验 07 的 11,191）
3.3 单点数值比对，容差取论文精度位数（确定性实验可用 1e-4）
3.4 跑不通 → 定位是环境、数据还是代码缺失，写入 `analysis/gray_areas.md`

**G3**: 基线对齐，或灰区记录完整

---

### Phase 4: 增量实现与修复 / Incremental Implementation

**输出**: `implementation/delta_report.json`

4.1 按 DAG 拓扑序修复：数据加载 → 模型构建 → 训练循环 → 评估
4.2 每个修复独立 commit，注明论文 Eq. 编号或 bug 现象
4.3 每次修复后重跑最小规模验证，delta 超容差则回退

**已验证的修复补丁**（`fin_tool/registry.py` 中 `fixes` 字段）：

| 实验 | 症状 | 修复 |
|------|------|------|
| 02 | WGAN discriminator shape mismatch | `train.py:93` 的 `input_dim` 由 `x_real_dim * n_lags`(16) 改为 `x_real_dim * x_real.shape[1]`(17) |
| 10 | `keras_metadata.pb` 与 TF 2.15 不兼容 | 代码内重建 weight_decoder 架构，逐层拷贝权重 |
| 04 | BCVA 第二阶段 0% CPU 挂起 | 改 `Agg` 后端 + 去掉 `plt.show()`；仍 OOM 则拆分两阶段 |

**G4**: 所有模块通过 delta 验证

---

### Phase 5: 统计验证 / Statistical Verification

**输出**: `results/statistical_summary.json`

5.1 **多种子**: N ≥ 5（GAN/MC 类实验必须；确定性实验可 N=1 并注明）
5.2 **指标**（`fin_tool.metrics`）:
    年化 Sharpe（252 交易日）、Sortino、最大回撤、对冲概率、相对误差
5.3 **区间估计**: `bootstrap_ci()` 给出均值的 95% 置信区间
5.4 **五态判决**（`fin_tool.metrics.verdict`）:

| 判决 | 条件 |
|------|------|
| `pass` | 相对误差 ≤ tol |
| `approx` | tol < 相对误差 ≤ 3·tol |
| `fail` | 相对误差 > 3·tol |
| `not_testable` | 无参考值（合成数据替代了授权数据） |
| `blocked` | 实验根本跑不起来（缺代码/缺数据/内存不足） |

**G5**: 每个目标数值均有判决 + CI

---

### Phase 6: 报告生成 / Report Generation

**输出**: `实验复现结果汇总/` 中英双语文档

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

**G6**: 每个子实验目录结构完整，`总览/` 提供跨实验汇总

---

## 内建实验档案 / Built-in Experiment Registry

10 篇论文的真实复现结果（WSL2 Ubuntu, 8 核 CPU, 3.7 GB RAM, 无 GPU）：

| 编号 | 实验 | 期刊 | 环境 | 状态 | 关键结果 / 阻塞原因 |
|------|------|------|------|------|--------------------|
| 01 | Robust Deep Hedging | Quantitative Finance 2022 | financial | ✅ 完成 | 4/4 notebooks 执行成功 |
| 02 | Sig-Wasserstein GANs | Mathematical Finance 2023 | sigtorch39 | ✅ 完成 | 4/4 组实验（需 discriminator 维度修复） |
| 03 | Joint Calibration SPX/VIX | Mathematical Finance 2024 | sigtorch39 | ⚠️ 部分 | configs 2–5 输出 `Rho_d=4.npy`；6–8 空目录 |
| 04 | Deep xVA Solver | SIAM J. Fin. Math 2023 | financial | ⚠️ 部分 | callOption Y0≈1.9673, fvaForward Y0≈1.98；BCVA 挂起 |
| 05 | Fin-GAN | Quantitative Finance 2024 | financial | ✅ 完成 | SR_w(test)=0.88, SR_w(val)=2.19（合成数据） |
| 06 | Signature-Based Models | SIAM J. Fin. Math 2023 | sigtorch39 | ❌ 阻塞 | 缺 Bloomberg SPX 到期日/行权价数据 |
| 07 | Network Superhedging | Mathematical Finance 2022 | sigtorch39 | ✅ 完成 | λ=200: 1.3274/0.4072；λ=1e5: 2.0952/0.9966 |
| 08 | Signature Volatility Models | SIAM J. Fin. Math 2025 | sigtorch39 | ❌ 阻塞 | 上游仓库缺 fourier.py 等核心模块 |
| 09 | Optimal Stopping Randomized NN | Frontiers Math Fin. 2023 | financial | ✅ 完成 | 全部 configs 通过，NLSM price ≈ 10.9–21.7 |
| 10 | Deep Weighted Monte Carlo | Quantitative Finance 2023 | financial | ⚠️ 部分 | 模型已修复，完整 notebook 内存不足 |

**统计**: 完全复现 5 / 部分复现 3 / 无法复现 2

实验 07 是唯一达到 0.01% 容差内逐项匹配的实验，可作为框架的正确性基准：

| 配置 | 指标 | 复现值 | 论文值 | 判决 |
|------|------|--------|--------|------|
| λ=200 | 价格 | 1.3274 | 1.3274 | pass |
| λ=200 | 对冲概率 | 0.4072 | 0.4072 | pass |
| λ=1e5 | 价格 | 2.0952 | 2.0952 | pass |
| λ=1e5 | 对冲概率 | 0.9966 | 0.9966 | pass |
| — | 参数总量 | 11,191 | 11,191 | pass |

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

- Robust Deep Hedging — *Quantitative Finance*, 2022
- Sig-Wasserstein GANs for Time Series Generation — *Mathematical Finance*, 2023
- Joint Calibration to SPX and VIX Options — *Mathematical Finance*, 2024
- Deep xVA Solver — *SIAM Journal on Financial Mathematics*, 2023
- Fin-GAN: Forecasting and Classifying Financial Time Series — *Quantitative Finance*, 2024
- Signature-Based Models for Option Pricing — *SIAM J. Financial Mathematics*, 2023
- Superhedging with Neural Networks — *Mathematical Finance*, 2022
- Signature Volatility Models — *SIAM J. Financial Mathematics*, 2025
- Optimal Stopping with Randomized Neural Networks — *Frontiers of Mathematical Finance*, 2023
- Deep Weighted Monte Carlo — *Quantitative Finance*, 2023
