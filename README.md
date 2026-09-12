# Math-Read-Do-OBJ：通用 OBJ 输出实验复刻框架 + Nature 系列子技能

## 概述

**math-read-do-obj** 是一个面向"输出 .obj 文件"的计算机图形学/几何处理实验的标准化复刻框架，同时集成了多个 **nature-\*** 学术工具子技能（reader / figure / paper2ppt / framework）。

以 **QEM 网格简化** (Garland & Heckbert, SIGGRAPH 1997) 为首个内建范本，验证框架的通用性和正确性。

一句话：**输入 .obj + 算法规格 → 自动复现 → 输出简化 .obj + 双语对比报告**

## 项目结构

```
math-read-do/
├── qem_tool/                # QEM 网格简化工具链
│   ├── cli.py               # CLI 入口
│   ├── qem_core.py          # QEM 算法引擎
│   └── obj_io.py            # 通用 .obj 解析/导出
├── nature-reader/           # 学术论文阅读与提取
├── nature-figure/           # 论文配图制作 (matplotlib/seaborn → PDF/SVG)
├── nature-paper2ppt/        # 论文转演示文稿
├── nature-framework/        # 架构图/模型图渲染引擎
├── _shared/                 # 共享核心模块（伦理/术语/工作流）
├── tests/                   # 测试套件
├── scripts/                 # 验证 + 基准
├── templates/               # 报告模板
└── results/                 # 运行结果
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

### QEM 网格简化

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

### Nature 系列子技能

| 子技能 | 功能 | 入口 |
|--------|------|------|
| nature-reader | 学术论文阅读、提取、结构化 | `nature-reader/SKILL.md` |
| nature-figure | 论文配图制作（结果图/示意图/多面板） | `nature-figure/SKILL.md` |
| nature-paper2ppt | 论文转演示文稿 | `nature-paper2ppt/SKILL.md` |
| nature-framework | 架构图/模型图 JSON → 渲染 | `nature-framework/SKILL.md` |

## 依赖

| 包 | 用途 | 必要 |
|----|------|------|
| numpy | 矩阵运算 (QEM) | ✅ |
| pytest | 测试运行 | ❌ (推荐) |
| matplotlib | 可视化 | ❌ (可选) |

## Nature 子技能依赖

| 子技能 | 核心依赖 |
|--------|---------|
| nature-figure | matplotlib, seaborn |
| nature-paper2ppt | python-pptx |
| nature-reader | mineru-open-sdk |
| nature-framework | Node.js (mjs 渲染器) |

## 与 math-read-do 的关系

| 维度 | math-read-do | math-read-do-obj |
|------|-------------|-----------------|
| 领域 | 通用数学论文复现 | OBJ 输出图形学实验 + Nature 学术工具 |
| 算法获取 | PDF → MinerU → 理解 | 直接算法理解（跳过 PDF） |
| 输入 | PDF 论文链接 | .obj 文件 / 论文 / 架构 JSON |
| 验证 | 多随机种子统计 | 多模型交叉验证 |
| 核心依赖 | mineru-open-sdk | numpy |

## 许可

MIT
