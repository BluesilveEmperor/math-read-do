---
name: math-read-do
description: >-
  数学文献实验复现标准化工作流 / Standardized Math Paper Reproduction Pipeline
  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析(含公式/表格/图表) →
  按用户指定视角输出审阅报告(研究生/导师/审稿人) →
  环境重建 → 基线验证 → 增量实现 → 统计验证(五态判决+95%CI) → 双语报告。
  覆盖数学全领域：纯数学、应用数学、统计学、运筹学、计算数学、AI4Math等。
  支持 Python(R/Python) / C++(CUDA/OpenGL) 多语言生态。
  每份报告必须中英双语。

  领域自适应路由：自动检测项目语言生态 (Python vs C++/CUDA)，匹配对应的环境构建、
  依赖管理、增量实现和产出物验证策略。C++/CUDA 项目自动启用 vcpkg + MSBuild 链路、
  OBJ 模型质量基线和 GPU kernel 性能剖析。

  集成三大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：出版级图表生成 (Python/R, Nature/CNS 风格)
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)

  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现,
  重现论文, 论文重现, 数值复现, 论文复现, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 重现结果, 重现图表, 复现结果, 复现图表,
  reproducibility check, 可复现性评估, 复现验证

  # C++/CUDA mesh/geometry triggers
  网格简化, mesh simplification, QEM, quadric error metrics, 面片简化, 减面,
  GPU简化, CUDA网格, .obj简化, 模型LOD, geometry processing, 几何处理,
  mesh decimation, 点云简化, surface simplification, OpenGL网格,
  CUDA kernel, nvcc, vcpkg, MSBuild

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
  # C++/CUDA 生态 (Phase 0/2/3/4/5 自适应启用)
  - CUDA Toolkit >= 12.0 (nvcc, nvidia-smi, Nsight Compute)
  - Visual Studio 2022 (MSBuild v145+, PlatformToolset)
  - vcpkg (C++ 包管理器, x64-windows-static triplet)
  - GLM, GLEW, GLFW3, SDL2 (3D 图形管线依赖)
  - Hausdorff 距离计算工具 (mesh-to-mesh comparison: MeshLab/PyMeshLab/libigl)
  - Wavefront OBJ (.obj) 格式读写支持
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

## 核心原则 / Core Principles

1. **双语输出**: 所有报告必须有中英双版本 (`.md` 英文 + `-CN.md` 中文)
2. **增量验证**: 每添加一个模块即验证一次
3. **可审计**: 每步产生结构化产物，溯源链完整
4. **人机协同**: 风险分级审批
5. **锁定即契约**: 版本/环境/依赖每步锁定，不信任隐式继承
6. **先问后做**: 用户无指令时先主动提问，确认操作后再执行

## 领域自适应路由 / Domain-Adaptive Routing

本技能启动时，自动检测项目类型并匹配对应的子策略：

### 检测矩阵 / Detection Matrix

| 检测信号 | Python 生态 | C++/CUDA 生态 | C++/3D 图形生态 |
|---------|------------|--------------|----------------|
| 入口文件 | `requirements.txt`, `setup.py`, `pyproject.toml`, `environment.yml` | `.vcxproj`, `CMakeLists.txt`, `Makefile`, `.cu` 文件 | `.vcxproj` + OpenGL/GLEW/GLFW 依赖 |
| GPU 类型 | `torch.cuda`, `cupy`, `tensorflow` | `cuda_runtime.h`, `nvcc`, `cudaMalloc` | CUDA + GLM + `GL/glew.h` |
| 构建系统 | pip/conda/poetry | MSBuild/CMake/Make | MSBuild + vcpkg |
| 包管理 | pip/conda/mamba | vcpkg/conan/apt | vcpkg x64-windows-static |
| 产出物 | 数值结果 (CSV/NPZ) / 图表 | 可执行文件 + 性能数据 | .obj 模型 + 渲染截图 |

### 路由决策 / Routing Decision

```
检测到 .vcxproj + .cu + GLEW/GLM → "C++/CUDA/3D 图形" 子策略
   ├─ Phase 0: 增加 CUDA Toolkit + MSBuild + vcpkg 检测
   ├─ Phase 2: vcpkg 环境构建替代 conda
   ├─ Phase 3: 增加 OBJ 模型质量基线 (Hausdorff / 法线偏差 / 体积比)
   ├─ Phase 4: C++ 编译单元增量 + CUDA kernel 性能验证
   ├─ Phase 5: 增加 3D 质量度量 (Hausdorff distance, normal deviation, volume ratio)
   └─ Phase 6: 增加 实验模型/ 产出物目录

检测到 .py + torch → "Python ML" 子策略 (默认, 无变更)

检测到 .R + renv.lock → "R 统计" 子策略
```

