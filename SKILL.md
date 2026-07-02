---
name: math-paper-reproduction
description: >-
  数学文献实验复现标准化工作流 / Standardized Math Paper Reproduction Pipeline
  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析 → 三方视角审阅(研究生/导师/审稿人) →
  环境重建 → 基线验证 → 增量实现 → 统计验证 → 双语报告 → 制品打包。
  支持数值计算/符号代数/AI4Math/统计/优化/经济学。每份报告必须中英双语。
  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现
compatibility:
  - python3 (mineru-open-sdk >= 0.2.5, openai)
  - 配置文件: ~/.mineru/config.yaml (MinerU token)
  - 环境变量: LLM_API_KEY, LLM_API_BASE, LLM_MODEL
---

# Mathematical Literature Experiment Reproduction Standardized Workflow
# 数学文献实验复现标准化流程

## 概述 / Overview

本 Skill 定义了通用的数学文献实验复现标准化流程，覆盖从宿主环境检测到制品打包发布的完整链路。所有实验报告、数据对比文档均需生成**中英双语版本**。

This skill defines a standardized workflow for reproducing experiments from mathematical literature, covering the complete pipeline from host environment detection to artifact packaging. **All experiment reports and data comparison documents MUST be generated in both Chinese and English versions.**

### 适用领域 / Applicable Domains
- 数值计算 / Numerical Computing (PDE, FEM, optimization)
- 符号代数 / Symbolic Algebra (computer algebra systems)
- AI4Math / AI for Mathematics (PINN, neural solvers)
- 统计学 / Statistics (MCMC, Bayesian inference)
- 优化 / Optimization (convex, non-convex, combinatorial)
- **经济学 / Economics (计量/DID/IV/DSGE)** ← 新增经济类论文支持

### 核心原则 / Core Principles
1. **双语输出** / **Bilingual Output**: 所有报告文档必须有中英文双版本，文件命名 `.md`(英文) / `.zh.md`(中文)
2. **增量验证** / **Incremental Validation**: 每添加一个模块即验证一次
3. **可审计** / **Auditable**: 每步产生结构化产物，溯源链完整
4. **人机协同** / **Human-AI Collaboration**: 风险分级审批机制

---

## 流程总览 / Pipeline Overview

```
Phase 0:      Phase 0.5:       Phase 1:          G01               Phase 2:
基础设施      版本管理          论文解析+审阅     可复现性门禁        环境重建
│             │                │                 │                 │
├─ 宿主检测    ├─ 版本需求检测    ├─ PDF解析(MinerU) │ reproducibility_ │ ├─ 依赖扫描
├─ 需求分析 ───┼── 可复现性评估   ├─ 结构化提取       │ assessment.json  │ ├─ 环境构建
│  (含可行性   │  (G0门禁输入)   ├─ 领域分类         │ decide:          │ ├─ 确定性配置
│   预判)      └─ 锁定+验证       ├─ 三方视角审阅    │ ✓ proceed        │ └─ 环境验证
├─ 环境构建                       └─ 可复现性评估 ───→│ ⚠ proceed_with_  │
├─ GPU配置                                          │   caution        │        Phase 3:
└─ 验证                                             │ ✗ needs_human_   │        基线验证
      │             │                 │              │   approval       │        │
      │             │                 │                               │
      └─────────────┴─────────────────┴───────────────────────────────┴────────┘
                                        │
                              ┌─────────▼──────────┐
                              │  Phase 4:           │
                              │  增量实现             │
                              │  (若需从零实现)        │
                              └─────────┬──────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
               Phase 5:            Phase 6:             Phase 7:
               实验验证             双语报告              制品打包
               ├─ 多轮运行           ├─ 复现报告(中+英)   ├─ 证据包
               ├─ 统计验证           ├─ 对比表(中+英)     ├─ 溯源链
               ├─ 结果判决 ← 引用    ├─ 诊断(中+英)       └─ 三方审阅纳入
               │  审稿人视角          ├─ RUN_SUMMARY(中+英)
               ├─ 诊断输出 ← 引用    └─ 图表源码清单
               │  审稿人问题点
               └─ 图表+代码导出
```

---

## 阶段 0：基础设施决策与编排 / Infrastructure Orchestration

### 目标 / Objective
检测宿主环境，选择并配置最佳运行环境（Linux VM / 容器 / 原生）。

### 输入 / Input
宿主操作系统信息。

### 输出 / Output
`infra/infra_manifest.json` + 对应环境配置文件。

### 步骤 / Steps

