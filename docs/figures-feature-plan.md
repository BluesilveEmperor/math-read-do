# math-read-do 论文插图功能方案 v2 —— 把 paperfig 内化为自身功能

> 版本：v2（2026-09-12）｜取代 v1（v1 的问题：把 paperfig 当"第二个技能"挂上去，属**关联**而非**内化**）
> 目标：为 math-read-do **新增一项自身功能**——论文插图生成（六类：研究框架图 / 技术路线图 / 方法·模型架构图 / 系统架构图 / 论文结构图 / 实验流程图），实现载体是把 paperfig 的渲染内核吸收为内部模块。
> 状态：设计稿，未实施。

---

## 0. 定位修正（v1 → v2）

| 维度 | v1（关联两个技能）❌ | **v2（内化为自身功能）✅** |
|---|---|---|
| 用户怎么用 | 需要知道存在 `paperfig` 这个技能，再调用它 | 直接说"给我画研究框架图"，由 math-read-do 自己出图 |
| 技能数量 | 变成 2 个技能（主技能 + 第 4 个子技能） | **仍是 1 个技能**，只是多了一项功能 |
| 入口 | `paperfig/SKILL.md` 独立入口 + 主技能路由表多一行 | 只有 math-read-do 的 `SKILL.md` + 自身 CLI，功能写在**自身阶段步骤**里 |
| paperfig 的地位 | 平级伙伴，鼓励它独立演进、可单独使用 | **内部实现细节**，与 `python-pptx`、`PyMuPDF` 同级，写进依赖表 |
| 产物落点 | 独立的 `figures/` 域 | 归入既有产物体系 `实验复刻结果汇总/` |
| 触发词 | 挂在子技能描述里 | 写进 **math-read-do 自己的 description triggers** |
| 演进节奏 | 跟随上游 paperfig | 按 math-read-do 自己的节奏改，不再承诺同步上游 |

一句话：**paperfig 是"供货商"，不是"同事"。** 它的代码进仓库、它的名字退出用户视野。

---

## 1. 六类图 ↔ 引擎类型映射（内化后仍沿用该词表）

| 功能产出的图 | 引擎 type | 语义要点 |
|---|---|---|
| 研究框架图 | `framework` | 问题层→研究内容层→成果层；一映射只画真实对应，禁臆造连线 |
| 技术路线图 | `route` | 目标→方法→结论的分支路径；分支必须显式汇合或终止于具名结论 |
| 方法/模型架构图 | `model` | 层/块/张量形状/残差跳连/×N 重复块；`tensor_shape` 为语义数据不可删 |
| 系统架构图 | `system` | client/service/storage 分层；跨层边标真实协议（HTTP/gRPC/SQL） |
| 论文结构图 | `structure` | 一章一节点 + 章标题；只画真实"章节→内容"映射 |
| 实验流程图 | `experiment` | 数据→预处理→训练→评估→指标；baseline/ablation 侧向汇入 eval |

引擎内部共享一套 typed IR（`modules`/`groups`/`connections`/`cards`），六类图只是词表与排版约定不同——因此**对外呈现为"一项功能、六种图"，对内是一套引擎**。

---

## 2. 功能入口：怎么让用户"感觉不到"paperfig

### 2.1 主技能功能清单（改 `SKILL.md` 交互规则段的提问模板）

```
请选择要执行的操作：

1️⃣ 阅读论文 — 解析PDF并输出指定视角的审阅报告
2️⃣ 复现实验 — 启动完整复现流程（Phase 0→7）
3️⃣ 生成图表 — ① 数据图（曲线/对比/消融，出版级）
              ② 论文插图（研究框架图/技术路线图/方法架构图/系统架构图/论文结构图/实验流程图）
4️⃣ 制作PPT — 将论文或复现结果转为演示文稿
```

即：**图能力并入既有第 3 项功能位**，不新增菜单项——这是"新功能"而非"新技能"的直接体现。数据图与论文插图并列，因为两者产出同属"给论文配图"这一件事。

### 2.2 触发词（写进 `SKILL.md` frontmatter 的 `description`）

```
# 论文插图 triggers
研究框架图, 技术路线图, 方法架构图, 模型架构图, 系统架构图, 论文结构图, 实验流程图,
framework figure, technical route, model architecture figure, system architecture,
paper structure diagram, experiment pipeline, PRISMA 流程图, CONSORT 流程图,
开题报告插图, 学位论文插图, 组会配图, 期刊投稿插图, 画架构图, 画流程图, 画路线图
```

