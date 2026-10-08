<!-- 本文件从 SKILL.md 外移的低频道详细内容，主文档保留摘要 + 链接指向此处。 -->
### 1.5 辅助架构图征询（可选但必须询问） / Auxiliary Architecture Diagram Offer

**触发条件**: 论文理解阶段完成后、G01 门禁判决后，无论 proceed / caution / discourage 均须征询。用户未主动要求时也必须主动提出。

**步骤 1 — 主动征询**:

> 基于这篇论文的内容，我可以帮您制作 Nature 级别的研究框架图或技术路线图，方便组会汇报或开题使用。这些图不需要等实验跑完。您想现在制作吗？

- 用户拒绝 → 记录到 `review_manifest.json`（`diagram_offer: "declined"`），跳到 G01 后的流程
- 用户同意 → 进入步骤 2

**步骤 2 — 强制 6 项逐项询问**（不可合并、不可默认、不可跳过，直接复用 nature-archify 第 0 步）:

| # | 询问项 | 候选项 | 说明 |
|---|--------|--------|------|
| 1 | **主题 / Subject** | — | 论文核心研究问题与方法路径 |
| 2 | **图类型** | `architecture` / `workflow` / `sequence` / `dataflow` / `lifecycle` | 根据论文特征推荐 1-2 种 |
| 3 | **图语言** | `zh-CN` / `en` | 中文论文必须 zh-CN |
| 4 | **动画模式** | `trace` / `none` | 默认 none（静态）；交互式展示用 trace |
| 5 | **视觉预设** | `classic` / 其他 12 种 | 默认 classic；共 13 种，含 paper / brutalism / apple 等 |
| 6 | **输出格式** | `HTML` / `HTML + PNG` / `HTML + SVG` | 产物为自包含 HTML，导出在 Viewer 内完成 |

- 用户已声明过的项可复用，不重复问
- 多张图可共享一轮回答
- 若用户要求推荐，按论文领域给出 1-2 种建议并说明理由

**步骤 3 — 执行**:

按 nature-archify SKILL.md 第 0 步→第 5 步执行：选类型→读 schema/examples→写 candidate JSON→validate→deliver。

**图类型可用矩阵**（依据 nature-archify 硬规则）:

| 图类型 | 用途 | 需要实验数据 | 当前阶段可产出 |
|--------|------|:---:|------|
| `architecture` | 系统架构、部署拓扑、云与安全边界 | ❌ | ✅ 终版 |
| `workflow` | 技术流程：节点与连线表达的步骤 | ❌ | ✅ 终版 |
| `sequence` | 调用时序：参与者之间的消息往返 | ❌ | ✅ 终版 |
| `dataflow` | 数据管道与血缘：提取→转换→落库 | ❌ | ✅ 终版 |
| `lifecycle` | 状态机：状态、迁移与触发条件 | ❌ | ✅ 终版 |

**约束**:
- 五类图都只描述结构与流程，不承载实验数值，Phase 1-6 均可交付终版
- 论文的**方法/模型架构图**与**实验流程图**不在 nature-archify 图类型内（PRISMA/CONSORT 等必须写入真实样本量与排除数），需要时另行接入 paperfig 类渲染器
- 输出到 `figures/` 目录；每张图产出 `.html`（PNG/SVG 在 Viewer 内导出）
- 用户偏好（语言/预设/格式）写入 `review_manifest.json`，Phase 4/5/6 复用，不重复询问