```
0.1 宿主环境检测 / Host Detection
    ├── OS: Windows / macOS / Linux
    ├── GPU: NVIDIA (nvidia-smi) / AMD / Intel / 无
    ├── 内存容量 / Total Memory
    ├── 磁盘: 可用空间 / 文件系统 (NTFS / ext4)
    ├── 虚拟化能力: WSL2 / Hyper-V / VirtualBox / Docker
    ├── 当前Shell: PowerShell / bash / zsh
    └── 产出: infra/host_detection.json

0.2 需求分析 / Requirements Analysis
    ├── 论文需求检测:
    │   ├── 需要 CUDA? (关键词: cuda, gpu, cudnn)
    │   ├── 需要 MPI? (关键词: mpi, openmpi, mpich)
    │   ├── 需要 Fortran? (关键词: fortran, gfortran, .f90)
    │   ├── 需要 MATLAB? (关键词: matlab, .m)
    │   └── 需要特定 Linux 库? (关键词: libxxx, apt, make)
    ├── **可行性预判 / Feasibility Pre-check** ← 快速预判(不替代Phase 1.4完整分析)
    │   ├── 扫描论文PDF/arXiv页面快速判断:
    │   │   ├── 代码公开? → 高概率可复现
    │   │   ├── 仅伪码/无代码? → 需从零实现，告知用户
    │   │   ├── 无数据/私有数据? → 标记数据风险
    │   │   └── 方法描述模糊? → 标记灰色地带
    │   ├── 产出: 初步可行性标记到决策日志 (info/feasibility_precheck.json)
    │   └── 注: 此步骤仅为快速预估，精确的可复现性评估由 Phase 1.4 导师视角产出
    ├── 跨平台兼容性检查
    └── 决策矩阵 / Decision Matrix:
        ├── Windows + 无特殊需求 → Native (Conda)
        ├── Windows + 需Linux工具 → WSL2 (推荐) / Vagrant VM
        ├── Windows + 需完整隔离 → Vagrant VM (VirtualBox/Hyper-V)
        ├── Windows + 需CI对齐   → Docker Desktop
        ├── macOS + 需Linux      → Docker / Lima VM
        └── Linux                → Native + Docker (可选)

0.3 环境构建 / Environment Build
    ├── 路径A - WSL2:
    │   ├── wsl --install -d Ubuntu-24.04
    │   ├── (如已安装) wsl --set-version <distro> 2
    │   ├── CUDA on WSL: 安装 NVIDIA CUDA on WSL driver
    │   ├── 文件系统建议: 代码放在 \\wsl$\Ubuntu\home\<user>\ 避免跨FS性能损失
    │   └── 失败处理:
    │       ├── wsl --install 失败 → 检查 BIOS 虚拟化开启 + Hyper-V 启用
    │       └── 仍失败 → 切换到 Vagrant VM (路径B)
    ├── 路径B - Vagrant VM:
    │   ├── vagrant init ubuntu/noble64
    │   ├── vagrant up --provider virtualbox
    │   ├── vagrant ssh 进入VM
    │   └── 失败处理:
    │       ├── vagrant up 超时 → vagrant destroy -f && vagrant up --no-provision
    │       └── 仍失败 → 使用 Vagrantfile 中备用 provider (vmware/hyperv)
    ├── 路径C - Docker:
    │   ├── docker pull ubuntu:24.04
    │   ├── docker compose up -d
    │   └── 失败处理:
    │       ├── docker pull 超时 → 配置国内镜像源 (/etc/docker/daemon.json registry-mirrors)
    │       └── 仍失败 → 切换到 Native (路径D)
    └── 路径D - Native:
        └── 直接使用宿主包管理器

0.4 基础设施验证 / Infrastructure Validation
    ├── 架构: uname -m (Linux) / wmic os get osarchitecture (Win)
    ├── 内核: uname -r
    ├── 内存: free -h (Linux) / systeminfo (Win)
    ├── GPU: nvidia-smi (如适用)
    └── 磁盘: df -h (Linux) / Get-PSDrive C (Win)

0.9 GPU配置与启用 / GPU Configuration & Enablement
    ├── GPU类型识别:
    │   ├── NVIDIA独立显卡 → CUDA路径 (执行 scripts/enable_gpu.sh)
    │   ├── AMD独立显卡   → ROCm路径
    │   ├── Intel Arc     → XPU路径
    │   └── 仅有集显或无GPU → CPU模式 (跳过后续GPU步骤)
    ├── NVIDIA专用配置:
    │   ├── 检查CUDA驱动: nvidia-smi → 记录驱动版本
    │   ├── 设置CUDA_VISIBLE_DEVICES="0" (指定独显, 多卡时"0,1")
    │   ├── 设置CUDA_DEVICE_ORDER="PCI_BUS_ID"
    │   └── 验证: python -c "import torch; print(torch.cuda.get_device_name(0))"
    ├── AMD专用配置:
    │   ├── rocminfo → 记录GPU信息
    │   └── export HIP_VISIBLE_DEVICES=0
    ├── 框架GPU可用性验证:
    │   ├── PyTorch: torch.cuda.is_available() → True
    │   ├── TensorFlow: tf.config.list_physical_devices('GPU') → 非空
    │   ├── JAX: jax.devices() → GPU devices
    │   └── 任一框架验证失败时尝试其他框架或降级CPU模式
    ├── 性能配置 (非确定性实验):
    │   ├── torch.backends.cudnn.benchmark = True
    │   ├── torch.backends.cuda.matmul.allow_tf32 = True
    │   └── PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
    ├── 精度优先配置 (需精确复现时):
    │   ├── torch.backends.cudnn.deterministic = True
    │   ├── torch.backends.cudnn.benchmark = False
    │   └── CUBLAS_WORKSPACE_CONFIG=:4096:8
    ├── Windows WSL2场景:
    │   ├── 确保 Windows 端安装了 NVIDIA CUDA on WSL driver
    │   └── WSL2 内无需额外安装CUDA驱动 (宿主驱动透传)
    ├── Docker场景:
    │   ├── 使用 nvidia/cuda 基础镜像
    │   ├── docker run --gpus all 启用GPU
    │   └── 或 docker compose 中 device_ids: ["0"]
    └── 产出: infra/gpu_manifest.json (GPU类型/驱动/框架可用性/显存)
```

### 质量门禁 / Quality Gate
- 基础设施检测完成，与论文需求一致
- `infra/infra_manifest.json` 已验证写入
- GPU配置完成: `infra/gpu_manifest.json` 记录GPU信息
- 对应环境配置文件就绪

---

## 阶段 0.5：语言运行时与工具链版本管理 / Language Runtime & Toolchain Version Management

### 目标 / Objective
安装并锁定语言运行时版本、编译器、CUDA等，确保跨环境一致。

### 输入 / Input
`infra/infra_manifest.json` + 论文/仓库版本线索。

### 输出 / Output
`env/version_spec.json` + `env/reproduction_manifest.json`

### 步骤 / Steps

```
0.5.1 版本需求检测 / Version Requirement Detection
    ├── 扫描仓库识别版本线索:
    │   ├── Python: .python-version / runtime.txt / pyproject.toml
    │   ├── Julia:  Manifest.toml → julia_version 字段
    │   ├── R:      .Rprofile / renv.lock
    │   ├── CUDA:   nvcc --version 线索 / requirements 中 cudatoolkit
    │   ├── C/C++:  CMakeLists.txt / Makefile 编译器标志
    │   └── Node.js: .nvmrc / .node-version / package.json engines
    ├── 版本约束求解: 检测到多个需求时进行兼容性分析
    └── 写入 env/version_spec.json

0.5.2 版本管理器安装 / Version Manager Installation (如缺失)
    ├── Python: pyenv
    │   ├── Linux: curl https://pyenv.run | bash
    │   └── 验证: pyenv --version
    ├── Julia: juliaup
    │   ├── curl -fsSL https://install.julialang.org | sh
    │   └── 验证: juliaup --version
    ├── R: rig
    │   ├── curl -Ls https://github.com/r-lib/rig | sh
    │   └── 验证: rig --version
    ├── Node: nvm
    │   ├── curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    │   └── 验证: nvm --version
    ├── Java: sdkman
    │   ├── curl -s "https://get.sdkman.io" | bash
    │   └── 验证: sdk version
    └── Rust: rustup
        ├── curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        └── 验证: rustup --version

0.5.3 特定版本安装 / Specific Version Installation
    ├── Python: pyenv install <version> && pyenv local <version>
    ├── Julia:  juliaup add <version> && juliaup default <version>
    ├── R:      rig add <version> && rig default <version>
    ├── Node:   nvm install <version> && nvm use <version>
    ├── Java:   sdk install java <version>
    ├── CUDA:
    │   ├── Conda场景: conda install cudatoolkit=<version>
    │   ├── WSL2场景:  apt install cuda-toolkit-<version>
    │   └── Docker场景:  FROM nvidia/cuda:<version>-runtime-ubuntu24.04
    ├── GCC多版本:
    │   ├── apt install gcc-<version> g++-<version> gfortran-<version>
    │   └── update-alternatives 设置优先级
    └── MPI: apt install libopenmpi-dev / libmpich-dev

0.5.4 版本锁定 / Version Locking
    ├── Conda: conda env export --no-builds > conda-lock.yml
    │          或 conda-lock -f environment.yml -p linux-64
    ├── Julia: julia --project -e 'using Pkg; Pkg.instantiate()'
    │          复制 Manifest.toml 到 env/
    ├── pip:   pip freeze > env/requirements-locked.txt
    ├── R:     renv::snapshot()
    ├── 系统级: dpkg --get-selections > env/system-packages.txt (Linux)
    └── 版本管理器快照:
        ├── pyenv versions > env/pyenv-versions.txt
        ├── juliaup list > env/juliaup-channels.txt
        └── nvm list > env/nvm-versions.txt

0.5.5 版本一致性验证 / Version Consistency Verification
    ├── python --version && which python
    ├── julia --version
    ├── gcc --version && gfortran --version
    ├── nvcc --version (如需要CUDA)
    ├── mpirun --version (如需要MPI)
    └── 对比 version_spec.json 与实际版本，记录差异
```

