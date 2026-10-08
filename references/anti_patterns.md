<!-- 本文件从 SKILL.md 外移的低频道详细内容，主文档保留摘要 + 链接指向此处。 -->
## 反模式 / Anti-Patterns & Blacklist

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 合成数据结果直接与论文数值对比 | 结论无效 | 标记 `skip`，只做"方法可运行性"验证 |
| 2 | 单次运行结果与论文比对 | GAN/MC 方差被当成偏差 | N≥5 种子 + bootstrap 95% CI |
| 3 | 在一个 conda 环境里同时装 TF 2.15 和 signatory | 依赖地狱，numpy 版本互斥 | 双环境，`conda run -n <env>` 调用 |
| 4 | `pip install signatory` | 必然失败 | 从源码编译（需 g++），且只支持 torch 1.9 |
| 5 | torch 1.9 环境装 numpy>=2 | 导入即崩 | 锁 `numpy<2`；esig 需 0.9.8.3 |
| 6 | notebook 里留 `plt.show()` 跑批处理 | 进程 0% CPU 永久挂起（实验 04 原因） | 批处理一律 `matplotlib.use("Agg")` + `savefig` |
| 7 | 直接 load TF1 时代的 SavedModel | `keras_metadata.pb` 与 TF 2.15 不兼容 | 代码里重建架构 + 逐层拷权重（实验 10 修复） |
| 8 | 3.7 GB RAM 下并行 6 个训练 | kernel died，全部白跑 | 最多并行 4–5 个轻量任务，重实验串行 |
| 9 | 假定 `n_lags` 等于真实时间步数 | discriminator 维度不匹配（实验 02 bug） | 用 `x_real.shape[1]` 取真实步数 |
| 10 | 不记录随机种子与超参 | 结果不可重现 | 每次运行落 `results/<exp>/run_config.json` |
| 11 | 年化 Sharpe 时用 365 天 | 数值系统性偏高 | 交易日 252（`fin_tool.metrics.TRADING_DAYS`） |
| 12 | 训练日志只打屏不落盘 | 挂起后无法定位 | 一律 `> logs/<exp>/<run>.log 2>&1` |
