# 文件结构 / Directory Structure

> 本文档从 SKILL.md 外移的低频道参考内容（完整目录树），SKILL.md 原位置仅保留摘要。

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
│   ├── generate_templates.py # 模板批量生成器
│   └── three_perspective_review.py # 旧版三方审阅兼容入口 (新流程用 literature_reader.py)
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