⚠️ 注意：**不出现 `paperfig`**。用户搜"论文插图"就该命中这个技能。

### 2.3 对外命令（唯一门面，Python）

```bash
# 列出当前论文的图清单与状态
python scripts/figures.py list

# 六类图统一渲染入口
python scripts/figures.py render <framework|route|model|system|structure|experiment> \
        --stage <draft|confirmed|final> [--motion off|hover|flow|tour] [--pdf] [--preset <p>]

# 阅读阶段一键出三张（Phase 1.5 自动调用）
python scripts/figures.py init-reading analysis/literature_reading.json

# 复现阶段：路线图初稿 / 已有初稿则补充
python scripts/figures.py route-draft analysis/literature_reading.json
python scripts/figures.py route-supplement implementation/delta_report.json

# 实验流程图定稿（唯一硬门禁）
python scripts/figures.py render experiment --stage final
```

**Node 不出现在用户视野**：`scripts/figures.py` 内部调用内嵌的 JS 渲染内核（子进程）。SKILL.md 的 compatibility 段只写一行：

```
- 论文插图: 内置渲染内核（Node >= 18），无需额外安装
```

### 2.4 出图前必问清单（新增硬约定）

**图的细节由用户定，数学流程不得默默决定任何一项。** 出图前一次性问清（只问对话中尚未确定的项），每项附推荐与理由，用户可一句"都按推荐"：

| 项目 | 选项 | 为什么必须问 |
|---|---|---|
| 图类型 | 六类之一 | 用户说法含糊时先给推荐再确认（沿用引擎的 guide 逻辑） |
| **主题（视觉预设）** | 素白（默认推荐）/ 深色 / 制图线稿 / 新粗野 / 趣味 / 新拟态 / 孟菲斯 / 玻璃 / 包豪斯 / 苹果风 | **本次新增的必问项**。投稿印刷推荐素白；表现系预设仅用户点名时使用 |
| **数据流动形式** | 静止 `off` / 悬停 `hover` / 流动 `flow` / 巡演 `tour` | 既有硬约定；只交付 PDF/EPS 时须同时说明动效不进打印产物 |
| 文字语言 | 中文 `zh-CN` / 英文 `en` | 决定"中文优先"检查是否强制；中英混排论文按正文语言选 |
| 排版规格 | 单栏（默认）/ 双栏 | 取决于目标期刊或学位论文版面 |
| 输出格式 | HTML（默认）/ PDF / EPS | 投稿要 PDF/EPS，预览用 HTML |
| 定稿阶段 | `draft` / `confirmed` / `final` | 与 §4 状态机联动；实验流程图只有真实数据齐备才可 final |

**问答协议**：① 已说过的项不重复问；② 批量出图同一轮答案覆盖全部，一批只问一次；③ 用户明确弃权的项回落到推荐默认，**并在交付说明里写明"该项未指定，按默认交付"**（不允许静默采用默认）。

对应 CLI：

```bash
python scripts/figures.py render <type> --stage <draft|confirmed|final> \
        --preset <paper|paper-dark|...> --motion <off|hover|flow|tour> \
        --lang <zh-CN|en> --column <single|double> [--pdf|--eps]
```

任一必问项缺席且用户未弃权 → `figures.py` **拒绝渲染**（`exit 2`），提示缺失项清单——把"必问"做成代码约束而非文档建议。

---

## 3. 技术形态：Python 门面 + 内嵌 Node 内核

math-read-do 现有脚本全是 Python（`literature_reader.py`、`math_pdf_extract.py`…），而 paperfig 内核是 Node。内化时的正确处理是**不重写内核、只包一层门面**：

```
math-read-do/
├── scripts/
│   ├── figures.py                 ← 新增：唯一用户门面（list/render/init-reading/route-supplement）
│   └── figuregen/                 ← 新增：功能实现（对内）
│       ├── gates.py               ← 三类定稿门禁
│       ├── state.py               ← 图状态机 draft→confirmed→final
│       ├── manifest.py            ← figures/manifest.json 读写 + schema 校验
│       ├── presets.py             ← 10 种视觉预设枚举（供 CLI 补全）
│       ├── engine/                ← 内嵌渲染内核（源自 paperfig，MIT）
│       │   ├── paperfig.mjs       ← CLI 内核（被 Python 子进程调用）
│       │   ├── render-model.mjs
│       │   ├── geometry.mjs  shapes.mjs  utils.mjs  validator.mjs
│       │   ├── schemas/           ← diagram.schema.json + common.schema.json
│       │   └── assets/            ← 字体子集 + template.html
│       ├── NOTICE.md              ← MIT 归属声明（见 §9）
│       └── templates/             ← 六类图的 spec 骨架（中英双语标签占位）
```

