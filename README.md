# Math-Read-Do-OBJ：通用 OBJ 输出实验复刻框架 + Nature 系列子技能

## 概述

**math-read-do-obj** 是一个面向"输出 .obj 文件"的计算机图形学/几何处理实验的标准化复刻框架，同时集成了多个 **nature-\*** 学术工具子技能（reader / figure / paper2ppt / framework）。

以 **QEM 网格简化** (Garland & Heckbert, SIGGRAPH 1997) 为首个内建范本，验证框架的通用性和正确性。

一句话：**输入 .obj + 算法规格 → 自动复现 → 输出简化 .obj + 双语对比报告**

## 分支特性（obj）

obj 分支 = 面向"输出 .obj 文件"的计算机图形学/几何处理实验的复刻落地形态：

- **qem_tool 工具链**：QEM 网格简化（Garland & Heckbert, SIGGRAPH 1997）纯 Python + NumPy 实现，CLI 支持 `--faces` / `--ratio` 两种简化模式与 `--info` 模型检查
- **对原始 C++ 实现的关键改进**：最优位置解 4×4 线性系统（论文 Eq.5）、增量 heapq O(log n)/步、标记-清理面删除 O(1)、法线加权平均重建、边界约束保护
- **验证 + 基准闭环**：`scripts/verify_qem.py`（支持 Hausdorff 距离检查）+ `scripts/benchmark_qem.py` 性能基准 + `tests/` 测试套件
- **多模型交叉验证**：区别于通用流程的多随机种子统计验证，本分支以多模型交叉对比作为正确性依据
- **网格语料清单（corpus/）**：`corpus/MANIFEST.json` 以 sha256 + 顶点/面数锚定 6 个实验网格（bs_rest / dragon_fat / capsule / spot / boxpart / spot_subdiv），`scripts/verify_corpus.py` 提供完整性校验（篡改/缺失即 FAIL）与 `--regen` 重生成
- **金样本回归测试（corpus/golden/）**：ICE（Intrinsic Error Metrics, SIGGRAPH 2023）18 个已验证稀疏矩阵（延拓/拉普拉斯/质量矩阵，标量与向量版）作为金样本；spot 系列 9 个入仓全量断言，dragon 系列 9 个按需启用（设 `ICE_GOLDEN_DRAGON_DIR` 指向本地矩阵目录，未设则 SKIP）；解析库 `corpus/spmat.py`
- **G9 发布前交叉校验门**：SKILL.md Phase 7 + 门禁总表——报告数字与验证产物逐格核对、表格标签行列双重核对、参数声称对账（含"输入数=目标数+移除数"自洽检查）；以 `EXPERIMENT_REPORT.md` 7 处手抄数字错误为登记回归案例
- **algos 插件化架构（RFC + 骨架）**：`docs/rfc/001-algos-registry.md`（registry schema、qem_tool→algos/qem 三阶段迁移、ICE adapter subprocess-wrapper 优先、金样本版本化）+ `algos/registry.yaml` 骨架（qem active + ice planned）——多算法基准平台的 E1/E2 设计依据

## 项目结构

```
math-read-do/
├── qem_tool/                # QEM 网格简化工具链
│   ├── cli.py               # CLI 入口
│   ├── qem_core.py          # QEM 算法引擎
│   └── obj_io.py            # 通用 .obj 解析/导出
├── corpus/                  # 网格语料清单 + 金样本矩阵
│   ├── MANIFEST.json        # 语料清单（sha256 锚定）
│   ├── spmat.py             # 稀疏矩阵解析库
│   └── golden/              # ICE 金样本（spot 入仓 + dragon 外部）
├── algos/                   # 算法插件注册表骨架
│   └── registry.yaml        # qem(active) + ice(planned)
├── docs/
│   └── rfc/                 # RFC（001: algos 插件化注册表）
├── nature-reader/           # 学术论文阅读与提取
├── nature-figure/           # 论文配图制作 (matplotlib/seaborn → PDF/SVG)
├── nature-paper2ppt/        # 论文转演示文稿
├── nature-archify/        # 系统架构/流程/时序/数据流图渲染引擎
├── _shared/                 # 共享核心模块（伦理/术语/工作流）
├── tests/                   # 测试套件
├── scripts/                 # 验证 + 基准 + 语料校验
├── templates/               # 报告模板
└── results/                 # 运行结果
```

