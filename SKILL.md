---
name: math-read-do-routine
description: >-
  机器人路径优化论文实验复现标准化工作流 / Robotics Path Optimization Paper Reproduction Pipeline
  面向机器人路径优化方向（路径规划 Path Planning、轨迹规划 Trajectory Planning、运动规划 Motion Planning），
  覆盖基于凸优化 (CVXPY/SOCP/MICP)、基于搜索 (A*/RRT/PRM)、基于采样 (RRT*/BIT*)、基于学习、MCP 等方法。

  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析(含公式/表格/图表) →
  按用户指定视角输出审阅报告(研究生/导师/审稿人) →
  环境重建（自动检测求解器/碰撞检测器） → 基线验证 → 增量实现 → 统计验证(五态判决+95%CI) → 双语报告。
  每份报告必须中英双语。

  集成三大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：出版级图表生成 (Python/R, Nature/CNS 风格)
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)

  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现,
  重现论文, 论文重现, 数值复现, 论文复现, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 重现结果, 重现图表, 复现结果, 复现图表,
  reproducibility check, 可复现性评估, 复现验证,
  路径规划, path planning, 轨迹规划, trajectory planning, 运动规划, motion planning,
  机器人路径, robot path, 无人机路径, UAV path, 凸优化路径, convex optimization path,
  RRT, PRM, A*, Dijkstra, CVXPY, SOCP, MICP, GCS, FastPathPlanning, 网格简化复现

  # nature-reader triggers
  读论文, 读文献, 论文阅读, 论文分析, read paper, read article, 审阅论文, extract paper,
  understand paper, 文献分析, 论文理解, 文章解读, 解析文献, 科研论文阅读

  # nature-figure triggers
  nature figure, 论文配图, 学术图表, 科研绘图, 作图, figure, plot for paper,
  publication figure, 出版级图表, 杂志图, 论文图, figure for paper, scientific figure,
  journal figure, figure generation, 图表生成, 可视化论文, 数据可视化

  # nature-paper2ppt triggers
  论文做PPT, 论文汇报, 组会PPT, 文献汇报, 学术汇报, 做幻灯片, 讲paper,
  读书报告PPT, paper to slides, journal club, 论文转PPT, 学术演讲
compatibility:
  - python3 (mineru-open-sdk >= 0.2.5)
  - 配置文件: ~/.mineru/config.yaml (MinerU token)
  - nature-reader: python-pptx, Pillow (图提取), PyMuPDF (PDF渲染)
  - nature-figure: Python (matplotlib/seaborn) 或 R (ggplot2/patchwork/ComplexHeatmap)
  - nature-paper2ppt: python-pptx, PyMuPDF, Pillow, zipfile
  - robotics: numpy, scipy, networkx, cvxpy, clarabel, matplotlib
---

# Mathematical Literature Experiment Reproduction Standardized Workflow
# 数学文献实验复现标准化流程

## 交互规则 / Interaction Rules

用户未输入任何具体操作指令时，**不允许默认执行任何操作**。必须主动向用户提问，列出可执行的操作选项，等待用户选择后执行。

**标准提问模板**:
```
请选择要执行的操作：

1️⃣ 阅读论文 — 解析PDF并输出指定视角的审阅报告
2️⃣ 复现实验 — 启动完整复现流程（Phase 0→7）
3️⃣ 生成图表 — 基于实验数据出版级图表
4️⃣ 制作PPT — 将论文或复现结果转为演示文稿
```

用户做出选择后，按对应流程执行。用户未指定审阅视角时，默认使用**研究生视角**（学习理解导向）。

## 自更新策略 / Self-Update Policy

每次技能被调用（load_skill）时，**必须先执行自更新检查**，确保技能本身是最新版本后再执行业务逻辑。

### 调用前检查 / Pre-Invocation Check

```bash
1. cd $SKILL_ROOT
2. bash scripts/auto_update.sh
   (内部逻辑: git fetch origin math-read-do-routine → 比较 HEAD → 有更新则 stash → merge --ff-only → pop)
3. 更新完成后，继续执行正常的 Phase 0→7 流程
```