**为什么保留 Node 内核而不移植成 Python**：内嵌内核有 43KB 渲染器 + 11 项几何自证检查 + 字体子集嵌入逻辑，移植等于重写并重新验证 11 项检查，风险远大于收益。包一层 Python 门面既让用户只面对 math-read-do 自己的 CLI，又保留了内核的正确性。Node ≥18 作为内部依赖声明即可（`doctor` 会检测）。

---

## 4. 阶段归属：写进自身阶段体系（不是"子技能协同"）

v1 把 paperfig 挂在"子技能路由表"里；v2 把它**拆进 math-read-do 自己的阶段步骤**：

### 4.1 新增/修改的阶段步骤

| 阶段 | 步骤 | 内容 | 产出 |
|---|---|---|---|
| **Phase 1.4** 文献阅读 | 末尾**新增 1.5** | **默认产出三张图**：研究框架图(final) + 技术路线图(draft) + 论文结构图(final) | `figures/out/*.html` + manifest 三条记录 |
| **Phase 4** 增量实现 | 入口 **新增 4.0** | ① 无路线图 → 出初稿；② 已有 → 走补充模式追加结果节点 | `figures/specs/route.json` 更新 + 版本 +1 |
| **Phase 4/5** | **新增 4.4 / 5.6** | 方法·模型架构图、系统架构图（代码跑通后出，`soft_code_verified` 门禁） | 两张 HTML + 可选 PDF |
| **Phase 5.5** 统计判决后 | **新增 5.7 实验流程图定稿** | **唯一硬门禁**：必须基于真实实验数据 | `figures/out/experiment.html/pdf` |
| **Phase 7** 最终整理 | 既有 7.1 扩展 | 插图**归位**到 `实验复刻结果汇总/论文插图（含规格）/` | 与既有双语报告并列 |

### 4.2 Gate 表新增（并入既有 G0…G8）

| Gate | 位置 | 条件 | 违反动作 |
|---|---|---|---|
| **G9** | Phase 5.7 → 6 | 实验流程图 `final` 已过 `requires_experiment_data` 门禁；六张图均在 manifest 中登记且状态合法 | **拒绝进入报告阶段**（实验流程图缺失或仍为 draft 时） |
| **G10** | Phase 7 | 插图中文标签检查通过（引擎检查 11 `text-language`）；每张图有 spec 与 SHA-256 收据 | 补译/补收据 |

### 4.3 定稿门禁矩阵（对应你的硬性要求）

| 图 | 触发阶段 | 默认执行 | 门禁 | 定稿时点 |
|---|---|---|---|---|
| 研究框架图 | Phase 1.5 | ✅ 默认 | `none` | Phase 1 即 final |
| 论文结构图 | Phase 1.5 | ✅ 默认 | `none` | Phase 1 即 final |
| 技术路线图 | Phase 1.5 初稿 | ✅ 默认（初稿） | `none` | 初稿=draft；Phase 4 补结果后升版 |
| 方法/模型架构图 | Phase 3/4 | 按需 | `soft_code_verified` | 代码跑通后 final |
| 系统架构图 | Phase 4 | 按需 | `soft_code_verified` | 实现后 final |
| **实验流程图** | **Phase 5.7** | 按需（最晚） | **`requires_experiment_data`（硬）** | **只在真实实验数据齐备后** |

**你的三条硬性要求逐条对账**：
1. 阅读阶段默认三张 → Phase 1.5（framework final + route draft + structure final）
2. 复现先出路线初稿、有则补充 → Phase 4.0（`--supplement` 追加模式，禁改拓扑）
3. 只有实验流程图须实验后定稿 → Phase 5.7 + G9 硬门禁

---

## 5. 图状态机

| 状态 | 含义 | 数字约束 | 标题处理 |
|---|---|---|---|
| `draft` | 计划/预期产物 | 只允许预计值 + 占位标注 | 自动加"（初稿）"/"（预计流程）" |
| `confirmed` | 结构已定，数值未跑通 | 结构性事实确定 | 无标注 |
| `final` | 已过门禁，可入稿 | 必须全部真实值 | 无标注 |