## 内建算法：QEM 网格简化

Quadric Error Metric (QEM) — 经典边收缩网格简化算法。

**对比原始 C++ 实现的优化项**：

| 优化项 | 原始 C++ | 本实现 |
|--------|---------|--------|
| 最优位置 | 中点 (v1+v2)/2 | 解 4×4 线性系统 (论文 Eq.5) |
| 堆管理 | 全重建 O(n log n)/步 | 增量 heapq O(log n)/步 |
| 面删除 | O(n²) 遍历 + 迭代器失效 | 标记-清理 O(1) |
| 法线导出 | ❌ 无 | ✅ 加权平均重建 |
| 边界保护 | ❌ 无 | ✅ 约束优化 |
| 编译依赖 | OpenGL + GLFW + SDL2 | 纯 Python + NumPy |
| 参数化 | 硬编码宏 | CLI 参数 (`--faces`/`--ratio`) |

## 快速开始

### QEM 网格简化

```bash
# 查看模型信息
python -m qem_tool.cli -i model.obj --info

# 简化到指定面数
python -m qem_tool.cli -i model.obj -o simplified.obj -f 2000

# 按比例简化
python -m qem_tool.cli -i model.obj -o simplified.obj -r 0.1

# 运行全部测试
python -m pytest tests/ -v

# 验证简化质量
python scripts/verify_qem.py -i model.obj -f 2000 --check-hausdorff

# 性能基准测试
python scripts/benchmark_qem.py -i model.obj
```

### 网格语料与金样本测试

```bash
# 校验网格语料清单（MANIFEST.json 对照 sha256/顶点/面数；篡改或缺失即 FAIL）
python scripts/verify_corpus.py --mesh-dir <meshes_dir>
python scripts/verify_corpus.py --regen --mesh-dir <meshes_dir>   # 重生成 MANIFEST

# 金样本矩阵回归测试（spot 9 矩阵全量断言；dragon 9 矩阵未设目录时 SKIP）
python -m pytest tests/test_golden_matrices.py -v
```

dragon 系列金样本不入仓（体积原因）。如本地已有矩阵目录（来源：obj_exp
`ICE_Experiment_Logs/matrices/`，快照 `ICE_Experiment_Logs.7z`），设置环境变量后
测试自动启用其全量校验（sha256/维度/nnz/统计值/数值性质）：

```bash
# PowerShell
$env:ICE_GOLDEN_DRAGON_DIR = "<path/to/matrices>"; python -m pytest tests/test_golden_matrices.py -v

# bash
ICE_GOLDEN_DRAGON_DIR=<path/to/matrices> python -m pytest tests/test_golden_matrices.py -v
```

各矩阵性质断言与已知现象（dragon 向量延拓行偏差 ≈8.9e-2、上游空行 HACK 等）见
`corpus/golden/README.md`；发布前请走 SKILL.md Phase 7 的 G9 交叉校验门。

### Nature 系列子技能

| 子技能 | 功能 | 入口 |
|--------|------|------|
| nature-reader | 学术论文阅读、提取、结构化 | `nature-reader/SKILL.md` |
| nature-figure | 论文配图制作（结果图/示意图/多面板） | `nature-figure/SKILL.md` |
| nature-paper2ppt | 论文转演示文稿 | `nature-paper2ppt/SKILL.md` |
| nature-archify | 系统架构/流程/时序/数据流/生命周期图渲染（16 条命令：doctor/guide/demo/出图三步 render·validate·deliver + visual-check/compare/migrate/brands 等；接受 Mermaid 素材、支持架构 delta 对比） | `nature-archify/SKILL.md` |

## 依赖

