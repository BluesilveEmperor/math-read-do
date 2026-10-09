---
name: math-read-do
description: >-
  数学文献实验复现标准化工作流 / Standardized Math Paper Reproduction Pipeline
  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析(含公式/表格/图表) →
  按用户指定视角输出审阅报告(研究生/导师/审稿人) →
  环境重建 → 基线验证 → 增量实现 → 统计验证(五态判决+95%CI) → 双语报告。
  覆盖数学全领域：纯数学、应用数学、统计学、运筹学、计算数学、AI4Math等。每份报告必须中英双语。

  集成四大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：出版级图表生成 (Python/R, Nature/CNS 风格)
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)
  - nature-archify/：系统架构图渲染器（5 类图 architecture/workflow/sequence/dataflow/lifecycle，13 视觉预设，9 项 showcase 校验，self-contained inline-SVG HTML）；与 nature-figure 形成互补——本子技能专做系统/流程/时序/数据流架构图，nature-figure 专做数据可视化图

  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现,
  重现论文, 论文重现, 数值复现, 论文复现, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 重现结果, 重现图表, 复现结果, 复现图表,
  reproducibility check, 可复现性评估, 复现验证,
  T-MPC, topology-driven, 同伦轨迹优化, homotopy trajectory, corridor 复现,
  guidance planner, mpc_planner, acados FORCES Pro, ROS2 Jazzy 复现

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
  - nature-archify: Node.js >= 18（CLI: nature-archify/bin/archify.mjs；零外部依赖）；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体，离线可打印；Python 桥接：scripts/nature_archify_bridge.py
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

用户做出选择后，按对应流程执行。用户未指定审阅视角时，**必须先向用户询问**（研究生 / 导师 / 审稿人 / 三方全出），禁止默认。

## 核心原则 / Core Principles

1. **双语输出**: 所有报告必须有中英双版本 (`.md` 英文 + `-CN.md` 中文)
2. **增量验证**: 每添加一个模块即验证一次
3. **可审计**: 每步产生结构化产物，溯源链完整
4. **人机协同**: 风险分级审批
5. **锁定即契约**: 版本/环境/依赖每步锁定，不信任隐式继承
6. **先问后做**: 用户无指令时先主动提问，确认操作后再执行

## 反例与黑名单 / Anti-Patterns & Blacklist

13 条反模式清单（MinerU token 未配置 / Windows 直跑 Linux 脚本 / 先装包后装运行时 / 单种子下判决 / 只生成英文报告 / 跳过三方审阅 / 图表不导出生成代码 / 跳过可行性预判 / 基线失败不记录偏离 / conda+pip 混装 / 单点均值忽略方差 / 翻译不校对术语 / 增量实现不标论文出处）见 [`references/anti_patterns.md`](references/anti_patterns.md)。

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| 0 | 宿主检测→环境构建→GPU配置 | `infra_manifest.json` | G0: 基础设施就绪 |
| 0.5 | 版本检测→安装→锁定→验证 | `version_spec.json` | G1: 版本一致 |
| 1 | PDF解析→结构化提取→领域分类→三方审阅 | `reproducibility_assessment.json` | G01: 可复现性门禁 |
| 2 | 依赖扫描→环境构建→确定性配置→验证 | `conda-lock.yml` | G3: 环境就绪 |
| 3 | 官方代码运行→指标对齐→失败诊断→锁定 | `baseline_metrics.json` | G4: 基线建立 |
| 4 | 模块拆解→增量实现→代码管理 | `delta_report.json` | -- |
| 5 | 多轮运行→统计计算→五态判决→图表导出 | `判决结果.json` | 5.1 参数确认 |
| 6 | 数据就绪检测→双语报告生成(含模板) | `实验复刻结果汇总/实验报告/复现报告.md` + `-CN.md` | 数据就绪 |
| 7 | 最终整理→完整性确认 | `实验复刻结果汇总/` 完整目录 | 文件就位确认 |

---

## 阶段详述 / Phase Detail

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

