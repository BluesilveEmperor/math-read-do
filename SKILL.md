---
name: math-read-do-obj
description: >-
  通用 OBJ 输出实验复刻工作流 / General-Purpose OBJ Experiment Reproduction Pipeline
  
  以 Surface Simplification Using Quadric Error Metrics 为设计范本，
  构建面向"任意输出 .obj 文件的图形学/几何处理实验"的标准化复刻框架。
  
  框架结构：
    Phase 0-3: 通用层 — 基础设施、版本管理、算法理解、环境构建
    Phase 4:   适配层 — 按目标算法 DAG 拓扑序增量实现
    Phase 5-6: 验证层 — 多模型交叉验证、Hausdorff 距离、退化面/重复面检测
    Phase 7:   收口层 — 发布前交叉校验门 G9（报告数字与验证产物逐格核对）
  
  当前内建算法示例：Quadric Error Metric (QEM) 边收缩简化
    Ref: Garland & Heckbert, SIGGRAPH 1997
  工具链：.obj I/O 解析器 + QEM 简化引擎 + CLI 命令行

  集成四大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：科研数据可视化顾问（先思考后绘制，8 步工作流，视觉自检闭环）
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)
  - nature-archify/：系统架构图渲染器（5 类图 architecture/workflow/sequence/dataflow/lifecycle，13 视觉预设，9 项 showcase 校验，self-contained inline-SVG HTML）；与 nature-figure 形成互补——本子技能专做系统/流程/时序/数据流架构图，nature-figure 专做数据可视化图

  Triggers / 触发词:
  OBJ, .obj, 网格简化, mesh simplification, QEM, quadric error metrics,
  表面简化, surface simplification, 模型减面, model decimation,
  多边形缩减, polygon reduction, 边收缩算法, edge collapse,
  网格抽取, mesh decimation, LOD 生成, level of detail,
  3D 模型, 3D model, 三角网格, triangle mesh,
  Garland Heckbert, 二次误差度量, 实验复刻, 复现实验,
  reproduce experiment, 图形学复现, graphics reproduction

compatibility:
  - python >= 3.9
  - numpy >= 1.21
  - 推荐: pytest (测试), matplotlib (可视化), meshlab (对比验证)
  - nature-reader: python-pptx, Pillow (图提取), PyMuPDF (PDF渲染)
  - nature-figure: matplotlib + seaborn + SciencePlots (静态) + plotly (交互)，CJK 字体自动配置
  - nature-paper2ppt: python-pptx, PyMuPDF, Pillow, zipfile
  - nature-archify: Node.js >= 18（CLI: nature-archify/bin/archify.mjs；零外部依赖）；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体，离线可打印；Python 桥接：scripts/nature_archify_bridge.py
---

# General OBJ Experiment Reproduction Framework
# 通用 OBJ 输出实验复刻框架

## 自动更新 / Auto-Update

**每次调用该 Skill 前，自动执行以下步骤：**

1. 运行 `scripts/auto_update.sh`
2. 脚本检测远程仓库 `https://github.com/BluesilveEmperor/math-read-do` 的 `math-read-do-obj` 分支
3. **代码同步**：
   - 尚未初始化 Git → 自动 `git init` + 添加 remote + fetch 最新代码
   - 已有 Git 仓库 → fetch + 快速前进合并 (ff-only) 更新
   - 本地有未提交修改 → 自动 stash → 更新后 pop 恢复
4. **无网络降级**：远程不可达 → 跳过更新，继续使用本地代码

> **注意**：该更新仅同步框架基础设施（SKILL.md、模板、脚本、测试夹具等），
> 不覆盖 `qem_tool/` 下的算法定制代码（此类变动会通过 git 冲突机制提示手动合并）。

**自动执行的 Shell 命令（封装在 `scripts/auto_update.sh` 中）：**

```bash
# 1. 检测网络 ⇨ 选最快源
# 2. git fetch --depth=1 <selected_repo>
# 3. git merge --ff-only (或 rebase 回退)
# 4. 恢复本地修改 (stash pop)
```

---

## 设计理念 / Design Philosophy

本框架的**核心洞察**：大量计算机图形学、几何处理、计算几何领域的实验的输出产物是 `.obj` 文件。与传统数学论文复现（需要 PDF 解析、公式理解、数值验证）不同，这类实验有如下特点：