| 包 | 用途 | 必要 |
|----|------|------|
| numpy | 矩阵运算 (QEM) + 金样本断言 | ✅ |
| pytest | 测试运行 | ❌ (推荐) |
| PyYAML | `algos/registry.yaml` 解析 | ❌ (推荐) |
| matplotlib | 可视化 | ❌ (可选) |

## Nature 子技能依赖

| 子技能 | 核心依赖 |
|--------|---------|
| nature-figure | matplotlib, seaborn |
| nature-paper2ppt | python-pptx |
| nature-reader | mineru-open-sdk |
| nature-archify | Node.js (mjs 渲染器) |

**Phase 1.6 辅助架构图征询**：论文阅读完成后必须主动征询是否制作架构图，用户同意后强制 6 项逐项询问（主题/图类型/图语言/动效模式/视觉风格/输出格式），不重复提问。

## 与 math-read-do 的关系

| 维度 | math-read-do | math-read-do-obj |
|------|-------------|-----------------|
| 领域 | 通用数学论文复现 | OBJ 输出图形学实验 + Nature 学术工具 |
| 算法获取 | PDF → MinerU → 理解 | 直接算法理解（跳过 PDF） |
| 输入 | PDF 论文链接 | .obj 文件 / 论文 / 架构 JSON |
| 验证 | 多随机种子统计 | 多模型交叉验证 |
| 核心依赖 | mineru-open-sdk | numpy |

## 性能优化记录（2026-10-09）

### P0（关键修复）
- **G1**: QEM O(F2) 消除 -> 增量邻接 O(deg)，6400 面 4.4s->0.565s（提速 8x）
- **H2**: preserve_boundary 参数失效修复
- **E2/E3**: 门禁统一 + 五态判决枚举统一

### P1（高价值优化）
- **G2**: Hausdorff 向量化（scipy.cKDTree），5.3x 提速
- **H5**: obj_io 错误路径校验（ValueError + 行号）
- **F1**: SKILL.md 外移低频道到 references/（-31.5%）

### P2（一致性收敛）
- **G3**: benchmark 复用 simplifier 实例
- **G10**: _compute_all_quadrics 向量化（numpy 批量）
- **H6/H7**: dragon 金样本文档化 + corpus 标准几何体入库

### 测试：90 passed, 9 skipped

## WSL 环境自动检测 + 评测框架同步

- **新增 `scripts/detect_wsl.sh`**: 实验复现时自动检测用户是否已有 WSL 且 Linux 环境已配置好（Python3 + numpy + scipy）。若已配置好 → 使用 WSL Linux 进行复现；否则 → 在当前系统直接运行。不强制安装 WSL。
- **环境管理工具检测**: 优先检测 UV（`uv venv` + `uv pip install`），UV 不好处理的情况检测 conda 兜底。输出 `env_manager` 字段（`uv`/`conda`/`none`）。
- **SKILL.md Phase 0.0**: 新增"环境选择 / Environment Selection"步骤，在 Phase 0 之前执行平台选择。
- **`_shared/eval/` 同步**: 评测框架（grader.py + metrics_collector.py + test-prompts.json + __init__.py）已同步到所有分支。

## 实验复现规范（全平台适用）

- **目录结构**: 初次使用 `mkdir -p ~/projects`（Windows 下 `~` = `C:\Users\<username>\`），每个实验单独一个文件夹 `~/projects/<experiment-name>/`，后续所有实验均放在 `~/projects/` 目录下
- **环境隔离**: 每个实验单独一个环境，以实验名命名。UV: `uv venv ~/projects/<exp>/.venv`；conda: `conda create -n <exp> python=3.x`
- **全程留痕**: 实验目录下保留 `code/`（代码脚本）、`logs/`（实验日志）、`logs/errors/`（报错记录）、`results/`（结果）、`env/`（环境锁定）、`README.md`（实验说明）
- **detect_wsl.sh 增强**: 新增 `projects_dir` 和 `projects_exists` 字段，检测 `~/projects` 目录是否已存在

## 许可

MIT