状态**只升不降**；spec 一经修改，`state.py` 自动降回 `draft` 并要求重跑门禁（防"改了图沿用旧 final"）。

`figures/manifest.json`（Phase 7 归位时一并移入 `实验复刻结果汇总/论文插图（含规格）/`）：

```json
{
  "schema_version": "1.0",
  "paper": "论文标题",
  "engine": { "internal": "figuregen", "version": "0.1.0", "upstream_commit": "<paperfig commit SHA>" },
  "global_motion": "flow",
  "figures": [
    { "id": "fig-framework", "type": "framework", "stage": "final", "gate": "none",
      "spec": "figures/specs/framework.json", "output_html": "figures/out/framework.html",
      "output_pdf": "figures/out/framework.pdf", "quality": "showcase",
      "checks": { "passed": 11, "total": 11, "errors": 0, "warnings": 0 },
      "sha256": { "spec": "…", "html": "…" }, "updated": "2026-09-12T14:40:00+08:00" },
    { "id": "fig-experiment", "type": "experiment", "stage": "draft",
      "gate": "requires_experiment_data", "data_source": null,
      "blocked_reason": "缺少 figures/data/experiment_counts.json：最终版实验流程图必须基于真实实验数据",
      "label_suffix": "（预计流程）" }
  ]
}
```

---

## 6. 定稿门禁的实现（含实验流程图硬门禁）

`scripts/figures.py render` 是**唯一**允许触碰渲染内核的入口，各阶段不得绕过（保证门禁不可规避）。

```python
# scripts/figuregen/gates.py（节选）
EXPERIMENT_REQUIRED_FIELDS = [
    "initial_n",     # 初始样本/数据量
    "excluded",      # [{"n": int, "reason": str}]  排除数量与原因（PRISMA 要求逐条具名）
    "included_n",    # 最终纳入
    "groups",        # [{"name": str, "n": int, "allocation": str}]  分组与每组 n
    "attrition",     # [{"n": int, "reason": str, "type": "lost|withdrawn|excluded"}]  失访/退出/剔除
    "analyzed_n",    # 进入分析的人数
    "metrics",       # 评价指标
]

def gate_experiment(stage):
    if stage != "final":
        return Ok(label_suffix="（预计流程）")      # 计划阶段允许预计版

    data = FIG / "data" / "experiment_counts.json"
    if not data.exists():
        fail("最终版实验流程图必须基于真实实验数据：缺少 figures/data/experiment_counts.json。"
             "计划阶段请改用 --stage draft 输出预计流程图。")

    counts = json.loads(data.read_text(encoding="utf-8"))
    missing = [f for f in EXPERIMENT_REQUIRED_FIELDS if not counts.get(f)]
    if missing:
        fail(f"实验数据不完整，缺少字段：{missing}。这些数字不能靠推测编造，"
             "请等实验跑完、数据整理完再定稿。")

    if not counts.get("raw_metrics_sha256"):
        fail("未记录 results/raw_metrics.csv 哈希：无法证明数字来自真实实验产物。")

    if sum(g["n"] for g in counts["groups"]) > counts["included_n"]:
        fail("分组人数合计超过纳入人数，数据自相矛盾。")

    if counts.get("flow_diagram_kind") in ("PRISMA", "CONSORT"):
        if any(not e.get("reason") for e in counts["excluded"]):
            fail(f"{counts['flow_diagram_kind']} 流程图要求每条排除都必须写明原因与篇数。")

    return Ok(stage="final")
```

**为什么只有它必须等实验后**：这张图里的每个数字和分支（初始样本、排除原因与数量、纳入数、分组、每组人数、失访/退出/剔除、进入分析数、评价指标）是**实验的事实记录**，不是设计意图。事实只能事后填；其余五张图的主体是**设计**，设计阶段即成立——model/route 只是"结果数值"待回填，属细节补充，不是结构重画。

---

## 7. 补充模式（技术路线图）

Phase 4.0 若已存在路线图，进入 `--supplement`：

```
旧 spec 节点 ID 集合 ⊇ 新 spec 节点 ID 集合      # 不得删除
旧主路径连接对 ⊆ 新连接对                        # 主路径不得改向
新增节点必须挂在既有节点下游 或 作为结果叶节点    # 不得插入主路径中段
新增边必须携带非空 label                         # 结果标注要写清是什么结果
```

