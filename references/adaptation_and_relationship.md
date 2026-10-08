# 适配新算法 & 与 math-read-do 的关系（从 SKILL.md 外移）

> 本文件由 SKILL.md 外移的低频道内容，完整保留原信息。首响无需加载，按需查阅。

## 适配新算法 / Adapting to a New Algorithm

要适配一个新的 .obj 输出算法（如网格参数化、变形、布尔运算），只需替换三个**范本文件**：

| 步骤 | 替换文件 | 说明 |
|------|---------|------|
| 1 | `qem_tool/qem_core.py` → `new_algo_core.py` | 用你的算法引擎替换 QEM 核心 |
| 2 | `qem_tool/cli.py` → 更新 | 更新 CLI 参数和调用逻辑 |
| 3 | `tests/test_qem_core.py` → `test_new_algo.py` | 写新测试，fixtures 可复用 |

**框架层文件无需修改**：`obj_io.py`, `tests/test_obj_io.py`, `scripts/`, `templates/` 完全可复用。

---

## 与 math-read-do 的关系 / Relationship to math-read-do

| 维度 | math-read-do (通用数学实验复现) | math-read-do-obj (OBJ 图形学实验复现) |
|------|-------------------------------|----------------------------------------|
| 目标 | 任意数学论文复现（数值/符号/统计） | 任意输出 .obj 的图形学/几何算法复现 |
| Phase 1 | PDF 解析 + MinerU + 三方审阅 | 直接算法理解 + 关键公式提取（无 PDF 解析） |
| 输入 | PDF 论文 / arXiv 链接 | .obj 文件 + 算法规格 |
| Phase 5 | 多随机种子统计验证 (N>=5) | 多模型 + 多参数交叉验证（确定性算法为主） |
| 核心依赖 | mineru-open-sdk, pyyaml | numpy |
| 输出 | 双语报告 + 判决 | 简化 .obj + 双语对比表 |
| 典型用户 | 数学研究者 | 图形学/3D 开发者 |