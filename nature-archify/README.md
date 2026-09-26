# `nature-archify` 技能

`nature-archify` 把系统架构、技术流程、调用时序、数据流和状态机画成可交互 HTML。输入是一份小型 typed JSON 规格，输出是自包含的单文件 HTML（内联 SVG、内嵌中文字体、深/浅双主题）。

## 功能

- **5 类图共享一套 JSON-IR**：`architecture` / `workflow` / `sequence` / `dataflow` / `lifecycle`
- **13 种视觉预设，几何与材质解耦**：切换预设只换外观，不动布局
  - 技术系：`classic`（默认）/ `signal-flow` / `blueprint` / `editorial`
  - 表现系：`paper` / `paper-dark` / `brutalism` / `playful` / `neumorphism` / `memphis` / `glass` / `bauhaus` / `apple`
- **深 / 浅双主题**；可选 `trace` 动效（默认静态，打印与 `prefers-reduced-motion` 恒为静态）
- **9 项 showcase 校验**：单 SVG、有限坐标、正交箭头、标签避让、关系交叉、关系走廊、容器边框、路由节奏、图例间距
- **产物自包含**：内嵌 HarmonyOS Sans Medium 子集字体，离线可开、可打印；PNG / SVG / WebM 导出在 Viewer 内完成
- **确定性交付**：`deliver` 输出规格与产物的 SHA-256 回执，`visual-check` 提供独立于它的浏览器实测证据
- **接受 Mermaid 作为素材**：读 `flowchart` / `sequenceDiagram` / `stateDiagram` 的拓扑与语义，再写成 Archify JSON —— 不照搬 Mermaid 的样式
- **架构对比与版本迁移**：`compare` 出两份架构规格的 delta，`migrate` 把 workflow 旧规格升到 v2

## 命令

```bash
# 上手
node bin/archify.mjs doctor                 # 15 项环境与资源自检
node bin/archify.mjs examples               # 列出 examples/ 下已渲染的示例产物
node bin/archify.mjs guide "<场景或问题>"    # 按场景给创作建议（--lang en|zh）
node bin/archify.mjs demo [out-dir]         # 生成一套演示产物

# 出图：核心三步
node bin/archify.mjs validate <type> spec.json --quality showcase --json
node bin/archify.mjs deliver  <type> spec.json out.html --quality showcase --json
node bin/archify.mjs visual-check out.html --json

# 其它
node bin/archify.mjs render  <type> spec.json out.html      # 不走质量门禁，直接渲染
node bin/archify.mjs preview <type> spec.json               # 热重载预览（只绑 127.0.0.1）
node bin/archify.mjs inspect <type> spec.json               # 解析并打印规格结构
node bin/archify.mjs check   out.html                       # 检查已生成的产物
node bin/archify.mjs compare architecture base.json head.json delta.html --receipt r.json
node bin/archify.mjs migrate workflow old.json new.json --to-schema 2
node bin/archify.mjs brands [名称或类别]                     # 品牌徽标目录
node bin/archify.mjs brands capture <url>                   # 抓取品牌徽标
```

`<type>` ∈ `architecture` / `workflow` / `sequence` / `dataflow` / `lifecycle`。
需要 Node.js ≥ 18，运行时零外部依赖。`examples/` 下有 14 份现成规格可作起点。

**四个出图命令的差别**：`render` 不检查；`validate` 只检查、不写产物；`deliver` 校验通过才原子提交并给回执；`visual-check` 是独立的浏览器证据，**不能替代** `deliver` 的确定性检查。

## Python 调用

```python
import sys
sys.path.insert(0, "scripts")           # 宿主仓库根下的 scripts/
from nature_archify_bridge import NatureArchitecture

cli = NatureArchitecture()               # 自动定位本模块根
cli.doctor()
cli.validate("architecture", "spec.json", quality="showcase")
cli.deliver("architecture", "spec.json", "out.html", quality="showcase")
cli.visual_check("out.html")
```

相对路径按调用方 cwd 解析（CLI 自身以模块根为 cwd）。

## 触发短语

- 画架构图 / 系统架构图 / 部署拓扑图 / 云与安全边界图
- 画流程图 / 技术路线 / 调用时序图 / 时序图
- 数据流图 / 数据管道 / 数据血缘 / 状态机图 / 生命周期图
- 把 Mermaid 转成好看的图 / 美化 mermaid
- 架构对比 / 架构 delta / 新旧架构同屏
- architecture diagram / sequence diagram / dataflow / state machine

## 能力边界

本模块**不含** `model` / `framework` / `route` / `structure` / `experiment` 五类图：

- 论文的**方法 / 模型架构图**不在其内；
- **实验流程图**（PRISMA / CONSORT 等）也不在其内 —— 这类图必须写入真实初始样本量、排除数与原因、分组人数、失访 / 剔除、最终分析人数，不能靠想象编。

需要这两类图时，另行接入 paperfig 类渲染器。

## 注意事项

- 未显式要求视觉风格时保持默认 `classic`（或按图类型选 `architecture` / `workflow` 等对口的默认）；预设切换绝不改变几何。
- 交付前先把 `validate` 跑到 9 项全过、0 error / 0 warning；`deliver` 非零退出不得描述为成功。
- 不要用 `overflow: hidden`、内部滚动条、拉伸 SVG 或缩小字号来「骗过」版面检查。
- 需要模型图 / 实验流程图时不要用本模块硬凑，如实说明能力边界。

详见 [`SKILL.md`](SKILL.md) 与 [`references/`](references/)。
