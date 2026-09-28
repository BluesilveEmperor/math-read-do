# Statistical Verification Skill / 统计验证技能

## Description / 描述
对实验结果进行统计验证，产出五态判决。

## Phase / 阶段
verification

## Steps / 步骤

### Step 1: Multi-Seed Execution / 多轮运行
对每个实验配置运行 N 个种子 (默认 N=5)，收集所有指标到 `results/raw_metrics.csv`。

### Step 2: Statistical Computation / 统计计算
判决基准必须匹配论文报告口径（口径匹配原则）。对每个指标计算:

**连续指标**（代价/时间类）:
- 成功试验**中位数** + **percentile bootstrap 95% CI**
- bootstrap 参数: 重采样 ≥20,000 次、固定种子、每次重采样**有放回抽取与样本量相同的点数**
- 样本均值 x̄ ± 95% t-置信区间降为**参考输出**（辅助列，不参与判决）
- 论文明确报告均值时，可切换为 t-CI 判决（口径匹配原则，须在判决 JSON 登记 `ci_method`）

**比例指标**（成功率 p）:
- **Wilson score 95% 区间**（小样本下优于正态近似）

**容差判定**: 双侧语义——|Δ| 超容差即判，超出方向由归因标注（见 Step 4 attribution 字段）

### Step 2.5: CI Degradation Self-Check / CI 退化自检（强制，判决产出前）
1. 断言每次 bootstrap 重采样抽取点数 = 样本量且 **≥2**（防"每次抽 1 点"退化为数据极差 [min, max]）
2. 当成功样本数 ≥2 且非退化分布时，**断言 CI 宽度 < 数据极差**；违例即报错并降级为人工审查，不得静默输出
3. 重采样次数与种子写入判决 JSON（`bootstrap_n_resamples` / `bootstrap_seed`，可审计）

### Step 3: Five-State Verdict / 五态判决
| Verdict | Meaning |
|---------|---------|
| within_ci | Paper claim inside 95% CI（判决基准匹配论文口径: 连续指标中位数 bootstrap CI / 比例指标 Wilson 区间） |
| close_outside_ci | Outside CI but within tolerance（双侧语义: \|Δ\| 在容差内） |
| outside_tolerance | Outside both CI and tolerance（双侧语义: \|Δ\| 超容差即判，方向由归因标注） |
| not_testable | Could not execute |
| static_check_failed | Config/check failed |

### Step 4: Diagnostic Output / 诊断输出
失败时生成诊断，链接到 Top-12 失败模式。

## Outputs / 产出
- `results/raw_metrics.csv`: 原始指标
- `reports/verdict.json`: 判决结果 (含中英文字段)
- `reports/diagnosis.md` / `reports/diagnosis.zh.md`: 诊断报告
