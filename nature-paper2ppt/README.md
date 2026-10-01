# `nature-paper2ppt` 技能

`nature-paper2ppt` 用于把科研论文转换为简洁中文汇报幻灯片，用于文献汇报、组会、实验室会议或论文分享，并以 Nature 风格证据叙事组织内容。

出片层是 **XeLaTeX + Beamer**（不是 python-pptx）：产出一份可 diff 的 `.tex` 源与它编译出的 `.pdf`。

## 功能

- 将科研论文转换为 10-16 页中文演示文稿。
- 使用论文的科学论证作为幻灯片主线，而不是照搬章节顺序。
- 先判断论文类型，再选择叙事逻辑。
- 把关键图、表或面板作为证据，而不是装饰。
- 撰写中文标题、精简 bullet、图注、takeaway 和 speaker notes。
- 生成**可复现、可 diff** 的 Beamer 源码与 PDF 作为主交付物（排版由 LaTeX 保证，不靠手工调框）。

## 主交付物

```text
output/
├── slides/
│   ├── slides.tex              # Beamer 源码，排版可复现（主可编辑交付物）
│   ├── slides.pdf              # 编译产物，主交付物
│   └── ntsettings.tex          # 由 build.sh 生成的构建参数
├── qa_report.md                # 页数、插图数、自检缺陷清单
├── asset_manifest.md           # 图源可追溯
└── assets/figures/             # 抽取或裁剪出的图源
```

`.tex` 与 `.pdf` 一起交付：前者可版本管理、可评审，后者可直接放映。
需要可编辑的 `.pptx` 时，由 PDF 另行转换，不作为本技能的默认产物。

## 主题

四个内置主题，共用同一套版式宏，切换主题无需改内容：

| 主题 | 定位 |
|---|---|
| `slate` | 灰蓝单色，通用学术（默认） |
| `navy` | 深蓝 + 暖橙，正式汇报 / 长报告 |
| `ink` | 近黑无彩，大标题，图优先 |
| `paper` | 暖白纸底，衬线标题，打印友好 |

选择指南见 `beamer/THEMES.md`。

## 触发短语

- 论文做PPT / 论文汇报 / 组会PPT / 文献汇报
- 学术汇报 / 做幻灯片 / 讲paper / 读书报告PPT
- paper to slides / journal club

## 注意事项

- 默认语言为简体中文，保留重要技术术语英文。
- 不要编造源论文没有支持的数值、方法或图像解释。
- 密集结果图应裁剪或拆分，不能压缩进不可读的对称双栏版式。
- 编译不等于版面对，交付前必须跑 `build/build.sh all` 的净空复核并逐页看图（见 `beamer/README.md`「验收流程」）。
