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