### 质量门禁 / Quality Gate
- 所有语言运行时和编译器版本与 `version_spec.json` 一致
- 锁定文件已写入 `env/` 目录
- 版本一致性验证通过

---

## 阶段 1：论文解析与信息提取 / Paper Parsing & Information Extraction

### 目标 / Objective
从论文中提取数学模型、算法伪码、超参数、数据集、评估指标。

### 输入 / Input
PDF文件路径 / arXiv链接。

### 输出 / Output
`analysis/paper_summary.json` + `analysis/*_review.md` (三方审阅) + `analysis/reproducibility_assessment.json`

### 步骤 / Steps

```
1.1 PDF解析 / PDF Parsing
    ├── 🔴 CHECKPOINT: 确认 MinerU token 已配置 (检查 ~/.mineru/config.yaml)
    │   ├── 已配置 → 使用 MinerU SDK (首选)
    │   ├── 未配置 → 引导用户创建配置文件，或降级到 LaTeXML/PyMuPDF
    │   └── 降级后果: 公式/表格识别精度下降
    ├── 解析方法 (按优先级降序尝试):
    │   1. MinerU SDK (mineru-open-sdk) ← 首选 (含公式/表格/图表识别)
    │      ├── 安装: pip install mineru-open-sdk
    │      ├── 配置: ~/.mineru/config.yaml (token)
    │      ├── 执行: python scripts/math_pdf_extract.py <pdf> --output-dir analysis/
    │      ├── 参数: --model vlm (默认), --ocr (扫描件), --pages "1-20" (分批)
    │      ├── 语言: 英文 --language en, 中文 --language ch
    │      ├── 公式识别: 默认开启 (--no-formula 关闭)
    │      ├── 日用量跟踪: 自动记录到 daily_usage.json (日限额 2000 页)
    │      └── 优点: 原生支持数学公式/表格/图表提取，无需本地 GPU
    │   2. arXiv HTML → LaTeXML (后备, 无 MinerU token 时)
    │   3. PyMuPDF (fitz) 直接提取文本 (二级后备)
    │   4. OCR (Tesseract) 最终后备 (需启用 --ocr)
    ├── 公式提取:
    │   ├── MinerU → 自动提取 LaTeX 格式公式
    │   ├── LaTeXML → 保留 LaTeX 格式
    │   ├── Mathpix / LaTeX-OCR 辅助 (若 MinerU 公式识别不全)
    │   └── 手动提取复杂公式 (若自动解析结果不可用)
    └── 产出: analysis/parsed_text.md + analysis/formulas.tex
    └── 注: MinerU 解析后自动报告 API 当日用量

1.2 结构化信息提取 / Structured Extraction
    ├── 从 parsed_text.md (MinerU) 或 parsed_text.txt (后备) 中提取
    ├── 核心方法/模型:
    │   ├── 数学公式和方程 (MinerU 自动保留 LaTeX 格式)
    │   ├── 算法伪码
    │   └── 网络架构 (AI4Math)
    ├── 超参数/配置:
    │   ├── 学习率、批大小、优化器
    │   ├── 网格大小、时间步长 (数值计算)
    │   └── 收敛阈值、最大迭代
    ├── 数据集 / 输入规范
    ├── 评估指标 / 验证方式
    ├── 基线方法
    └── "灰色地带"标记 (作者未明确的细节)

1.3 领域分类 / Domain Classification
    ├── 关键词匹配 + 依赖库检测
    └── 路由到对应子领域策略:
        ├── numerical_computing: 容忍度+CI验证
        ├── symbolic_algebra: 等价性检查
        ├── ai4math: 统计验证+消融
        ├── statistics: CI+假设检验
        └── optimization: 收敛曲线+目标值

1.4 三方视角深度分析 / Three-Perspective Deep Analysis
    ├── 目的 / Purpose:
    │   ├── 不满足于浅层信息提取，而是从三个不同身份视角深度理解论文
    │   ├── 研究生视角 → 深度理解模型/公式/方法，直接输入 Phase 2-4 复现计划
    │   ├── 导师视角 → 可复现性评级，决定 G0 门禁 (是否值得/可能复现)
    │   └── 审稿人视角 → 批判性审查，辅助 Phase 5 判决引擎
    ├── 执行方式 / Execution:
    │   ├── 使用 scripts/three_perspective_review.py 自动执行
    │   │   └── python scripts/three_perspective_review.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json
    │   ├── 需设置 LLM_API_KEY 环境变量 (建议: gpt-4o / claude-3.5 / deepseek-chat)
    │   ├── 未配置 LLM_API_KEY 时输出占位分析并提示用户
    │   └── 三种视角可独立运行或全部执行 (--perspective student/advisor/reviewer/all)
    ├── 研究生视角 (Phase 1.4-A) / Student Perspective:
    │   ├── 输出框架:
    │   │   1. 摘要 — 核⼼内容综合提炼
    │   │   2. 文献综述 — 理论根基、关键文献、研究空白
    │   │   3. 研究问题 — RQ 列表 (未明确时标注推断)
    │   │   4. 研究方法 — 模型设定、推导逻辑、数据来源
    │   │   5. 研究结果 — 主要发现、核心数据
    │   │   6. 讨论与评价 — 诚实评估、对复现的启发
    │   │   7. 关键公式与概念 — 核心数学/经济公式
    │   ├── 产出: analysis/<paper_stem>_student_review.md
    │   └── 消费方: Phase 2 (环境重建时参考方法栈)、Phase 4 (增量实现的公式/算法参考)
    ├── 导师视角 (Phase 1.4-B) / Advisor Perspective:
    │   ├── 输出框架:
    │   │   1. 文献定位 — 发表信息、领域、难度/创新评级
    │   │   2. 研究问题与贡献评估
    │   │   3. 方法论评估 (重点: 可复现性)
    │   │   4. 可复现性评估表 — 代码/数据/环境/方法清晰度评级
    │   │   5. 教学与指导建议
    │   │   6. 对学生/复现者的启发
    │   ├── 产出: analysis/<paper_stem>_advisor_review.md
    │   ├── 核心产出: analysis/reproducibility_assessment.json
    │   │   ├── reproducibility_rating: high/medium/low/very_low
    │   │   ├── recommendation: proceed / proceed_with_caution / needs_confirmation / needs_human_approval / discourage
    │   │   └── risk_flags: 风险标记列表
    │   └── 消费方: G0 门禁 (决定是否进入复现流程)
    ├── 审稿人视角 (Phase 1.4-C) / Reviewer Perspective:
    │   ├── 输出框架:
    │   │   1. 总体评价 — 推荐意见 + 评分 (创新/方法/写作)
    │   │   2. 研究问题与创新性评估
    │   │   3. 方法论评估 (数学: 证明严谨; 经济: 识别策略)
    │   │   4. 论证与证据评估
    │   │   5. 具体修改意见 (强制性/建议性/细节)
    │   │   6. 写作与呈现质量
    │   │   7. 总结与建议
    │   ├── 产出: analysis/<paper_stem>_reviewer_review.md
    │   └── 消费方: Phase 5 (判决引擎)、Phase 6 (诊断章节引用)
    ├── 三方视角综合 / Cross-Perspective Synthesis:
    │   ├── 输出视角交叉对比表 (维度: 主要优势/主要担忧)
    │   ├── 明确各视角产出在复现流水线中的消费位置
    │   └── 所有产出在 analysis/review_manifest.json 中汇总
    ├── 产出: analysis/
    │   ├── <paper_stem>_student_review.md    # 研究生审阅
    │   ├── <paper_stem>_advisor_review.md     # 导师审阅
    │   ├── <paper_stem>_reviewer_review.md    # 审稿人审阅
    │   ├── reproducibility_assessment.json    # 可复现性评估 (G0门禁输入)
    │   └── review_manifest.json               # 审阅清单
    └── 门禁: G2 论文理解门禁扩展 — paper_summary.json 审查 + reproducibility_assessment.json 可用

    └── 🔴 G01 门禁: 审查 reproducibility_assessment.json 决定是否继续
        ├── recommendation=proceed → 直接进入 Phase 2
        ├── recommendation=proceed_with_caution → 进入 Phase 2，记录已知风险
        ├── recommendation=needs_confirmation → 🛑 STOP: 向用户展示风险标记，获取确认
        └── recommendation=discourage → 🛑 STOP: 不建议复现，展示理由供用户决策
```