| 特点 | 含义 |
|------|------|
| **输入明确** | 输入往往是标准 .obj 文件（结构化良好） |
| **算法可拆解** | 增量实现可按 DAG 拓扑序逐个模块独立验证 |
| **产物可对比** | 输出的 .obj 可直接 diff（顶点数、面数、Hausdorff 距离） |
| **无需 PDF 解析** | 算法已知，Phase 1 直接做算法理解而非 PDF 解析 |

因此本框架设计为 **"轻量级算法复现"**：跳过 PDF 解析和环境复杂性，聚焦算法的正确性实现和增量优化。

### 框架 vs 范本

```
math-read-do-obj/
├── 框架层 (Framework Core)              # 通用 .obj 实验复现流程
│   ├── Phase 0-3 / 5-6                 # 通用阶段（环境/理解/验证/报告）
│   ├── qem_tool/obj_io.py             # 通用 .obj 解析/导出层
│   └── templates/                      # 可复用报告模板
│
└── 范本层 (Exemplar: QEM)              # 第一个内建示例算法
    ├── qem_tool/qem_core.py           # QEM 简化算法实现
    ├── qem_tool/cli.py                # QEM CLI 入口
    └── tests/                          # QEM 专属测试 + 验证脚本
```

**未来扩展方式**：替换 `qem_tool/qem_core.py` 和 `qem_tool/cli.py`，即可适配任意新的 .obj 输出算法（如网格参数化、变形、布尔运算等）。

---

## 交互规则 / Interaction Rules

### Pre-flight：自动更新

每次执行任何操作前，**先自动运行** `scripts/auto_update.sh`：
- 检测 GitHub / GitCode 网络连通性
- 选择最快远程仓库
- 拉取最新代码（无网络则跳过）

更新完成后，才进入用户交互阶段。

### 用户交互规则

用户未输入具体操作指令时，**不允许默认执行任何操作**。必须主动向用户提问，列出可执行的操作选项，等待用户选择后执行。

> **提问前提示**：如果上方自动更新拉取了新代码，应在提问模板下附加一行：
> ```
> 💡 检测到新版本更新（YYYY-MM-DD HH:MM），建议先查看更新内容。
> ```

**标准提问模板**:
```
请选择操作类型：

=== 框架通用操作 ===
1️⃣ 算法理解 — 分析目标算法的输入/输出/公式/流程
2️⃣ 简化模型 — 对 .obj 文件执行简化，输出简化后模型
3️⃣ 查看信息 — 显示 .obj 模型的顶点/面数/包围盒信息
4️⃣ 验证结果 — 验证 .obj 输出正确性（退化面/重复面/Hausdorff距离）
5️⃣ 性能基准 — 对 .obj 文件做多个参数的性能测试

=== 完整复现流程 ===
6️⃣ 完整复现 — 启动完整实验复现流水线（Phase 0→6）

=== 当前内建算法 ===
  当前加载: Quadric Error Metric (QEM) 网格简化
  算法参考: Garland & Heckbert, SIGGRAPH 1997
```

用户做出选择后，按对应流程执行。

---

## 核心原则 / Core Principles

0. **自动更新**: 每次使用前自动检测网络、选择最快镜像、拉取最新框架代码（`scripts/auto_update.sh`）
1. **双语输出**: 所有报告必有中英双版本 (`.md` + `-CN.md`)
2. **增量验证**: 每添加一个模块即验证一次（`pytest test_module.py`）
3. **可审计**: 每步产生结构化产物，溯源链完整
4. **先问后做**: 用户无指令时先主动提问，确认操作后再执行
5. **.obj 产物即契约**: 输出的 .obj 文件是"可执行规格"—— 输入 → 算法 → 输出的 .obj 自证正确性

---

## 通用反模式 / Anti-Patterns & Blacklist

8 项通用反模式（单模型验证/仅视觉判断/忽略退化面/编码/中点替代/法线缺失/索引基混淆/参数不记录）及后果与正确做法详见 [references/anti_patterns.md](references/anti_patterns.md)。

---

## QEM 验证反模式 / QEM-Specific Anti-Patterns

7 项源自原始 C++ 实现的问题（索引排序 bug/中点替代/堆重建/迭代器失效/无法线/无边界保护/硬编码）及本框架修复详见 [references/anti_patterns.md](references/anti_patterns.md)。

