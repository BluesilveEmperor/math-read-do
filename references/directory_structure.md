# 文件结构 / Directory Structure（从 SKILL.md 外移）

> 本文件由 SKILL.md 外移的低频道内容，完整保留原信息。首响无需加载，按需查阅。

```
math-read-do-obj/
├── SKILL.md                        # 本文件 — Skill 入口
├── README.md                       # 快速开始
│
├── qem_tool/                       # 算法工具链（可整体替换适配新算法）
│   ├── __init__.py
│   ├── cli.py                      # [范本] QEM CLI 入口（替换以适配新算法）
│   ├── qem_core.py                 # [范本] QEM 算法引擎（替换为核心算法）
│   └── obj_io.py                   # [框架] 通用 .obj 解析/导出层（可复用）
│
├── tests/                          # 测试套件（适配新算法时替换）
│   ├── __init__.py
│   ├── test_obj_io.py              # [框架] OBJ I/O 通用测试
│   ├── test_qem_core.py            # [范本] QEM 专用测试
│   └── fixtures/                   # 内嵌测试模型
│
├── scripts/                        # 辅助脚本（通用，无需替换）
│   ├── auto_update.sh              # [框架] 自动更新脚本 — 检测双源、选最快镜像拉取
│   ├── verify_qem.py               # 验证脚本（通用 .obj 验证逻辑）
│   └── benchmark_qem.py            # 性能基准（通用框架）
│
├── templates/                      # 报告模板（通用，无需替换）
│   ├── reproduction_report.template.md
│   ├── comparison_table.template.md
│   └── diagnosis.template.md
│
├── results/                        # 运行结果
├── analysis/                       # 算法分析产物
├── implementation/                 # 增量实现日志
├── memory/                         # 持久化记忆
├── infra/                          # 基础设施 manifest
└── env/                            # 环境锁定文件
```