# Statistical Verification Skill / 统计验证技能

## Description / 描述
对实验结果进行统计验证，产出五态判决。

## Phase / 阶段
verification

## Steps / 步骤

### Step 1: Multi-Seed Execution / 多轮运行
对每个实验配置运行 N 个种子 (默认 N=5)，收集所有指标到 `results/raw_metrics.csv`。

### Step 2: Statistical Computation / 统计计算
对每个指标计算:
- 样本均值 x̄
- 样本标准差 s
- 95% t-置信区间: x̄ ± t_{0.025, N-1} · s/√N

### Step 3: Five-State Verdict / 五态判决
| Verdict | Meaning |
|---------|---------|
| within_ci | Paper claim inside 95% CI |
| close_outside_ci | Outside CI but within tolerance |
| outside_tolerance | Outside both CI and tolerance |
| not_testable | Could not execute |
| static_check_failed | Config/check failed |

### Step 4: Diagnostic Output / 诊断输出
失败时生成诊断，链接到 Top-12 失败模式。

## Outputs / 产出
- `results/raw_metrics.csv`: 原始指标
- `reports/verdict.json`: 判决结果 (含中英文字段)
- `reports/diagnosis.md` / `reports/diagnosis.zh.md`: 诊断报告
