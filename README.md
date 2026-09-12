# Math-Read-Do-Finance：量化金融实验复现框架

## 概述

**math-read-do-finance** 是面向「量化金融 + 深度学习」论文实验的标准化复现框架，
基于 10 篇顶刊论文（Quantitative Finance / Mathematical Finance /
SIAM J. Financial Mathematics / Frontiers of Mathematical Finance, 2022–2025）
的真实复现经验构建。

一句话：**论文 + 数据分诊 → 双环境复现 → 五态判决 + 95% CI → 中英双语报告**

## 核心洞察

量化金融复现的失败，**大多不是算法写错了**：

- **数据是商业授权的** — CRSP/WRDS、Bloomberg、ICAP 拿不到（10 个实验里 3 个卡在这）
- **环境天然冲突** — signatory 只支持 torch 1.9，与 TF 2.15 无法共存
- **上游代码残缺** — 论文仓库漏提交核心模块
- **内存是硬墙** — 3.7 GB RAM 下 notebook 直接 kernel died

所以框架的第一优先级不是"跑通"，而是**在开跑前分清"跑不通的原因"**，
并用五态判决（pass / approx / fail / not_testable / blocked）诚实地表达出来。

## 框架架构

```
框架层 (Framework)              档案层 (Registry: 10 papers)
  metrics.py  (金融指标+判决)      registry.py  (10 个实验的真实复现数据)
  cli.py      (命令行)             tests/       (18 个测试)
  templates/  (双语报告模板)
  scripts/    (自动更新)

适配新论文只需在 registry.py 追加一条记录，框架层不变。
```

## 复现状态总览

| 编号 | 实验 | 期刊 | 状态 | 关键结果 |
|------|------|------|------|---------|
| 01 | Robust Deep Hedging | QF 2022 | ✅ | 4/4 notebooks |
| 02 | Sig-Wasserstein GANs | MF 2023 | ✅ | 4/4 runs（含维度修复） |
| 03 | Joint Calibration SPX/VIX | MF 2024 | ⚠️ | configs 2–5 完成 |
| 04 | Deep xVA Solver | SIFIN 2023 | ⚠️ | Y0≈1.9673 / 1.98；BCVA 挂起 |
| 05 | Fin-GAN | QF 2024 | ✅ | SR_w=0.88 (test) |
| 06 | Signature-Based Models | SIFIN 2023 | ❌ | 缺 Bloomberg 数据 |
| 07 | Network Superhedging | MF 2022 | ✅ | 1.3274 / 0.4072（精确匹配） |
| 08 | Signature Volatility Models | SIFIN 2025 | ❌ | 上游缺 fourier.py |
| 09 | Optimal Stopping Randomized NN | FMF 2023 | ✅ | NLSM ≈ 10.9–21.7 |
| 10 | Deep Weighted Monte Carlo | QF 2023 | ⚠️ | 模型已修，notebook OOM |

**完全复现 5 / 部分复现 3 / 无法复现 2**

## 快速开始

```bash
# 复现状态总表
python -m fin_tool.cli status

# 某实验的完整档案
python -m fin_tool.cli show 07

# 五态判决
python -m fin_tool.cli verdict --value 1.3274 --ref 1.3274 --tol 1e-4

# PnL 风险指标 + bootstrap CI
python -m fin_tool.cli metrics --pnl AMZN-FinGAN-PnL.csv

# 测试
python -m pytest tests/ -v
```

## Python API

```python
from fin_tool import metrics as M, registry as R

M.sharpe_ratio(returns)            # 年化 Sharpe（252 交易日）
M.sortino_ratio(returns)
M.max_drawdown(cum_pnl)
M.hedge_probability(pnl)           # 实验 07 的 hedge_prob
M.bootstrap_ci(sample, seed=42)    # 确定性 95% CI
M.verdict(value, ref, tol=0.01)    # pass/approx/fail/not_testable/blocked

R.get("07").metrics                # 复现数值
R.by_status(R.BLOCKED)             # 跑不了的实验及原因
R.summary()                        # {'done': 5, 'partial': 3, 'blocked': 2}
```

## 环境

两个 conda 环境**必须隔离**（signatory 与 TF 2.15 依赖互斥）：

```bash
# 环境 A：TensorFlow 系（实验 01/04/05/09/10）
conda create -n financial python=3.11
pip install tensorflow==2.15.0

# 环境 B：torch + signature 系（实验 02/03/06/07/08）
conda create -n sigtorch39 python=3.9
pip install torch==1.9.1 "numpy<2"
# signatory 必须从源码编译（需 g++），pip install 会失败
```

`fin_tool` 本身只依赖 numpy>=1.21，两个环境都能导入。

## 已验证的修复补丁

| 实验 | 症状 | 修复 |
|------|------|------|
| 02 | WGAN discriminator shape mismatch | `train.py:93` 的 `input_dim` 由 `x_real_dim * n_lags`(16) 改为 `x_real_dim * x_real.shape[1]`(17) |
| 10 | `keras_metadata.pb` 与 TF 2.15 不兼容 | 代码内重建架构 + 逐层拷权重 |
| 04 | BCVA 第二阶段 0% CPU 挂起 | `matplotlib.use("Agg")`，移除 `plt.show()` |

## 项目结构

```
math-read-do-finance/
├── SKILL.md                    # Skill 入口（Phase Δ-1 → 6 完整流程）
├── README.md                   # 本文件
├── fin_tool/
│   ├── metrics.py              # [框架] 金融指标 + 五态判决引擎
│   ├── registry.py             # [档案] 10 个实验的复现数据
│   └── cli.py                  # 命令行入口
├── tests/                      # 18 个测试
├── scripts/auto_update.sh      # 自动更新
└── templates/                  # 双语报告模板
```

## 参考

复现数据来源：`math-read-do-financial-best-repro`（2026-08-05/06，
WSL2 Ubuntu, 8 核 CPU, 3.7 GB RAM, 纯 CPU 无 GPU）

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
