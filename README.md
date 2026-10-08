# Math-Read-Do：数学文献阅读与实验复现工作流

## 概述

**Math-Read-Do** 是一个面向数学文献的标准化"阅读→复现→验证"工作流（Skill），专为 AI Agent 设计。输入一篇数学论文 PDF，即可自动完成从文献理解到结果验证的全流程。

核心价值在于将数学论文的**阅读理解**（Read）与**实验复现**（Do）有机结合，避免只读不练或盲目复现。

## 8 阶段全链路

| 阶段 | 名称 | 核心产出 |
|------|------|----------|
| Phase 0 | 基础设施检测 | `infra_manifest.json` |
| Phase 0.5 | 版本管理 | `version_spec.json` |
| Phase 1 | 论文解析 & 视角审阅 | `reproducibility_assessment.json` |
| Phase 2 | 环境重建 | `conda-lock.yml` |
| Phase 3 | 基线验证 | `baseline_metrics.json` |
| Phase 4 | 增量实现（按需） | `delta_report.json` |
| Phase 5 | 统计判决 & 图表导出 | `判决结果.json` + `口径B通过率矩阵.md` |
| Phase 6 | 双语报告生成 | `复现报告.md / -CN.md` |
| Phase 7 | 最终整理与完整性确认 | `实验复刻结果汇总/` |

## 视角审阅

按用户指定视角输出审阅报告，用户未指定时主动询问：

- **研究生视角** — 深度理解论文方法、公式、实验设计
- **导师视角** — 可复现性评级与教学建议
- **审稿人视角** — 批判性审查，发现论文弱点

## 支持的领域

覆盖数学全领域：纯数学 · 应用数学 · 统计学 · 运筹学 · 计算数学 · AI4Math 等

## 快速开始

```bash
# 1. 配置 MinerU Token（用于 PDF 解析）
mkdir -p ~/.mineru
echo "token: 'your-api-key'" > ~/.mineru/config.yaml
# 获取 Token：https://mineru.net/apiManage/token

# 2. 安装依赖
pip install mineru-open-sdk pyyaml

# 3. 运行复现
python scripts/math_pdf_extract.py paper.pdf --output-dir analysis/
python scripts/three_perspective_review.py analysis/parsed_text.md --output-dir analysis/
```

## 项目结构

```
reproduction/
├── SKILL.md              # 工作流定义
├── infra/                # 基础设施配置
├── provisioning/         # 环境配置脚本
├── env/                  # 环境锁定文件
├── analysis/             # 论文分析与三方审阅
├── code/                 # 复现代码
├── logs/                 # 运行日志
├── results/              # 实验结果与图表
├── reports/              # 双语报告
├── implementation/       # 增量实现记录
└── dist/                 # 发布制品
```

## 分支特性（routine）

routine 是数学文献"阅读→复现→验证"的主工作流分支，在通用 8 阶段流程之上内置一套实验质量与可信度机制：

- **输入数据预检**（Phase 5.0）：二进制文件 schema + 叶子类型抽检、CSV BOM/编码检查、空值预检、修复后验证分类（目标缺陷修复与无关既有缺陷分开陈述）
- **运行审计**（Phase 3.1 / 5.1）：硬超时执行、异常分类计数（含被捕获异常与非零退出码）、退出码审计、计时指标语义登记（`Σtst` 校验，语义不明禁止直接对比判决）、空值普查、过程数据留痕（时间戳/worker 标识/全量日志归档）
- **断点续传**（长时运行脚本强制义务）：逐单元立即落盘、重启幂等跳过已完成单元；不可行时须在偏差登记表登记理由与中断损失评估
- **偏差登记表**：`analysis/gray_areas.md` 结构化——每条偏差含 ID、类型（数据/环境/框架/执行）、量化影响、证据、对判决的影响方向；双语报告必备偏差登记节
- **两口径判决**：口径 A（求解器自身成功判据）与口径 B（独立 checker 判据）语义不同、数字不混用；口径 B 通过率矩阵（实例 × 算法）为标准产物
- **稳健统计**：判决基准匹配论文报告口径——连续指标 = 成功试验中位数 + percentile bootstrap 95% CI（≥20,000 重采样、固定种子），比例指标 = Wilson score 区间；均值 x̄ ± t-CI 仅作参考输出
- **拒绝归因证据分级**：每个被拒试验的归因须附诊断证据并标注分级（实证/推断/估计），禁止无证据的容差归因
- **G9 发布前交叉校验门**：报告数字与判决 JSON 逐格核对（零不一致方可交付）、算法标签与矩阵行列双重核对、机制参数声称与实测配置对账

## 输出规范

- 所有报告**中英双语**（`.md` + `.zh.md`）
- 图表附带独立可运行生成代码（`results/figures/code/plot_*.py`）
- 判决结果使用五态分类：OK / approx / FAIL / WARN / FAIL
- 统计验证使用 95% 置信区间，至少 N=5 随机种子；判决基准匹配论文口径（中位数 percentile bootstrap / Wilson score）
- 报告须同时呈现口径 A 与口径 B 总通过率，两套数字不得混用

## 依赖

| 包 | 用途 |
|---|------|
| mineru-open-sdk | PDF → Markdown（含公式、表格、图表） |
| pyyaml | MinerU 配置解析 |

## 子技能 / Sub-Skills

本分支集成四个 nature-* 子 Skill，可独立调用也可在主流程里协同：

| 子技能 | 角色 | 与谁互补 |
|--------|------|---------|
| `nature-reader/` | 科研论文智能阅读、结构化提取 (PDF/HTML/DOI/arXiv) | — |
| `nature-figure/` | 科研数据可视化（matplotlib/seaborn，8 步工作流 + 视觉自检闭环） | 跟 nature-archify 互补 |
| `nature-paper2ppt/` | 论文→中文 PPTX（6 类叙事弧 + 自审校） | — |
| `nature-archify/` | 系统架构图渲染器（5 类图：architecture/workflow/sequence/dataflow/lifecycle，13 视觉预设，9 项 showcase 校验；产物 self-contained inline-SVG HTML，内嵌 HarmonyOS Sans Medium 子集字体，深/浅双主题） | 跟 nature-figure 互补——本子技能专做系统/流程/时序/数据流架构图 |

`nature-archify` 需要 Node.js ≥ 18，零外部依赖；Python 侧通过 `scripts/nature_archify_bridge.py` 调用。

**Phase 1.5 辅助架构图征询**：论文阅读完成后必须主动征询是否制作架构图，用户同意后强制 6 项逐项询问（主题/图类型/图语言/动画模式/视觉预设/输出格式），不重复提问。

## 性能优化记录（2026-10-09）

### P0（关键修复）
- **H1**: 清理 17 个 .pyc + 回填 .gitignore
- **E2/E3**: 门禁统一 + 五态判决枚举统一
- **F2**: auto_update 加超时 + TTL 缓存

### P1（高价值优化）
- **E4**: Phase 1 统一为 literature_reader.py
- **F4**: 创建 VERSION 文件
- **G6/G7**: call_llm 超时+重试 / MinerU 超时+降级
- **H4**: test_templates.py 改 pytest
- **F1**: SKILL.md 外移低频道（-21.9%）

### P2（一致性收敛）
- **H8**: 跨分支路径/命名统一（path_aliases）
- **H10/H11**: __main__ guard + 无 TTY 降级

### 测试：54 passed, 6 skipped

## 许可

MIT
