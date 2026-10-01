# nature-beamer — 用 LaTeX Beamer 出汇报幻灯片

`nature-paper2ppt` 的构建层（原第 7 步的 python-pptx）替换为 **XeLaTeX + Beamer**。
产出一份可 diff 的 `.tex` 与一份 `.pdf`，排版可复现。

论文解读、叙事弧线、图表即证据、术语账本、自检环这些规则**不变**，仍由技能的
`static/` 与 `references/` 层提供。本目录只负责「把内容排成幻灯片」。

## 目录

```
beamer/
├── common/beamer-nature-common.sty   四个主题共用的引擎（版式宏、字体、中文排版）
├── themes/beamerthemenature-*.sty    四个主题，只定义配色与页面装饰
├── demo/demo.tex                     覆盖全部版式的示例稿
├── build/build.sh                    编译入口
├── build/pdf_tools.py                页数/宽高比检查 + 预览渲染
├── build/check_clearance.py          图表页「结论条 vs 页脚」净空量化复核
├── build/compare_sheet.py            四主题对比总图
└── THEMES.md                         主题选择指南
```

## 快速开始

```bash
cd beamer

bash build/build.sh slate          # 编译单主题（XeLaTeX 两遍）
bash build/build.sh all            # 四个主题全编
bash build/build.sh slate --bib    # latexmk + biber，需要 \cite 时用
bash build/build.sh path/to/deck.tex
```

产物落在 `build/`：`demo-<theme>.pdf` 与 `preview/demo-<theme>-NN.png`。
`bash build/build.sh all` 结束后还会打印一张净空复核表（见「验收流程」）。

编译后必须检查两件事，脚本已内建：

1. 日志中 `!` 开头的错误数为 0；
2. 页面宽高比为 1.778（16:9）。不是这个数说明纸张设错了。

## 在文档里使用

```latex
\documentclass[aspectratio=169,10pt]{beamer}

\makeatletter
\def\input@path{{../common/}{../themes/}}
\makeatother

\providecommand{\ntFiguresRoot}{}
\def\ntThemeName{slate}
\InputIfFileExists{ntsettings.tex}{}{}   % 由 build.sh 生成
\usetheme{nature-\ntThemeName}
```

`ntsettings.tex` 由 `build.sh` 每次编译前重写，只含两行 `\def`：

```latex
\def\ntThemeName{slate}
\def\ntFiguresRoot{/abs/path/to/beamer}
```

**不要用 `-usepretex` 传参。** XeLaTeX 在导言区之后才应用它，因此它无法覆盖文档
自己的定义——无论那里写的是 `\providecommand` 还是 `\def`。实测两者都被文档内的
定义压住，主题永远停在默认值。读文件是唯一可靠的传参方式。

## 版式宏

四个主题共用同一套 API，切换主题无需改内容。

| 宏 | 用途 |
|---|---|
| `\naturetitlepage` | 标题页 |
| `\naturesection{标题}` | 章节分隔页 |
| `\begin{frame}{标题} … \end{frame}` | 正文页 |
| `\naturefigurepage[宽度]{标题}{图路径}{来源}{takeaway}` | 图表页 |
| `\naturetwocol{标题}{左头}{左体}{右头}{右体}` | 双栏对比 |
| `\natureclosing{结语}` | 结尾页 |

辅助宏：

| 宏 | 用途 |
|---|---|
| `\nttakeaway{一句话}` | 灰底结论条 |
| `\ntsource{出处}` | 图注小字 |
| `\ntenterm{exome}` | 英文技术名词，保持正体 |
| `\note{…}` | 讲者备注（Beamer 原生） |

图表路径**相对于 `\ntFiguresRoot`**（即 `beamer/` 目录），写成 `assets/fig1.pdf`
即可。不要写 `../assets/...`。

## 踩过的坑

以下每一条都在 TeX Live 2026 / Windows 上复现过，改主题或改构建脚本前请先读。

**1. `../` 在图形路径里会被 kpathsea 拒绝。**
只要用了 `-output-directory`，XeLaTeX 就按输出目录解析相对图形路径，而含 `../`
的路径会直接失败——放进 `\graphicspath` 也一样。必须用绝对路径，因此有
`\ntFiguresRoot`。

**2. `\currfiledir` 在带输出目录时为空串。**
所以不能靠它拼绝对路径。`-output-directory` 一旦启用，XeLaTeX 就把源目录报成 `./`。