任一违反 → 拒绝写入，提示"补充模式只允许追加，需重画请显式 `--force-rewrite`"。这样初稿与终稿始终可对照（计划 vs 执行），正是"先出初稿、复现后补充"的价值所在。

---

## 8. 产物归位（沿用 math-read-do 既有输出约定）

Phase 7 整理时，插图并入既有中文目录体系：

```
实验复刻结果汇总/
├── 实验报告/                     # 既有：双语报告 + 判决 JSON
├── 实验图表（含代码）/            # 既有：数据图 PNG/PDF + plot_*.py
├── 实验结果对比表/                # 既有：双语对比表
└── 论文插图（含规格）/             + 新增
    ├── 研究框架图.html / .pdf
    ├── 技术路线图.html / .pdf
    ├── 方法架构图.html / .pdf
    ├── 系统架构图.html / .pdf
    ├── 论文结构图.html / .pdf
    ├── 实验流程图.html / .pdf
    ├── spec/                     # 六类图的源规格（可重跑）
    │   └── *.json
    ├── data/experiment_counts.json  # 实验流程图数字的唯一事实来源
    └── manifest.json             # 状态机 + 收据
```

工作期（Phase 1~6）图先落在 `figures/`，Phase 7 归位——与既有"各阶段产物先落工作目录、Phase 7 统一归位"的约定一致。

---

## 9. 许可与归属（MIT 合规，但不进用户视野）

内嵌内核源自 paperfig（MIT）。必须保留归属，但**放对位置**：

- ✅ `scripts/figuregen/NOTICE.md`：写明"Sections of scripts/figuregen/engine derive from paperfig (MIT License, © paperfig)"+ 许可证全文与上游 commit
- ✅ `figures/manifest.json` 的 `engine.upstream_commit` 记录内嵌时点
- ❌ 不在 `SKILL.md` 描述、路由表或提问模板里出现 `paperfig` 字样；用户只看到"论文插图"功能

---

## 10. 文件改动清单

| # | 文件 | 动作 | 内容 |
|---|---|---|---|
| 1 | `scripts/figures.py` | 新增 | 唯一用户门面：`list` / `render` / `init-reading` / `route-draft` / `route-supplement`；**实现 §2.4 出图前必问清单的强制校验**（缺项且用户未弃权 → exit 2 并列出缺失项） |
| 2 | `scripts/figuregen/` | 新增 | `gates.py` / `state.py` / `manifest.py` / `presets.py` + `engine/`（内嵌内核）+ `templates/`（六类 spec 骨架）+ `NOTICE.md` |
| 3 | `figures/manifest.json` | 运行期生成 | 状态机注册表（工作期位置） |
| 4 | `schemas/figure_manifest.schema.json` | 新增 | 校验 manifest（stage/gate/checks/sha256） |
| 5 | `SKILL.md` | 改 | ① frontmatter description 加插图触发词；② 提问模板第 3 项扩为"数据图 / 论文插图"；③ Phase 1 加 1.5 默认三张；④ Phase 4 加 4.0 初稿/补充 + 4.4；⑤ Phase 5 加 5.6、5.7；⑥ Phase 7 加插图归位；⑦ **Gate 表加 G9/G10**；⑧ 反模式表加 4 条（§11）；⑨ 文件结构树加 figuregen 与 论文插图（含规格）/；⑩ compatibility 加"内置渲染内核（Node ≥ 18）"；⑪ **写入 §2.4 出图前必问清单**（主题/动效/语言/栏宽/格式/阶段） |
| 6 | `scripts/literature_reader.py` | 改 | 报告生成完毕后调用 `figures.py init-reading`（可用 `--no-figures` 关闭） |
| 7 | `README.md` / `VERSION` | 改 | 功能清单加"论文插图（六类）"；版本 +0.1 |
| 8 | `tests/test_figures.py` | 新增 | 门禁/状态机/补充模式单测（§12） |
| 9 | `test-prompts.json` | 改 | 加 4 个验收场景 |
| 10 | ~~`skills/registry.yaml`~~ | **不改** | v2 的图能力是主流程阶段步骤，不是独立 skill，**无需注册子技能** ← 这正是内化的关键差异 |

---