输出: "✅ math-read-do-routine 已自动更新到最新版本" 或 "✅ 已是最新版本"

### 修改后推送 / Push After Modification

```
任何对 SKILL.md / templates / scripts/ / references/ 的本地修改完成后:
1. git add -A
2. git commit -m "<feat/fix/chore>: <描述>"
3. git pull --rebase origin math-read-do-routine
4. git push origin math-read-do-routine
5. 输出: "✅ 技能优化已推送至 origin/math-read-do-routine"
```

### 防冲突策略 / Conflict Prevention

- 每次推送前先 `git pull --rebase`，确保基于最新远程版本
- 若 rebase 冲突 → 以本地修改为准 (`git checkout --theirs` 冲突文件 → `git rebase --continue`)
- 若 push 被拒 → `git pull --rebase` 后重新 push
- 最大重试次数: 3 次；超过则停止并报告冲突，等待人工介入

### 实现要求 / Implementation Requirement

- 此自更新逻辑是**强制性**的，不可跳过
- 实现为 skill 加载时的第一个动作，早于任何用户交互
- 更新失败不阻塞后续流程（降级为使用当前版本 + 警告）

## 核心原则 / Core Principles

1. **双语输出**: 所有报告必须有中英双版本 (`.md` 英文 + `-CN.md` 中文)
2. **增量验证**: 每添加一个模块即验证一次
3. **可审计**: 每步产生结构化产物，溯源链完整
4. **人机协同**: 风险分级审批
5. **锁定即契约**: 版本/环境/依赖每步锁定，不信任隐式继承
6. **先问后做**: 用户无指令时先主动提问，确认操作后再执行

## 反例与黑名单 / Anti-Patterns & Blacklist

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | MinerU token 未配置就执行 Phase 1.1 | 脚本报 401 | 先检查 `~/.mineru/config.yaml`，未配置则引导用户获取 |
| 2 | Windows 上直跑 Linux 路径脚本 | 换行符/路径分隔符不兼容 | 使用 WSL2 或 `scripts/enable_gpu.ps1` 等 Windows 原生脚本 |
| 3 | 先装包再装语言运行时 | Conda/pip SAT 死锁 | 严格 运行时→版本管理器→锁定→包的顺序 |
| 4 | 只跑一个种子就下判决 | 非确定性被忽略 | 至少 N=5 种子, 95% CI 统计判决 |
| 5 | 只生成英文报告 | 中文用户无法阅读 | 每份报告同时生成 `.md`(英文) 和 `-CN.md`(中文) |
| 6 | 跳过三方审阅直接进 Phase 2 | 论文理解不充分 | 必须跑完 Phase 1.4, 获得 reproducibility_assessment.json |
| 7 | 导出图表时不导出生成代码 | 图表无法独立复现 | 每张图附带 `results/figures/code/plot_*.py` |
| 8 | 跳过可行性预判直接建环境 | 遇到私有数据/硬件时大量浪费 | Phase 0 先快速可行性标记 |
| 9 | 基线失败时不记录偏离 | 丢失诊断信息 | 基线失败必须写 `analysis/gray_areas.md` |
| 10 | conda + pip 一次性混合安装 | SAT 求解器死锁 | 严格 conda→pip 顺序，单步验证 |
| 11 | 单点均值比较忽略方差 | CI 很宽时判决虚假积极 | 用 95% CI 区间验证, 报告 x-bar ± CI |
| 12 | 自动翻译不校对专业术语 | 术语混淆 (identification != 识别) | 术语先在 glossary.md 对齐, 翻译后人工校对 |
| 13 | 增量实现时不标注论文出处 | 代码溯源断裂 | 每个函数 docstring 写 `Ref: Section X.Y, Eq.(Z)` |

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| 0 | 宿主检测→环境构建→GPU配置 | `infra_manifest.json` | G0: 基础设施就绪 |
| 0.5 | 版本检测→安装→锁定→验证 | `version_spec.json` | G1: 版本一致 |
| 1 | PDF解析→结构化提取→领域分类→三方审阅 | `reproducibility_assessment.json` | G01: 可复现性门禁 |
| 1.5 | 论文类型自动检测→路由到子策略 | `repro_plan.json` | 类型判定 |
| 2 | 依赖扫描→环境构建→确定性配置→验证 | `conda-lock.yml` | G3: 环境就绪 |
| 3 | 官方代码运行→指标对齐→失败诊断→锁定 | `baseline_metrics.json` | G4: 基线建立 |
| 4 | 模块拆解→增量实现→代码管理 | `delta_report.json` | -- |
| 5 | 多轮运行→统计计算→五态判决→图表导出 | `判决结果.json` | 5.1 参数确认 |
| 6 | 数据就绪检测→双语报告生成(含模板) | `实验复刻结果汇总/实验报告/复现报告.md` + `-CN.md` | 数据就绪 |
| 7 | 最终整理→完整性确认 | `实验复刻结果汇总/` 完整目录 | 文件就位确认 |

