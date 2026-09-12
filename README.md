# Math-Read-Do

数学文献阅读与实验复现工作流家族 / Mathematical Literature Reproduction Pipeline Family

**Math-Read-Do** 是一个面向数学文献的标准化"阅读→复现→验证"工作流（Skill）家族，专为 AI Agent 设计。输入一篇论文 PDF，即可自动完成从文献理解到结果验证的全流程。

本仓库包含多个分支，面向不同研究方向。请选择适合的分支开始使用。

| 分支 | 方向 | Phase 1 做什么 | 核心风险 |
|------|------|---------------|---------|
| [main](https://github.com/BluesilveEmperor/math-read-do/tree/main) | 通用数学文献 | PDF 解析 (MinerU) + 三视角审阅 | 公式理解偏差 |
| [math-read-do-routine](https://github.com/BluesilveEmperor/math-read-do/tree/math-read-do-routine) | 机器人路径优化 | 论文类型检测 + 子策略路由 | 求解器配置 |
| [math-read-do-obj](https://github.com/BluesilveEmperor/math-read-do/tree/math-read-do-obj) | 图形学 / OBJ 几何 | 算法理解（无需 PDF 解析） | 几何退化 |
| [financial](https://github.com/BluesilveEmperor/math-read-do/tree/financial) | 量化金融 + 深度学习 | **数据可得性分诊** | 数据授权 + 环境冲突 |

---

## 分支导航 / Branch Navigation

### 🤖 [math-read-do-routine](https://github.com/BluesilveEmperor/math-read-do/tree/math-read-do-routine)

**机器人路径优化论文复现** / Robotics Path Optimization Paper Reproduction

面向机器人路径/轨迹/运动规划方向的论文复现，覆盖：
- **凸优化路径规划**：FastPathPlanning、GCS、CVXPY/SOCP/MICP
- **基于搜索**：A*、D*、Theta*、ANYA
- **基于采样**：RRT、PRM、RRT*、BIT*、Informed RRT*
- **基于学习 / MPC**
- **交互式轨迹可视化**：双击 HTML 即看实时轨迹（支持绕起点旋转 / 自由旋转两种相机模式）

适用平台：UAV、移动机器人、机械臂、足式机器人、水下机器人

**特色功能**：
- Phase 1.5 自动检测论文类型并路由到对应子策略
- CVXPY 环境自动配置（CLARABEL/MOSEK/ECOS）
- 轨迹动画 + 障碍物渲染 + 播放控制

---

### 🎨 [math-read-do-obj](https://github.com/BluesilveEmperor/math-read-do/tree/math-read-do-obj)

**QEM 网格简化 / 图形学 OBJ 复现** / QEM Mesh Simplification & Graphics OBJ Reproduction

面向图形学/几何处理方向，以 QEM 边收缩简化为范本，构建面向"任意输出 .obj 文件的图形学实验"的标准化复刻框架：
- **通用 .obj 实验复刻**：适配任意输出 .obj 的算法
- **多模型交叉验证**：不同 .obj 模型跑同一算法
- **Hausdorff 距离**：简化前后模型差异量化
- **退化面 / 重复面检测**
- **3D 可视化**：MeshCat 渲染

适用论文：QEM (Garland & Heckbert, SIGGRAPH 1997)、Progressive Mesh、纹理简化等

**特色功能**：
- 完整的 .obj I/O 解析器 + QEM 简化引擎 + CLI
- C++/CUDA/3D 项目专属检测与构建

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
- Phase 1 **数据可得性分诊** — 本领域最大时间陷阱是 CRSP/WRDS/Bloomberg/ICAP 授权数据，开跑前先分诊
- **五态判决**：`pass` / `approx` / `fail` / `not_testable`（合成数据替代）/ `blocked`（缺代码或缺算力）
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

**视角审阅**：研究生 / 导师 / 审稿人三视角

---

## 快速开始 / Quick Start

```bash
# 克隆特定分支
git clone -b math-read-do-routine https://github.com/BluesilveEmperor/math-read-do.git
git clone -b math-read-do-obj     https://github.com/BluesilveEmperor/math-read-do.git
git clone -b financial            https://github.com/BluesilveEmperor/math-read-do.git
```

每个分支都有独立的 `SKILL.md`，包含该方向的完整使用说明。

## 自更新 / Auto-Update

`math-read-do-routine`、`math-read-do-obj` 和 `financial` 分支内置自更新机制，每次调用前自动检查远程仓库是否有更新。

## 子技能 / Sub-Skills

每个分支都集成四个 nature-* 子 Skill，可独立调用也可在主流程里协同：

| 子技能 | 角色 | 与谁互补 |
|--------|------|---------|
| `nature-reader/` | 科研论文智能阅读、结构化提取 (PDF/HTML/DOI/arXiv) | — |
| `nature-figure/` | 科研数据可视化（matplotlib/seaborn/SciencePlots/plotly，8 步工作流 + 视觉自检闭环） | 跟 nature-framework 互补 |
| `nature-paper2ppt/` | 论文→中文 PPTX（6 类叙事弧 + 自审校） | — |
| `nature-framework/` | **科研架构图渲染器**（6 类图：model/framework/route/system/structure/experiment；10 视觉预设；11 项 showcase 校验；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体） | 跟 nature-figure 互补——本子技能专做架构/框架/流程图 |

`nature-framework` 需要 Node.js ≥ 18，零外部依赖；Python 侧通过 `scripts/nature_architecture_bridge.py` 调用。详见 [nature-framework/SKILL.md](nature-framework/SKILL.md)。

## 许可 / License

MIT