### 关键差异速查 / Key Divergence Quick-Ref

| 维度 | Python 默认路径 | C++/CUDA/3D 路径 |
|------|---------------|------------------|
| 环境构建 | conda create + pip install | vcpkg install + MSBuild |
| 构建验证 | `python -c "import X"` | `MSBuild .sln /t:Build /p:Configuration=Release` |
| 确定性配置 | `PYTHONHASHSEED` + torch seed | `CUBLAS_WORKSPACE_CONFIG` + CUDA deterministic |
| 基线指标 | RMSE/MAE/Accuracy | Hausdorff distance / normal deviation / volume ratio |
| 模块验证 | `python -c "from mod import *; test()"` | MSBuild 编译 + 单元测试运行 |
| GPU 验证 | `torch.cuda.is_available()` | `nvidia-smi` + `nvcc --version` + 测试程序运行 |
| 增量单元 | Python .py 文件 | C++ .cpp / CUDA .cu 编译单元 |
| 核心产出 | 数值指标 + 图表 | .obj 模型文件 + 数值指标 + 渲染截图 |

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
| 14 | C++/CUDA 项目用 pip 装依赖 | 缺少 C++ 编译工具链 | 检测 .vcxproj/.cu → 自动切 vcpkg+MSBuild 路径 |
| 15 | CUDA kernel 不验证 CPU 等价性 | GPU 结果可能存在数值偏差 | 每个 kernel 必须有 CPU reference 实现对比 |
| 16 | 3D 模型复现只跑一种简化率 | 无法评估算法鲁棒性 | 至少 5 种简化率 (90%/70%/50%/30%/10%) |
| 17 | 导出 .obj 不附带原始模型 | 无法追溯对比 | 复现产出必须同时归档 original/ 和 simplified/ |
| 18 | MSBuild 构建不锁定 PlatformToolset | 不同 VS 版本 ABI 不兼容 | 锁定 v145 (VS2022)，写入 env/build_config.json |

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| 0 | 宿主检测→环境构建→GPU配置 (C++: +CUDA Toolkit+MSBuild+vcpkg) | `infra_manifest.json` | G0: 基础设施就绪 |
| 0.5 | 版本检测→安装→锁定→验证 (C++: +nvcc版本+MSVC工具集) | `version_spec.json` | G1: 版本一致 |
| 1 | PDF解析→结构化提取→领域分类→三方审阅 (图形学: +公式→代码映射) | `reproducibility_assessment.json` | G01: 可复现性门禁 |
| 2 | 依赖扫描→环境构建→确定性配置→验证 (C++: vcpkg→MSBuild→CUDA确定性) | `conda-lock.yml` / `vcpkg_manifest.json` | G3: 环境就绪 |
| 3 | 官方代码运行→指标对齐→失败诊断→锁定 (3D: +OBJ质量基线) | `baseline_metrics.json` | G4: 基线建立 |
| 4 | 模块拆解→增量实现→代码管理 (C++: 编译单元+Kernel验证) | `delta_report.json` | -- |
| 5 | 多轮运行→统计计算→五态判决→图表导出 (3D: +Hausdorff/法线/体积) | `判决结果.json` | 5.1 参数确认 |
| 6 | 数据就绪检测→双语报告生成(含模板) (3D: +实验模型归档) | `实验复刻结果汇总/实验报告/复现报告.md` + `-CN.md` | 数据就绪 |
| 7 | 最终整理→完整性确认 (3D: +OBJ模型配对检查) | `实验复刻结果汇总/` 完整目录 | 文件就位确认 |

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

### Phase 0-CXX: C++/CUDA/3D 项目专属检测 / C++/CUDA/3D-Specific Detection

**触发条件**: 检测到 `.vcxproj` + `.cu` 文件 或 GLM/GLEW/OpenGL 依赖

0-CXX.1 **CUDA 工具链检测**:
    - `nvidia-smi` → GPU 型号、驱动版本、CUDA 版本
    - `nvcc --version` → CUDA Toolkit 版本 (要求 >= 12.0)
    - 确认 compute capability (如 A6000 = sm_86, RTX 4090 = sm_89)
    - 产出: `infra/cuda_manifest.json`

