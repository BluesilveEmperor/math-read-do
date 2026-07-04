# Results Comparison Table: {{PAPER_TITLE}}
# 实验结果对比表：{{PAPER_TITLE}}

## 1. 主要实验结果对比 / Main Results Comparison

| Metric / 指标 | Paper / 论文 | Reproduced / 复现 | Std Dev / 标准差 | 95% CI | Δ(%) | Verdict / 判决 |
|---------------|-------------|-------------------|-----------------|--------|------|---------------|
{% for metric in metrics %}
| {{metric.name}} | {{metric.paper_value}} | {{metric.reproduced_mean}} | ±{{metric.std}} | [{{metric.ci_lower}}, {{metric.ci_upper}}] | {{metric.delta_pct}} | {{metric.verdict_icon}} {{metric.verdict}} |
{% endfor %}

## 2. 按种子详细结果 / Per-Seed Detailed Results

| Seed / 种子 | {% for m in metrics %} {{m.name}} | {% endfor %} |
|------------|{% for m in metrics %}---|{% endfor %}|
{% for seed in seeds %}
| {{seed.id}} | {% for val in seed.metrics %} {{val}} | {% endfor %} |
{% endfor %}

| Mean / 均值 | {% for m in metrics %} {{m.reproduced_mean}} | {% endfor %} |
| Std / 标准差 | {% for m in metrics %} ±{{m.std}} | {% endfor %} |

## 3. 消融实验对比 / Ablation Study Comparison

| Variant / 变体 | Paper / 论文 | Reproduced / 复现 | Δ | Status / 状态 |
|---------------|-------------|-------------------|---|---------------|
{% for ablation in ablations %}
| {{ablation.name_en}} / {{ablation.name_zh}} | {{ablation.paper}} | {{ablation.reproduced}} | {{ablation.delta}} | {{ablation.status_icon}} {{ablation.status_en}} / {{ablation.status_zh}} |
{% endfor %}

## 4. 基线方法对比 / Baseline Method Comparison

| Method / 方法 | Paper Reported / 论文报告 | This Run / 本次 | Gap / 差距 |
|--------------|-------------------------|----------------|-----------|
{% for baseline in baselines %}
| {{baseline.name}} | {{baseline.paper}} | {{baseline.reproduced}} | {{baseline.gap}} |
{% endfor %}

## 5. 计算资源对比 / Computational Resource Comparison

| Resource / 资源 | Paper Reported / 论文报告 | This Run / 本次 |
|----------------|-------------------------|----------------|
| GPU | {{PAPER_GPU}} | {{OUR_GPU}} |
| GPU Memory / 显存 | {{PAPER_GPU_MEM}} GB | {{OUR_GPU_MEM}} GB |
| Training Time / 训练时间 | {{PAPER_TIME}} | {{OUR_TIME}} |
| Parameters / 参数量 | {{PAPER_PARAMS}} | {{OUR_PARAMS}} |

---

*本文件位于 `实验复刻结果汇总/实验结果对比表/`*
*Table generated on / 表格生成于 {{DATE}}*
