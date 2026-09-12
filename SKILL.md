---
name: math-read-do
description: >-
  数学文献实验复现标准化工作流 / Standardized Math Paper Reproduction Pipeline
  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析(含公式/表格/图表) →
  按用户指定视角输出审阅报告(研究生/导师/审稿人) →
  环境重建 → 基线验证 → 增量实现 → 统计验证(五态判决+95%CI) → 双语报告。
  覆盖数学全领域：纯数学、应用数学、统计学、运筹学、计算数学、AI4Math等。每份报告必须中英双语。

  集成三大 Nature 子技能：
  - nature-reader/：科研论文智能阅读与结构化提取 (PDF/HTML/DOI/arXiv)
  - nature-figure/：科研数据可视化顾问（先思考后绘制，8 步工作流，视觉自检闭环）
  - nature-paper2ppt/：论文一键转为中文组会PPT (6类论文叙事弧)

  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现,
  重现论文, 论文重现, 数值复现, 论文复现, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 重现结果, 重现图表, 复现结果, 复现图表,
  reproducibility check, 可复现性评估, 复现验证

  # nature-reader triggers
  读论文, 读文献, 论文阅读, 论文分析, read paper, read article, 审阅论文, extract paper,
  understand paper, 文献分析, 论文理解, 文章解读, 解析文献, 科研论文阅读

  # nature-figure triggers
  nature figure, 论文配图, 学术图表, 科研绘图, 作图, figure, plot for paper,
  publication figure, 出版级图表, 杂志图, 论文图, figure for paper, scientific figure,
  journal figure, figure generation, 图表生成, 可视化论文, 数据可视化, 不知道用什么图, 怎么展示数据, 用什么图好, 期刊投稿图, 误差棒, 显著性标注, 色盲安全配色, 矢量图导出, 中文论文图表, 多面板

  # nature-paper2ppt triggers
  论文做PPT, 论文汇报, 组会PPT, 文献汇报, 学术汇报, 做幻灯片, 讲paper,
  读书报告PPT, paper to slides, journal club, 论文转PPT, 学术演讲
compatibility:
  - 论文插图: 内置渲染内核（Node >= 18），无需额外安装
  - python3 (mineru-open-sdk >= 0.2.5)
  - 配置文件: ~/.mineru/config.yaml (MinerU token)
  - nature-reader: python-pptx, Pillow (图提取), PyMuPDF (PDF渲染)
  - nature-figure: matplotlib + seaborn + SciencePlots (静态) + plotly (交互)，CJK 字体自动配置
  - nature-paper2ppt: python-pptx, PyMuPDF, Pillow, zipfile
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
3️⃣ 生成图表 — ① 数据图：基于实验数据的出版级图表
              ② 论文插图：研究框架图/技术路线图/方法架构图/系统架构图/论文结构图/实验流程图