---

## 阶段 2：环境重建与依赖管理 / Environment Setup & Dependency Management

### 目标 / Objective
重建论文的计算环境。

### 输入 / Input
`analysis/paper_summary.json` + `env/version_spec.json`

### 输出 / Output
`env/environment.yml` + `env/requirements-locked.txt`

### 步骤 / Steps

```
2.1 依赖扫描 / Dependency Scanning
    ├── 扫描仓库配置文件:
    │   ├── requirements.txt, pyproject.toml, setup.py
    │   ├── environment.yml, Dockerfile
    │   ├── Manifest.toml (Julia)
    │   └── renv.lock (R)
    ├── 静态分析代码 import 语句
    └── 合并论文中提及的额外依赖

2.2 环境构建 / Environment Build
    ├── Conda/Mamba:
    │   ├── mamba env create -f env/environment.yml
    │   └── 失败处理:
    │       ├── 依赖冲突 → mamba clean --all && mamba env create --force
    │       └── 仍失败 → 逐个安装核心包，跳过冲突依赖，记录排除项
    ├── Python venv:
    │   ├── python -m venv .venv && pip install -r requirements.txt
    │   └── 失败处理:
    │       ├── pip install 超时 → pip --default-timeout=120 install -r requirements.txt
    │       └── 仍失败 → 分批次安装: 先核心(科学计算)再领域包
    ├── Julia:
    │   ├── julia --project -e 'using Pkg; Pkg.instantiate()'
    │   └── 失败处理:
    │       ├── 注册表问题 → julia -e 'using Pkg; Pkg.Registry.add("General")'
    │       └── 仍失败 → 使用 Manifest.toml 精确版本
    └── 系统级库:
        ├── apt install / yum install (在VM/容器内)
        └── 失败处理:
            ├── apt install 权限 → sudo 或无密码 sudo 配置
            └── 仍失败 → 使用 conda 安装替代包

2.3 确定性配置 / Deterministic Configuration
    ├── 随机种子固定:
    │   ├── torch.manual_seed(seed)
    │   ├── np.random.seed(seed)
    │   ├── random.seed(seed)
    │   └── tf.random.set_seed(seed)
    ├── 浮点确定性:
    │   ├── torch.use_deterministic_algorithms(True)
    │   ├── torch.backends.cudnn.deterministic = True
    │   └── torch.backends.cudnn.benchmark = False
    └── 环境变量: PYTHONHASHSEED, CUBLAS_WORKSPACE_CONFIG

2.4 环境验证 / Environment Validation
    ├── 基础导入测试: python -c "import torch; print(torch.__version__)"
    ├── 版本一致性检查
    ├── GPU可用性: python -c "import torch; print(torch.cuda.is_available())"
    └── 锁定: conda-lock / pip freeze > env/requirements-locked.txt
```

---

## 阶段 3：基线验证 / Baseline Verification

### 目标 / Objective
确认官方代码可运行且复现基线指标。

### 输入 / Input
`analysis/paper_summary.json` + 就绪环境

### 输出 / Output
`results/baseline_metrics.json` + `results/tolerance_spec.json`

### 步骤 / Steps