---

## 阶段详述 / Phase Detail

### Phase 0: 基础设施检测与配置 / Infrastructure Detection & Setup

**输入**: 宿主操作系统信息
**输出**: `infra/infra_manifest.json` + 环境配置

0.1 **宿主检测**: OS/GPU/内存/磁盘/虚拟化 → `infra/host_detection.json`
0.2 **需求分析**: 扫描论文关键词 (CUDA/MPI/Fortran/MATLAB) + 可行性预判 → `info/feasibility_precheck.json`
    - 决策矩阵: Windows→WSL2/Vagrant/Docker; macOS→Docker/Lima; Linux→Native/Docker
0.3 **环境构建**: 路径 A WSL2 → B Vagrant → C Docker → D Native (按序 fallback)
    - 失败处理: `wsl --install` 失败→检查 BIOS 虚拟化→切 Vagrant; `vagrant up` 超时→`destroy -f && --no-provision`; `docker pull` 超时→配置国内镜像
0.4 **验证**: 架构/内核/内存/GPU/磁盘 → `infra/infra_manifest.json`
0.9 **GPU 配置**: NVIDIA→CUDA (执行 scripts/enable_gpu.sh), AMD→ROCm, Intel→XPU, 集显→CPU
    - 精度 vs 性能配置: deterministic=False (性能) / deterministic=True (可复现)
    - WSL2: 宿主装 CUDA on WSL driver, WSL2 内无需额外安装
    - Docker: `--gpus all` + nvidia/cuda 基础镜像
    - 产出: `infra/gpu_manifest.json`

**G0**: 基础设施检测完成, manifest 已验证, GPU 配置就绪, 环境配置齐备。任一不满足→返回修复。

---

### Phase 0.5: 版本管理 / Version Management

**输入**: `infra/infra_manifest.json` + 版本线索
**输出**: `env/version_spec.json` + `env/reproduction_manifest.json`

0.5.1 **需求检测**: 扫描 `.python-version` / `Manifest.toml` / `.Rprofile` / `.nvmrc` / `CMakeLists.txt` 等
0.5.2 **版本管理器**: pyenv/juliaup/rig/nvm/sdkman/rustup (缺失则自动安装)
0.5.3 **版本安装**: pyenv install / juliaup add / rig add / nvm install / conda cudatoolkit / apt gcc 等
0.5.4 **版本锁定**: conda env export → `conda-lock.yml`; pip freeze → `requirements-locked.txt`; 复制 `Manifest.toml`; dpkg 快照
0.5.5 **一致性验证**: 对比 `version_spec.json` 与运行版本, 记录差异

**G1**: 所有运行时版本与 `version_spec.json` 一致, 锁定文件已写入 `env/`。版本不匹配→修复后继续。

---

### Phase 1: 论文解析与三方审阅 / Paper Parsing & 3-Perspective Review

**输入**: PDF 文件路径 / arXiv 链接
**输出**: `analysis/paper_summary.json` + 三方审阅报告 + `reproducibility_assessment.json`