4️⃣ 制作PPT — 将论文或复现结果转为演示文稿
```

用户做出选择后，按对应流程执行。**用户未指定审阅视角时，必须向用户询问**（研究生／导师／审稿人／三方全出），不得代为默认——脚本在缺少 `--perspective` 时会进入交互询问。

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
| 14 | 实验没跑完就画"最终版"实验流程图，数字靠推测 | 造假风险；PRISMA/CONSORT 数字自相矛盾 | 计划阶段只出 `--stage draft`；final 必过 `requires_experiment_data` 硬门禁 |
| 15 | 手工修改交付 HTML 冒充校验通过 | 收据 SHA-256 对不上，溯源断裂 | 只改 spec 用 `figures.py render` 重跑；HTML 视为只读产物 |
| 16 | 路线图补充时重排/删除既有节点 | 初稿与终稿不可比，失去计划-执行对照 | 走 `route-supplement` 追加；结构 diff 拒绝删除，需重画用 `--force-rewrite` |
| 17 | 出图前不问主题/动效/语言/栏宽/格式/阶段，直接套默认出图 | 风格不合投稿要求返工；"动效没进 PDF"预期落空 | 按「出图前必问清单」一次问全；用户弃权才回落默认并在交付说明写明 |

## 阶段速查 / Phase Quick-Ref

| Stage | What | Key Artifact | CHECKPOINT |
|-------|------|-------------|------------|
| 0 | 宿主检测→环境构建→GPU配置 | `infra_manifest.json` | G0: 基础设施就绪 |
| 0.5 | 版本检测→安装→锁定→验证 | `version_spec.json` | G1: 版本一致 |
| 1 | PDF解析→结构化提取→领域分类→文献阅读报告 | `文献阅读.md` + `reproducibility_assessment.json` | G01: 可复现性门禁 |
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
    - **视角控制**: **未指定 `--perspective` 时脚本会进入交互询问**（研究生 / 导师 / 审稿人 / 三方全出），**不设默认值、不得代选**；`--perspective all` 输出三个视角 + 交叉对比。非交互环境（管道/CI）且未给该参数时脚本直接报错退出，不静默代选。
    - ⚠️ **只有包含导师视角（`advisor` 或 `all`）才会产出 `reproducibility_assessment.json`**；只选研究生或审稿人视角时不产出该文件，G01 门禁无法通过、无法进入 Phase 2+。脚本在这种情况下会打印明确警告。
    - 报告包含:
      - **论文结构导航**: 章节/页码/论证功能(gap→contribution→result→limits)
      - **术语表**: 专业术语 + 英文全称 + 中文译法 + 首次出现位置
      - **关键图表索引**: 图表/表格的 ID、标题、页码、关联分析
      - **关键公式索引**: 公式编号、LaTeX、描述、来源页码
      - **视角分析**: 研究生 / 导师 / 审稿人（**必须向用户询问，不设默认**）
      - **复现指导**: 核心算法、超参数、数据集、主要风险
    - 产出:
      - `analysis/文献阅读.md` -- 完整中文审阅报告 (自带嵌入式 CSS，MPE 打开即用)
      - `analysis/literature_reading.json` -- 结构化数据 (供下游消费)
      - `analysis/reproducibility_assessment.json` -- 可复现性评估 (G01 门禁)
    - **MPE 兼容**: 报告 Markdown 自带嵌入式 CSS，可在 VS Code + Markdown Preview Enhanced 中直接预览
    - **旧脚本已移除**: `scripts/three_perspective_review.py` 及其配套模板 `templates/three_perspective_review.template.md` 已于 2026-09-12 删除，其功能由 `scripts/literature_reader.py` 承担

    **使用示例**:
    ```bash
    # 未给参数：先询问模板，再询问视角（两步都会停下来等输入）
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json

    # 指定模板：跳过模板询问（视角仍会被询问）
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --template templates/literature_reader.print.md

    # 全部视角
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --perspective all

    # 指定模板 + 全部视角（两个参数都给 → 全程无需交互，可进 CI）
    python scripts/literature_reader.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json --template templates/literature_reader.sans.md --perspective all
    ```

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
| G9 | Phase 5.7 → 6 | 实验流程图 final 已过 `requires_experiment_data` 硬门禁；六张图均在 manifest 登记且状态合法 | 拒绝进入报告阶段（实验流程图缺失或仍为 draft 时） |
| G10 | Phase 7 | 插图中文标签检查通过（检查 11 `text-language`）；每张图有 spec 与 SHA-256 收据 | 补译/补收据 |

---

## 论文插图 / Figures（六类图，内置渲染内核）

唯一入口：`python scripts/figures.py`（内嵌渲染内核，Node >= 18；`figures.py doctor` 自检）。
实现与门禁细节见 `docs/figures-feature-plan.md`；内核归属见 `scripts/figuregen/NOTICE.md`。

### 出图前必问清单（缺任一项且用户未弃权 → exit 2，不静默出图）

| 项目 | 选项 | 默认（仅用户弃权时） |
|---|---|---|
| 图类型 | framework / route / model / system / structure / experiment | 按用户说法给推荐再确认 |
| 主题（视觉预设） | 素白 paper（投稿推荐）/ 深色 / 制图线稿 / 新粗野 / 趣味 / 新拟态 / 孟菲斯 / 玻璃 / 包豪斯 / 苹果风 | 素白 |
| 数据流动形式 | off 静止 / hover 悬停 / flow 流动 / tour 巡演 | off |
| 文字语言 | zh-CN / en | zh-CN |
| 排版规格 | single 单栏 / double 双栏 | single |
| 输出格式 | HTML / PDF / EPS（PDF/EPS 内核尚未实现，见已知限制） | HTML |
| 定稿阶段 | draft / confirmed / final | — |

问答协议：已说过的项不重复问；批量出图一批只问一次；用户弃权须用 `--declined` 显式声明，并在交付说明写明"该项未指定，按默认交付"。

### 阶段归属（并入 Phase 体系）

| 阶段 | 步骤 | 产出 |
|---|---|---|
| Phase 1.5（阅读） | 默认三张：framework(final) + route(draft) + structure(final) | `figures/out/*.html` + manifest |
| Phase 4.0（复现） | 无路线图出初稿；有则 `route-supplement` 追加（禁删节点/禁改主路径方向） | `figures/specs/route.json` 升版 |
| Phase 4.4 / 5.6 | 方法·模型架构图、系统架构图（`soft_code_verified`，代码跑通后 final） | 两张 HTML |
| Phase 5.7 | 实验流程图 final —— **唯一硬门禁 `requires_experiment_data`** | `figures/out/experiment.html` |
| Phase 7 | 六图 + spec + data + manifest 归位到 `实验复刻结果汇总/论文插图（含规格）/`（G9/G10） | 归位完成 |

### 常用命令

```bash
python scripts/figures.py doctor
python scripts/figures.py list
python scripts/figures.py render framework --stage final --preset paper --motion off --lang zh-CN --column double --format html
python scripts/figures.py init-reading analysis/literature_reading.json
python scripts/figures.py route-supplement --spec figures/specs/route_new.json
```

已知限制：PDF/EPS 与 visual-check 为内核 Phase 2 桩，当前交付自包含 HTML（HarmonyOS Sans 子集 base64 内嵌，可离线打印）。

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
├── nature-figure/               # 子技能：科研数据可视化顾问 (scipilot-figure-skill)
│   ├── SKILL.md
│   ├── README.md
│   ├── LICENSE
│   ├── requirements.txt
│   ├── references/              # 选图决策、数据剖析、期刊规范、绘图配方、视觉自检
│   │   ├── chart_selection.md   # 选图决策框架
│   │   ├── data_profiling.md    # 数据剖析报告解读
│   │   ├── journal_specs.md     # 期刊规范 (Nature/Science/IEEE/中文核心)
│   │   ├── plot_recipes.md      # 9 类图配方
│   │   ├── publication_checklist.md # 投稿前形式合规清单
│   │   ├── visual_review.md     # AI 读图 8 项清单 + 回改循环
│   │   └── viz_pitfalls.md      # 18 条科研画图禁忌
│   └── scripts/
│       ├── profile_data.py      # EDA：列类型/样本量/分布/异常/相关
│       ├── setup_style.py       # 期刊预设 + CJK 字体配置
│       ├── export_figure.py     # 多格式导出 + 灰度预览
│       ├── check_figure.py      # 文件合规自检
│       ├── layout_tools.py      # 子图标签对齐 + 版面整理
│       └── visual_qa.py         # 渲染预览 + 程序自检
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
├── scripts/            # 脚本 (PDF提取/文献阅读报告/图表导出等)
│   ├── literature_reader.py # 文献阅读报告生成器 (主脚本)
│   └── generate_templates.py # 模板批量生成器
├── templates/          # 文献阅读报告模板 (9 种排版风格)
│   ├── literature_reader.markleaf.md   # LaTeX 风格 (推荐)
│   ├── literature_reader.print.md      # 印刷品
│   ├── literature_reader.retro-print.md # 铅字印刷
│   ├── literature_reader.sans.md       # 无衬线
│   ├── literature_reader.serif.md      # 衬线
│   ├── literature_reader.magazine.md   # 杂志
│   ├── literature_reader.minimal.md    # 极简
│   ├── literature_reader.notebook.md   # 手记
│   ├── literature_reader.print-double.md # 双色印刷
│   └── literature_reader.mpe.css       # MPE 独立样式 (备用)
├── schemas/            # 校验 JSON Schema
├── tests/              # 测试
├── infra/              # 基础设施 (manifest/Vagrantfile/Dockerfile/apptainer)
├── provisioning/       # 配置脚本 (ansible/版本管理器/CUDA/HPC)
├── env/                # 环境锁定 (version_spec/conda-lock/requirements/Manifest)
├── figures/            # 论文插图工作期目录 (specs/ out/ data/ manifest.json)
├── analysis/           # 论文分析 (summary/parsed/formulas/gray_areas/文献阅读)
│   ├── 文献阅读.md     # 中文审阅报告 (自带 CSS，MPE 打开即用)
│   ├── literature_reading.json # 结构化数据 (下游消费)
│   └── ...             # 其他分析文件
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

**论文插图（内置渲染内核）**：需要 Node ≥ 18（`python scripts/figures.py doctor` 自检）；字体子集已随仓库内嵌（HarmonyOS Sans，约 500KB woff2），无需安装字体。

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
| nature-figure | `nature-figure/` | `SKILL.md` | 科研数据可视化顾问：8 步工作流，matplotlib+seaborn+SciencePlots+plotly，视觉自检闭环 |
| nature-paper2ppt | `nature-paper2ppt/` | `SKILL.md` + `manifest.yaml` | 论文→中文 PPTX，6类论文叙事弧，自审校循环 |
| _shared | `_shared/` | 无入口，被子技能引用 | 术语账本、论文类型分类法、伦理规范、Nat Communs 格式 |

### 与主流程的协同

- **nature-reader** 可增强 Phase 1 (论文解析与视角审阅)，提供替代 PDF 解析策略和结构化输出格式。**用户未指定审阅视角时必须询问**（不设默认值），与 `literature_reader.py` 的交互询问保持一致。
- **nature-figure** 可增强 Phase 5 (图表导出)，作为"可视化顾问"：先剖析数据→推荐图型→拦截错误→绘制→视觉自检闭环，提供出版级图表样式和质量门禁。
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
