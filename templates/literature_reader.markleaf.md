---
html:
  styles:
    - "data:text/css;base64,{% raw %}{{ css_base64 }}{% endraw %}"
---

<style>
{% raw %}
/* ===== MarkLeaf LaTeX 风格 — 文献阅读报告 ===== */
/* 设计来源: markleaf/packages/styles/latex.css + base.css + colors-*.css */

:root {
  /* 排版变量 (来自 base.css) */
  --ml-line-height: 1.7;
  --ml-font-size: 16px;
  --ml-max-width: 820px;

  /* 浅色主题 (来自 colors-apple-blue.css) */
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-hover: #f2f1f5;
  --bg-selected: #e7e7ef;
  --bg-selected-hover: #dddde8;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-tertiary: #999999;
  --theme-light: #0284f9;
  --theme-dark: #0079f3;

  /* 字体 (来自 latex.css) */
  --font-serif: "Latin Modern Roman", "Computer Modern", "CMU Serif",
                "Times New Roman", "宋体-简", "宋体", serif;
  --font-sans: "Latin Modern Roman", "Computer Modern", "CMU Serif",
               "Helvetica", "方正黑体_GBK", "黑体", sans-serif;
  --font-mono: "Latin Modern Mono", "Computer Modern Typewriter",
               "CMU Typewriter Text", "Courier New", monospace;
  --font-cjk: "霞鹜文楷", "LXGW WenKai", "Noto Serif CJK SC",
              "Source Han Serif CN", "宋体-简", "宋体", serif;
}

/* ===== 文档主体 (来自 base.css) ===== */
.markdown-preview.markdown-preview {
  width: min(100%, var(--ml-max-width));
  margin: 0 auto;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-serif), var(--font-cjk);
  font-size: var(--ml-font-size);
  line-height: var(--ml-line-height);
  text-align: justify;
  padding: 2em 2.5em;
}

/* ===== 标题 (来自 latex.css) ===== */
.markdown-preview.markdown-preview h1 {
  font-family: var(--font-sans), var(--font-cjk);
  font-size: calc(var(--ml-font-size) * 1.8);
  font-weight: bold;
  font-synthesis: none;
  margin-top: 1.8em;
  margin-bottom: 0.8em;
  padding-bottom: 0.3em;
  border-bottom: 2px solid var(--text-primary);
  text-align: center;
  line-height: 1.4;
}

.markdown-preview.markdown-preview h2 {
  font-family: var(--font-sans), var(--font-cjk);
  font-size: calc(var(--ml-font-size) * 1.4);
  font-weight: bold;
  font-synthesis: none;
  margin-top: 1.5em;
  margin-bottom: 0.6em;
  padding-bottom: 0.25em;
  border-bottom: 1px solid var(--bg-selected);
  line-height: 1.4;
}

.markdown-preview.markdown-preview h3 {
  font-family: var(--font-sans), var(--font-cjk);
  font-size: calc(var(--ml-font-size) * 1.1);
  font-weight: bold;
  font-synthesis: none;
  margin-top: 1.3em;
  margin-bottom: 0.5em;
  line-height: 1.4;
}

.markdown-preview.markdown-preview h4 {
  font-family: var(--font-sans), var(--font-cjk);
  font-size: var(--ml-font-size);
  font-weight: bold;
  font-synthesis: none;
  margin-top: 1.1em;
  margin-bottom: 0.4em;
  line-height: 1.4;
}

/* ===== 段落 (来自 base.css) ===== */
.markdown-preview.markdown-preview p {
  margin: calc(var(--ml-line-height) * 0.53em) 0;
  text-indent: 0;
}

/* ===== 粗体/斜体 (来自 latex.css) ===== */
.markdown-preview.markdown-preview strong,
.markdown-preview.markdown-preview b {
  font-family: var(--font-sans), var(--font-cjk);
  font-weight: bold;
  font-synthesis: none;
}

.markdown-preview.markdown-preview em,
.markdown-preview.markdown-preview i {
  font-family: "Latin Modern Roman", "Computer Modern", "CMU Serif",
               "Times New Roman", "楷体", "KaiTi", serif;
  font-style: italic;
  font-synthesis: none;
}

/* ===== 链接 (来自 latex.css) ===== */
.markdown-preview.markdown-preview a {
  color: var(--theme-dark);
  text-decoration: none;
}

/* ===== 分隔线 (来自 base.css) ===== */
.markdown-preview.markdown-preview hr {
  width: 10em;
  height: 1px;
  margin: 2em auto;
  border: 0;
  background: var(--text-primary);
}

