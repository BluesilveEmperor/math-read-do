# Reproduction Diagnosis Report
# 复现诊断报告

## Failure Summary / 失败摘要

{{FAILURE_SUMMARY_EN}}

{{FAILURE_SUMMARY_ZH}}

## Detection & Analysis / 检测与分析

### {{DIAG_ITEM_1_TITLE_EN}}
### {{DIAG_ITEM_1_TITLE_ZH}}

| Property / 属性 | Value / 值 |
|----------------|-----------|
| Observation / 观察 | {{OBS_1_EN}} / {{OBS_1_ZH}} |
| Hypothesis / 假说 | {{HYP_1_EN}} / {{HYP_1_ZH}} |
| Evidence / 证据 | {{EVIDENCE_1_EN}} / {{EVIDENCE_1_ZH}} |
| Confidence / 置信度 | {{CONF_1}}% |

### {{DIAG_ITEM_2_TITLE_EN}}
### {{DIAG_ITEM_2_TITLE_ZH}}

| Property / 属性 | Value / 值 |
|----------------|-----------|
| Observation / 观察 | {{OBS_2_EN}} / {{OBS_2_ZH}} |
| Hypothesis / 假说 | {{HYP_2_EN}} / {{HYP_2_ZH}} |
| Evidence / 证据 | {{EVIDENCE_2_EN}} / {{EVIDENCE_2_ZH}} |
| Confidence / 置信度 | {{CONF_2}}% |

## Failure Mode Classification / 失败模式分类

| # | Failure Mode / 失败模式 | Match / 匹配 |
|---|------------------------|-------------|
| 1 | 代码/数据缺失 | {{FM1}} |
| 2 | 环境漂移 | {{FM2}} |
| 3 | CUDA版本冲突 | {{FM3}} |
| 4 | 编译器ABI不兼容 | {{FM4}} |
| 5 | 包依赖冲突 | {{FM5}} |
| 6 | 非确定性 | {{FM6}} |
| 7 | BLAS变体差异 | {{FM7}} |
| 8 | 跨平台路径 | {{FM8}} |
| 9 | 数据泄露 | {{FM9}} |
| 10 | 预训练权重漂移 | {{FM10}} |
| 11 | 选择性报告 | {{FM11}} |
| 12 | 上游依赖位腐 | {{FM12}} |

## Recommended Fix / 推荐修复

### Priority 1 / 优先级 1

{{FIX_1_EN}}

{{FIX_1_ZH}}

### Priority 2 / 优先级 2

{{FIX_2_EN}}

{{FIX_2_ZH}}

## Context / 上下文

- Error Log: `logs/run_experiment_{{RUN_ID}}.log`
- Baseline: `results/baseline_metrics.json`
- Version Spec: `env/version_spec.json`
- Infra: `infra/infra_manifest.json`