```
3.1 运行官方代码 / Run Official Code
    ├── 按README说明执行
    ├── 使用论文指定的参数
    └── 记录完整输出到 logs/run_baseline.log

3.2 指标对齐 / Metric Alignment
    ├── 提取所有指标 (数值/图表/收敛曲线)
    ├── 对比论文声称值
    ├── 设置容忍度:
    │   ├── 数值容差: ±X% (默认 5%)
    │   ├── 统计容差: 95%置信区间
    │   └── 趋势一致: 方法A>B的顺序不变
    └── 记录 tolerance_spec.json

3.3 基线失败处理 / Baseline Failure Handling
    ├── 环境诊断:
    │   ├── 依赖缺失 → pip list / conda list 对比 requirements
    │   ├── 版本冲突 → conda env export 查看实际版本 vs paper 声明
    │   ├── 路径问题 → 检查 PYTHONPATH / LD_LIBRARY_PATH / JULIA_LOAD_PATH
    │   └── GPU 不可用 → 检查 nvidia-smi + CUDA_VISIBLE_DEVICES + framework 版本
    ├── 代码修复: 仅必要的最小改动
    │   ├── import 路径修正 → 修复相对/绝对路径
    │   ├── API 变更适配 → 查阅 changelog，仅替换已废弃 API
    │   └── Python 2/3 差异 → 使用 six/future 兼容层
    │   └── 规则: 不做功能扩展，只做最小化兼容修复
    ├── 记录所有偏离到 analysis/gray_areas.md
    │   ├── 环境差异: 原始版本 vs 实际版本
    │   ├── 代码改动: 原始代码 vs 适配后代码 (git diff)
    │   └── 参数假设: 论文未明确参数 vs 本次使用的值
    ├── 失败处理:
    │   ├── 代码 bug 无法绕过 → 创建 issue 记录，标记为 not_testable
    │   ├── 环境不可重建 → 切换到不同 OS/容器重试
    │   └── 如基线无法建立 → 标记为 not_testable，输出完整诊断
    └── 产出: analysis/gray_areas.md (含所有偏离记录)

3.4 基线锁定 / Baseline Lock
    ├── 记录 commit SHA / 代码快照
    ├── 运行复现锁定:
    │   ├── conda-lock.yml 或 requirements-locked.txt
    │   ├── Manifest.toml (Julia)
    │   └── env/system-packages.txt
    └── 产出 reproducibility_manifest.json (更新)
```

---

## 阶段 4：增量实现 / Incremental Implementation (按需)

### 目标 / Objective
若无官方代码或需从零实现，按模块增量构建，每步验证。

### 输入 / Input
`analysis/paper_summary.json` + `results/baseline_metrics.json`

### 输出 / Output
`implementation/implementation_log.md` + `implementation/delta_report.json`

### 步骤 / Steps

```
4.1 模块拆解 / Module Decomposition
    ├── 将方法拆分为功能模块 (DAG依赖图)
    ├── 定义每个模块的输入/输出接口
    └── 拓扑排序确定实现顺序

4.2 增量实现循环 / Incremental Implementation Loop
    └── 每步循环:
        1. 实现一个模块 (指向论文公式/算法编号)
        2. 快速验证 (小规模测试)
        3. 对比基线
        4. 记录增量偏差 delta
        5. 如 delta 异常 → 排查 → 修复 → 重测
        6. 确认后进入下一模块

4.3 代码管理 / Code Management
    ├── Git 版本控制 (每个模块独立 commit)
    ├── 每个函数/类添加 docstring 标注论文出处
    └── 命名规范遵循领域习惯
```

---

## 阶段 5：实验验证与统计分析 / Experiment Execution & Statistical Verification

### 目标 / Objective
统计验证实验结果的可靠性。

### 输入 / Input
可运行代码 + `results/tolerance_spec.json`

### 输出 / Output
`results/raw_metrics.csv` + `reports/verdict.json` + `results/figures/` (图表 + 生成代码)

### 步骤 / Steps

```
5.1 多轮运行 / Multi-Seed Execution
    ├── 🔴 CHECKPOINT: 确认实验参数和运行次数
    │   ├── 基线代码可用? (Phase 3 已通过 → 继续)
    │   ├── 随机种子数: 默认 N=5 (可自定义)
    │   ├── 预期运行时间: 根据测试运行估算
    │   └── GPU 已启用? (检查 infra/gpu_manifest.json)
    ├── 设置 N 个随机种子 (默认 N=5)
    ├── 每轮独立执行
    └── 记录所有指标到 results/raw_metrics.csv

5.2 统计计算 / Statistical Computation
    ├── 对每个指标计算:
    │   ├── 样本均值 x̄
    │   ├── 样本标准差 s
    │   └── 95% t-置信区间: x̄ ± t_{0.025, N-1} · s/√N
    └── 记录到 results/statistical_summary.json

5.3 结果判决 / Verdict (五态)
    ├── within_ci: 论文声称值在95%CI内 → ✓ 复现成功
    ├── close_outside_ci: 在CI外但在容忍度内 → ≈ 部分复现
    ├── outside_tolerance: 在CI外且超容忍度 → ✗ 未复现
    ├── not_testable: 环境/依赖问题无法运行 → ⚠ 待处理
    └── static_check_failed: 静态检查未通过 → ✗ 配置错误

5.4 诊断输出 / Diagnostic Output
    ├── 失败时生成 ≥2 条诊断假说
    ├── 链接到 Top-12 复现失败模式
    ├── 引用 Phase 1.4-C 审稿人视角发现的问题点 (如适用)
    ├── 交叉对比审稿人视角的"方法论评估"与实际复现偏差
    └── 写入 reports/diagnosis.md 和 reports/diagnosis.zh.md

5.5 图表生成与代码导出 / Figure Generation with Code Export
    ├── 检测是否需输出图表 (用户要求或论文有图表对比):
    │   ├── 若用户明确要求生成实验图表，或复现报告含图表对比需求
    │   └── 若无图表需求可跳过此步骤
    ├── 图表生成:
    │   ├── 收敛曲线 / 损失曲线 (convergence.png / convergence.pdf)
    │   ├── 指标对比柱状图 / 箱线图 (comparison.png)
    │   ├── 消融实验对比图 (ablation.png)
    │   ├── 散点图 / 热力图 (如适用, scatter.png / heatmap.png)
    │   └── 格式: PNG (嵌入报告) + PDF (出版级)
    ├── 图表源码同步导出 / Figure Code Export:
    │   ├── 每个图必须附带一个可独立运行的生成脚本:
    │   │   ├── results/figures/code/plot_convergence.py → convergence.png
    │   │   ├── results/figures/code/plot_comparison.py → comparison.png
    │   │   └── results/figures/code/plot_ablation.py → ablation.png
    │   ├── 脚本规范:
    │   │   ├── 自包含: 单独 python plot_*.py 即可复现对应图
    │   │   ├── 数据来源: 从 results/raw_metrics.csv 读取或硬编码关键数据
    │   │   ├── 可重现: 固定随机种子, 记录 matplotlib/seaborn 版本
    │   │   ├── 注释: 标注论文对应图号/表号
    │   │   └── 样式: 对齐论文的配色/字体/线型 (从论文截取风格采样)
    │   └── 验证: python results/figures/code/plot_convergence.py → 输出一致
    └── 产出:
        ├── results/figures/*.png / *.pdf (图表)
        └── results/figures/code/plot_*.py (图表生成代码)
```