1.1 **PDF 解析**: 确认 MinerU token 已配置
    - 优先级: MinerU SDK (首选, 含公式/表格/图表) → LaTeXML → PyMuPDF → OCR
    - 参数: `--model vlm`, `--ocr`, `--pages`, `--language`
    - 执行: `python scripts/math_pdf_extract.py <pdf> --output-dir analysis/`
    - 日用量跟踪: 自动记录到 `daily_usage.json` (限额 2000 页)
    - 产出: `analysis/parsed_text.md` + `analysis/formulas.tex`

1.2 **结构化提取**: 核心方法/数学公式/超参数/数据集/评估指标/灰色地带

1.3 **领域分类**: 关键词+依赖 → 路由到数值/符号/AI4Math/统计/优化/经济子策略

1.4 **视角审阅**: 按用户指定视角输出审阅报告；未指定时默认**研究生视角**
    - **用户未指定视角 → 默认研究生**: 直接以研究生视角执行审阅（学习理解导向）
    - **研究生**: 深度理解 -- 摘要/文献综述/研究问题/方法/结果/讨论/关键公式
      → 消费方: Phase 2 环境重建方法栈, Phase 4 增量实现的公式/算法参考
    - **导师**: 可复现性评级 -- 方法评估/可复现性表/教学建议/reproducibility_assessment.json
      → 消费方: G01 门禁 (决定是否进入复现流程)
    - **审稿人**: 批判审查 -- 总体评价/方法论评估/修改意见(强制/建议/细节)/总结
      → 消费方: Phase 5 判决引擎, Phase 6 诊断章节引用
    - 执行: `python scripts/three_perspective_review.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json`
    - 产出: `analysis/<paper>_{student,advisor,reviewer}_review.md`（仅输出指定视角）
    - **严禁默认输出全部视角，仅输出用户指定的单一视角**

**G01 门禁**: 审查 `reproducibility_assessment.json`
    - `proceed` → 直接进 Phase 1.5
    - `proceed_with_caution` → 进 Phase 1.5, 记录已知风险
    - `needs_human_approval` → STOP: 展示风险标记, 获取用户确认
    - `discourage` → STOP: 不建议复现, 展示理由

---

### Phase 1.5: 论文类型自动检测与路由 / Auto-Type Detection & Routing

**输入**: `analysis/paper_summary.json`
**输出**: `analysis/repro_plan.json`

1.5.1 **类型检测**: 执行 `python scripts/robotics_repro.py --paper-json analysis/paper_summary.json`
    - 自动判定论文属于：凸优化 / 搜索 / 采样 / 非凸优化 / 学习 / MPC
    - 识别机器人平台：UAV / 移动机器人 / 机械臂 / 足式 / 水下
    - 识别规划类型：Path / Trajectory / Motion

1.5.2 **求解器推荐**: 根据类型推荐求解器栈
    - 凸优化 → `cvxpy` + `clarabel` (免费) 或 `mosek` (学术)
    - 采样 → `ompl` + `numpy` + `scipy`
    - 学习 → `torch` / `tensorflow` + GPU
    - MPC → `casadi` / `acados`

1.5.3 **路由决策**: 生成 `repro_plan.json`，包含：
    - `paper_type`: 检测到的论文类型
    - `recommended_solver`: 推荐求解器
    - `repro_steps`: 针对该类型的定制化复现步骤
    - `metrics`: 关键评估指标（规划时间、路径成本、成功率等）

---

### Phase 2: 环境重建 / Environment Setup

**输入**: `analysis/paper_summary.json` + `env/version_spec.json` + `analysis/repro_plan.json`
**输出**: `env/environment.yml` + `env/requirements-locked.txt`

2.1 **依赖扫描**: 扫描 repo 配置文件 (`requirements.txt`, `environment.yml`, `Manifest.toml`, `renv.lock`) + 静态分析 import
2.2 **环境构建**: Conda/Mamba → Python venv → Julia → 系统级库 (逐级 fallback)
    - Conda 冲突→`mamba clean --all && --force`; 仍失败→逐个安装核心包
    - pip 超时→`--default-timeout=120`; 仍失败→分批次先科学计算再领域包
