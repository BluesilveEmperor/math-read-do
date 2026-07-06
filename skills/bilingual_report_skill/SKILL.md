# Bilingual Report Skill / 双语报告生成技能

## Description / 描述
基于所有实验数据生成中英双语版本的完整报告、对比表和摘要。

## Phase / 阶段
reporting

## Mandatory Rule / 强制规则
所有报告文档必须同时生成 `.md` (英文) 和 `-CN.md` (中文) 两个版本。

## 文档清单 / Document Inventory

| Doc | EN file | ZH file | Source Template |
|-----|---------|---------|----------------|
| 完整复现报告 | `实验复刻结果汇总/实验报告/复现报告.md` | `实验复刻结果汇总/实验报告/复现报告-CN.md` | `templates/reproduction_report.template.md` |
| 实验结果对比表 | `实验复刻结果汇总/实验结果对比表/实验结果对比表.md` | `实验复刻结果汇总/实验结果对比表/实验结果对比表-CN.md` | `templates/comparison_table.template.md` |
| 运行摘要 | `实验复刻结果汇总/实验报告/运行摘要.md` | `实验复刻结果汇总/实验报告/运行摘要-CN.md` | `templates/RUN_SUMMARY.template.md` |
| 诊断分析 | `实验复刻结果汇总/实验报告/诊断分析.md` | `实验复刻结果汇总/实验报告/诊断分析-CN.md` | `templates/diagnosis.template.md` |

## 报告规范 / Report Specifications

### 1. 标题格式 / Title Format
第一行英文标题，空行后第二行中文标题:
```markdown
# Reproduction Report: Paper Title
# 复现报告：论文标题
```

### 2. 表格格式 / Table Format
列标题使用英文，必要时括号附中文:
```markdown
| Metric / 指标 | Paper / 论文 | Reproduced / 复现 | Δ(%) |
|---------------|-------------|-------------------|------|
```

### 3. 数值格式 / Number Format
统一小数位数，同一表中保持一致。

### 4. 状态标识 / Status Icons
| Icon | Meaning EN | Meaning ZH |
|------|-----------|-----------|
| ✅ | Success / Within CI | 成功 / 在置信区间内 |
| ⚠️ | Partial / Close outside CI | 部分复现 / 在容忍度内 |
| ❌ | Failed / Outside tolerance | 失败 / 超出容忍度 |
| 🚫 | Not testable | 无法测试 |
| 🔧 | Config error | 配置错误 |

### 5. 文件命名 / File Naming
- 英文版: `文件名.md`
- 中文版: `文件名-CN.md`
- JSON 数据: `文件名.json` (字段含 `_en` / `_zh` 后缀)

## Step-by-Step Process / 执行步骤

### Step 1: Gather Data / 收集数据
从各阶段产物中提取:
- `实验复刻结果汇总/实验报告/判决结果.json` - 判决结果
- `results/raw_metrics.csv` - 原始指标 (中间产物)
- `results/statistical_summary.json` - 统计分析 (中间产物)
- `infra/infra_manifest.json` - 基础设施
- `env/reproduction_manifest.json` - 环境清单

### Step 2: Generate Reports / 生成报告
使用 templates/ 目录下的模板，填充数据生成四个文档的双语版本。

### Step 3: Cross-Validation / 交叉验证
- 中英文版本数据一致
- 数值与 `判决结果.json` 一致
- 图表引用正确

## Outputs / 产出
- `实验复刻结果汇总/实验报告/复现报告.md` + `-CN.md`
- `实验复刻结果汇总/实验结果对比表/实验结果对比表.md` + `-CN.md`
- `实验复刻结果汇总/实验报告/运行摘要.md` + `-CN.md`
- `实验复刻结果汇总/实验报告/诊断分析.md` + `-CN.md`
- `实验复刻结果汇总/实验报告/判决结果.json` (含中英文双字段)