/* ===== 列表 (来自 base.css) ===== */
.markdown-preview.markdown-preview ul,
.markdown-preview.markdown-preview ol {
  padding-left: 1.5em;
  margin: calc(var(--ml-line-height) * 0.53em) 0;
}

.markdown-preview.markdown-preview li {
  padding-left: 0.3em;
  margin-bottom: 0.2em;
}

.markdown-preview.markdown-preview li > p {
  margin: 0;
}

/* ===== 引用框 ===== */
.markdown-preview.markdown-preview blockquote {
  margin: 0.8em 0;
  padding: 0.5em 0.85em;
  border: 2px solid #dddde8;
  border-radius: 6px;
  color: #1a1a1a;
  background: #f8f9fa;
  font-style: normal;
}

.markdown-preview.markdown-preview blockquote p {
  color: #1a1a1a;
  font-style: normal;
  text-indent: 0;
}

/* ===== 三线表 ===== */
.markdown-preview.markdown-preview table {
  width: auto;
  min-width: 50%;
  margin: 1em auto;
  border: 0;
  border-top: 1.5px solid #1a1a1a;
  border-bottom: 1.5px solid #1a1a1a;
  border-collapse: collapse;
  background: transparent;
}

.markdown-preview.markdown-preview th {
  border: 0;
  border-bottom: 0.75px solid #1a1a1a;
  background: transparent;
  padding: 5px 12px;
  font-weight: 600;
  text-align: left;
}

.markdown-preview.markdown-preview td {
  border: 0;
  padding: 4px 12px;
  background: transparent;
}

.markdown-preview.markdown-preview table p {
  text-indent: 0;
  margin: 0;
}

/* ===== 代码 (来自 latex.css) ===== */
.markdown-preview.markdown-preview code {
  font-family: var(--font-mono);
  font-size: calc(var(--ml-font-size) * 0.9);
  background: transparent;
  color: var(--text-primary);
  padding: 0.12em 0.35em;
  border-radius: 3px;
}

.markdown-preview.markdown-preview pre {
  background: transparent;
  border: 1px solid var(--text-primary);
  border-radius: 0;
  padding: 0.8em 1em;
  margin: 1em 0;
  overflow-x: auto;
}

.markdown-preview.markdown-preview pre code {
  color: var(--text-primary);
  background: transparent;
  padding: 0;
}

/* ===== 公式 ===== */
.markdown-preview.markdown-preview .katex-display {
  margin: 1.2em 0;
  padding: 0.8em 1em;
  border-left: 3px solid #0079f3;
  background: #f8f9fa;
  border-radius: 0 4px 4px 0;
  overflow-x: auto;
}

/* ===== 视角卡片 ===== */
.markdown-preview.markdown-preview .perspective-card {
  margin: 1.5em 0;
  padding: 0;
  border: 2px solid #dddde8;
  border-radius: 6px;
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

/* 研究生视角 — 蓝色 */
.markdown-preview.markdown-preview .perspective-card.student {
  border-color: #0969da;
  background: #f0f7ff;
}
.markdown-preview.markdown-preview .perspective-card.student > blockquote:first-child {
  background: #0969da;
  color: #ffffff;
}

/* 导师视角 — 绿色 */
.markdown-preview.markdown-preview .perspective-card.advisor {
  border-color: #1a7f37;
  background: #f0f9f0;
}
.markdown-preview.markdown-preview .perspective-card.advisor > blockquote:first-child {
  background: #1a7f37;
  color: #ffffff;
}

/* 审稿人视角 — 紫色 */
.markdown-preview.markdown-preview .perspective-card.reviewer {
  border-color: #8250df;
  background: #f5f0ff;
}
.markdown-preview.markdown-preview .perspective-card.reviewer > blockquote:first-child {
  background: #8250df;
  color: #ffffff;
}

/* ===== 信息头卡片 ===== */
.markdown-preview.markdown-preview > blockquote:first-of-type {
  background: #f8f9fa;
  border: 1px solid #dddde8;
  border-radius: 6px;
  padding: 1em 1.2em;
  font-size: 0.95em;
}

.markdown-preview.markdown-preview > blockquote:first-of-type p {
  margin: 0.3em 0;
}

/* ===== 打印优化 ===== */
@media print {
  .markdown-preview.markdown-preview {
    max-width: 100%;
    padding: 0;
    font-size: 12pt;
    line-height: 1.6;
  }
  .markdown-preview.markdown-preview h1 { font-size: 16pt; }
  .markdown-preview.markdown-preview h2 { font-size: 14pt; }
  .markdown-preview.markdown-preview h3 { font-size: 12pt; }
  .markdown-preview.markdown-preview table { font-size: 10pt; }
}
{% endraw %}
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
