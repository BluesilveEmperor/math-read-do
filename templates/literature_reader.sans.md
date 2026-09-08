<style>
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-hover: #f2f1f5;
  --bg-selected: #e7e7ef;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --theme-dark: #0079f3;
}

.markdown-preview.markdown-preview {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: "SF Pro Display", "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
  font-size: 16px;
  line-height: 1.8;
  text-align: justify;
  max-width: 820px;
  margin: 0 auto;
  padding: 2em 2.5em;
}

.markdown-preview.markdown-preview h1 {
  font-family: "SF Pro Display", "Microsoft YaHei", sans-serif;
  font-size: 28.8px;
  font-weight: bold;
  text-align: center;
  line-height: 1.4;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
}

.markdown-preview.markdown-preview h2 {
  font-family: "SF Pro Display", "Microsoft YaHei", sans-serif;
  font-size: 1.4em;
  font-weight: bold;
  margin-top: 1.5em;
  margin-bottom: 0.6em;
  padding-bottom: 0.25em;
  border-bottom: 1px solid var(--bg-selected);
}

.markdown-preview.markdown-preview h3 {
  font-family: "SF Pro Display", "Microsoft YaHei", sans-serif;
  font-size: 1.1em;
  font-weight: bold;
  margin-top: 1.3em;
  margin-bottom: 0.5em;
}

.markdown-preview.markdown-preview p {
  margin: 0.6em 0;
  text-indent: 0;
}

.markdown-preview.markdown-preview strong,
.markdown-preview.markdown-preview b {
  font-family: "SF Pro Display", "Microsoft YaHei", sans-serif;
  font-weight: bold;
}

.markdown-preview.markdown-preview em,
.markdown-preview.markdown-preview i {
  font-style: italic;
}

.markdown-preview.markdown-preview a {
  color: var(--theme-dark);
  text-decoration: none;
}

.markdown-preview.markdown-preview hr {
  width: 10em;
  height: 1px;
  margin: 2em auto;
  background: var(--text-primary);
  border: 0;
}

.markdown-preview.markdown-preview ul,
.markdown-preview.markdown-preview ol {
  padding-left: 1.5em;
}

.markdown-preview.markdown-preview li > p {
  margin: 0;
  text-indent: 0 !important;
}

.markdown-preview.markdown-preview table {
  width: auto;
  min-width: 50%;
  margin: 1em auto;
  border: 0;
  border-collapse: collapse;
  background: transparent;
}

.markdown-preview.markdown-preview th,
.markdown-preview.markdown-preview td {
  border: 0;
  background: transparent;
  padding: 5px 12px;
}

.markdown-preview.markdown-preview th {
  font-weight: 600;
}

.markdown-preview.markdown-preview table p {
  text-indent: 0;
  margin: 0;
}

.markdown-preview.markdown-preview blockquote {
  margin: 0.8em 0;
  padding: 0.5em 1em;
  border: 2px solid #e7e7ef;
  border-radius: 6px;
  background: #f8f9fa;
  font-style: normal;
}

.markdown-preview.markdown-preview blockquote p {
  text-indent: 0;
}

.markdown-preview.markdown-preview code,
.markdown-preview.markdown-preview pre code {
  font-family: "SF Mono", "Consolas", monospace;
  font-size: 0.9em;
}

.markdown-preview.markdown-preview pre {
  border: 1px solid var(--bg-selected);
  border-radius: 4px;
  padding: 0.8em 1em;
  margin: 1em 0;
  overflow-x: auto;
}

.markdown-preview.markdown-preview .perspective-card {
  margin: 1.5em 0;
  padding: 0;
  border: 2px solid #e7e7ef;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.markdown-preview.markdown-preview .perspective-card > blockquote:first-child {
  margin: 0;
  padding: 0.5em 1em;
  border: 0;
  border-radius: 0;
  font-weight: 600;
  font-size: 1.05em;
}

.markdown-preview.markdown-preview .perspective-card > *:not(:first-child) {
  padding-left: 1em;
  padding-right: 1em;
}