2.3 **CVXPY 环境特化** (凸优化论文): 
    - 执行 `python scripts/cvxpy_env_setup.py --solver clarabel --paper-json analysis/paper_summary.json`
    - 安装 CVXPY + 推荐求解器 (clarabel/mosek/ecos/scs)
    - 验证求解器可用性: `python -c "import cvxpy; print(cvxpy.installed_solvers())"`
2.4 **确定性配置**: 固定随机种子 (torch/np/random/tf) + 浮点确定性 + `PYTHONHASHSEED`
2.5 **验证**: 基础导入测试 + 版本一致 + GPU 可用性 + 锁定

**G3**: 导入测试通过, 锁定文件已写入, GPU 可用/已降级。任一不满足→返回 2.4 修复。

---

### Phase 3: 基线验证 / Baseline Verification

**输入**: `analysis/paper_summary.json` + 就绪环境
**输出**: `results/baseline_metrics.json` + `results/tolerance_spec.json` + `analysis/gray_areas.md`

3.1 **运行官方代码**: 按 README 执行, 记录完整日志
3.2 **指标对齐**: 提取所有指标 → 对比论文声称值 → 设置容忍度 (数值 +/- 5%, 统计 95% CI, 趋势一致)
3.3 **基线失败处理**:
    - 环境诊断: 依赖缺失→pip list 对比; 版本冲突→conda env export; GPU 不可用→nvidia-smi
    - 代码修复: 仅最小改动 (import 路径/API 变更/Python 2/3); 不做功能扩展
    - 记录偏离到 `analysis/gray_areas.md` (环境/代码/参数偏离 + git diff + 参数假设)
    - 失败分支: bug 无法绕过→标记 `not_testable`; 环境不可重建→切 OS/容器; 基线不可建→输出完整诊断
3.4 **基线锁定**: commit SHA + 复现锁定 + `reproduction_manifest.json` 更新

**G4**: 基线指标已记录, tolerance_spec 已设定。基线未建立→用户决定是否继续进 Phase 4。

---

### Phase 4: 增量实现 / Incremental Implementation (按需)

**输入**: `analysis/paper_summary.json` + `results/baseline_metrics.json`
**输出**: `implementation/implementation_log.md` + `implementation/delta_report.json`

4.1 **模块拆解**: DAG 依赖图 + 每个模块的 I/O 接口 + 拓扑排序 → `implementation/modules_dag.json`
4.2 **增量循环** (按拓扑序):
    1. 实现当前模块 (标注论文公式/算法编号)
    2. 小规模测试: `python -c "from module import *; test_small()"`
    3. 对比基线: `python analysis/compare.py --module <name> --baseline results/baseline_metrics.json`
    4. 记录偏差到 `implementation/delta_report.json`
    5. delta 超容忍度→排查→修复→回到第 2 步
    6. 确认后 `git commit` → 记录到 `implementation_log.md` → 下一模块
4.3 **代码管理**: 每个模块独立 commit (含论文公式编号); 每个函数 docstring 写 `Ref: Section X.Y, Eq.(Z)`; 领域命名约定

---

### Phase 5: 实验验证与统计判决 / Experiment Execution & Verdict

**输入**: 可运行代码 + `results/tolerance_spec.json`
**输出**: `results/raw_metrics.csv` + `实验复刻结果汇总/实验报告/判决结果.json` + `实验复刻结果汇总/实验图表（含代码）/` (图 + 生成代码)