0.0.4 **实验复现规范**（全平台适用: WSL/Linux/Windows/macOS）:

    a) **目录结构**:
       - 初次使用: `mkdir -p ~/projects`（Windows 下 `~` = `C:\Users\<username>\`）
       - 每个实验单独一个文件夹: `~/projects/<experiment-name>/`
       - 后续所有实验均放在 `~/projects/` 目录下
       - 建议命名: 论文姓氏+年份 或 项目简称（如 `~/projects/smith2023-qem/`）

    b) **环境隔离**（每个实验单独一个环境，以实验名命名）:
       - UV: `uv venv ~/projects/<experiment-name>/.venv`
             `source ~/projects/<experiment-name>/.venv/bin/activate`
             `uv pip install -r requirements.txt`
       - conda: `conda create -n <experiment-name> python=3.x`
                `conda activate <experiment-name>`
       - 环境名 = 实验名，确保隔离且可辨识

    c) **全程留痕**（实验目录下保留所有记录）:
       ~/projects/<experiment-name>/
       ├── code/           # 所用代码脚本（含修改过的官方代码）
       ├── logs/           # 实验日志（stdout/stderr 完整捕获）
       │   └── errors/     # 报错记录（含堆栈、环境信息、复现命令）
       ├── results/        # 实验结果（metrics、图表）
       ├── env/            # 环境锁定文件（requirements-locked.txt / conda-lock.yml）
       └── README.md       # 实验说明（论文出处、复现命令、结果摘要）

**设计原则**: 优先使用已配置好的 Linux 环境（WSL）进行复现，以保证与论文原始实验环境的一致性；若用户未配置 WSL，则在当前系统直接运行，降低使用门槛。

**实现文件**: `scripts/detect_wsl.sh`

---

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

### Phase 1: 论文解析与文献阅读 / Paper Parsing & Literature Reading

**输入**: PDF 文件路径 / arXiv 链接
**输出**: `analysis/paper_summary.json` + `文献阅读.md` + `reproducibility_assessment.json` + `literature_reading.json`

1.1 **PDF 解析**: 确认 MinerU token 已配置
    - 优先级: MinerU SDK (首选, 含公式/表格/图表) → LaTeXML → PyMuPDF → OCR
    - 参数: `--model vlm`, `--ocr`, `--pages`, `--language`
    - 执行: `python scripts/math_pdf_extract.py <pdf> --output-dir analysis/`
    - 日用量跟踪: 自动记录到 `daily_usage.json` (限额 2000 页)
    - 产出: `analysis/parsed_text.md` + `analysis/formulas.tex`

1.2 **结构化提取**: 核心方法/数学公式/超参数/数据集/评估指标/灰色地带

1.3 **领域分类**: 关键词+依赖 → 路由到数值/符号/AI4Math/统计/优化/经济子策略

1.4 **文献阅读报告生成**: 生成结构化的中文审阅分析报告
    - 执行: `python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json`
    - **交互流程**: 未指定 `--template` 时，脚本启动后会**先列出 9 种模板供用户选择**，用户输入编号后才会开始生成报告
    - **模板选择**: 可选模板列表如下：
      1. `markleaf` — **LaTeX 风格（推荐）**: CMU 字体 + tcolorbox 卡片 + 三线表，适合学术文献阅读
      2. `print` — **印刷品**: Times New Roman + 两端对齐 + 首行缩进，适合长文阅读
      3. `retro-print` — **铅字印刷**: KingHwaOldSong 复古字体，适合文学/历史类
      4. `sans` — **无衬线**: SF Pro Display + 现代简洁，适合技术文档
      5. `serif` — **衬线**: Source Han Serif，默认清晰易读
      6. `magazine` — **杂志**: Georgia + 大标题，适合图文混排
      7. `minimal` — **极简**: Segoe UI + 无多余装饰，适合快速浏览
      8. `notebook` — **手记**: 霞鹜文楷 + 楷体，适合笔记风格
      9. `print-double` — **双色印刷**: 蓝色强调，适合打印输出
    - **视角控制**: 未指定 `--perspective` 时，**必须先向用户询问**（研究生 / 导师 / 审稿人 / 三方全出），禁止默认；`--perspective all` 输出三个视角 + 交叉对比
    - 报告包含:
      - **论文结构导航**: 章节/页码/论证功能(gap→contribution→result→limits)
      - **术语表**: 专业术语 + 英文全称 + 中文译法 + 首次出现位置
      - **关键图表索引**: 图表/表格的 ID、标题、页码、关联分析
      - **关键公式索引**: 公式编号、LaTeX、描述、来源页码
      - **视角分析**: 研究生/导师/审稿人(由用户指定视角决定，未指定时先询问，见 Phase 1.4 视角控制)
      - **复现指导**: 核心算法、超参数、数据集、主要风险
    - 产出:
      - `analysis/文献阅读.md` -- 完整中文审阅报告 (自带嵌入式 CSS，MPE 打开即用)
      - `analysis/literature_reading.json` -- 结构化数据 (供下游消费)
      - `analysis/reproducibility_assessment.json` -- 可复现性评估 (G01 门禁)
    - **MPE 兼容**: 报告 Markdown 自带嵌入式 CSS，可在 VS Code + Markdown Preview Enhanced 中直接预览
    - **兼容入口**: `scripts/three_perspective_review.py` 仍保留在 `scripts/` 作为旧版三方审阅兼容入口（未移入 legacy/），新流程统一使用 `literature_reader.py`

    **使用示例**:
    ```bash
    # 默认流程：询问模板 + 询问审阅视角后输出
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json

    # 指定模板：跳过询问
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --template templates/literature_reader.print.md

    # 全部视角
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --perspective all

    # 指定模板 + 全部视角
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --template templates/literature_reader.sans.md --perspective all
    ```

**G01 门禁**: 审查 `reproducibility_assessment.json`
    - `proceed` → 直接进 Phase 2
    - `proceed_with_caution` → 进 Phase 2, 记录已知风险
    - `needs_human_approval` → STOP: 展示风险标记, 获取用户确认
    - `discourage` → STOP: 不建议复现, 展示理由

### 1.5 辅助架构图征询（可选但必须询问） / Auxiliary Architecture Diagram Offer

**触发条件**: 1.4 视角审阅完成后、G01 门禁判决后，无论 proceed / caution / discourage 均须征询。用户未主动要求时也必须主动提出。

**步骤 1 — 主动征询**:

> 基于这篇论文的内容，我可以帮您制作 Nature 级别的研究框架图或技术路线图，方便组会汇报或开题使用。这些图不需要等实验跑完。您想现在制作吗？

- 用户拒绝 → 记录到 `review_manifest.json`（`diagram_offer: "declined"`），跳到 G01 后的流程
- 用户同意 → 进入步骤 2

**步骤 2 — 强制 6 项逐项询问**（不可合并、不可默认、不可跳过，直接复用 nature-archify 第 0 步）:

| # | 询问项 | 候选项 | 说明 |
|---|--------|--------|------|
| 1 | **主题 / Subject** | — | 论文核心研究问题与方法路径 |
| 2 | **图类型** | `architecture` / `workflow` / `sequence` / `dataflow` / `lifecycle` | 根据论文特征推荐 1-2 种 |
| 3 | **图语言** | `zh-CN` / `en` | 中文论文必须 zh-CN |
| 4 | **动画模式** | `trace` / `none` | 默认 none（静态）；交互式展示用 trace |
| 5 | **视觉预设** | `classic` / 其他 12 种 | 默认 classic；共 13 种，含 paper / brutalism / apple 等 |
| 6 | **输出格式** | `HTML` / `HTML + PNG` / `HTML + SVG` | 产物为自包含 HTML，导出在 Viewer 内完成 |

- 用户已声明过的项可复用，不重复问
- 多张图可共享一轮回答
- 若用户要求推荐，按论文领域给出 1-2 种建议并说明理由

**步骤 3 — 执行**:

按 nature-archify SKILL.md 第 0 步→第 5 步执行：选类型→读 schema/examples→写 candidate JSON→validate→deliver。

**图类型可用矩阵**（依据 nature-archify 硬规则）:

| 图类型 | 用途 | 需要实验数据 | 当前阶段可产出 |
|--------|------|:---:|------|
| `architecture` | 系统架构、部署拓扑、云与安全边界 | ❌ | ✅ 终版 |
| `workflow` | 技术流程：节点与连线表达的步骤 | ❌ | ✅ 终版 |
| `sequence` | 调用时序：参与者之间的消息往返 | ❌ | ✅ 终版 |
| `dataflow` | 数据管道与血缘：提取→转换→落库 | ❌ | ✅ 终版 |
| `lifecycle` | 状态机：状态、迁移与触发条件 | ❌ | ✅ 终版 |

**约束**:
- 五类图都只描述结构与流程，不承载实验数值，Phase 1-6 均可交付终版
- 论文的**方法/模型架构图**与**实验流程图**不在 nature-archify 图类型内（PRISMA/CONSORT 等必须写入真实样本量与排除数），需要时另行接入 paperfig 类渲染器
- 输出到 `figures/` 目录；每张图产出 `.html`（PNG/SVG 在 Viewer 内导出）
- 用户偏好（语言/预设/格式）写入 `review_manifest.json`，Phase 4/5/6 复用，不重复询问

---

### Phase 2: 环境重建 / Environment Setup

**输入**: `analysis/paper_summary.json` + `env/version_spec.json`
**输出**: `env/environment.yml` + `env/requirements-locked.txt`

2.1 **依赖扫描**: 扫描 repo 配置文件 (`requirements.txt`, `environment.yml`, `Manifest.toml`, `renv.lock`) + 静态分析 import
2.2 **环境构建**: Conda/Mamba → Python venv → Julia → 系统级库 (逐级 fallback)
    - Conda 冲突→`mamba clean --all && --force`; 仍失败→逐个安装核心包
    - pip 超时→`--default-timeout=120`; 仍失败→分批次先科学计算再领域包
2.3 **确定性配置**: 固定随机种子 (torch/np/random/tf) + 浮点确定性 + `PYTHONHASHSEED`
2.4 **验证**: 基础导入测试 + 版本一致 + GPU 可用性 + 锁定

**G3**: 导入测试通过, 锁定文件已写入, GPU 可用/已降级。任一不满足→返回 2.4 修复。

---

### Phase 3: 基线验证 / Baseline Verification

**输入**: `analysis/paper_summary.json` + 就绪环境
**输出**: `results/baseline_metrics.json` + `results/tolerance_spec.json` + `analysis/gray_areas.md`

3.1 **运行官方代码**: 按 README 执行, 记录完整日志
    - 基线运行审计 (精简形式, 与实验阶段 5.1 同构): 超时、被捕获异常、非零退出码记录到 `analysis/gray_areas.md` (与 3.3 偏离记录义务合并)
    - 断点续传义务 (与 5.1 同构): 长时基线运行同样适用 5.1 **断点续传**条目 (逐单元立即落盘、重启跳过已完成单元; 不可行时按 3.3 偏差登记表登记理由与中断损失评估)
3.2 **指标对齐**: 提取所有指标 → 对比论文声称值 → 设置容忍度 (数值 +/- 5%, 统计 95% CI, 趋势一致)
3.3 **基线失败处理**:
    - 环境诊断: 依赖缺失→pip list 对比; 版本冲突→conda env export; GPU 不可用→nvidia-smi
    - 代码修复: 仅最小改动 (import 路径/API 变更/Python 2/3); 不做功能扩展
    - 记录偏离到 `analysis/gray_areas.md` (环境/代码/参数偏离 + git diff + 参数假设)
    - **偏差登记表** (deviation register): `gray_areas.md` 结构化——每条偏差含 ID、类型 (数据/环境/框架/执行)、量化影响、证据、对判决的影响方向
    - 标准条目类型: 已知实验条件偏差 (基元池比例/异构主机/依赖双版本/时限执行缺陷)、计时指标语义偏差 (见 5.1)、计数目标与实测之差 (须机制性解释)、文档声称与实测对账差异、样本量局限与翻转风险 (见统计验证稳健性自检)
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
**输出**: `results/raw_metrics.csv` + `实验复刻结果汇总/实验报告/判决结果.json` + `实验复刻结果汇总/实验报告/口径B通过率矩阵.md` + `实验复刻结果汇总/实验图表（含代码）/` (图 + 生成代码)

5.0 **输入数据预检** (基准/基线运行前; Phase 3 基线运行前同样适用):
    - 输入数据预检细则（二进制 schema 完整性 / CSV BOM 编码 / 空值预检 / 修复后验证分类）+ 两口径语义声明（口径 A = 求解器自身判据，口径 B = 独立 checker 判据，数字不得混用）详见 [`references/phase5_audit_spec.md`](references/phase5_audit_spec.md)。

5.1 **多轮运行**: 确认参数 (基线可行? N=5 种子? 运行时间? GPU 启用?) → 每轮独立执行 → `raw_metrics.csv`

    **运行审计 / 过程数据留痕 / 断点续传**（详细规范）: 硬超时执行、异常分类计数、退出码审计、计时指标语义登记、空值普查；逐试验时间戳与 worker 标识、日志可信度校验、全量归档；断点续传可行/不可行 MUST、证据回执——详见 [`references/phase5_audit_spec.md`](references/phase5_audit_spec.md)。
5.2 **统计计算**: 判决基准匹配论文报告口径——连续指标 = 成功试验**中位数** + percentile bootstrap 95% CI (≥20,000 重采样、固定种子、有放回抽 N 点), 比例指标 = Wilson score 区间; 容差判定双侧语义 (|Δ| 超容差即判); 均值 x-bar ± t-CI 仅作**参考输出** (论文明确报告均值时可切换 t-CI 判决, 登记 ci_method) → `statistical_summary.json`
5.3 **五态判决**（统一枚举）: `pass`→通过 / `approx`→近似 / `within_ci`→置信区间内 / `fail`→不通过 / `skip`→跳过（口径 A; 旧 within_ci→within_ci, close_outside_ci→approx, outside_tolerance→fail, not_testable→skip, static_check_failed→fail）
    - 口径 B (独立 checker) 通过率矩阵 (实例 × 算法) 作为标准产物与口径 A 并列报告 → `实验复刻结果汇总/实验报告/口径B通过率矩阵.md` / `-CN.md`
    - **拒绝归因证据分级**: 每个被拒试验的归因 (真实越界 / 终点容差不匹配 / 未知) 须附诊断证据并标注分级 (实证/推断/估计), **禁止无证据的容差归因**
5.4 **诊断输出**: >=2 条诊断假说 + Top-12 失败模式 + 引用审稿人视角发现 → `实验复刻结果汇总/实验报告/诊断分析.md` / `诊断分析-CN.md`
5.5 **交互式轨迹可视化** (机器人路径优化论文):
    - 生成双击即可在浏览器打开的 3D 可视化 HTML（基于 Three.js）
    - 执行: `python scripts/trajectory_visualizer.py --data results/uav_path_data.json --output trajectory.html`
    - 产出: 对应论文根目录下直接生成 `trajectory.html`
    - 支持两种相机模式（可在页面切换）:
      - **绕起点旋转 (orbit-start)**: 自动环绕起点垂直轴旋转观察
      - **自由旋转 (free)**: 鼠标拖拽 + 滚轮缩放，双击重置
    - 支持播放控制（播放/暂停/速度调节）、实时轨迹跟踪
    - 支持障碍物显示、起点/终点标记
    - 支持 3 种演示模式: `--demo-maze` / `--demo-random-boxes` / `--demo-uav-village`
5.6 **图表+代码导出**:
    - 图形: 收敛曲线(convergence.png) / 指标对比(comparison.png) / 消融图(ablation.png) / 散点图/热力图
    - 格式: PNG (嵌入报告) + PDF (出版级)
    - 代码自包含: 每图附带独立可运行 `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py` (固定种子+对齐论文配色)
    - 验证: `python 实验复刻结果汇总/实验图表（含代码）/code/plot_convergence.py` → 输出一致
    - 产出: `实验复刻结果汇总/实验图表（含代码）/*.png/.pdf` + `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py`

**Top-12 失败模式**: 代码/数据缺失 | 环境漂移 | CUDA 冲突 | ABI 不兼容 | 依赖冲突 | 非确定性 | BLAS 变体 | 跨平台路径 | 数据泄露 | 预训练权重漂移 | 选择性报告 | 上游依赖位腐

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
- `实验复刻结果汇总/实验报告/口径B通过率矩阵.md` -- 口径 B (独立 checker) 通过率矩阵 (英文)
- `实验复刻结果汇总/实验报告/口径B通过率矩阵-CN.md` -- 口径 B 通过率矩阵 (中文)
- `实验复刻结果汇总/实验结果对比表/实验结果对比表.md` -- 对比表 (英文)
- `实验复刻结果汇总/实验结果对比表/实验结果对比表-CN.md` -- 对比表 (中文)
- `实验复刻结果汇总/实验图表（含代码）/*.png/.pdf` -- 实验图表
- `实验复刻结果汇总/实验图表（含代码）/code/plot_*.py` -- 图表生成代码 (自包含, 可独立运行)

**格式**: 英文版 = `文件名.md`，中文版 = `文件名-CN.md`; 英文标题+中文标题; 表格列头 `Metric / 指标`; 数值统一精度; 图表标题 EN/ZH 标注

**报告必备节**:
- 双语报告必须含**偏差登记节** (来自 `analysis/gray_areas.md` 偏差登记表, 见 3.3)
- 报告须同时呈现**口径 A 与口径 B 的总通过率**, 两套数字不得混用 (见 Phase 5 两口径语义声明)

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
     **发布前交叉校验** (强制):
     - 报告数字与判决 JSON / raw_metrics **逐格核对** (零不一致方可交付)
     - **算法标签与矩阵行列双重核对** (行列错位检测)
     - 机制参数声称 (终止容差、预算等) 与实测配置对账

---

## 门禁总表 / Gate Map

| Gate | 位置 | 条件 | 违反动作 |
|------|------|------|---------|
| GΔ | Phase Δ-1 自动更新 | 网络可达时同步至最新 | 静默跳过，不阻塞流程 |
| G0 | Phase 0 -> 0.5 | infra_manifest.json + GPU 就绪 | 返回修复 manifest/环境 |
| G00 | Phase 0.9 | GPU 框架检测通过或 CPU 降级 | 检查驱动，降级 CPU |
| G1 | Phase 0.5 -> 1 | 版本一致性通过 | 修复版本冲突后继续 |
| G01 | Phase 1.4 -> 2 | reproducibility_assessment 决策 proceed | 用户介入决策 |
| G2 | Phase 2 依赖扫描 | 依赖清单完整+导入测试通过 | 返回修复依赖/环境 |
| G3 | Phase 2 -> 3 | 导入测试+锁定+GPU | 返回 2.4 修复 |
| G4 | Phase 3 -> 4 | 基线指标记录+tolerance | 用户决策是否继续 |
| G5 | Phase 4 | 每个模块 delta 在预期内 | 排查修复后重跑 |
| G6 | Phase 5 | 五态判决产出 | 补跑统计验证 |
| G66 | Phase 5.5 | 有图表时每图有独立源码 | 补导出生成代码 |
| G7 | Phase 6 | 所有报告中英双语 (`.md` + `-CN.md`) | 补译缺失语言版本 |
| G8 | Phase 7 | `实验复刻结果汇总/` 下所有文件就位 | 补缺文件 |
| G9 | Phase 7.2 交叉校验 | 报告数字与判决 JSON 零不一致+标签核对 | 回到 Phase 6 修正报告 |

---

## 文件结构 / Directory Structure

完整目录树（含 nature-reader/nature-figure/nature-paper2ppt/_shared/scripts/templates/schemas/infra/provisioning/env/analysis/code/logs/results/implementation/实验复刻结果汇总 等子树注释）见 [`references/directory_structure.md`](references/directory_structure.md)。

**顶层速查**:
- `SKILL.md` — 主 skill 入口
- `scripts/` — PDF 提取 / 三方审阅 / 图表导出等脚本
- `templates/` — 双语报告模板（Jinja2）
- `analysis/` — 论文分析产物（summary/parsed/formulas/gray_areas/三视角审阅）
- `实验复刻结果汇总/` — 最终输出（在论文所在目录创建，非本目录）

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

本 skill 集成四个独立 Nature 子技能（`nature-reader` / `nature-figure` / `nature-paper2ppt` / `nature-archify`）+ 共享层 `_shared/`，位于 `math-read-do/` 下，可独立调用或作为 Phase 1-6 增强工具。子技能路由表、与主流程协同细节、调用方式见 [`references/nature_skills_integration.md`](references/nature_skills_integration.md)。

**要点摘要**:
- **nature-reader** → 增强 Phase 1（论文解析与视角审阅），未指定视角时主动询问
- **nature-figure** → 增强 Phase 5（出版级图表生成，Python/R 双后端，含 QA 循环）
- **nature-archify** → Phase 1/2/6 系统架构/流程/时序/数据流/状态机图（JSON→inline-SVG HTML）
- **nature-paper2ppt** → Phase 6 后生成汇报 PPTX

## 参考文献 / References

完整参考文献列表（MaRDI / ICERM / OpenResearch / paper-replay / repro-agent / MaRDIFlow / repo2docker / Apptainer / nature-* 等 12 条）见 [`references/references_list.md`](references/references_list.md)。