---

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| **Δ-1** | **自动更新** — 检测网络、选最快镜像、拉取框架代码 | `git log -1` 显示最新提交 | **GΔ**: 网络可达时同步至最新 |
| 0 | 宿主检测 + 环境构建 | `infra/infra_manifest.json` | G0: Python+NumPy 就绪 |
| 0.5 | 版本检测 + 锁定 | `env/version_spec.json` | G1: 版本一致 |
| 1 | 算法理解 + 关键提取 | `analysis/algorithm_summary.json` | G01: 算法理解确认 |
| 2 | 依赖环境构建 | `env/` | G2: 导入测试通过 |
| 3 | 基线验证 | `results/baseline_metrics.json` | G4: 基线对齐 |
| 4 | 增量模块实现 (DAG 拓扑序) | `implementation/delta_report.json` | G5: 每模块 delta 验证 |
| 5 | 多模型统计验证 | `results/statistical_summary.json` | G6: 判决产出 |
| 6 | 双语报告生成 | `实验复刻结果汇总/` | G7: 各子实验目录完整，OBJ模型归位 |
| **7** | **发布前交叉校验与收口** | 逐格核对记录（附于报告或 `results/`） | **G9**: 报告数字与验证产物零不一致 |

---

## 门禁总表 / Gate Map

> **说明**：obj 分支门禁编号已与 routine/main 分支统一。Phase 3–6 的门禁经重编号（原 G3→G4, G4→G5, G5→G6, G6→G7），使同一语义门禁跨分支编号一致。

| Gate | 所属阶段 | 检查项摘要 | 失败动作 |
|------|---------|-----------|---------|
| GΔ | Phase Δ-1 自动更新 | 网络可达时同步至最新 | 静默跳过，不阻塞流程 |
| G0 | Phase 0 宿主检测 | Python+NumPy 就绪 | 返回修复 manifest/环境 |
| G1 | Phase 0.5 版本检测 | 版本一致性通过 | 修复版本冲突后继续 |
| G01 | Phase 1 算法理解 | 算法理解确认 | 用户介入确认 |
| G2 | Phase 2 依赖环境 | 导入测试通过 | 返回修复依赖/环境 |
| G4 | Phase 3 基线验证 | 基线指标记录+容忍度设定 | 用户决策是否继续 |
| G5 | Phase 4 增量实现 | 每模块 delta 验证通过 | 排查修复后重跑 |
| G6 | Phase 5 统计判决 | 五态判决产出 | 补跑统计验证 |
| G7 | Phase 6 双语报告 | 各子实验目录完整，OBJ模型归位 | 补缺文件/补译 |
| **G9** | Phase 7（发布前交叉校验与收口） | ① 报告数字与验证产物逐格核对，零不一致方可交付；② 对比表格算法标签行列双重核对；③ 参数声称对账（CLI 实际 vs 报告声称 + 数据自洽） | 回到 Phase 6 修正报告，修正后重新走查 G9 |