5.1 **多轮运行**: 确认参数 (基线可行? N=5 种子? 运行时间? GPU 启用?) → 每轮独立执行 → `raw_metrics.csv`
5.2 **统计计算**: 均值 x-bar + 标准差 s + 95% t-CI: x-bar +/- t*s/sqrt(N) → `statistical_summary.json`
5.3 **五态判决**: `within_ci`→OK / `close_outside_ci`→approx / `outside_tolerance`→FAIL / `not_testable`→WARN / `static_check_failed`→FAIL
5.4 **诊断输出**: >=2 条诊断假说 + Top-12 失败模式 + 引用审稿人视角发现 → `实验复刻结果汇总/实验报告/诊断分析.md` / `诊断分析-CN.md`
5.5 **图表+代码导出**:
    - 图形: 收敛曲线(convergence.png) / 指标对比(comparison.png) / 消融图(ablation.png) / 散点图/热力图
    - 格式: PNG (嵌入报告) + PDF (出版级)
    - 代码自包含: 每图附带独立可运行 `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py` (固定种子+对齐论文配色)
    - 验证: `python 实验复刻结果汇总/实验图表（含代码）/code/plot_convergence.py` → 输出一致
    - 产出: `实验复刻结果汇总/实验图表（含代码）/*.png/.pdf` + `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py`

**Top-12 失败模式**: 代码/数据缺失 | 环境漂移 | CUDA 冲突 | ABI 不兼容 | 依赖冲突 | 非确定性 | BLAS 变体 | 跨平台路径 | 数据泄露 | 预训练权重漂移 | 选择性报告 | 上游依赖位腐

**机器人路径优化特有失败模式**:
- 求解器数值问题 (MIP gap, tolerance)
- 离散化误差 (栅格/采样分辨率)
- 碰撞模型不匹配 (包围盒 vs 精确几何)
- 动力学简化 (微分平坦性假设)
- 地图/环境差异 (随机种子/障碍物分布)

---

### Phase 6: 双语报告生成 / Bilingual Report Generation

**输入**: 所有阶段产出
**输出**: `实验复刻结果汇总/` 中英双语文档（在论文所在目录下创建）

**确认所有数据就绪** → 判决/图表/三方审阅/路径一致 → 生成报告

在论文所在目录下创建 `实验复刻结果汇总/` 文件夹，内含三个子目录：

**文档清单**:
- `实验复刻结果汇总/实验报告/复现报告.md` -- 完整报告 (英文版，模板: templates/reproduction_report.template.md)
- `实验复刻结果汇总/实验报告/复现报告-CN.md` -- 完整报告 (中文版)
- `实验复刻结果汇总/实验报告/诊断分析.md` -- 诊断分析 (英文)
- `实验复刻结果汇总/实验报告/诊断分析-CN.md` -- 诊断分析 (中文)
- `实验复刻结果汇总/实验报告/运行摘要.md` -- 运行摘要 (英文)
- `实验复刻结果汇总/实验报告/运行摘要-CN.md` -- 运行摘要 (中文)
- `实验复刻结果汇总/实验报告/判决结果.json` -- 判决 JSON (中英双语字段)
- `实验复刻结果汇总/实验结果对比表/实验结果对比表.md` -- 对比表 (英文)
- `实验复刻结果汇总/实验结果对比表/实验结果对比表-CN.md` -- 对比表 (中文)
- `实验复刻结果汇总/实验图表（含代码）/*.png/.pdf` -- 实验图表
- `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py` -- 图表生成代码 (自包含, 可独立运行)

**格式**: 英文版 = `文件名.md`，中文版 = `文件名-CN.md`; 英文标题+中文标题; 表格列头 `Metric / 指标`; 数值统一精度; 图表标题 EN/ZH 标注

---

### Phase 7: 最终整理与完整性确认 / Final Consolidation & Integrity Check

**输入**: 所有阶段产物
**输出**: `实验复刻结果汇总/` 完整目录

7.1 **文件归位**: 确认所有阶段产物已按以下结构归位
     - `实验复刻结果汇总/实验报告/` — 双语报告 + 判决 JSON
     - `实验复刻结果汇总/实验图表（含代码）/` — 图表 PNG/PDF + 独立可运行源码
     - `实验复刻结果汇总/实验结果对比表/` — 双语对比表
     CHECKPOINT: 完整性确认 (所有文件就位/双语配对/图表代码齐全)
7.2 **一致性验证**: 对比 `判决结果.json` 与报告中的数值一致性，确认图表引用正确

---

## 门禁总表 / Gate Map

