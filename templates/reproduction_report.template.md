# Reproduction Report / 复现报告

> Fill both the English file (`复现报告.md`) and the Chinese file (`复现报告-CN.md`).
> 英文版与中文版必须同时产出。

## 1. Metadata / 元信息

| Field | Value |
|-------|-------|
| Experiment ID | `{{EID}}` |
| Paper | {{PAPER_TITLE}} |
| Venue / Year | {{VENUE}} |
| Upstream repo | {{REPO_URL}} |
| Conda environment | `financial` \| `sigtorch39` |
| Host | {{CPU}} cores, {{RAM}} GB RAM, GPU: {{GPU}} |
| Run date | {{DATE}} |
| Random seeds | {{SEEDS}} |

## 2. Data Triage / 数据分诊

| Source | Class | Handling |
|--------|-------|----------|
| {{SOURCE}} | `open` / `licensed` / `absent` | {{HANDLING}} |

> If any source is `licensed` and was substituted by synthetic data, every
> number below MUST be marked `not_testable` rather than compared to the paper.
> 若使用合成数据替代授权数据，下方所有数值判决必须为 `not_testable`，不得与论文数值直接比对。

## 3. Target Metrics / 目标数值

| Metric | Paper value | Reproduced | 95% CI | Rel. error | Tol | Verdict |
|--------|-------------|-----------|--------|-----------|-----|---------|
| {{NAME}} | {{REF}} | {{VAL}} | [{{LO}}, {{HI}}] | {{ERR}} | {{TOL}} | {{VERDICT}} |

Verdict legend: `pass` / `approx` / `fail` / `not_testable` / `blocked`

## 4. Architecture Check / 架构校验

| Component | Paper spec | Implementation | Match |
|-----------|-----------|----------------|-------|
| {{COMPONENT}} | {{SPEC}} | {{IMPL}} | ✅/❌ |
| Total parameters | {{REF_PARAMS}} | {{IMPL_PARAMS}} | ✅/❌ |

## 5. Fixes Applied / 已应用修复

| # | Symptom | Root cause | Patch |
|---|---------|-----------|-------|
| 1 | {{SYMPTOM}} | {{CAUSE}} | {{PATCH}} |

## 6. Blockers / 阻塞项

| Blocker | Type | Impact |
|---------|------|--------|
| {{BLOCKER}} | data / code / hardware | {{IMPACT}} |

## 7. Overall Verdict / 总体判决

| Aspect | Verdict |
|--------|---------|
| Numerical accuracy | {{V1}} |
| Training convergence | {{V2}} |
| Architecture fidelity | {{V3}} |
| **Overall** | **{{OVERALL}}** |

## 8. Artifacts / 产物清单

- `训练结果/` — {{WEIGHTS}}
- `日志/` — {{LOGS}}
- `实验图表（含代码）/` — {{FIGURES}}
- `实验报告/判决结果.json` — machine-readable verdicts
