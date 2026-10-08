# Phase 6 报告目录结构（从 SKILL.md 外移）

> 本文件由 SKILL.md 外移的低频道内容，完整保留原信息。首响无需加载，按需查阅。

```
实验复刻结果汇总/                     # 根目录
│
├── <子实验1名称>/                   # 按参数/模型/配置拆分的小实验
│   ├── OBJ模型/
│   │   └── *.obj                    # 该子实验输出的 .obj 模型文件
│   ├── 实验报告/
│   │   ├── 复现报告.md              # 英文
│   │   ├── 复现报告-CN.md           # 中文
│   │   ├── 诊断分析.md              # 英文
│   │   ├── 诊断分析-CN.md           # 中文
│   │   └── 判决结果.json            # 双语 JSON
│   ├── 实验结果对比表/
│   │   ├── 实验结果对比表.md        # 英文
│   │   └── 实验结果对比表-CN.md     # 中文
│   └── 实验图表（含代码）/
│       ├── comparison.png
│       ├── error_distribution.png
│       └── code/
│           ├── plot_comparison.py
│           ├── plot_comparison.tex          # LaTeX/TikZ 版本
│           ├── plot_error_distribution.py
│           └── plot_error_distribution.tex  # LaTeX/TikZ 版本
│
├── <子实验2名称>/                   # 第二个子实验，结构同上
│   └── ...
│
└── 总览/                            # 跨子实验的汇总
    ├── 汇总报告.md                  # 英文总体报告
    ├── 汇总报告-CN.md               # 中文总体报告
    ├── 对比总表.md                  # 所有子实验指标一览
    └── 总判决结果.json              # 总体判决
```

**子实验命名规范**: `<模型名>_<参数标记>`，如 `bunny_50pct`、`sphere_200faces`、`用户输入_ratio0.1`