### Top-12 复现失败模式 / Top-12 Reproduction Failure Modes

| # | 失败模式 | 诊断线索 | 修复方向 |
|---|---------|---------|---------|
| 1 | 代码/数据缺失 | 文件不存在 | 搜索补充源 |
| 2 | 环境漂移 | 版本不匹配 | 用锁文件重建 |
| 3 | CUDA版本冲突 | nvidia-smi vs conda list | 统一CUDA工具包 |
| 4 | 编译器ABI不兼容 | GCC版本不一致 | update-alternatives |
| 5 | 包依赖冲突 | conda solver挂起 | 单通道/一次安装 |
| 6 | 非确定性 | 多轮结果差异大 | 固定种子+确定性算法 |
| 7 | BLAS变体差异 | MKL vs OpenBLAS | 固定BLAS实现 |
| 8 | 跨平台路径 | Windows路径在Linux失效 | 使用WSL2/VM |
| 9 | 数据泄露 | 训练/测试集重叠 | 验证数据划分 |
| 10 | 预训练权重漂移 | 权重版本不一致 | 固定SHA-256 |
| 11 | 选择性报告 | 仅报告最优种子 | 统计性多轮验证 |
| 12 | 上游依赖位腐 | 包API变更 | 版本锁定+隔离 |

---

## 阶段 6：双语报告生成 / Bilingual Report Generation

### 目标 / Objective
生成所有实验数据报告和结果对比的中英双语版本。

### 输入 / Input
所有阶段产出的结构化数据。

### 输出 / Output
`reports/` 目录下的中英双语文档。

### 步骤 / Steps

```
🔴 CHECKPOINT: 确认所有数据就绪再生成报告
├── Phase 5 判决产出? (reports/verdict.json)
├── Phase 5.5 图表就绪? (results/figures/*.png)
├── Phase 1.4 三方审阅就绪? (analysis/*_review.md)
└── 所有路径正确? (检查 relative path 一致性)
```

### 文档清单 / Document Inventory

每个文档必须同时生成 `.md` (英文) 和 `.zh.md` (中文) 两个版本:

```
reports/
├── reproduction_report.md          # 完整复现报告 (EN)
├── reproduction_report.zh.md       # 完整复现报告 (ZH)
├── comparison_table.md             # 实验结果对比表 (EN)
├── comparison_table.zh.md          # 实验结果对比表 (ZH)
├── verdict.json                    # 判决结果 (JSON, 中英双语字段)
├── diagnosis.md                    # 诊断分析 (EN)
├── diagnosis.zh.md                 # 诊断分析 (ZH)
├── RUN_SUMMARY.md                  # 运行摘要 (EN)
├── RUN_SUMMARY.zh.md               # 运行摘要 (ZH)
└── html/                           # (可选) HTML 格式版本
    ├── report_en.html
    └── report_zh.html
```

### 报告生成规范 / Report Generation Specification

#### 格式要求 / Format Requirements

1. **标题**: 英文标题 + 空行 + 中文标题
2. **表格**: 列标题用英文，主表格列头含双语括号注释: `Metric / 指标`
3. **数值**: 统一格式，小数位数一致
4. **图表标题**: 英文在上/中文在下，或使用 `(EN) / (ZH)` 标注

#### 完整复现报告模板 / Reproduction Report Template

参见: `templates/reproduction_report.template.md`

```markdown
# Reproduction Report: [Paper Title]
# 复现报告：[论文标题]

## 1. 元信息 / Metadata

| Field / 字段 | Value / 值 |
|-------------|------------|
| Paper / 论文 | [title] |
| Authors / 作者 | [authors] |
| Venue / 发表 | [conference/journal] |
| Reproduction Date / 复现日期 | [YYYY-MM-DD] |
| Host OS / 宿主系统 | [OS info] |
| Runtime / 运行环境 | [env summary] |

## 2. 判决结果 / Verdict

| Metric / 指标 | Paper Claim / 论文值 | Reproduced / 复现值 | 95% CI | Verdict / 判决 |
|---------------|---------------------|--------------------|--------|---------------|
| [metric_1]    | [value]             | [value]            | [CI]   | ✅ within_ci  |
| [metric_2]    | [value]             | [value]            | [CI]   | ⚠️ close_outside_ci |

## 3. 环境摘要 / Environment Summary

[infra_manifest.json 关键字段展示]

## 4. 实验结果对比 / Results Comparison

| Metric | Paper | This Run | Δ(%) | Verdict |
|--------|-------|----------|------|---------|
| ...    | ...   | ...      | ...  | ...     |

| 指标 | 论文值 | 本次复现 | 偏差(%) | 判决 |
|-----|-------|---------|---------|------|
| ...  | ...   | ...     | ...     | ...  |

## 5. 诊断与讨论 / Diagnosis & Discussion

[详细诊断信息，中英双语]

## 6. 锁定文件 / Lock Files

- `env/conda-lock.yml`
- `env/requirements-locked.txt`
- `env/reproduction_manifest.json`
```

#### 对比表模板 / Comparison Table Template

表格必须并行展示中英文:

| Metric / 指标 | Paper / 论文 | Reproduced / 复现 | Δ(%) | Within Tol? / 在容忍度内? |
|---------------|-------------|-------------------|------|-------------------------|
| Accuracy      | 92.5%       | 91.8%             | -0.8 | ✅ Yes / 是              |
| F1-Score      | 0.893       | 0.901             | +0.9 | ✅ Yes / 是              |

#### 运行摘要模板 / RUN_SUMMARY Template

```
# RUN SUMMARY
# 运行摘要

Paper / 论文: [title]
Date / 日期: [YYYY-MM-DD]
Status / 状态: ✅ Reproduced / 复现成功

## Key Results / 关键结果
[table with bilingual headers]

## Environment / 环境
- Python: [version]
- CUDA: [version]
- GPU: [model]
- RAM: [size]

## Artifacts / 制品
- `reports/reproduction_report.md` (EN)
- `reports/reproduction_report.zh.md` (ZH)
- `results/raw_metrics.csv`
```

---

## 阶段 7：制品打包与溯源 / Artifact Packaging & Provenance

### 目标 / Objective
打包完整可重现的证据包，建立可追溯的溯源链。

### 输入 / Input
所有阶段产物。

### 输出 / Output
`dist/artifact_bundle.zip` + `dist/provenance_chain.json`

### 步骤 / Steps

