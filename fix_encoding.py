import sys, os
sys.stdout.reconfigure(encoding='utf-8')

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, 'SKILL.md')

content = r'''---
name: math-paper-reproduction
description: >-
  数学文献实验复现标准化工作流 / Standardized Math Paper Reproduction Pipeline
  8阶段全链路：宿主检测 → 版本管理 → MinerU PDF解析(含公式/表格/图表) →
  三方视角审阅(研究生深度理解/导师可复现性评估/审稿人批判审查) →
  环境重建 → 基线验证 → 增量实现 → 统计验证(五态判决+95%CI) → 双语报告 → 制品打包。
  支持数值计算/符号代数/AI4Math/统计/优化/经济学。每份报告必须中英双语。
  Triggers: 复现, reproduction, 实验复现, reproduce paper, 复现论文, 重现实验,
  reproduce experiment, 复现报告, reproduction report, PDF解析, paper parsing, 实验重现,
  重现论文, 论文重现, 数值复现, 论文复现, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 重现结果, 重现图表, 复现结果, 复现图表,
  reproducibility check, 可复现性评估, 复现验证
compatibility:
  - python3 (mineru-open-sdk >= 0.2.5, openai)
  - 配置文件: ~/.mineru/config.yaml (MinerU token)
  - 环境变量: LLM_API_KEY, LLM_API_BASE, LLM_MODEL
---

# Mathematical Literature Experiment Reproduction Standardized Workflow
# 数学文献实验复现标准化流程

## 核心原则 / Core Principles

1. **双语输出**: 所有报告必须有中英双版本 (`.md` + `.zh.md`)
2. **增量验证**: 每添加一个模块即验证一次
3. **可审计**: 每步产生结构化产物，溯源链完整
4. **人机协同**: 风险分级审批
5. **锁定即契约**: 版本/环境/依赖每步锁定，不信任隐式继承

## 反例与黑名单 / Anti-Patterns & Blacklist

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | MinerU token 未配置就执行 Phase 1.1 | 脚本报 401 | 先检查 `~/.mineru/config.yaml`，未配置则引导用户获取 |
| 2 | Windows 上直跑 Linux 路径脚本 | 换行符/路径分隔符不兼容 | 使用 WSL2 或 `scripts/enable_gpu.ps1` 等 Windows 原生脚本 |
| 3 | 先装包再装语言运行时 | Conda/pip SAT 死锁 | 严格 运行时→版本管理器→锁定→包的顺序 |
| 4 | 只跑一个种子就下判决 | 非确定性被忽略 | 至少 N=5 种子, 95% CI 统计判决 |
| 5 | 只生成英文报告 | 中文用户无法阅读 | 每份报告同时生成 `.md` 和 `.zh.md` |
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
| 2 | 依赖扫描→环境构建→确定性配置→验证 | `conda-lock.yml` | G3: 环境就绪 |
| 3 | 官方代码运行→指标对齐→失败诊断→锁定 | `baseline_metrics.json` | G4: 基线建立 |
| 4 | 模块拆解→增量实现→代码管理 | `delta_report.json` | -- |
| 5 | 多轮运行→统计计算→五态判决→图表导出 | `verdict.json` | 5.1 参数确认 |
| 6 | 数据就绪检测→双语报告生成(含模板) | `reproduction_report.md/zh.md` | 数据就绪 |
| 7 | 证据包→溯源链→签名存证 | `artifact_bundle.zip` | 完整性确认 |

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

1.4 **三方视角审阅**: 使用 `scripts/three_perspective_review.py` 自动执行
    - **研究生** (Phase 1.4-A): 深度理解 -- 摘要/文献综述/研究问题/方法/结果/讨论/关键公式
      → 消费方: Phase 2 环境重建方法栈, Phase 4 增量实现的公式/算法参考
    - **导师** (Phase 1.4-B): 可复现性评级 -- 方法评估/可复现性表/教学建议/reproducibility_assessment.json
      → 消费方: G01 门禁 (决定是否进入复现流程)
    - **审稿人** (Phase 1.4-C): 批判审查 -- 总体评价/方法论评估/修改意见(强制/建议/细节)/总结
      → 消费方: Phase 5 判决引擎, Phase 6 诊断章节引用
    - 需要 `LLM_API_KEY` 环境变量; 未配置时输出占位分析
    - 执行: `python scripts/three_perspective_review.py analysis/parsed_text.md --output-dir analysis/ --paper-summary analysis/paper_summary.json`
    - 产出: `analysis/<paper>_{student,advisor,reviewer}_review.md` + `reproducibility_assessment.json` + `review_manifest.json`
    - 三方综合: 交叉对比表 + review_manifest.json 汇总

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
**输出**: `results/raw_metrics.csv` + `reports/verdict.json` + `results/figures/` (图 + 生成代码)

5.1 **多轮运行**: 确认参数 (基线可行? N=5 种子? 运行时间? GPU 启用?) → 每轮独立执行 → `raw_metrics.csv`
5.2 **统计计算**: 均值 x-bar + 标准差 s + 95% t-CI: x-bar +/- t*s/sqrt(N) → `statistical_summary.json`
5.3 **五态判决**: `within_ci`→OK / `close_outside_ci`→approx / `outside_tolerance`→FAIL / `not_testable`→WARN / `static_check_failed`→FAIL
5.4 **诊断输出**: >=2 条诊断假说 + Top-12 失败模式 + 引用审稿人视角发现 → `reports/diagnosis.md/zh.md`
5.5 **图表+代码导出**:
    - 图形: 收敛曲线(convergence.png) / 指标对比(comparison.png) / 消融图(ablation.png) / 散点图/热力图
    - 格式: PNG (嵌入报告) + PDF (出版级)
    - 代码自包含: 每图附带独立可运行 `results/figures/code/plot_*.py` (固定种子+对齐论文配色)
    - 验证: `python results/figures/code/plot_convergence.py` → 输出一致
    - 产出: `results/figures/*.png/.pdf` + `results/figures/code/plot_*.py`

**Top-12 失败模式**: 代码/数据缺失 | 环境漂移 | CUDA 冲突 | ABI 不兼容 | 依赖冲突 | 非确定性 | BLAS 变体 | 跨平台路径 | 数据泄露 | 预训练权重漂移 | 选择性报告 | 上游依赖位腐

---

### Phase 6: 双语报告生成 / Bilingual Report Generation

**输入**: 所有阶段产出
**输出**: `reports/` 中英双语文档

**确认所有数据就绪** → 判决/图表/三方审阅/路径一致 → 生成报告

**文档清单** (每个 `.md` + `.zh.md`):
- `reproduction_report.md` -- 完整报告 (模板: templates/reproduction_report.template.md)
- `comparison_table.md` -- 对比表 (双列表格: EN/ZH 并行)
- `diagnosis.md` -- 诊断分析
- `RUN_SUMMARY.md` -- 运行摘要 (状态/关键结果/环境/制品)
- `verdict.json` -- 判决 JSON (中英双语字段)

**格式**: 英文标题+中文标题; 表格列头 `Metric / 指标`; 数值统一精度; 图表标题 EN/ZH 标注

---

### Phase 7: 制品打包与溯源 / Artifact Packaging & Provenance

**输入**: 所有阶段产物
**输出**: `dist/artifact_bundle.zip` + `dist/provenance_chain.json`

7.1 **证据包**: 代码快照 + 环境锁定 + 检测报告 + 版本锁定 + 运行日志 + 原始结果 + 三方审阅 + 双语报告 → 打包
     CHECKPOINT: 完整性确认 (SHA/锁文件/审阅/双语配对/图表代码)
7.2 **溯源链**: 每条输入→处理→输出的 SHA-256 记录 → `provenance_chain.json`
7.3 **签名**: GPG 签名 + ACM Badge 相容存证 (可选提交公共复现账本)

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
| G7 | Phase 6 | 所有报告中英双语 | 补译 |
| G8 | Phase 7 | 证据包完整性校验通过 | 补文件 |

---

## 文件结构 / Directory Structure

```
reproduction/
├── SKILL.md
├── skills/registry.yaml
├── infra/              # 基础设施 (manifest/Vagrantfile/Dockerfile/apptainer)
├── provisioning/       # 配置脚本 (ansible/版本管理器/CUDA/HPC)
├── env/                # 环境锁定 (version_spec/conda-lock/requirements/Manifest)
├── analysis/           # 论文分析 (summary/parsed/formulas/gray_areas/三视角审阅)
├── code/               # 代码 (Git repo)
├── logs/               # 运行日志
├── results/            # 实验 (baseline/tolerance/raw/stat/figures+code)
├── reports/            # 双语报告 (repro/comparison/verdict/diagnosis/RUN_SUMMARY/html)
├── implementation/     # 增量实现 (log/delta)
└── dist/               # 发布制品 (bundle/provenance)
```

## 依赖与配置 / Dependencies & Configuration

| 包 | 用途 | 安装 |
|---|------|------|
| mineru-open-sdk | PDF->Markdown (含公式/表格) | `pip install mineru-open-sdk` |
| openai | 三方审阅 LLM 后端 | `pip install openai` |
| pyyaml | MinerU 配置解析 | `pip install pyyaml` |

**环境变量**: `LLM_API_KEY` (必填), `LLM_API_BASE` (默认 `https://api.openai.com/v1`), `LLM_MODEL` (默认 `gpt-4o`)

**首次配置**:
```bash
# MinerU token
mkdir -p ~/.mineru && echo "token: 'your-api-key'" > ~/.mineru/config.yaml
# 来源: https://mineru.net/apiManage/token
# 依赖安装
pip install mineru-open-sdk openai pyyaml
# LLM API
export LLM_API_KEY='your-key'
```

## 决策响应 / Decision Responses

| 操作 | EN | ZH |
|------|----|-----|
| 批准 | approve / ok / yes | 可以 / 好的 / 继续 / 同意 / 批准 |
| 修订 | revise | 修改 |
| 拒绝 | reject | 拒绝 |
| 跳过 | skip | 跳过 |

**风险分级**: 低(只读分析, 无需审批) / 中(运行前计划审批) / 高(逐条审批)

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
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Written {len(content)} bytes to SKILL.md")

# Verify
with open(path, 'rb') as f:
    raw = f.read()
decoded = raw.decode('utf-8')
good_keywords = ['宿主检测', '版本管理', '三方视角审阅', '可复现性评估', '复现验证']
for kw in good_keywords:
    if kw in decoded:
        print(f"  OK: '{kw}' found")
    else:
        print(f"  BAD: '{kw}' NOT found")