0-CXX.2 **MSBuild 编译器检测**:
    - 定位 VS2022: `"C:\Program Files\Microsoft Visual Studio\2022"` 或 vswhere.exe
    - 确认 PlatformToolset: v145 (VS2022)
    - 确认平台: x64
    - 产出: `infra/compiler_manifest.json`

0-CXX.3 **vcpkg 包管理器检测**:
    - `vcpkg --version` → 已安装确认
    - 检测 triplet: x64-windows-static
    - 如缺失: 引导用户 `git clone https://github.com/Microsoft/vcpkg.git && bootstrap-vcpkg.bat`
    - 产出: `infra/vcpkg_manifest.json`

0-CXX.4 **3D 图形依赖扫描**:
    - 扫描 `.vcxproj` 中的 `<AdditionalDependencies>` 提取: glew, glfw3, SDL2, opengl32, glm
    - 区分 bundled (项目内 `res/libs/`) vs system (vcpkg 安装)
    - 记录头文件路径 (`AdditionalIncludeDirectories`)
    - 产出: `infra/dependency_manifest.json`

**G0-CXX**: CUDA Toolkit + MSBuild + vcpkg + 3D 依赖全部就绪。任一缺失→返回修复。

---

### Phase 0.5: 版本管理 / Version Management

**输入**: `infra/infra_manifest.json` + 版本线索
**输出**: `env/version_spec.json` + `env/reproduction_manifest.json`

0.5.1 **需求检测**: 扫描 `.python-version` / `Manifest.toml` / `.Rprofile` / `.nvmrc` / `CMakeLists.txt` 等
    - **C++/CUDA 项目**: 额外扫描 `.vcxproj` 中的 `<PlatformToolset>`, `<CUDA 版本号>.props`, `<CodeGeneration>` 标记
0.5.2 **版本管理器**: pyenv/juliaup/rig/nvm/sdkman/rustup (缺失则自动安装)
    - **C++ 工具链**: 检测 `$(CUDA_PATH)` 环境变量 → nvcc 版本; 检测 MSVC 工具集版本 (v145=VS2022); 检测 Windows SDK 版本
0.5.3 **版本安装**: pyenv install / juliaup add / rig add / nvm install / conda cudatoolkit / apt gcc 等
0.5.4 **版本锁定**: conda env export → `conda-lock.yml`; pip freeze → `requirements-locked.txt`; 复制 `Manifest.toml`; dpkg 快照
    - **C++/CUDA 项目**: 生成 `env/cuda_version.json` (包含 toolkit 版本, driver 版本, compute capability, nvcc flags); 生成 `env/build_config.json` (PlatformToolset, Configuration, Platform, CUDA CodeGeneration)
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
    - **图形学/几何处理论文**: 额外提取
      * 算法类型: mesh_decimation / subdivision / remeshing / smoothing / parametrization
      * 并行识别: 标注算法的 embarrassingly parallel / topology-dependent / sequential 阶段
      * 公式→代码映射: 论文公式编号 → 预期数据结构/函数
      * 输入/输出格式: .obj / .ply / .stl / .off
      * 质量度量: Hausdorff distance / normal deviation / volume preservation / visual fidelity
    - 产出追加: `analysis/qem_algorithm_notes.md` (仅当领域分类为 computer_graphics 时)
