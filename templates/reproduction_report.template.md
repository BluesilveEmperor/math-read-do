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

## 2. 判决结果 / Verdict

| Metric / 指标 | Paper Claim / 论文值 | Reproduced Mean / 复现均值 | 95% CI | Δ(%) | Verdict / 判决 |
|---------------|---------------------|--------------------------|--------|------|---------------|
{% for metric in metrics %}
| {{metric.name}} | {{metric.paper_value}} | {{metric.reproduced_mean}} | {{metric.ci_lower}} ~ {{metric.ci_upper}} | {{metric.delta_pct}} | {{metric.verdict_icon}} {{metric.verdict}} |
{% endfor %}

**整体判决 / Overall Verdict**: {{OVERALL_VERDICT_ICON}} {{OVERALL_VERDICT_EN}} / {{OVERALL_VERDICT_ZH}}

## 3. 论文深度分析 / Paper Deep Analysis

### 3.1 研究生视角 — 方法理解 / Student Perspective — Method Understanding

{{STUDENT_ANALYSIS}}

### 3.2 导师视角 — 可复现性评估 / Advisor Perspective — Reproducibility Assessment

| Dimension / 维度 | Rating / 评级 |
|-----------------|--------------|
| Reproducibility Rating / 可复现性 | {{REPRO_RATING}} |
| Code Available / 代码可用 | {{CODE_AVAIL}} |
| Data Available / 数据可用 | {{DATA_AVAIL}} |
| Environment Specified / 环境说明 | {{ENV_SPEC}} |
| Recommendation / 建议 | {{REPRO_RECOMMENDATION}} |

### 3.3 审稿人视角 — 批判性审查 / Reviewer Perspective — Critical Review

| Dimension / 维度 | Finding / 发现 |
|-----------------|---------------|
| Overall Recommendation / 总体推荐 | {{REVIEWER_RECOMMENDATION}} |
| Key Strengths / 主要优势 | {{REVIEWER_STRENGTHS}} |
| Key Concerns / 主要担忧 | {{REVIEWER_CONCERNS}} |
| Methodological Issues Found / 发现的方法论问题 | {{REVIEWER_ISSUES}} |

> 三方审阅详情见 `analysis/<paper>_student_review.md` / `_advisor_review.md` / `_reviewer_review.md`

## 4. 判决含义 / Verdict Definitions

| 判决 / Verdict | 含义 / Meaning |
|---------------|---------------|
| ✅ within_ci | 论文声称值在复现的95%置信区间内 / Paper claim falls within the 95% CI of reproduced runs |
| ⚠️ close_outside_ci | 在CI外但在容忍度内 / Outside CI but within tolerance band |
| ❌ outside_tolerance | 超出容忍度范围 / Outside both CI and tolerance |
| 🚫 not_testable | 无法完整运行实验 / Could not complete execution |
| 🔧 static_check_failed | 静态检查未通过 / Static analysis check failed |

## 5. 环境摘要 / Environment Summary

### 宿主系统 / Host System

| Property / 属性 | Value / 值 |
|----------------|-----------|
| Operating System / 操作系统 | {{HOST_OS_DETAIL}} |
| Kernel / 内核 | {{KERNEL}} |
| CPU / 处理器 | {{CPU_INFO}} |
| Memory / 内存 | {{MEMORY}} |
| GPU | {{GPU_DETAIL}} |

### 运行环境 / Runtime Environment

| Property / 属性 | Value / 值 |
|----------------|-----------|
| Python | {{PYTHON_VERSION}} |
| Julia | {{JULIA_VERSION}} |
| CUDA | {{CUDA_VERSION}} |
| GCC | {{GCC_VERSION}} |
| Conda Env | {{CONDA_ENV_NAME}} |

### 锁定文件 / Lock Files

- `env/conda-lock.yml`: {{CONDA_LOCK_HASH}}
- `env/requirements-locked.txt`: {{PIP_LOCK_HASH}}
- `env/reproduction_manifest.json`: {{MANIFEST_HASH}}

## 6. 实验结果对比 / Results Comparison

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

## 7. 诊断与讨论 / Diagnosis & Discussion

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

## 8. 复现结论 / Reproduction Conclusion

**{{CONCLUSION_EN}}**

**{{CONCLUSION_ZH}}**

## 9. 图表与源码清单 / Figures & Source Code

| Figure / 图 | File / 文件 | Source Code / 源码 | Paper Ref / 论文引用 |
|------------|------------|-------------------|-------------------|
{% for fig in figures %}
| {{fig.title_en}} / {{fig.title_zh}} | `results/figures/{{fig.filename}}` | `results/figures/code/plot_{{fig.code_name}}.py` | {{fig.paper_ref}} |
{% endfor %}

验证所有图表可独立复现:
```bash
cd results/figures/code
python -m pip install -r requirements.txt
python plot_convergence.py   # 应输出 convergence.png
python plot_comparison.py    # 应输出 comparison.png
```

## 10. 附件 / Attachments

- `results/raw_metrics.csv`: 所有种子的原始指标 / Raw metrics from all seeds
- `results/figures/`: 实验结果图表 / Experiment figures
- `results/figures/code/`: 图表生成代码 (自包含, 可独立运行) / Figure generation code (self-contained, standalone)
- `logs/run_experiment_*.log`: 完整运行日志 / Full execution logs
- `env/reproduction_manifest.json`: 复现环境清单 / Reproduction manifest
- `infra/gpu_manifest.json`: GPU检测与配置记录 / GPU detection and configuration
- `analysis/*_student_review.md`: 研究生视角审阅报告 / Student perspective review
- `analysis/*_advisor_review.md`: 导师视角审阅报告 / Advisor perspective review
- `analysis/*_reviewer_review.md`: 审稿人视角审阅报告 / Reviewer perspective review
- `analysis/reproducibility_assessment.json`: 可复现性评估 / Reproducibility assessment

---

*Report generated on / 报告生成于 {{DATE}} by Math Paper Reproduction Workflow Skill*
