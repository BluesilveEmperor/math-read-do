<!-- 本文件从 SKILL.md 外移的低频道详细内容，主文档保留摘要 + 链接指向此处。 -->
<!-- 此清单的单一真相源为 fin_tool/registry.py（REGISTRY 字典）。本文件为人类可读视图，
     请勿手动编辑具体参数；如需更新实验状态/数值/修复，请修改 registry.py 后同步本文件。
     验证：python -c "from fin_tool import registry as R; print(R.summary())" -->
## 内建实验档案 / Built-in Experiment Registry

> ⚠️ **单一真相源**：实验档案的权威数据定义在 [`fin_tool/registry.py`](../fin_tool/registry.py) 的 `REGISTRY` 字典中。本文件为人类可读视图，具体参数（名称/公式/字段/状态/修复）以 `registry.py` 为准。

10 篇论文的真实复现结果（WSL2 Ubuntu, 8 核 CPU, 3.7 GB RAM, 无 GPU）：

| 编号 | 实验 | 期刊 | 环境 | 状态 | 关键结果 / 阻塞原因 |
|------|------|------|------|------|--------------------|
| 01 | Robust Deep Hedging | Quantitative Finance 2022 | financial | ✅ 完成 | 4/4 notebooks 执行成功 |
| 02 | Sig-Wasserstein GANs | Mathematical Finance 2023 | sigtorch39 | ✅ 完成 | 4/4 组实验（需 discriminator 维度修复） |
| 03 | Joint Calibration SPX/VIX | Mathematical Finance 2024 | sigtorch39 | ⚠️ 部分 | configs 2–5 输出 `Rho_d=4.npy`；6–8 空目录 |
| 04 | Deep xVA Solver | SIAM J. Fin. Math 2023 | financial | ⚠️ 部分 | callOption Y0≈1.9673, fvaForward Y0≈1.98；BCVA 挂起 |
| 05 | Fin-GAN | Quantitative Finance 2024 | financial | ✅ 完成 | SR_w(test)=0.88, SR_w(val)=2.19（合成数据） |
| 06 | Signature-Based Models | SIAM J. Fin. Math 2023 | sigtorch39 | ❌ 阻塞 | 缺 Bloomberg SPX 到期日/行权价数据 |
| 07 | Network Superhedging | Mathematical Finance 2022 | sigtorch39 | ✅ 完成 | λ=200: 1.3274/0.4072；λ=1e5: 2.0952/0.9966 |
| 08 | Signature Volatility Models | SIAM J. Fin. Math 2025 | sigtorch39 | ❌ 阻塞 | 上游仓库缺 fourier.py 等核心模块 |
| 09 | Optimal Stopping Randomized NN | Frontiers Math Fin. 2023 | financial | ✅ 完成 | 全部 configs 通过，NLSM price ≈ 10.9–21.7 |
| 10 | Deep Weighted Monte Carlo | Quantitative Finance 2023 | financial | ⚠️ 部分 | 模型已修复，完整 notebook 内存不足 |

**统计**: 完全复现 5 / 部分复现 3 / 无法复现 2

实验 07 是唯一达到 0.01% 容差内逐项匹配的实验，可作为框架的正确性基准：

| 配置 | 指标 | 复现值 | 论文值 | 判决 |
|------|------|--------|--------|------|
| λ=200 | 价格 | 1.3274 | 1.3274 | pass |
| λ=200 | 对冲概率 | 0.4072 | 0.4072 | pass |
| λ=1e5 | 价格 | 2.0952 | 2.0952 | pass |
| λ=1e5 | 对冲概率 | 0.9966 | 0.9966 | pass |
| — | 参数总量 | 11,191 | 11,191 | pass |