.markdown-preview.markdown-preview .perspective-card > :last-child {
  padding-bottom: 1em;
}

.markdown-preview.markdown-preview .perspective-card.student {
  border-color: #0969da;
}

.markdown-preview.markdown-preview .perspective-card.advisor {
  border-color: #1a7f37;
}

.markdown-preview.markdown-preview .perspective-card.reviewer {
  border-color: #8250df;
}

.markdown-preview.markdown-preview .katex-display {
  margin: 1.2em 0;
  padding: 0.8em 1em;
  border-left: 3px solid var(--theme-dark);
  background: var(--bg-secondary);
  border-radius: 0 4px 4px 0;
  overflow-x: auto;
}

.markdown-preview.markdown-preview > blockquote:first-of-type {
  background: var(--bg-secondary);
  border: 1px solid var(--bg-selected);
  border-radius: 6px;
  padding: 1em 1.2em;
}

@media print {
  .markdown-preview.markdown-preview {
    max-width: 100%;
    padding: 0;
    font-size: 12pt;
  }
}
</style>


# 文献阅读：{{PAPER_TITLE}}

> **论文**: {{PAPER_TITLE}}
> **作者**: {{AUTHORS}}
> **发表**: {{VENUE}}
> **领域**: {{DOMAIN}}
> **论文类型**: {{PAPER_TYPE}} — {{PAPER_TYPE_DESC}}
> **审阅日期**: {{DATE}}
> **审阅视角**: {{PERSPECTIVE}}

---

## 论文结构导航

| 章节 | 页码 | 论证功能 | 核心内容 |
|------|------|---------|---------|
{% for section in sections %}
| {{section.title}} | p.{{section.page}} | {{section.function}} | {{section.summary}} |
{% endfor %}

---

## 术语表

| 术语 | 英文全称 | 中文译法 | 首次出现 | 备注 |
|------|---------|---------|---------|------|
{% for term in terminology %}
| {{term.term}} | {{term.full_name}} | {{term.translation}} | {{term.first_appearance}} | {{term.notes}} |
{% endfor %}

---

## 关键图表索引

| ID | 内容 | 页码 | 关联分析 |
|----|------|------|---------|
{% for fig in figures %}
| {{fig.id}} | {{fig.caption_zh}} | p.{{fig.page}} | {{fig.related_section}} |
{% endfor %}

---

{% if PERSPECTIVE in ["student", "all"] %}
## 研究生视角

<div class="perspective-card student">

> 🎓 以学习理解为导向 — 深度理解论文核心方法

### 4.1 摘要

{{STUDENT_ABSTRACT}}
*(来源: p.1 Abstract)*

### 4.2 研究问题

{% for rq in research_questions %}
{{loop.index}}. **{{rq.question}}**
   *(来源: {{rq.source}})*
{% endfor %}

### 4.3 核心方法

{{STUDENT_METHODS}}

**关键公式**:

{% for formula in key_formulas %}
- **{{formula.label}}** — {{formula.description}} *(来源: {{formula.source}})*:

$$
{{formula.latex}}
$$

{% endfor %}

### 4.4 实验结果

| 指标 | 论文声称值 | 来源 | 证据强度 |
|------|-----------|------|---------|
{% for metric in student_metrics %}
| {{metric.name}} | {{metric.value}} | {{metric.source}} | {{metric.evidence_strength}} |
{% endfor %}

### 4.5 对复现的指导

- **核心算法**: {{REPRO_CORE_ALGORITHM}}
- **关键超参数**: {{REPRO_HYPERPARAMS}}
- **数据集**: {{REPRO_DATASETS}}
- **主要风险**: {{REPRO_RISKS}}

</div>

{% endif %}

{% if PERSPECTIVE in ["advisor", "all"] %}

---

## 导师视角

<div class="perspective-card advisor">

> 🎓 以指导评估为导向 — 判断学术价值与复现可行性

### 5.1 文献定位