G9 检查项语义与 routine 分支 G9 保持一致（纯文档级门禁，无配套脚本），并已适配 obj 分支产物体系（`verify_qem.py`/`benchmark_qem.py` 原始输出、`corpus/MANIFEST.json`、`corpus/golden/checksums.json`、双语对比表格模板）。完整检查清单与回归案例见 [Phase 7](#phase-7-发布前交叉校验与收口--pre-release-cross-check--wrap-up)。

---

## 阶段详述 / Phase Detail

### Phase Δ-1: 自动更新 / Auto-Update

**始终在 Skill 流程入口自动执行**，不接受用户干预（除非网络不可用而静默跳过）。

**输入**: 当前本地代码
**输出**: 同步后的最新代码（或本地不变）

Δ.1 **网络检测**:
    - 同时探测 `github.com` 和 `gitcode.com` 连通性 (connect-timeout 3s)
    - 优先选择响应最快的仓库地址

Δ.2 **Git 同步**:
    - 无 `.git` → `git init` + 添加 remote + fetch 最新代码
    - 已有 `.git` → `git fetch --depth=1` + `git merge --ff-only`
    - 本地有未提交修改 → stash → 更新 → stash pop

Δ.3 **失败处理**:
    - 所有远程不可达 → 跳过，`echo` 提示
    - fetch/merge/rebase 失败 → 自动回退，不阻塞流程

**GΔ**: 网络可达时成功同步远程最新版本；网络不可达时静默跳过。

**实现文件**: `scripts/auto_update.sh`

---

### Phase 0: 基础设施检测 / Infrastructure Detection

**输入**: 宿主操作系统信息
**输出**: `infra/infra_manifest.json`

0.1 **宿主检测**:
    - `python --version` → Python >= 3.9
    - `python -c "import numpy; print(numpy.__version__)"` → >= 1.21
    - 磁盘剩余空间: 至少 100MB
    - 可选: `matplotlib` / `meshlab` 用于可视化对比

0.2 **环境构建**:
    - 路径 A: `pip install numpy`
    - 路径 B: `python -m venv .venv && pip install numpy`

**G0**: `python -c "from qem_tool.obj_io import load_obj; print('OK')"` 无误

---

### Phase 0.5: 版本管理 / Version Management

**输入**: `infra/infra_manifest.json`
**输出**: `env/version_spec.json`

0.5.1 **需求检测**: 扫描 `.python-version` / `pyproject.toml` / 算法特定版本线索
0.5.2 **版本锁定**:
    ```json
    {"python": ">=3.9", "numpy": ">=1.21", "algorithm": "QEM v1.0"}
    ```
0.5.3 **一致性验证**: `python --version` vs `version_spec.json`

**G1**: 所有运行时版本与 `version_spec.json` 一致

---

### Phase 1: 算法理解 / Algorithm Understanding

**输入**: 目标算法论文 + 参考实现代码（如有）
**输出**: `analysis/algorithm_summary.json`

1.1 **代码/论文分析**:
    - 读取原始实现（QEM 则为 `MeshSimplification.cpp`）
    - 理解核心数据结构和算法流程
    - 标记实现中的已知缺陷/bug

1.2 **关键公式提取**: 提取算法核心方程，标记论文中的 Eq. 编号

1.3 **I/O 接口定义**:
    ```
    Input:  .obj 文件 (顶点 + 面 + 可选纹理/法线)
    Params: 目标面数 / 简化比 / 边界保护开关 / ...
    Output: 简化后的 .obj 文件 (顶点 + 面 + 重建法线)
    ```

1.4 **问题标记**: 列出参考实现中已知的 bug / 性能瓶颈 / 功能缺失

**G01**: `analysis/algorithm_summary.json` 完成，用户确认算法理解无误

1.5 **nature-archify 参与（算法理解阶段，可选）**: 理解确认后可用 nature-archify 绘制不依赖实验数据的系统与流程图——`architecture` 系统架构图、`workflow` 技术流程图、`sequence` 调用时序图、`dataflow` 数据流图、`lifecycle` 状态机图（预计版；五类图都不承载实验数值）。执行前遵守 nature-archify 第 0 步必问。

### 1.6 辅助架构图征询（可选但必须询问） / Auxiliary Architecture Diagram Offer

1.5 完成后必须主动征询是否制作 Nature 级研究框架图/技术路线图；用户同意后强制 6 项逐项询问（主题/图类型/图语言/动画模式/视觉预设/输出格式），再按 nature-archify 第 0→5 步执行。图类型可用矩阵（architecture/workflow/sequence/dataflow/lifecycle 五类，均不需实验数据）及完整约束详见 [references/archify_diagram_offer.md](references/archify_diagram_offer.md)。

---

### Phase 2: 环境构建 / Environment Setup

**输入**: `analysis/algorithm_summary.json`
**输出**: `env/` 锁定文件

2.1 **依赖扫描**: 识别算法所需的 Python 包
    - 核心依赖: `numpy`（矩阵运算）
    - 测试依赖: `pytest`
    - 可视化: `matplotlib`（可选）

2.2 **环境构建**: `pip install -r requirements.txt`

2.3 **确定性配置**: 固定随机种子（如算法涉及随机性）

2.4 **验证**: 导入测试通过，`python -c "from qem_tool.cli import main"` 无误

**G2**: 导入测试通过

---

### Phase 3: 基线验证 / Baseline Verification

**输入**: `analysis/algorithm_summary.json` + 就绪环境
**输出**: `results/baseline_metrics.json` + `analysis/gray_areas.md`

3.1 **运行参考实现**:
    - 原 C++ 项目编译运行（如可行）
    - 或使用已有输出产物作为基线
    - 或使用第三方参考实现（如 MeshLab 的 QEM filter）

3.2 **运行本框架实现做对比**:
    ```bash
    python -m qem_tool.cli --input baseline_test.obj --output test_out.obj --faces 1000
    ```

3.3 **指标对齐**（通用 OBJ 对比指标）:

| 指标 | 说明 |
|------|------|
| 输出面数 | 精确等于目标值（或 ≤ 目标值） |
| 顶点坐标差异 | L2 距离 < 0.1% of bbox 对角线 |
| Hausdorff 距离 | < 0.5% of bbox 对角线 |
| 面拓扑对称差 | 边集差异 < 5% |
| 退化面率 | < 0.1% |
| 重复面率 | < 0.01% |

3.4 **基线失败处理**:
    - 参考实现不可用 → 记录 `not_testable`，用第三方参考
    - 输出偏差 > 容忍度 → 记录到 `analysis/gray_areas.md`，标记待修复

3.5 **基线锁定**: commit `baseline_metrics.json`，确认容忍度设置

**G4**: 基线指标记录，容忍度设定。基线不可建→用户决定是否继续 Phase 4

---

### Phase 4: 增量实现 / Incremental Implementation

**输入**: `analysis/algorithm_summary.json` + `results/baseline_metrics.json`
**输出**: `implementation/implementation_log.md` + `implementation/delta_report.json`

4.1 **模块拆解**: DAG 依赖图 + 每个模块的 I/O 接口

    **QEM 示例 DAG**:
    ```
    obj_io.py: 解析/导出 ← 无依赖（可最先实现）
    qem_core.py: Q 矩阵计算 ← obj_io 提供顶点/面数据
    qem_core.py: 边收缩 + 堆管理 ← Q 矩阵计算
    qem_core.py: 边界保护 ← 边收缩
    cli.py: 管线集成 ← 所有模块
    ```

4.2 **增量循环** (按 DAG 拓扑序):
    1. 实现当前模块（标注论文公式/算法编号）
    2. 小规模测试: `pytest tests/test_module.py -v`
    3. 对比基线: delta 是否在容忍度内？
    4. 记录偏差到 `implementation/delta_report.json`
    5. delta 超容忍度→排查→修复→回到第 2 步
    6. 确认后→下一模块

4.3 **代码管理**:
    - 每个模块独立 commit（含参考文献引用）
    - 函数 docstring 标注 `Ref: Section X.Y, Eq.(Z)`
    - 按领域命名约定

**G5**: 所有模块实现并通过 delta 验证，`delta_report.json` 完整

---

### Phase 5: 统计验证 / Statistical Verification

**输入**: 可运行工具链 + `results/tolerance_spec.json`
**输出**: `results/statistical_summary.json` + 图表

5.1 **多模型交叉验证**: （QEM 是确定性算法 → 不需要随机种子，但需要多模型）

| 测试模型 | 几何特征 | 测试目的 |
|----------|--------|----------|
| `cube.obj` (12 面) | 平面+尖锐边 | 边界保持、平面简化极限 |
| `tetrahedron.obj` (4 面) | 极简网格 | 最小退化测试 |
| `sphere.obj` (low-poly) | 曲面 | 曲面简化质量 |
| `bunny.obj` (Stanford) | 复杂形状 | 通用质量 |
| user-provided | 用户输入 | 自定义 |

> **外部测试网格获取**：`cube/tetrahedron/sphere` 已内置于 `tests/fixtures`。
> `bunny.obj` 需从 Stanford 3D Scanning Repository 下载：
> `wget http://graphics.stanford.edu/pub/3DScanpoint/bunny.tar.gz`（解压后取 `bun_zipper.res2`）。
> **dragon 系列金样本矩阵**（9 个 `.spmat`，intrinsic-simplification 实验导出）未入库，
> 仅校验和登记于 `corpus/golden/checksums.json`；获取后设置环境变量
> `ICE_GOLDEN_DRAGON_DIR` 指向 `.spmat` 所在目录即可启用全量校验，详见
> `corpus/golden/README.md`「dragon 系列获取与用法」。对应输入网格 `dragon_fat.obj`
> 见 `corpus/MANIFEST.json`。

5.2 **多参数测试**: 每个模型测试多个参数值（QEM: 50%, 20%, 10%, 5%, 1%）

5.3 **输出指标**:
    - 面数精确度、Hausdorff 距离（归一化）、退化面率、重复面率
    - 处理速率 (faces/sec)、QEM 误差分布（最小/最大/均值/中位数）

5.4 **五态判决**（统一枚举）: `pass` → 通过 / `approx` → 近似通过 / `within_ci` → 置信区间内 / `fail` → 不通过 / `skip` → 跳过（旧 within_tolerance→pass, close_outside→approx, outside→fail）

5.5 **图表导出**（可选，每图必须附带 Python + LaTeX 双版本生成代码）:
    - 简化前后对比图 (comparison.png + 可选 comparison.pdf)
    - 误差分布直方图 (error_distribution.png + 可选 error_distribution.pdf)
    - 每图附带独立可运行生成代码: Python (`plot_*.py`) + LaTeX/TikZ (`plot_*.tex`)

5.6 **架构/流程图导出**（可选，走 nature-archify）: 数据图表走 nature-figure；系统架构/技术流程/调用时序/数据流/状态机图一律经 nature-archify 渲染。注意：`experiment` 实验流程图（PRISMA/CONSORT 等，需真实样本量与排除数）**不在 nature-archify 的五类图内**，需要时另行接入 paperfig 类渲染器。

**G6**: 判决产出，所有验证通过

---

### Phase 6: 报告生成 / Report Generation

**输入**: 所有阶段产物
**输出**: `实验复刻结果汇总/` 中英双语文档

**nature-archify 参与（报告插图）**: 报告中的系统架构图/技术流程图/时序图/数据流图/状态机图由 nature-archify 产出（self-contained inline-SVG HTML，可加 trace 动效；13 种视觉预设）；实验流程图不在其图类型内，另行接入 paperfig 类渲染器。

报告输出到 `实验复刻结果汇总/`，按子实验（`<模型名>_<参数标记>`）拆分，每个子实验含 `OBJ模型/`/`实验报告/`（双语 + 判决 JSON）/`实验结果对比表/`/`实验图表（含代码）/`，根下 `总览/` 提供跨实验汇总。完整目录树与命名规范详见 [references/report_directory_layout.md](references/report_directory_layout.md)。

**G7**: 每个子实验的目录结构完整，.obj 模型存放于各子实验的 `OBJ模型/` 文件夹内，`总览/` 提供跨实验汇总

---

### Phase 7: 发布前交叉校验与收口 / Pre-Release Cross-Check & Wrap-Up

**输入**: `实验复刻结果汇总/` 双语报告 + 全部验证产物
**输出**: 逐格核对记录（附于报告修订记录或 `results/`），零不一致后交付

Phase 6 产出报告后、对外交付前，必须走一遍 G9 交叉校验。这一步针对的是**同一类事故**：把脚本/日志里的数字手抄进报告时的错位、漏改与误读——手工转录永远是最脆弱的一环。

G9 包含三项核对：7.1 报告数字与验证产物逐格核对（`verify_qem.py`/`benchmark_qem.py` 原始输出、`corpus/MANIFEST.json`、`corpus/golden/checksums.json` 为机械出处）、7.2 对比表格算法标签行列双重核对、7.3 参数声称对账（CLI 实际 vs 报告声称 + 数据自洽）；任一不一致则回 Phase 6 修正后重新完整走查。7.1-7.4 详述及 G9 回归案例（EXPERIMENT_REPORT.md 7 处数字错误）详见 [references/g9_cross_check_detail.md](references/g9_cross_check_detail.md)。

**G9**: 报告数字与验证产物逐格核对零不一致、表格标签行列双重核对通过、参数声称对账通过。

---

## 文件结构 / Directory Structure

框架由 `qem_tool/`（算法工具链）、`tests/`、`scripts/`、`templates/` 及产物目录（`results/`/`analysis/`/`implementation/`/`infra/`/`env/`）组成；`obj_io.py` 为通用 .obj 解析层，`qem_core.py`/`cli.py` 为可替换的范本。完整目录树详见 [references/directory_structure.md](references/directory_structure.md)。

## 适配新算法 / Adapting to a New Algorithm

适配新 .obj 输出算法只需替换三个范本文件（`qem_core.py`/`cli.py`/`test_qem_core.py`），框架层无需改动。完整步骤表详见 [references/adaptation_and_relationship.md](references/adaptation_and_relationship.md)。

---

## 与 math-read-do 的关系 / Relationship to math-read-do

math-read-do-obj 是 math-read-do 在 OBJ 图形学实验方向的特化（目标/Phase 1/输入/Phase 5/核心依赖/输出/典型用户 7 个维度对比）。完整对比表详见 [references/adaptation_and_relationship.md](references/adaptation_and_relationship.md)。

---

## 参考文献 / References

- Garland, M., & Heckbert, P. S. (1997). Surface simplification using quadric error metrics. SIGGRAPH '97.
- Original C++: `E:\1.Surface Simplification Using Quadric Error Metrics\`
- MeshLab: Quadric Edge Collapse Decimation filter
- math-read-do: `D:\Desktop\math-read-do\`
