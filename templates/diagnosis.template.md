# Diagnosis / 诊断分析

Use this template whenever an experiment is **not** `pass`.
任何非 `pass` 的实验都必须产出本诊断。

## 1. Failure classification / 失败归类

Pick exactly one root category. 必须且只能选一类：

| Category | Definition | Verdict |
|----------|-----------|---------|
| ☐ Licensed data missing / 数据授权缺失 | CRSP, WRDS, Bloomberg, ICAP ... | `not_testable` |
| ☐ Upstream code missing / 上游代码缺失 | Repo never committed required modules | `blocked` |
| ☐ Hardware limit / 硬件限制 | OOM, kernel died, timeout | `blocked` |
| ☐ Environment conflict / 环境冲突 | Version incompatibility | fix and re-run |
| ☐ Implementation deviation / 实现偏差 | Code runs but numbers differ | `fail` / `approx` |

## 2. Evidence / 证据

```
{{PASTE THE ACTUAL LOG EXCERPT / TRACEBACK / SHAPE MISMATCH HERE}}
```

Command that produced it / 复现命令:

```bash
{{COMMAND}}
```

## 3. Root cause analysis / 根因分析

**Symptom / 现象**: {{SYMPTOM}}

**Investigation / 排查过程**:
1. {{STEP}}
2. {{STEP}}

**Root cause / 根本原因**: {{ROOT_CAUSE}}

## 4. Remediation / 处置

| Option | Feasible | Cost | Decision |
|--------|----------|------|----------|
| Patch the code / 修改代码 | ☐ | {{COST}} | ☐ |
| Synthetic data substitute / 合成数据替代 | ☐ | {{COST}} | ☐ |
| Reduce scale / 降低规模 | ☐ | {{COST}} | ☐ |
| Declare blocked / 声明阻塞 | ☐ | — | ☐ |

**Chosen / 选定方案**: {{DECISION}}

### If synthetic substitution was chosen / 若选择合成数据

- Generator script / 生成脚本: {{SCRIPT}}
- Seed / 种子: {{SEED}}
- Dimension match with original / 与原数据维度一致: ☐ yes ☐ no
- ⚠️ All downstream numbers are `not_testable`.
  ⚠️ 下游所有数值判决降级为 `not_testable`，报告中必须显著标注。

## 5. Reproducibility impact / 对可复现性的影响

{{What can and cannot be concluded about the paper from this run.}}
{{本次运行对论文结论能验证什么、不能验证什么。}}