```
7.1 证据包构建 / Artifact Bundle
    ├── 🔴 CHECKPOINT: 确认证据包完整性
    │   ├── 代码快照就绪? (git commit SHA)
    │   ├── 环境锁文件完整? (env/conda-lock.yml + requirements-locked.txt)
    │   ├── 三方审阅已包含? (analysis/*_review.md)
    │   ├── 中英双语报告配对? (reports/*.md + *.zh.md)
    │   └── 图表代码自包含? (results/figures/code/plot_*.py)
    ├── 代码快照 (Git commit SHA + diff)
    ├── 环境锁定文件 (conda-lock / Manifest.toml / system-packages)
    ├── 基础设施检测 (infra/infra_manifest.json)
    ├── 版本锁定 (env/reproduction_manifest.json)
    ├── 运行日志 (logs/)
    ├── 原始结果 (results/raw_metrics.csv + 图)
    ├── 三方审阅 (analysis/*_review.md + reproducibility_assessment.json)
    ├── 双语报告 (reports/*.md + reports/*.zh.md)
    └── 打包: dist/reproduction_<paper>_<date>.zip

7.2 溯源链构建 / Provenance Chain
    ├── 每条从输入→处理→输出的溯源记录:
    │   ├── 代码版本 → 运行参数 → 日志 → 指标 → 图表
    │   └── 每条记录含 SHA-256 内容哈希
    └── 写入 dist/provenance_chain.json

7.3 (可选) 签名存证 / Optional: Sign & Attest
    ├── GPG 签名证据包
    ├── 生成 ACM Badge 兼容的存证:
    │   ├── artifacts_available
    │   ├── artifacts_evaluated_functional
    │   └── results_reproduced
    └── 可选: 提交到公共复现账本
```

---

## 领域路由表 / Domain Routing Table

| 领域 Domain | 验证方式 Verification | 典型工具 Tools | 注意事项 Notes |
|------------|---------------------|---------------|---------------|
| 数值计算 Numerical Computing | 容忍度+CI / Tolerance + CI | PETSc, FEniCS, deal.II, OpenFOAM, MFEM | BLAS变体影响浮点结果; 网格划分影响一致性 |
| 符号代数 Symbolic Algebra | 等价性检查 / Equivalence Check | OSCAR, SageMath, Mathematica, SymPy, Singular | 版本需精确匹配; CAS版本影响Groebner基结果 |
| AI4Math | 统计验证+消融 / Stats + Ablation | PyTorch, JAX, TensorFlow, DeepXDE, SciML | CUDA+cuDNN版本敏感; 随机种子管理 |
| 统计 Statistics | CI+假设检验 / CI + Hypothesis Test | R, Julia, SciPy, Stan, PyMC | MCMC链收敛诊断; 随机数生成器版本 |
| 优化 Optimization | 收敛曲线+目标值 / Convergence + Objective | JuMP, Gurobi, MOSEK, CVXPY, NLopt | 求解器版本影响; 许可限制 |

---

## 质量门禁总表 / Quality Gates Summary

| # | 门禁 Gate | 阶段 Phase | 通过条件 |
|--|----------|-----------|---------|
| G0 | 基础设施就绪 + 可行性预判 | Phase 0 | infra_manifest.json 包含完整宿主信息; feasibility_precheck.json 标记可行性 |
| G00 | GPU配置完成 | Phase 0.9 | gpu_manifest.json 记录GPU信息; 有独显时框架检测通过 |
| G01 | **可复现性评估** | **Phase 1.4 → Phase 2** | reproducibility_assessment.json 中 recommendation 为 proceed 或 proceed_with_caution; 若为 needs_human_approval 或 discourage 需用户确认 |
| G1 | 版本一致 | Phase 0.5 | 所有运行时版本与 version_spec.json 一致 |
| G2 | 论文理解 + 三方审阅 | Phase 1 | paper_summary.json 通过审查; reproducibility_assessment.json 可用; 至少一份审阅报告就绪 |
| G3 | 环境就绪 | Phase 2 | 基础导入测试通过 |
| G4 | 基线建立 | Phase 3 | 基线指标与论文差距在容忍度内 |
| G5 | 增量验证 | Phase 4 (按需) | 每个模块 delta 在预期范围内 |
| G6 | 统计验证 | Phase 5 | 五态判决产出 |
| G66 | 图表代码导出 | Phase 5.5 | 有图表输出时, 每图有对应的独立可运行源码 |
| G7 | 双语报告 | Phase 6 | 所有报告均有中英文双版本; 如有三方审阅则包含交叉对比章节 |
| G8 | 制品完整 | Phase 7 | 证据包完整性校验通过 |

---

## 标准化文件结构 / Standardized Directory Structure

```
reproduction/
├── SKILL.md                          # 本流程文档
├── skills/registry.yaml              # Skill 注册表
├── infra/                            # 基础设施
│   ├── infra_manifest.json            # 宿主检测结果
│   ├── Vagrantfile                    # VM定义
│   ├── Dockerfile                     # 容器定义
│   └── apptainer.def                  # HPC容器定义
├── provisioning/                      # 配置脚本
│   ├── playbook.yml                   # Ansible playbook
│   ├── install_version_managers.sh    # 版本管理器安装
│   ├── install_cuda.sh                # CUDA安装
│   └── install_hpc.sh                 # HPC库安装
├── env/                               # 环境锁定
│   ├── version_spec.json              # 版本需求声明
│   ├── reproduction_manifest.json     # 完整复现清单 (锁定)
│   ├── conda-lock.yml                 # Conda锁定
│   ├── requirements-locked.txt        # pip锁定
│   ├── Manifest.toml                  # Julia锁定
│   ├── system-packages.txt            # 系统包清单
│   └── environment.yml                # Conda环境定义
├── analysis/                          # 论文分析
│   ├── paper_summary.json             # 论文摘要
│   ├── parsed_text.md                 # 解析后文本 (MinerU 输出 .md / 后备 .txt)
│   ├── formulas.tex                   # 提取的公式
│   ├── gray_areas.md                  # 灰色地带标记
│   ├── <paper>_student_review.md      # 研究生视角审阅
│   ├── <paper>_advisor_review.md      # 导师视角审阅
│   ├── <paper>_reviewer_review.md     # 审稿人视角审阅
│   ├── reproducibility_assessment.json # 可复现性评估 (G0门禁输入)
│   ├── review_manifest.json           # 三方审阅清单
│   └── templates/                     # 审阅报告模板 (见 templates/)
├── code/                              # 代码 (Git repo)
├── logs/                              # 运行日志
│   ├── run_baseline.log
│   ├── run_experiment_*.log
│   └── run_smoke_test.log
├── infra/gpu_manifest.json            # GPU配置检测结果
├── results/                           # 实验结果
│   ├── baseline_metrics.json          # 基线指标
│   ├── tolerance_spec.json            # 容忍度设定
│   ├── raw_metrics.csv                # 所有种子原始指标
│   ├── statistical_summary.json       # 统计分析
│   └── figures/                       # 实验图表
│       ├── convergence.png            # 收敛曲线图
│       ├── comparison.png             # 指标对比图
│       └── code/                      # 图表生成代码 (自包含可独立运行)
│           ├── plot_convergence.py    # → convergence.png
│           ├── plot_comparison.py     # → comparison.png
│           └── requirements.txt       # 绘图依赖
├── reports/                           # 双语报告
│   ├── reproduction_report.md         # 完整报告 (EN)
│   ├── reproduction_report.zh.md      # 完整报告 (ZH)
│   ├── comparison_table.md            # 对比表 (EN)
│   ├── comparison_table.zh.md         # 对比表 (ZH)
│   ├── verdict.json                   # 判决 (双字段)
│   ├── diagnosis.md                   # 诊断 (EN)
│   ├── diagnosis.zh.md                # 诊断 (ZH)
│   ├── RUN_SUMMARY.md                 # 摘要 (EN)
│   ├── RUN_SUMMARY.zh.md              # 摘要 (ZH)
│   └── html/                          # HTML版本
├── implementation/                    # (增量实现时)
│   ├── implementation_log.md          # 实现日志
│   └── delta_report.json              # 增量偏差报告
└── dist/                              # 发布制品
    ├── artifact_bundle.zip
    └── provenance_chain.json
```