| Gate | 位置 | 条件 | 违反动作 |
|------|------|------|---------|
| G0 | Phase 0 -> 0.5 | infra_manifest.json + GPU 就绪 | 返回修复 |
| G00 | Phase 0.9 | GPU 框架检测通过或 CPU 降级 | 检查驱动 |
| G01 | Phase 1.4 -> 2 | reproducibility_assessment 决策 proceed | 用户介入 |
| G1 | Phase 0.5 -> 1 | 版本一致性通过 | 修复版本冲突 |
| G3 | Phase 2 -> 3 | 导入测试+锁定+GPU | 返回 2.4 |
| G4 | Phase 3 -> 4 | 基线指标记录+tolerance | 用户决策 |
| G5 | Phase 4 | 每个模块 delta 在预期内 | 排查修复 |
| G6 | Phase 5 | 五态判决产出 | 补跑统计 |
| G66 | Phase 5.5 | 有图表时每图有独立源码 | 补导出 |
| G7 | Phase 6 | 所有报告中英双语 (`.md` + `-CN.md`) | 补译 |
| G8 | Phase 7 | `实验复刻结果汇总/` 下所有文件就位 | 补缺文件 |

---

## 文件结构 / Directory Structure

```
math-read-do/
├── SKILL.md                     # 主 skill 入口
├── nature-reader/               # 子技能：论文阅读与结构化提取
│   ├── SKILL.md
│   ├── README.md
│   ├── manifest.yaml
│   ├── static/
│   │   ├── core/                # 核心原则、工作流、输出协议
│   │   └── fragments/source/    # 来源格式路由 (pdf-text/scanned-pdf/html/doi-arxiv/pasted-text)
│   └── references/              # 图提取、接地规则、输出规范、论文解剖
├── nature-figure/               # 子技能：出版级图表生成
│   ├── SKILL.md
│   ├── README.md
│   ├── manifest.yaml
│   ├── static/
│   │   ├── core/                # 核心契约、立场声明
│   │   └── fragments/backend/   # 后端选择 (python/r)
│   └── references/              # 图表契约、后端选择、设计理论、通用模式等
├── nature-paper2ppt/            # 子技能：论文→PPTX
│   ├── SKILL.md
│   ├── README.md
│   ├── manifest.yaml
│   ├── static/
│   │   ├── core/                # 原则、工具链、工作流、输出质量
│   │   └── fragments/paper_type/# 论文类型叙事弧 (discovery/methods/resource/clinical/materials/review)
│   └── references/              # 设计与布局、图表资产、自审校
├── _shared/                     # 共享层
│   ├── README.md
│   ├── core/                    # 伦理、论文类型分类、阅读工作流、术语账本
│   └── journal-formats/         # 期刊格式参考 (nat-comms)
├── skills/registry.yaml
├── scripts/            # 脚本 (PDF提取/三方审阅/图表导出等)
├── templates/          # 双语报告模板 (Jinja2)
├── schemas/            # 校验 JSON Schema
├── tests/              # 测试
├── infra/              # 基础设施 (manifest/Vagrantfile/Dockerfile/apptainer)
├── provisioning/       # 配置脚本 (ansible/版本管理器/CUDA/HPC)
├── env/                # 环境锁定 (version_spec/conda-lock/requirements/Manifest)
├── analysis/           # 论文分析 (summary/parsed/formulas/gray_areas/三视角审阅)
├── code/               # 代码 (Git repo)
├── logs/               # 运行日志
├── results/            # 实验 (baseline/tolerance/raw/stat)
├── implementation/     # 增量实现 (log/delta)
└── 实验复刻结果汇总/   # 最终输出 (在论文所在目录创建, 非本目录)
    ├── 实验报告/       # 双语复现报告 + 诊断 + 运行摘要 + 判决 JSON
    ├── 实验图表（含代码）/# 图表 PNG/PDF + 独立可运行源码
    └── 实验结果对比表/  # 双语实验结果对比表
```

## 依赖与配置 / Dependencies & Configuration

| 包 | 用途 | 安装 |
|---|------|------|
| mineru-open-sdk | PDF->Markdown (含公式/表格) | `pip install mineru-open-sdk` |
| pyyaml | MinerU 配置解析 | `pip install pyyaml` |