## 11. 反模式新增（并入既有 13 条）

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 14 | 实验复现没跑完就画"最终版"实验流程图，数字靠推测 | 造假风险；PRISMA/CONSORT 数字自相矛盾；投稿被撤 | 计划阶段只出 `--stage draft`；final 必过 `requires_experiment_data` |
| 15 | 手工修改交付 HTML 冒充校验通过 | 收据 SHA-256 对不上，溯源断裂 | 只改 spec 重跑；HTML 视为只读产物 |
| 16 | 路线图补充时重排/删除既有节点 | 初稿与终稿不可比，失去计划-执行对照 | 走 `--supplement` 追加；结构 diff 拒绝删除 |
| 17 | **出图前不问主题/动效等细节，直接套默认出图** | 用户拿到不合投稿要求的风格，返工；"动效没进 PDF"之类的预期落空 | 按 §2.4 清单**一次问全**；用户弃权才回落默认，且须在交付说明中写明 |

---

## 12. 验收用例

| ID | 场景 | 期望 |
|---|---|---|
| T7 | 只给 PDF，走 Phase 1 | `figures/out/` 出现 framework(final)、route(draft，标题带"（初稿）")、structure(final)；三张 showcase 11 项全过；manifest 三条记录 |
| T8 | 复现完成（有 raw_metrics.csv） | experiment 可 final 且登记 `data_source`；**随后删掉 `experiment_counts.json` 重跑 → 必须 exit 1** |
| T9 | 二次运行（route 已存在） | 走补充模式；追加结果节点被接受；删旧节点被拒并提示 `--force-rewrite` |
| T10 | 中文图 | 检查 11 `text-language` 通过，无裸英文描述词 |
| T11 | 代码跑通前给 model 图 final | 被 `soft_code_verified` 拦下，停在 confirmed 并要求确认 |
| T12 | 未指定动效模式 | 必须发起提问（静止/悬停/流动/巡演），不得静默产出 |
| T14 | 未指定主题（预设） | 必须一并提问；用户答"随便/默认" → 用素白并在交付说明写明"主题未指定，按素白交付" |
| T15 | 缺任一必问项且用户未弃权 | `figures.py` 拒绝渲染并列出缺失项（exit 2），不得先出图再补问 |
| T13 | Phase 7 | 六图 + spec + data + manifest 齐备归位于 `论文插图（含规格）/`；G9/G10 通过 |

---

## 13. 实施顺序与风险

| 轮次 | 内容 | 完成标志 |
|---|---|---|
| **M1 内化** | 复制内核进 `scripts/figuregen/engine/` + NOTICE；写 `figures.py` 门面（先通 `list`/`render` 六类型）；六类 spec 骨架 | 六张图都能出 showcase HTML，且命令里不出现 paperfig |
| **M2 门禁** | `state.py` + `gates.py` + manifest schema + 补充模式 + 单测 | T8/T9/T11/T12 通过 |
| **M3 接线** | SKILL.md 触发词/提问模板/阶段步骤/Gate G9-G10/反模式/文件树 + `literature_reader.py` 收尾调用 + Phase 7 归位 + 全流程演练 | T7~T13 全过；用一篇真实论文跑通 Phase 1→7 |

**风险与对策**

| 风险 | 对策 |
|---|---|
| 内嵌内核与上游 paperfig 分叉 | 接受分叉：内化后按 math-read-do 需要改，`engine.upstream_commit` 仅作溯源；不承诺同步 |
| paperfig 的 `--motion` 仍在未提交工作树 | 复制前先让 paperfig 侧提交，锁定一个干净 commit 作为内嵌基线 |
| 8MB 全量字体撑大仓库 | 只带子集（约 500KB）；全量 ttf 进 `.gitignore` |
| Node 依赖用户未装 | `figures.py` 启动即探测 Node ≥18，缺失时给出明确安装指引（并入既有 Phase 0 宿主检测的可选项） |
| PRISMA/CONSORT 数字来源 | `figures/data/experiment_counts.json` 为唯一事实来源，人工录入或从数据清洗日志解析，禁从图反推 |
| 分支策略 | 建议另开 `feature/figures` 分支实施，不污染 main 与本轮 worktree |

---

## 14. 待你决策

1. **内核形态**：保留 Node 内核 + Python 门面（推荐，风险最低）；还是要求完整移植为纯 Python（工作量大、需重验 11 项检查）？
2. **是否开工**：按 M1 → M2 → M3 顺序，每轮给你可验证产物；另开 `feature/figures` 分支实施。