**3. 中文粗体不能写 `BoldFont={Family Bold}`。**
fontspec 会把它当成一个字体族字符串（`"HarmonyOS Sans SCBold"`）而找不到。
必须用 `Font=` / `BoldFont=` 指定**具体字体文件名**。HarmonyOS Sans SC 没有 700
字重的独立文件，正文粗体落在 Medium。

**4. `\setmathfont` 首个字体必须是数学字体。**
先 `\setmathfont{Latin Modern Math}` 打底，再用
`range={up,it,bfup,bfit}` 把西文换成 Source Sans Pro。
`bf`/`sf`/`bfsf` 是输入命令而非输出字形，unicode-math 会直接报错。

**5. xeCJK 的选项键会变。**
`PunctuationSpace`、`AllowBreakBetweenPunct` 在 TeX Live 2026 里都不存在，
且**未知键是硬错误**而不是警告。只保留 `CJKmath`、`CheckSingle` 这类稳定键；
中文断行交给 `\XeTeXlinebreaklocale "zh"`。

**6. `\colorbox` 的 `\fboxsep` 会让盒子比预算高 4.4mm。**
它四边都加 padding 且按基线对齐，结果 takeaway 条压住页脚。现在改为固定
`\fboxsep` 并把 padding 只加在水平方向，且整个参数（含 `\par`）都在 `\colorbox` 内。

**7. 不要在一个宏里套用颜色名宏。**
`\color{\ntInkBlack}` 里 `\ntInkBlack` 是 `\definecolor` 的色名，xcolor 匹配的是
宏记号而不是展开后的色名，报 `Undefined color ''`。写 `\color{ntInkBlack}`。
`\color{\ntPaletteText}` 这种**间接**宏能work，因为展开结果是纯色名。

**8. beamer 的 `block begin` / `block end` 各自必须括号平衡。**
跨模板的 `\colorbox{...}` 会在 `\end{frame}` 处报
`Extra }, or forgotten \endgroup`。用 `\hbox\bgroup … \egroup` 或成对的环境。

**9. 自定义标题页会与 beamer 内置模板叠加。**
主题自己画封面时必须 `\setbeamertemplate{title page}{}`，否则 `\inserttitle` /
`\insertauthor` 会被排两遍，叠在 overlay 下面。

**10. 页脚用 overlay 画，不要用 `footline` 模板。**
`footline` 参与文本块，会和 takeaway 条抢垂直空间造成重叠；overlay 只叠加不占位。

**11. `\inserttotalframenumber` 第一遍是 1。**
页脚会显示成「3 / 1」。总页数要自己在 `\AtEndDocument` 里写进 `.aux` 再读回，
即 `\ntframecount`。

**12. Git Bash 传 PATH 必须用 POSIX 写法。**
`/d/texlive/2026/bin/windows` 可以，`D:/texlive/2026/bin/windows` 不行——
后者 `command -v` 找不到 `xelatex`。

**13. 检查删除是否真生效，不能只看退出码。**
用 `grep -cE '^!|Unable to load'` 数日志里的错误，并核对页数与宽高比。
「编译没报错」不等于「页面没错」——面板压页脚这类问题只在渲染图上才看得见。

## 验收流程

改完主题或版式宏后：

1. `bash build/build.sh all` — 四个主题都要 `errors=0 pages=N ratio=1.778`；
2. 脚本随后自动跑 `check_clearance.py`，四个主题都必须 `OK`（净空为正）；
3. `build/preview/` 下逐页看图，重点看图表页底部是否与页脚重叠；
4. 需要全貌时 `python build/compare_sheet.py .` 生成
   `build/compare/themes-contact-sheet.png`（每行一个主题，每列一页）。

净空检测看的是「结论条下沿」到「页脚文字上沿」的距离，脚本直接报数，
比目测可靠：

```
theme     page  panel_y1  footer_y0  clearance  status
slate        4     187.1      190.3        3.2  OK
navy         4     183.3      188.0        4.7  OK
ink          4     181.7      191.6        9.9  OK
paper        4     187.2      189.4        2.1  OK
```

`clearance > 0` 才算通过；任一主题为负，脚本返回非零退出码。

需要手工单查某个页面时：

```python
import pymupdf
p = pymupdf.open("build/demo-slate.pdf")[3]
panel = max((d["rect"].y1 for d in p.get_drawings()
             if d.get("fill") and 150 < d["rect"].width < 400
             and 5 < d["rect"].height < 40), default=None)
foot = min((l["bbox"][1] for b in p.get_text("dict")["blocks"]
            if b.get("type") == 0 for l in b["lines"]
            if "单细胞转录组" in "".join(s["text"] for s in l["spans"])), default=None)
print("clearance", None if None in (panel, foot) else foot - panel)
```
