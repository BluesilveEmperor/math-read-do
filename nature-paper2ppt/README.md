# `nature-paper2ppt` 技能

`nature-paper2ppt` 用于把科研论文转换为简洁中文 PowerPoint，用于文献汇报、组会、实验室会议或论文分享，并以 Nature 风格证据叙事组织内容。

## 功能

- 将科研论文转换为 10-16 页中文演示文稿。
- 使用论文的科学论证作为幻灯片主线，而不是照搬章节顺序。
- 先判断论文类型，再选择叙事逻辑。
- 把关键图、表或面板作为证据，而不是装饰。
- 撰写中文标题、精简 bullet、图注、takeaway 和 speaker notes。
- 生成可编辑的 `.pptx` 作为主交付物。

## 默认输出包

```text
output/
├── final_presentation_cn.pptx
├── qa_report.md
├── asset_manifest.md
└── assets/
    └── figures/
```

## 触发短语

- 论文做PPT / 论文汇报 / 组会PPT / 文献汇报
- 学术汇报 / 做幻灯片 / 讲paper / 读书报告PPT
- paper to slides / journal club

## 注意事项

- 默认语言为简体中文，保留重要技术术语英文。
- 不要编造源论文没有支持的数值、方法或图像解释。
- 密集结果图应裁剪或拆分，不能压缩进不可读的对称双栏版式。
