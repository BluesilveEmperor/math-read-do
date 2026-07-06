# Reproduction Report: {{PAPER_TITLE}}
# 复现报告：{{PAPER_TITLE}}

## 1. 元信息 / Metadata

| Field / 字段 | Value / 值 |
|-------------|------------|
| Paper / 论文 | {{PAPER_TITLE}} |
| Authors / 作者 | {{AUTHORS}} |
| Venue / 发表 | {{VENUE}} |
| Reproduction Date / 复现日期 | {{DATE}} |
| Host OS / 宿主系统 | {{HOST_OS}} |
| Runtime Environment / 运行环境 | {{ENV_SUMMARY}} |
| GPU / 显卡 | {{GPU_INFO}} |
| GPU Count / GPU数量 | {{GPU_COUNT}} |
| CUDA Version / CUDA版本 | {{CUDA_VERSION}} |
| GPU Mode / GPU模式 | {{GPU_MODE}} (Discrete / 独显) |
| Total Wall Time / 总耗时 | {{WALL_TIME}} |

## 2. 论文深度分析 / Paper Deep Analysis

{% if PERSPECTIVE_TYPE == 'advisor' %}

### 导师视角 — 可复现性评估 / Advisor Perspective — Reproducibility Assessment

| Dimension / 维度 | Rating / 评级 |
|-----------------|--------------|
| Reproducibility Rating / 可复现性 | {{REPRO_RATING}} |
| Code Available / 代码可用 | {{CODE_AVAIL}} |
| Data Available / 数据可用 | {{DATA_AVAIL}} |
| Environment Specified / 环境说明 | {{ENV_SPEC}} |
| Recommendation / 建议 | {{REPRO_RECOMMENDATION}} |

{% elif PERSPECTIVE_TYPE == 'reviewer' %}

### 审稿人视角 — 批判性审查 / Reviewer Perspective — Critical Review

| Dimension / 维度 | Finding / 发现 |
|-----------------|---------------|
| Overall Recommendation / 总体推荐 | {{REVIEWER_RECOMMENDATION}} |
| Key Strengths / 主要优势 | {{REVIEWER_STRENGTHS}} |
| Key Concerns / 主要担忧 | {{REVIEWER_CONCERNS}} |
| Methodological Issues Found / 发现的方法论问题 | {{REVIEWER_ISSUES}} |

{% else %}

### 研究生视角 — 方法理解 / Student Perspective — Method Understanding

{{STUDENT_ANALYSIS}}

{% endif %}

## 3. 方法原理 / Method Principles

### 核心原理 / Core Principles

{{PRINCIPLE_EN}}

{{PRINCIPLE_ZH}}

### 数学基础 / Mathematical Foundation

{% for formula in formulas %}
**{{formula.label_en}} / {{formula.label_zh}}**:

$$
{{formula.latex}}
$$

> {{formula.explanation_en}} / {{formula.explanation_zh}}

{% endfor %}

### 算法流程概述 / Algorithm Workflow Overview

{{ALGORITHM_WORKFLOW_EN}}

{{ALGORITHM_WORKFLOW_ZH}}

## 4. 创新点 / Innovations

| # | Innovation / 创新点 | Description / 描述 | Ref / 论文引用 |
|---|--------------------|--------------------|----|
{% for innov in innovations %}
| {{innov.id}} | {{innov.title_en}} / {{innov.title_zh}} | {{innov.description_en}} / {{innov.description_zh}} | {{innov.paper_ref}} |
{% endfor %}

{{INNOVATION_DISCUSSION_EN}}

{{INNOVATION_DISCUSSION_ZH}}

## 5. 优缺点分析 / Strengths & Weaknesses

### 优点 / Strengths

| # | Strength / 优点 | Evidence / 证据 | Impact / 影响 |
|---|----------------|----------------|--------------|
{% for strength in strengths %}
| {{strength.id}} | {{strength.title_en}} / {{strength.title_zh}} | {{strength.evidence}} | {{strength.impact}} |
{% endfor %}