---

## 决策词汇表 / Decision Vocabulary

用于审批流程的标准响应:

| 操作 | 英文 | 中文 |
|------|------|------|
| 批准 | approve / ok / yes | 可以 / 好的 / 继续 / 同意 / 批准 |
| 修订 | revise | 修改 / 改一下 |
| 拒绝 | reject | 拒绝 / 不行 |
| 跳过 | skip | 跳过 / 跳过这个 |

风险分级:
- **低** Low: 只读分析，无需审批
- **中** Medium: 运行前需计划审批
- **高** High: 逐条审批

---

## 反例与黑名单 / Anti-Patterns & Blacklist (dim9)

以下是在复现流程中反复踩到的陷阱，必须避免：

| # | 反模式 / Anti-Pattern | 后果 / Consequence | 正确做法 / Correct Approach |
|---|----------------------|-------------------|---------------------------|
| 1 | **MinerU token 未配置就执行 Phase 1.1** | 脚本报 401 错误，用户困惑 | 先检查 `~/.mineru/config.yaml`，未配置则引导用户前往 https://mineru.net/apiManage/token 获取 |
| 2 | **Windows 上直跑 Linux 路径的脚本** | `\r\n` 换行符破坏 shell 脚本，路径分隔符不兼容 | 使用 WSL2 或 `scripts/enable_gpu.ps1` 等 Windows 原生脚本 |
| 3 | **Phase 0.5 先装包再装语言运行时** | Conda/pip SAT 求解器死锁，版本冲突 | 严格按 语言运行时 → 版本管理器 → 锁定 → 包的顺序 |
| 4 | **Phase 5.1 只跑一个种子就下判决** | 非确定性被忽略，判决不可信 | 至少 N=5 个种子，用 95% CI 做统计判决，不用单次结果 |
| 5 | **Phase 6 只生成英文报告** | 中文用户/审稿人无法阅读 | 每份报告必须同时生成 `.md`(EN) 和 `.zh.md`(ZH)，双语表格表头用 `Metric / 指标` 格式 |
| 6 | **Phase 1.4 跳过三方审阅直接进 Phase 2** | 论文理解不充分，复现方向错误 | 必须跑完 Phase 1.4，至少获得 reproducibility_assessment.json 后再过 G01 门禁 |
| 7 | **Phase 5.5 导出图表时不导出生成代码** | 图表无法独立复现，违背 FAIR 原则 | 每张图必须附带可独立运行的 `results/figures/code/plot_*.py` |
| 8 | **Phase 0.2 跳过可行性预判直接上环境** | 遇到私有数据/专利代码/特定硬件时大量浪费 | Phase 0.2 先做快速可行性标记，Phase 1.4 再做精确的可复现性评估 |
| 9 | **Phase 3.4 不生成锁文件** | 环境漂移后无法精确重建，复现失败 | 每步环境配置后必须产生锁文件 (conda-lock / Manifest.toml / renv.lock) |
| 10 | **Phase 2 依赖用 pip 和 conda 混合一次性安装** | SAT 求解器死锁，或隐式覆盖 | 严格 conda → pip 顺序，单步验证，锁定后再安装下一个 |

---

| 依赖 / Dependency | 用途 / Purpose | 安装方式 / Install |
|------------------|---------------|-------------------|
| mineru-open-sdk | PDF → Markdown 解析 (含公式/表格识别) | `pip install mineru-open-sdk` |
| openai | 三方视角审阅的 LLM 调用后端 | `pip install openai` |
| pyyaml | MinerU 配置文件解析 | `pip install pyyaml` |

LLM 调用通过环境变量配置:

| 环境变量 / Env Var | 用途 / Purpose | 默认值 / Default |
|-------------------|---------------|-----------------|
| `LLM_API_KEY` | LLM API 密钥 | (必填) |
| `LLM_API_BASE` | API 端点 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o` |

### 首次使用前的快速配置 / Quick Setup Before First Use

```bash
# 1. MinerU token 配置
mkdir -p ~/.mineru
# 编辑 ~/.mineru/config.yaml，写入:
#   token: '你的API密钥'
# 若密钥: https://mineru.net/apiManage/token

# 2. 安装依赖
pip install mineru-open-sdk openai pyyaml

# 3. 配置 LLM API (三方视角审阅)
export LLM_API_KEY='your-key'
```

---

## 引用 / References

- MaRDI Mathematical Research Data Initiative. https://www.mardi4nfdi.de/
- ICERM Workshop on Reproducibility in Computational and Experimental Mathematics (2012). *Setting the Default to Reproducible*.
- ConanXu-math/Scientific-Computing-Reproduction---Auto-Tuning. https://github.com/ConanXu-math/Scientific-Computing-Reproduction---Auto-Tuning
- OpenResearch. https://github.com/armaanamatya/openresearch
- paper-replay. https://github.com/bettyguo/paper-replay
- repro-agent. https://github.com/hqygtr-prog/repro-agent
- MaRDIFlow: A Workflow Framework for Documentation and Integration of FAIR Computational Experiments. https://doi.org/10.52825/cordi.v1i.323
- repo2docker. https://repo2docker.readthedocs.io/
- Apptainer. https://apptainer.org/
