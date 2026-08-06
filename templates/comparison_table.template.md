# Comparison Table / 实验结果对比表

## Main results / 主要结果

| Config | Metric | Reproduced | Paper | Abs. error | Rel. error | Verdict |
|--------|--------|-----------|-------|-----------|-----------|---------|
| {{CFG}} | {{METRIC}} | {{VAL}} | {{REF}} | {{ABS}} | {{REL}} | {{VERDICT}} |

## Baseline comparison / 基线对比

| Strategy | Metric A | Metric B |
|----------|----------|----------|
| Analytic / classical baseline | {{A}} | {{B}} |
| Neural network ({{PARAM}}) | {{A}} | {{B}} |

## Multi-seed statistics / 多种子统计

| Metric | N seeds | Mean | Std | 95% CI | Paper | Verdict |
|--------|---------|------|-----|--------|-------|---------|
| {{METRIC}} | {{N}} | {{MEAN}} | {{STD}} | [{{LO}}, {{HI}}] | {{REF}} | {{VERDICT}} |

> Deterministic experiments may use N=1; GAN / Monte-Carlo experiments require N>=5.
> 确定性实验可 N=1 并注明；GAN 与蒙特卡洛类实验必须 N≥5。

## Architecture verification / 模型架构验证

| Component | Paper | Implementation | Match |
|-----------|-------|----------------|-------|
| {{COMPONENT}} | {{SPEC}} | {{IMPL}} | ✅/❌ |

## Training trace / 训练验证

| Epoch | Loss | Trend |
|-------|------|-------|
| 1 | {{L1}} | ↓ |
| 2 | {{L2}} | ↓ |

## Summary / 总结

| Aspect | Verdict |
|--------|---------|
| Numerical accuracy / 数值精度 | {{V1}} |
| Convergence / 训练收敛性 | {{V2}} |
| Architecture / 模型架构 | {{V3}} |
| Baseline / 基线对比 | {{V4}} |
| **Overall / 总体** | **{{OVERALL}}** |