### 缺点 / Weaknesses

| # | Weakness / 缺点 | Evidence / 证据 | Mitigation / 缓解方案 |
|---|----------------|----------------|---------------------|
{% for weakness in weaknesses %}
| {{weakness.id}} | {{weakness.title_en}} / {{weakness.title_zh}} | {{weakness.evidence}} | {{weakness.mitigation}} |
{% endfor %}

{{STRENGTH_WEAKNESS_SUMMARY_EN}}

{{STRENGTH_WEAKNESS_SUMMARY_ZH}}

## 6. 伪代码 / Pseudocode

### 核心算法伪代码 / Core Algorithm Pseudocode

```
{{PSEUDOCODE_MAIN}}
```

> {{PSEUDOCODE_MAIN_EXPLANATION_EN}} / {{PSEUDOCODE_MAIN_EXPLANATION_ZH}}

{% for sub_algo in sub_algorithms %}
### {{sub_algo.title_en}} / {{sub_algo.title_zh}}

```
{{sub_algo.pseudocode}}
```

> {{sub_algo.explanation_en}} / {{sub_algo.explanation_zh}}

{% endfor %}

## 7. 实验结果对比 / Results Comparison

### 7.1 主要指标 / Primary Metrics

| Metric / 指标 | Paper / 论文 | Reproduced / 复现 | Δ(%) | Within Tol? / 在容忍度内? |
|---------------|-------------|-------------------|------|-------------------------|
{% for metric in metrics %}
| {{metric.name}} | {{metric.paper_value}} | {{metric.reproduced_mean}} ± {{metric.std}} | {{metric.delta_pct}} | {{metric.within_tolerance_icon}} {{metric.within_tolerance_en}} / {{metric.within_tolerance_zh}} |
{% endfor %}

### 7.2 次指标 / Secondary Metrics

{% for sec in secondary_metrics %}
| {{sec.name_en}} / {{sec.name_zh}} | {{sec.paper_value}} | {{sec.reproduced_value}} | {{sec.delta_pct}} |
{% endfor %}

## 8. 诊断与讨论 / Diagnosis & Discussion

### 复现质量评估 / Reproduction Quality Assessment

{{QUALITY_ASSESSMENT_EN}}

{{QUALITY_ASSESSMENT_ZH}}

### 与论文差异分析 / Deviation Analysis

| Observation / 观察项 | Possible Cause / 可能原因 | Category / 类别 |
|---------------------|--------------------------|----------------|
{% for obs in observations %}
| {{obs.description_en}} / {{obs.description_zh}} | {{obs.cause_en}} / {{obs.cause_zh}} | {{obs.category}} |
{% endfor %}

### 灰色地带 / Gray Areas

以下内容在论文中未明确说明，复现过程中做了假设：

The following details were not explicitly specified in the paper; assumptions were made during reproduction:

{% for gray in gray_areas %}
- {{gray.en}} / {{gray.zh}}
{% endfor %}

## 9. 复现结论 / Reproduction Conclusion

**{{CONCLUSION_EN}}**

**{{CONCLUSION_ZH}}**

## 10. 图表与源码清单 / Figures & Source Code

| Figure / 图 | File / 文件 | Source Code / 源码 | Paper Ref / 论文引用 |
|------------|------------|-------------------|-------------------|
{% for fig in figures %}
| {{fig.title_en}} / {{fig.title_zh}} | `实验复刻结果汇总/实验图表（含代码）/{{fig.filename}}` | `实验复刻结果汇总/实验图表（含代码）/code/plot_{{fig.code_name}}.py` | {{fig.paper_ref}} |
{% endfor %}

验证所有图表可独立复现:
```bash
cd 实验复刻结果汇总/实验图表（含代码）/code
python -m pip install -r requirements.txt
python plot_convergence.py   # 应输出 convergence.png
python plot_comparison.py    # 应输出 comparison.png
```

---

*Report generated on / 报告生成于 {{DATE}} by Math Paper Reproduction Workflow Skill*