**首次配置**:
```bash
# MinerU token
mkdir -p ~/.mineru && echo "token: 'your-api-key'" > ~/.mineru/config.yaml
# 来源: https://mineru.net/apiManage/token
# 依赖安装
pip install mineru-open-sdk pyyaml
```

## 决策响应 / Decision Responses

| 操作 | EN | ZH |
|------|----|-----|
| 批准 | approve / ok / yes | 可以 / 好的 / 继续 / 同意 / 批准 |
| 修订 | revise | 修改 |
| 拒绝 | reject | 拒绝 |
| 跳过 | skip | 跳过 |

**风险分级**: 低(只读分析, 无需审批) / 中(运行前计划审批) / 高(逐条审批)

## 集成 Nature 子技能 / Integrated Nature Skills

本 skill 集成了三个独立的 Nature 子技能 (`nature-reader`, `nature-figure`, `nature-paper2ppt`) 和一个共享层 (`_shared/`)，它们位于 `math-read-do/` 目录下，可作为独立 skill 被调用，也可作为 Phase 1-6 的增强工具。

### 子技能路由

| 子技能 | 目录 | 入口文件 | 主要用途 |
|--------|------|---------|---------|
| nature-reader | `nature-reader/` | `SKILL.md` + `manifest.yaml` | 科研论文智能阅读、结构化提取、6种来源格式路由 |
| nature-figure | `nature-figure/` | `SKILL.md` + `manifest.yaml` | 出版级图表生成，Python/R 双后端，含 QA 循环 |
| nature-paper2ppt | `nature-paper2ppt/` | `SKILL.md` + `manifest.yaml` | 论文→中文 PPTX，6类论文叙事弧，自审校循环 |
| _shared | `_shared/` | 无入口，被子技能引用 | 术语账本、论文类型分类法、伦理规范、Nat Communs 格式 |

### 与主流程的协同

- **nature-reader** 可增强 Phase 1 (论文解析与视角审阅)，提供替代 PDF 解析策略和结构化输出格式。用户未指定审阅视角时，主动询问。
- **nature-figure** 可增强 Phase 5 (图表导出)，提供出版级图表样式和质量门禁。
- **nature-paper2ppt** 在 Phase 6 之后生成汇报 PPTX，将复现结果呈现为学术演示。

### 调用方式

每个子技能有独立的 `SKILL.md` + `manifest.yaml`，通过 load_skill 加载后自动读取对应的 static/fragments/references。子技能之间的共享内容通过 `_shared/` 目录引用，无需重复加载。

## 参考文献 / References

- MaRDI Mathematical Research Data Initiative. https://www.mardi4nfdi.de/
- ICERM Workshop on Reproducibility in Computational and Experimental Mathematics (2012)
- ConanXu-math/Scientific-Computing-Reproduction---Auto-Tuning
- OpenResearch. https://github.com/armaanamatya/openresearch
- paper-replay. https://github.com/bettyguo/paper-replay
- repro-agent. https://github.com/hqygtr-prog/repro-agent
- MaRDIFlow: A Workflow Framework for Documentation and Integration of FAIR Computational Experiments
- repo2docker. https://repo2docker.readthedocs.io/
- Apptainer. https://apptainer.org/
- nature-reader. https://github.com/Yuan1z0825/nature-skills
- nature-figure. https://github.com/Yuan1z0825/nature-skills
- nature-paper2ppt. https://github.com/Yuan1z0825/nature-skills

## 机器人路径优化参考 / Robotics Path Optimization References

- references/robotics_path_optimization.md — 路径优化论文复现参考手册（问题分类、算法模板、求解器对比、评估指标、常见陷阱）
  - 涵盖：凸优化路径规划 (FastPathPlanning, GCS)、基于搜索 (A*, RRT)、基于采样 (RRT*, BIT*)、基于学习、MPC
  - 求解器对比：CLARABEL, MOSEK, GUROBI, ECOS, SCS, OSQP
  - 评估指标：路径长度、规划时间、成功率、最优性差距、完备性
