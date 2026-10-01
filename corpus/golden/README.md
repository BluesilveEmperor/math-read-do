# 金样本矩阵（Golden Matrices）

intrinsic-simplification（SIGGRAPH 2023）实验导出的 18 个稀疏矩阵资产，作为算法性质回归测试的黄金基准。
来源：`ICE_Experiment_Logs/matrices/`（spot 系列实验输入 `spot.obj` 2,930 顶点、dragon 系列输入 `dragon_fat.obj` 15,746 顶点，见 `corpus/MANIFEST.json`）。

## 布局

```
corpus/golden/
├── README.md            # 本文件
├── checksums.json       # 18 矩阵登记（sha256/bytes/dims/nnz/统计范围）
└── spot/                # spot 系列 9 个 .spmat 全量入库（~0.94 MB）
```

- **spot 系列（9 个，`in_repo: true`）**：逐字节入库于 `spot/`，测试做完整性自检 + 数学性质断言。
- **dragon 系列（9 个，`in_repo: false`）**：单文件最大 1.4 MB+、整体不入库，仅以校验和登记（SHA-256/维度/nnz/取值范围/行和范围）；测试经环境变量 `ICE_GOLDEN_DRAGON_DIR` 指向文件所在目录后执行全量校验。

## 文件格式与解析

`.spmat` 为稀疏三元组文本：每行 `row col value`，索引 1-based（MATLAB 兼容）。解析用 `corpus/spmat.py` 的 `parse_spmat()`（非法行/空行显式报错，含文件名+行号）。

## 各 kind 数学性质（以实测为准）

| kind | 文件 | 实测性质 |
|------|------|----------|
| `scalar_prolongation` | `01_prolongation.spmat` / `01_dragon_prolongation.spmat` | 每行行和=1（spot 实测最大偏差 4.4e-16）；取值 ∈ [0,1]；矩阵为 2930×500（spot）/ 15746×1000（dragon），行=细化前顶点、列=粗化后顶点 |
| `laplacian` | `01_laplace.spmat` / `01_dragon_laplace.spmat` | 行和≈0（实测 ~1e-15，断言容差 1e-10）；对角元<0；**严格对称**（实测 max\|L_ij−L_ji\|=0） |
| `mass` | `01_mass.spmat` / `01_dragon_mass.spmat` | 纯对角；对角元>0 |
| `vector_prolongation_re/im` | `05_spot_vprolong_*` / `05_vector_prolongation_*` | （re,im）同稀疏模式配对为复矩阵；**非空行**逐行条目模长之和=1（每个条目=重心权重×单位旋转传输系数；spot 实测最大偏差 6.7e-16）；每行复数行和模长 ≤1（spot 实测恰为 1） |
| `connection_laplacian_re/im` | `05_spot_claplace_*` / `05_connection_laplace_*` | 复矩阵 Hermitian：re 部分对角>0 且**严格对称**；im 部分对角==0 且**严格反对称**（实测 max\|L_ij+L_ji\|=0） |
| `vector_mass_re/im` | `05_spot_vmass_*` / `05_vector_mass_*` | re 纯对角且对角>0；im 全零（显式零条目仍导出） |

## 已知现象登记

1. **dragon `05_vector_prolongation` 行偏差**：逐行条目模长之和存在少数行偏差（实测最大 8.9e-2，中位 0），根因待 E3 移植时调查。因此 **dragon 系列仅作校验和登记，不作性质断言**；性质断言仅覆盖 spot 系列。
2. **spot `05_spot_vprolong` 的 30 个空行**：2930 行中有 30 行无任何条目，系上游实现显式跳过切线空间对应失败的顶点（`get_vertex_vector_prolongation.cpp:71`：`|correspondence| < 1e-8` 时 `continue`）。性质断言仅对该矩阵的非空行生效（2900 行）。
3. **Laplacian 非对角元可为负**：spec 初稿曾断言"非对角元≥0"，实测 `01_laplace` 非对角最小值为 −0.715、`01_dragon_laplace` 为 −0.982——简化后的内在三角化并非 Delaunay，钝角 cotan 权重为负属正常现象。该断言已按实测修正为**严格对称性**断言（见上表）。

## dragon 系列获取与用法

dragon 系列文件保留在实验数据目录（不在本仓库内）：

```
<obj_exp>\ICE_Experiment_Logs\matrices\01_dragon_{prolongation,laplace,mass}.spmat
<obj_exp>\ICE_Experiment_Logs\matrices\05_vector_{prolongation,mass}_{re,im}.spmat
<obj_exp>\ICE_Experiment_Logs\matrices\05_connection_laplace_{re,im}.spmat
```

运行金样本测试时通过环境变量提供目录：

```bash
# 无 dragon 数据：spot 全量断言通过，dragon 用例 SKIP
pytest tests/test_golden_matrices.py -v

# 有 dragon 数据：追加全量校验（sha256/bytes/dims/nnz/统计范围，不匹配即 FAIL）
# pwsh
$env:ICE_GOLDEN_DRAGON_DIR = "<obj_exp>\ICE_Experiment_Logs\matrices"; pytest tests/test_golden_matrices.py -v
```

## 版本化

`checksums.json` 带 `schema_version` 字段；条目以 `filename` 为主键、`sha256` 锚定文件内容。任何矩阵文件的改动都会被 spot 自检或 dragon 校验捕获。schema 变更遵循语义化版本（见 `docs/rfc/001-algos-registry.md` 设计点④）。
