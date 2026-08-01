# Math-Read-Do-OBJ：通用 OBJ 输出实验复刻框架

## 概述

**math-read-do-obj** 是一个面向"输出 .obj 文件"的计算机图形学/几何处理实验的标准化复刻框架。以 **QEM 网格简化** (Garland & Heckbert, SIGGRAPH 1997) 为首个内建范本，验证框架的通用性和正确性。

一句话：**输入 .obj + 算法规格 → 自动复现 → 输出简化 .obj + 双语对比报告**

## 框架架构

```
框架层 (Framework)            范本层 (Exemplar: QEM)
  obj_io.py  (通用 .obj I/O)    qem_core.py (QEM 引擎)
  templates/ (报告模板)          cli.py     (QEM CLI)
  scripts/  (验证 + 基准)       tests/     (QEM 测试)
  
适配新算法只需替换 3 个范本文件，框架层不变。
```

## 内建算法：QEM 网格简化

Quadric Error Metric (QEM) — 经典边收缩网格简化算法。

**对比原始 C++ 实现的优化项**：

| 优化项 | 原始 C++ | 本实现 |
|--------|---------|--------|
| 最优位置 | 中点 (v1+v2)/2 | 解 4×4 线性系统 (论文 Eq.5) |
| 堆管理 | 全重建 O(n log n)/步 | 增量 heapq O(log n)/步 |
| 面删除 | O(n²) 遍历 + 迭代器失效 | 标记-清理 O(1) |
| 法线导出 | ❌ 无 | ✅ 加权平均重建 |
| 边界保护 | ❌ 无 | ✅ 约束优化 |
| 编译依赖 | OpenGL + GLFW + SDL2 | 纯 Python + NumPy |
| 参数化 | 硬编码宏 | CLI 参数 (`--faces`/`--ratio`) |

## 快速开始

```bash
# 查看模型信息
python -m qem_tool.cli -i model.obj --info

# 简化到指定面数
python -m qem_tool.cli -i model.obj -o simplified.obj -f 2000

# 按比例简化
python -m qem_tool.cli -i model.obj -o simplified.obj -r 0.1

# 运行全部测试
python -m pytest tests/ -v

# 验证简化质量
python scripts/verify_qem.py -i model.obj -f 2000 --check-hausdorff

# 性能基准测试
python scripts/benchmark_qem.py -i model.obj
```

## 项目结构

```
math-read-do-obj/
├── SKILL.md              # 工作流定义
├── README.md             # 本文件
├── qem_tool/             # 工具链（算法引擎可替换）
│   ├── cli.py            # CLI 入口
│   ├── qem_core.py       # QEM 算法引擎（替换以适配新算法）
│   └── obj_io.py         # 通用 .obj 解析/导出
├── tests/                # 测试套件
├── scripts/              # 验证 + 基准
├── templates/            # 报告模板
└── results/              # 运行结果
```

## 依赖

| 包 | 用途 | 必要 |
|----|------|------|
| numpy | 矩阵运算 (QEM) | ✅ |
| pytest | 测试运行 | ❌ (推荐) |
| matplotlib | 可视化 | ❌ (可选) |

## 与 math-read-do 的关系

| 维度 | math-read-do | math-read-do-obj |
|------|-------------|-----------------|
| 领域 | 通用数学论文复现 | OBJ 输出图形学实验 |
| 算法获取 | PDF → MinerU → 理解 | 直接算法理解（跳过 PDF） |
| 输入 | PDF 论文链接 | .obj 文件 |
| 验证 | 多随机种子统计 | 多模型交叉验证 |
| 核心依赖 | mineru-open-sdk | numpy |

## 许可

MIT