| 维度 | 评估 | 来源 |
|------|------|------|
| 发表会议 | {{ADVISOR_VENUE}} | — |
| 领域 | {{ADVISOR_DOMAIN}} | — |
| 难度评级 | {{ADVISOR_DIFFICULTY}} ⭐ / 5 | — |
| 创新程度 | {{ADVISOR_INNOVATION}} ⭐ / 5 | — |

### 5.2 可复现性评估

| 维度 | 状态 | 证据 |
|------|------|------|
| 代码公开 | {{ADVISOR_CODE_AVAIL}} | {{ADVISOR_CODE_EVIDENCE}} |
| 数据可用 | {{ADVISOR_DATA_AVAIL}} | {{ADVISOR_DATA_EVIDENCE}} |
| 环境说明 | {{ADVISOR_ENV_SPEC}} | {{ADVISOR_ENV_EVIDENCE}} |
| 方法清晰度 | {{ADVISOR_CLARITY}} | {{ADVISOR_CLARITY_EVIDENCE}} |
| **总体评级** | **{{ADVISOR_REPRO_RATING}}** | — |

### 5.3 指导建议

- **推荐指数**: {{ADVISOR_RECOMMENDATION}} ⭐ / 5
- **适合方向**: {{ADVISOR_SUITABLE}}
- **先修知识**: {{ADVISOR_PREREQUISITES}}
- **延伸方向**: {{ADVISOR_EXTENSIONS}}

</div>

{% endif %}

{% if PERSPECTIVE in ["all", "reviewer"] %}

---

## 审稿人视角

<div class="perspective-card reviewer">

> 🎯 以同行评审为导向 — 批判性审查

### 6.1 总体评价

| 维度 | 评分 | 依据 |
|------|------|------|
| 推荐意见 | {{REVIEWER_RECOMMENDATION}} | {{REVIEWER_RECOMMENDATION_RATIONALE}} |
| 创新性 | {{REVIEWER_INNOVATION}} ⭐ / 5 | {{REVIEWER_INNOVATION_RATIONALE}} |
| 方法论 | {{REVIEWER_METHODOLOGY}} ⭐ / 5 | {{REVIEWER_METHODOLOGY_RATIONALE}} |
| 写作质量 | {{REVIEWER_WRITING}} ⭐ / 5 | {{REVIEWER_WRITING_RATIONALE}} |

### 6.2 主要修改意见

**强制性**:
{% for item in reviewer_mandatory %}
{{loop.index}}. {{item.comment}} *(来源: {{item.source}})*
{% endfor %}

**建议性**:
{% for item in reviewer_suggested %}
{{loop.index}}. {{item.comment}} *(来源: {{item.source}})*
{% endfor %}

</div>

{% endif %}

{% if PERSPECTIVE == "all" %}

---

## 视角交叉对比

| 维度 | 研究生 | 导师 | 审稿人 |
|------|--------|------|--------|
| 主要优势 | {{CROSS_STRENGTH_STUDENT}} | {{CROSS_STRENGTH_ADVISOR}} | {{CROSS_STRENGTH_REVIEWER}} |
| 主要担忧 | {{CROSS_CONCERN_STUDENT}} | {{CROSS_CONCERN_ADVISOR}} | {{CROSS_CONCERN_REVIEWER}} |
| 方法洞察 | {{CROSS_METHOD_STUDENT}} | {{CROSS_METHOD_ADVISOR}} | {{CROSS_METHOD_REVIEWER}} |

{% endif %}

---

## 复现流程输入

| 产出 | 消费方 | 用途 |
|------|--------|------|
| 研究生审阅 | Phase 2-4 | 深度理解方法，指导复现计划 |
| 导师审阅 | G01 门禁 | 可复现性评级 → 决定是否继续 |
| 审稿人审阅 | Phase 5 | 批判性审查辅助判决 |
| 术语表 | Phase 4-6 | 代码/报告术语一致性 |
| 关键公式索引 | Phase 2, 4 | 环境重建与增量实现参考 |

---

*审阅生成于 {{DATE}} by Math-Read-Do Literature Reader Engine*