1.3 **领域分类**: 关键词+依赖 → 路由到数值/符号/AI4Math/统计/优化/经济/**图形学**子策略

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
    - `proceed` → 直接进 Phase 2
    - `proceed_with_caution` → 进 Phase 2, 记录已知风险
    - `needs_human_approval` → STOP: 展示风险标记, 获取用户确认
    - `discourage` → STOP: 不建议复现, 展示理由

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

### Phase 2-CXX: C++/CUDA 环境构建 / C++/CUDA Environment Setup

**触发条件**: 领域自适应路由判定为 C++/CUDA/3D 生态

2-CXX.1 **依赖扫描 (vcpkg)**:
    - 从 `.vcxproj` 的 `<AdditionalDependencies>` 提取依赖列表
    - 从项目 `res/libs/` 区分 bundled vs system 依赖
    - vcpkg manifest 模式: 生成 `vcpkg.json` (如项目未提供)
    - 示例 vcpkg.json:
    ```json
    {
      "name": "mesh-simplification",
      "version": "1.0.0",
      "dependencies": ["glew", "glfw3", "sdl2", "glm"]
    }
    ```

2-CXX.2 **环境构建 (vcpkg + MSBuild)**:
    - `vcpkg install --triplet x64-windows-static` → 安装所有 C++ 依赖
    - 如项目已自带部分 lib (bundled): 仅安装缺失项
    - 确认 CUDA Toolkit 路径: `$(CUDA_PATH)` 环境变量或默认 `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.2`
    - MSBuild 构建: `MSBuild MeshSimplification.sln /t:Build /p:Configuration=Release /p:Platform=x64`

2-CXX.3 **确定性配置 (C++/CUDA)**:
    - CUDA: 禁 fast math (`--use_fast_math` 关闭) → 确保数值可复现
    - MSVC: `/fp:precise` (非 `/fp:fast`) → IEEE 754 浮点
    - 锁定 compute capability: `compute_86,sm_86` (匹配目标 GPU)
    - 环境变量: `CUBLAS_WORKSPACE_CONFIG=:4096:8`

2-CXX.4 **验证**:
    - MSBuild 编译通过 (Release x64)
    - 可执行文件能启动 (不 crash, 能加载测试 .obj)
    - nvidia-smi 确认 GPU 可用
    - CUDA kernel 能正常分配 device memory (cudaMalloc 不报错)
    - 产出: `env/vcpkg_manifest.json` + `env/build_config.json`

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

### Phase 3-CXX: 3D 模型质量基线 / 3D Model Quality Baselines

**触发条件**: 产出物包含 .obj 模型文件

3-CXX.1 **OBJ 输出验证**:
    - 确认简化后 .obj 文件可被标准工具 (MeshLab, Blender) 正确读取
    - 验证顶点坐标在合理范围内 (无 NaN/Inf)
    - 验证面片索引合法 (不越界, 无退化三角形)
    - 检查是否保留了原始 UV (`vt`) 和法线 (`vn`) 信息

3-CXX.2 **质量基线指标**:
    - **Hausdorff 距离**: 原始模型与简化模型之间的最大/平均/RMS 距离
      * 工具: MeshLab (`meshlabserver -i orig.obj -i simpl.obj -s hausdorff.mlx`)
      * 容忍度: 最大 Hausdorff < 模型包围盒对角线的 2%
    - **法线偏差**: 简化后顶点法线与原始模型最近点法线的角度差
      * 容忍度: 平均偏差 < 5°
    - **体积保持率**: 简化模型体积 / 原始模型体积
      * 容忍度: 0.95 ~ 1.05
    - **退化面检测**: 面积 < 1e-8 的三角形数量 → 必须为 0

3-CXX.3 **GPU vs CPU 等价性验证**:
    - 同一模型、同一参数、CPU 路径 vs GPU 路径 → 逐顶点位置 delta
    - 容忍度: max(|delta|) < 1e-4 (单精度浮点误差范围)
    - 如超出 → 检查 GPU kernel 的数值精度 (atomicAdd 顺序、fast math 是否关闭)
    - 产出: `results/gpu_vs_cpu_delta.json`

3-CXX.4 **多模型基线矩阵**:
    - 测试模型集: 至少 3 种不同拓扑的 OBJ (如 bunny, cow, torus)
    - 每种模型记录: 原始顶点数/面数, 简化后顶点数/面数, 简化耗时, 质量指标
    - 产出: `results/multi_model_baseline.json`

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

### Phase 4-CXX: C++/CUDA 增量实现 / C++/CUDA Incremental Implementation

**触发条件**: 项目语言为 C++/CUDA

4-CXX.1 **模块拆解 (C++ 编译单元粒度)**:
    - 每个模块对应一个或一组 `.cpp` / `.cu` 文件
    - I/O 接口: 函数签名 + 数据结构 (struct/class) 定义
    - DAG 依赖图标注编译依赖关系 (#include 链)
    - 拓扑排序确保底层模块先编译验证
    - 产出: `implementation/modules_dag.json`

4-CXX.2 **增量循环 (C++ 编译 → 运行 → 对比 → commit)**:
    1. 实现/修改当前模块 (标注 Ref: Section X.Y, Eq.(Z))
    2. **编译验证**: `MSBuild MeshSimplification.sln /t:Build /p:Configuration=Release /p:Platform=x64`
       - 如编译失败 → 修复 → 回到第 2 步
    3. **运行测试**: 启动可执行文件, 处理测试模型
       - 验证 OBJ 输出正确可读
    4. **性能对比**: 使用 `std::chrono` profiler (代码中已有的) 对比模块优化前后耗时
       - CUDA kernel: 使用 `nvprof` 或 Nsight Compute 验证 GPU 耗时
    5. **正确性对比**: 模块优化前后 OBJ 输出逐顶点 delta 对比
       - delta > 容忍度 (1e-4) → 标记为性能/精度 trade-off → 记录到 delta_report
    6. **git commit** (含论文引用 + Delta 说明) → `implementation_log.md` → 下一模块

4-CXX.3 **CUDA Kernel 验证专项**:
    - 每个 `.cu` kernel 必须有对应的 CPU reference 实现
    - 数值对比: CPU 参考 vs GPU 输出, max delta < 1e-4
    - 性能剖析: `nvprof --print-gpu-trace ./app.exe` 记录 kernel 执行时间
    - 内存传输: 记录 cudaMemcpy H2D/D2H 耗时, 识别潜在 overlap 机会
    - 产出: `implementation/kernel_profiles.json`

4-CXX.4 **典型模块拆分示例 (QEM 网格简化)**:
    ```
    Module 0: Bug 修复 (initEdgeVector 边交换逻辑)           → 正确性保证
    Module 1: initVertexNeighbor O(V×E) → O(E) 优化          → 数据结构
    Module 2: vector+make_heap → priority_queue 增量更新     → 算法优化
    Module 3: calcEdgeError GPU 批量并行化 + 新增 .cu kernel → GPU 加速
    Module 4: CUDA atomicAdd → warp shuffle 归约优化         → Kernel 优化
    Module 5: 运行时参数化 (MAX_FACES → 命令行参数)           → 可用性
    Module 6: OBJ 导出完善 (保留 UV/法线 + 多级 LOD 输出)     → 产出质量
    ```

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

### Phase 5-CXX: 3D 模型实验矩阵与质量验证 / 3D Experiment Matrix & Quality Verification

**触发条件**: 产出物包含 .obj 模型文件

5-CXX.1 **实验矩阵设计**:
    ```
    模型  × 简化率      × 路径  × 种子  = 总实验数
    ─────────────────────────────────────────────
    5种   × 5档         × 2种   × 5个   = 250 次
    (bunny, (90%, 70%,   (CPU,   (N=5)
     cow,   50%, 30%,     GPU)
     foot,  10%)
     monkey,
     torus)
    ```
    - 每轮独立运行，输出独立的 OBJ 文件: `results/{model}_{path}_{ratio}_seed{N}.obj`
    - 记录: 耗时 (init / GPU compute / collapse loop), 输出面数, 文件大小

5-CXX.2 **质量度量计算**:
    - **Hausdorff 距离**: MeshLab CLI 批量计算 `results/hausdorff.csv`
    - **法线偏差**: 逐顶点法线夹角统计 `results/normal_deviation.csv`
    - **体积保持率**: 闭合网格体积比 (如模型非水密则跳过) `results/volume_ratio.csv`
    - **视觉保真度**: 可选 — 多视角渲染截图对比 (Phase 6 中用于报告)
    - 产出: `results/quality_metrics.csv`

5-CXX.3 **3D 专用图表** (Phase 5.5 扩展):
    - `quality_vs_faces.png` — X轴=保留面数, Y轴=Hausdorff距离, 双线(CPU/GPU)
    - `speedup_vs_model_size.png` — GPU 加速比 (CPU_time/GPU_time) 随原始面数变化
    - `vertex_delta_histogram.png` — 逐顶点位置 delta 的直方图 (验证 GPU vs CPU 一致性)
    - `side_by_side.png` — 原始模型 vs 简化模型并排渲染截图
    - 每图附带独立可运行 `code/plot_*.py` (Python + matplotlib, 读取 CSV 数据)

---

### Phase 6: 双语报告生成 / Bilingual Report Generation

**输入**: 所有阶段产出
**输出**: `实验复刻结果汇总/` 中英双语文档（在论文所在目录下创建）

**确认所有数据就绪** → 判决/图表/三方审阅/路径一致 → 生成报告

在论文所在目录下创建 `实验复刻结果汇总/` 文件夹，内含**四个**子目录：

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
- `实验复刻结果汇总/实验模型/original/*.obj` -- ★原始模型归档 (3D 项目专属)
- `实验复刻结果汇总/实验模型/simplified/*_{cpu,gpu}_{ratio}_seed{N}.obj` -- ★简化后模型归档 (3D 项目专属)
- `实验复刻结果汇总/实验模型/README.md` -- ★模型清单说明 (文件名→参数→指标 对照表)

**格式**: 英文版 = `文件名.md`，中文版 = `文件名-CN.md`; 英文标题+中文标题; 表格列头 `Metric / 指标`; 数值统一精度; 图表标题 EN/ZH 标注

---

### Phase 7: 最终整理与完整性确认 / Final Consolidation & Integrity Check

**输入**: 所有阶段产物
**输出**: `实验复刻结果汇总/` 完整目录

7.1 **文件归位**: 确认所有阶段产物已按以下结构归位
     - `实验复刻结果汇总/实验报告/` — 双语报告 + 判决 JSON
     - `实验复刻结果汇总/实验图表（含代码）/` — 图表 PNG/PDF + 独立可运行源码
     - `实验复刻结果汇总/实验结果对比表/` — 双语对比表
     - `实验复刻结果汇总/实验模型/original/` — ★原始 OBJ 模型 (3D 项目, 每个文件名与 simplified/ 对应)
     - `实验复刻结果汇总/实验模型/simplified/` — ★简化后 OBJ 模型 (3D 项目, 命名规范: {model}_{path}_{ratio}_seed{N}.obj)
     CHECKPOINT: 完整性确认 (所有文件就位/双语配对/图表代码齐全/**OBJ 模型对应关系正确**)
7.2 **一致性验证**: 对比 `判决结果.json` 与报告中的数值一致性，确认图表引用正确
    - **3D 项目**: 额外验证
      * 每个简化的 .obj 能否被 MeshLab/Blender 正确打开
      * original/ 和 simplified/ 的文件名对应关系
      * Hausdorff 指标与报告的数值一致
      * 多级 LOD 模型的顶点数递减关系正确 (简化率越高顶点越少)

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
| G0-CXX | Phase 0.3 → 0.5 | CUDA + MSBuild + vcpkg 就绪 | 安装缺失工具链 |
| G3-CXX | Phase 2-CXX → 3 | MSBuild 编译通过 + GPU kernel 可用 | 修复编译错误 |
| G4-CXX | Phase 3-CXX → 4 | GPU vs CPU 顶点 delta < 1e-4 | 检查 kernel 数值精度 |
| G7-CXX | Phase 6 | `实验模型/` 目录包含 original/ + simplified/ | 补缺 OBJ 文件 |
| G8-CXX | Phase 7 | 每个 simplified/*.obj 可被标准工具打开 | 修复损坏文件 |

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
    ├── 实验结果对比表/  # 双语实验结果对比表
    └── 实验模型/        # ★3D 项目专属: OBJ 模型归档
        ├── original/    #   原始模型文件
        ├── simplified/  #   简化后模型 (命名: {model}_{cpu,gpu}_{ratio}_seed{N}.obj)
        └── README.md    #   模型清单说明
```

## 依赖与配置 / Dependencies & Configuration

| 包 | 用途 | 安装 |
|---|------|------|
| mineru-open-sdk | PDF->Markdown (含公式/表格) | `pip install mineru-open-sdk` |
| pyyaml | MinerU 配置解析 | `pip install pyyaml` |

### C++/CUDA 专属依赖 / C++/CUDA-Specific Dependencies

| 工具/库 | 用途 | 安装/配置 |
|---------|------|----------|
| CUDA Toolkit >= 12.0 | GPU 加速 (nvcc + CUDA Runtime) | [NVIDIA 官网下载](https://developer.nvidia.com/cuda-downloads) |
| Visual Studio 2022 | C++ 编译器 (MSBuild v145) | [Visual Studio 下载](https://visualstudio.microsoft.com/) + "使用C++的桌面开发" 工作负载 |
| vcpkg | C++ 包管理器 | `git clone https://github.com/Microsoft/vcpkg.git && bootstrap-vcpkg.bat` |
| GLEW / GLFW3 / SDL2 | OpenGL 图形管线 | `vcpkg install glew:x64-windows-static glfw3:x64-windows-static sdl2:x64-windows-static` |
| GLM | 图形数学库 (头文件) | bundled 或 `vcpkg install glm:x64-windows-static` |
| MeshLab / PyMeshLab | OBJ 质量验证 (Hausdorff 距离) | [MeshLab 下载](https://www.meshlab.net/) 或 `pip install pymeshlab` |
| Nsight Compute | CUDA Kernel 性能剖析 | 随 CUDA Toolkit 安装或[单独下载](https://developer.nvidia.com/nsight-compute) |

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
