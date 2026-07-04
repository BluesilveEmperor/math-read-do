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

## 3. 实验结果对比 / Results Comparison

### 主要指标 / Primary Metrics

| Metric / 指标 | Paper / 论文 | Reproduced / 复现 | Δ(%) | Within Tol? / 在容忍度内? |
|---------------|-------------|-------------------|------|-------------------------|
{% for metric in metrics %}
| {{metric.name}} | {{metric.paper_value}} | {{metric.reproduced_mean}} ± {{metric.std}} | {{metric.delta_pct}} | {{metric.within_tolerance_icon}} {{metric.within_tolerance_en}} / {{metric.within_tolerance_zh}} |
{% endfor %}

### 次指标 / Secondary Metrics

{% for sec in secondary_metrics %}
| {{sec.name_en}} / {{sec.name_zh}} | {{sec.paper_value}} | {{sec.reproduced_value}} | {{sec.delta_pct}} |
{% endfor %}

## 4. 诊断与讨论 / Diagnosis & Discussion

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

## 5. 复现结论 / Reproduction Conclusion

**{{CONCLUSION_EN}}**

**{{CONCLUSION_ZH}}**

## 6. 图表与源码清单 / Figures & Source Code

| Figure / 图 | File / 文件 | Python | LaTeX | MATLAB | Tableau | Paper Ref / 论文引用 |
|------------|------------|--------|-------|--------|---------|-------------------|
{% for fig in figures %}
| {{fig.title_en}} / {{fig.title_zh}} | `实验复刻结果汇总/实验图表（含代码）/{{fig.filename}}` | `code/python/plot_{{fig.code_name}}.py` | `code/latex/plot_{{fig.code_name}}.tex` | {% if fig.has_matlab %}`code/matlab/plot_{{fig.code_name}}.m`{% else %}—{% endif %} | {% if fig.has_tableau %}`code/tableau/plot_{{fig.code_name}}.twb`{% else %}—{% endif %} | {{fig.paper_ref}} |
{% endfor %}

验证所有图表可独立复现:

```bash
# Python (必选)
cd 实验复刻结果汇总/实验图表（含代码）/code/python
pip install -r requirements.txt
python plot_convergence.py

# LaTeX (必选)
cd ../latex
pdflatex plot_convergence.tex

# MATLAB (若适用)
cd ../matlab
matlab -batch "plot_convergence"

# Tableau (若适用)
cd ../tableau && open plot_convergence.twb
```

---

*Report generated on / 报告生成于 {{DATE}} by Math Paper Reproduction Workflow Skill*
