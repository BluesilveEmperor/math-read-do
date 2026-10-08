# 反例与黑名单 / Anti-Patterns & Blacklist

> 本文档从 SKILL.md 外移的低频道参考内容（13 条反模式清单）。

## 反例与黑名单 / Anti-Patterns & Blacklist

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | MinerU token 未配置就执行 Phase 1.1 | 脚本报 401 | 先检查 `~/.mineru/config.yaml`，未配置则引导用户获取 |
| 2 | Windows 上直跑 Linux 路径脚本 | 换行符/路径分隔符不兼容 | 使用 WSL2 或 `scripts/enable_gpu.ps1` 等 Windows 原生脚本 |
| 3 | 先装包再装语言运行时 | Conda/pip SAT 死锁 | 严格 运行时→版本管理器→锁定→包的顺序 |
| 4 | 只跑一个种子就下判决 | 非确定性被忽略 | 至少 N=5 种子, 95% CI 统计判决 |
| 5 | 只生成英文报告 | 中文用户无法阅读 | 每份报告同时生成 `.md`(英文) 和 `-CN.md`(中文) |
| 6 | 跳过三方审阅直接进 Phase 2 | 论文理解不充分 | 必须跑完 Phase 1.4, 获得 reproducibility_assessment.json |
| 7 | 导出图表时不导出生成代码 | 图表无法独立复现 | 每张图附带 `results/figures/code/plot_*.py` |
| 8 | 跳过可行性预判直接建环境 | 遇到私有数据/硬件时大量浪费 | Phase 0 先快速可行性标记 |
| 9 | 基线失败时不记录偏离 | 丢失诊断信息 | 基线失败必须写 `analysis/gray_areas.md` |
| 10 | conda + pip 一次性混合安装 | SAT 求解器死锁 | 严格 conda→pip 顺序，单步验证 |
| 11 | 单点均值比较忽略方差 | CI 很宽时判决虚假积极 | 用 95% CI 区间验证, 判决基准匹配论文口径 (中位数 CI / Wilson), 均值 x-bar ± CI 仅参考 |
| 12 | 自动翻译不校对专业术语 | 术语混淆 (identification != 识别) | 术语先在 glossary.md 对齐, 翻译后人工校对 |
| 13 | 增量实现时不标注论文出处 | 代码溯源断裂 | 每个函数 docstring 写 `Ref: Section X.Y, Eq.(Z)` |
