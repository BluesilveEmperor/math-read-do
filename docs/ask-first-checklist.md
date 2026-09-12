# 需要询问 vs 不需要询问 · 完整清单

> 适用：math-read-do 主流程 + 数据图（nature-figure）+ 论文插图（原 paperfig，内化中）
> 依据：`SKILL.md`、`skills/registry.yaml`、`nature-figure/SKILL.md`、`paperfig/SKILL.md`、`scripts/literature_reader.py` 实读
> 版本：2026-09-12 v1

---

## 第 1 部分 · 必须询问（不问就不许动手）

### 1.1 入口层（4 条）

| # | 触发场景 | 要问什么 | 依据 |
|---|---|---|---|
| A1 | 技能被唤起但用户未给任何具体指令 | 列出 4 个操作选项等选择：①阅读论文 ②复现实验 ③生成图表 ④制作PPT | `SKILL.md:46,48,67` |
| A2 | 生成文献阅读报告且未指定模板 | 列出 **9 种排版模板**等用户选编号（markleaf/print/retro-print/sans/serif/magazine/minimal/notebook/print-double） | `SKILL.md:170-197`、`literature_reader.py:672` |
| A3 | 需要指定审阅视角 | 研究生 / 导师 / 审稿人 / 三方全出 —— **已裁定：必须询问，不设默认值**（脚本 `--perspective` 缺省即进入交互询问；非交互环境未给该参数直接报错退出） | `SKILL.md:58,170,176,459`、`literature_reader.py` |
| A4 | 画数据图且目标期刊不明 | 问一句目标期刊（毕业论文 / 中文核心 / 英文 SCI / NeurIPS 规范各不同） | `nature-figure/SKILL.md:92` |
| A5 | MinerU token 未配置 | 必须停下来引导用户获取并配置 `~/.mineru/config.yaml`，不得硬跑 | 反模式 1 |

### 1.2 风险分级审批（18 个动作）

总则：低=只读分析（无需审批）／中=运行前**计划审批**／高=**逐条审批**（`SKILL.md:442`）。

| 技能 | 需审批动作 | 实现状态 |
|---|---|---|
| infrastructure_orchestration | `vm_provisioning`、`docker_build`、`wsl_setup` | ✅ 有目录 |
| version_management | `install_language_runtime`、`change_compiler_version`、`install_cuda` | ✅ 有目录 |
| paper_parsing | `llm_api_call` | ⚠️ 无目录 |
| environment_setup | `dependency_change`、`system_package_install` | ⚠️ 无目录 |
| baseline_verification | `modify_source_code`、`run_experiment` | ⚠️ 无目录 |
| incremental_implementation | `write_code`、`modify_source`、`add_dependency` | ⚠️ 无目录 |
| experiment_execution | `run_multi_seed`、`extend_budget` | ⚠️ 无目录 |
| statistical_verification | 无 | — |
| bilingual_report | 无 | — |
| artifact_packaging | `publish_artifact`、`sign_attestation` | ⚠️ 无目录 |

⚠️ 更关键的是：`skills/registry.yaml` **没有任何代码读取**——它只是声明性文档，因此**这 18 条审批约束目前全部不在运行时生效**。详见 4.2。

### 1.3 阶段确认点（6 条）

| # | 阶段 | 确认内容 |
|---|---|---|
| C1 | Phase 1 → G01 门禁 | `reproducibility_assessment` 为 `needs_confirmation` / `needs_human_approval` / `discourage` → **STOP 获取用户确认** |
| C2 | Phase 3 → G4 | 基线未建立时，**由用户决定**是否继续进 Phase 4 |
| C3 | Phase 4.2 增量循环 | 每模块 delta 在容忍度内后，**确认才 `git commit`**，然进下一模块 |
| C4 | Phase 5.1 | 多轮运行前确认参数：基线可行？N=5 种子？运行时间？GPU 启用？ |
| C5 | Phase 6 | 确认所有数据就绪才生成双语报告（判决/图表/审阅/路径一致） |
| C6 | Phase 7 | 文件就位完整性确认（所有文件就位／双语配对／图表代码齐全） |

### 1.4 数据图（nature-figure，3 条）

| # | 场景 | 要问什么 |
|---|---|---|
| D1 | 用户丢来数据说"画成论文图" | **第 0 步先问"你这份数据主要想说服读者相信什么"**（组间差异？时间趋势？变量关系？） |
| D2 | 剖析完数据、给出图型推荐后 | **拿到用户确认才进入绘制**（推荐 + 理由 + 1-2 备选） |
| D3 | 用户坚持不推荐的画法 | 询问是否仍坚持，并**留下劝阻记录** |

### 1.5 论文插图（七项必问，一次问全）

| # | 项目 | 选项 |
|---|---|---|
| E1 | 图类型 | 研究框架图 / 技术路线图 / 方法·模型架构图 / 系统架构图 / 论文结构图 / 实验流程图 |
| E2 | **主题（视觉预设）** | 素白（推荐）/ 深色 / 制图线稿 / 新粗野 / 趣味 / 新拟态 / 孟菲斯 / 玻璃 / 包豪斯 / 苹果风 |
| E3 | **数据流动形式** | 静止 `off` / 悬停 `hover` / 流动 `flow` / 巡演 `tour` |
| E4 | 文字语言 | 中文 `zh-CN` / 英文 `en` |
| E5 | 排版规格 | 单栏（默认） / 双栏 |
| E6 | 输出格式 | HTML（默认） / PDF / EPS |
| E7 | 定稿阶段 | 初稿 `draft` / 已确认 `confirmed` / 最终版 `final` |

### 1.6 插图门禁触发的询问（方案 v2，待实施）

| # | 场景 | 处置 |
|---|---|---|
| F1 | `figures.py render` 缺任一必问项且用户未弃权 | **拒绝渲染（exit 2）**并列出缺失项 |
| F2 | 方法/模型架构图、系统架构图要 final 但代码未跑通 | 软门禁：停在 `confirmed`，**要用户显式确认** |
| F3 | 路线图补充模式被拒（想删改拓扑） | 提示需 `--force-rewrite`，**由用户显式决定** |
| F4 | 实验流程图要 final 但无真实实验数据 | **硬门禁直接拒绝**（不是询问，是拦住） |

**小计：约 41 条**（入口 5 + 审批 18 + 阶段 6 + 数据图 3 + 插图 7 + 门禁 2 项询问）

---

## 第 2 部分 · 不需要询问（自动执行或固定默认）

### 2.1 全流程自动项

| # | 项目 | 固定行为 |
|---|---|---|
| N1 | 双语输出 | 每份报告自动生成 `.md`（英）+ `-CN.md`（中），不问 |
| N2 | 领域路由 | 按关键词+依赖自动路由到 数值/符号/AI4Math/统计/优化/经济 子策略，不问 |
| N3 | 统计判决方法 | 五态判决 + 95% t-CI + N≥5 种子，自动 |
| N4 | 命名与目录约定 | `实验复刻结果汇总/` 三段结构、双语命名（`名.md`/`名-CN.md`）、表头 `Metric / 指标`，自动 |
| N5 | 每张数据图附可独立运行的 `plot_*.py` | 自动（G66 门禁，不问） |
| N6 | Phase 7 归位结构 | 自动按既定结构归位，只做完整性确认 |
| N7 | 数据图与插图的分离 | 数据图走 matplotlib 路线、插图走矢量图引擎，自动判定 |
| N8 | 图的字体与内嵌 | HarmonyOS Sans Medium 子集 base64 内嵌，自动 |
| N9 | 中英切换器文案 | 随 `locale` 自动（流动/悬停/巡演/静止 ↔ Flow/Hover/Tour/Still），自动 |
| N10 | 交付证据 | 快照 → 检查 → 原子提交 → SHA-256 收据，自动 |
| N11 | 许可归属 | NOTICE + manifest 记录上游 commit，自动 |

### 2.2 插图引擎自动项（不需要问，也不允许擅自改）

| # | 项目 | 固定行为 |
|---|---|---|
| N12 | 检查档位 | 默认 `showcase`（11 项全硬性），除非用户明确要更密的 `standard` |
| N13 | 数据流虚线颜色 | 按连线语义取主题强调色（forward→蓝 / loss→红 / data→灰），自动 |
| N14 | 流动时静态实线让位 | 一条边要么实线要么虚流，不叠加，自动 |
| N15 | `off` 模式产物 | 不含任何动效痕迹，自动 |
| N16 | 中文优先检查（第 11 项） | `locale: zh-CN` 时强制，白名单外必须中文，自动 |
| N17 | 连线自动路由 | 先自动路由；`via`/`fromSide`/`labelAt` 只在诊断后逐个加，**不预先询问** |
| N18 | 扇入扇出端点 | 自动散开（侧边 70% 槽位、按对端排序不交叉），不问 |
| N19 | 11 项几何自证检查 | 自动跑，不问 |
| N20 | 副标题 | 默认不加，**不得臆造**（用户明确要求才加）—— 不问 |
| N21 | 预览 | 默认不启动；只在用户要求即刻预览时加 `--open` |
| N22 | 张量形状标注 | 视为语义数据，碰撞时移动/缩短而非删除，自动 |

### 2.3 明确禁止项（既非"问"也非"默认"，属禁止）

| # | 禁止 |
|---|---|
| P1 | 用手改 HTML 冒充检查通过（收据 SHA-256 会对不上） |
| P2 | 用 `overflow:hidden`、截断、内部滚动条等伪造不溢出 |
| P3 | 非零退出却描述为成功 |
| P4 | 声称做了实际未做的视觉目检（审美评审须真人或具读图能力者） |
| P5 | 无真实实验数据就画"最终版"实验流程图 |

---

## 第 3 部分 · 条件性（满足条件即归入"不用问"）

| 项目 | 何时不用问 |
|---|---|
| 报告模板 | 用户已传 `--template` → 跳过询问 |
| 审阅视角 | 若裁定为"上下文已明确"（如用户明说"按审稿人视角"）→ 不问 |
| 插图七项 | 对话中已陈述过的项 → 不重复问 |
| 插图七项 | 用户明确弃权（"随便/默认/你定"）→ 回落推荐默认，但**交付说明必须写明"该项未指定，按默认交付"** |
| 批量出图 | 同一轮答案覆盖全部图，**一批只问一次**，不逐图重复问 |

---

## 第 4 部分 · 处置记录与遗留问题

### 4.1 已处置（2026-09-12）

| # | 问题 | 处置 | 验证 |
|---|---|---|---|
| Q1 | 审阅视角规则自相矛盾 | **裁定为"必须询问"**。已改：`SKILL.md` 四处（`:58` 默认研究生 → 必须询问；`:170` 补交互询问与 G01 依赖警告；`:176` 标注；`:459` 统一措辞）；`literature_reader.py` 的 `--perspective` 默认值由 `student` 改为 `None`，缺省即调用新增的 `select_perspective_interactive()` | 三条路径实测：非交互 + 无参数 → exit 1 干净拒绝；给了 `--template` → 正确追问视角后拒绝；两个参数都给 → exit 0 并写出报告 |
| Q4 | `render_report` 未定义，调用即 `NameError` | 已修：把误嵌在 `select_template_interactive()` 内的孤儿函数体（原 517-539 行的 Jinja2 渲染逻辑）恢复为模块级 `def render_report(template_path, data)` | 端到端跑通，产出 `文献阅读.md`（10,329 字节）+ `literature_reading.json` |
| Q5 | 根目录残留指向他人机器路径（`C:\Users\GLY\...`）的调试脚本 | 已删除 `check_encoding.py`、`fix_encoding.py`（均被 git 跟踪，可用 `git checkout -- <文件>` 恢复） | `git status` 显示 `D` 两条 |
| Q6 | *（本轮新发现）* 交互式选择存在**无限重试死循环**：`isatty()` 为真但输入流立即 EOF 时，`except (ValueError, EOFError)` 只打印警告并继续循环，实测刷出 47MB 输出 | 已修：`EOFError` 单独分支处理，打印指引并 `return None` 退出；两个选择器都加了非交互前置守卫 | 回归测试输出仅 455 字节、exit 1 |
| Q7 | *（本轮新发现）* **用户选的模板被丢弃**：`main()` 里交互选完模板后，渲染处又执行 `template_path = args.template or "templates/literature_reader.template.md"`，把用户选择覆盖为默认模板 | 已修：渲染处直接复用 `main()` 顶部解析好的 `template_path`，并在模板文件缺失时明确告警 | 同上测试 C 使用 markleaf 模板成功渲染 |

### 4.2 Q2 —— 6 个"注册了却没有目录"的技能在干什么

结论先说：**它们什么也没干。** 全仓库检索确认，`skills/registry.yaml` **没有任何代码读取**（无 import、无解析、无测试引用），它目前只是一份**声明性文档**。因此其中 18 条 `requires_approval_for` 审批约束**在运行时全部不生效**。

这 6 个技能的真实工作其实已经存在，只是散落在 `scripts/` 与手工阶段步骤里，没有按 registry 声明的形态落成目录：

| 注册名（无目录） | 声明的产出 | 工作目前实际在哪 |
|---|---|---|
| `paper_parsing_skill` | `analysis/paper_summary.json`、`parsed_text.md`、`*_student/advisor/reviewer_review.md`、`reproducibility_assessment.json` | `scripts/math_pdf_extract.py` + `scripts/literature_reader.py`（三视角审阅与评估生成都在这里） |
| `environment_setup_skill` | `env/environment.yml`、`requirements-locked.txt` | `scripts/cvxpy_env_setup.py` + Phase 2 手工程序 |
| `baseline_verification_skill` | `results/baseline_metrics.json`、`tolerance_spec.json` | Phase 3 手工步骤，无专门脚本 |
| `incremental_implementation_skill` | `implementation/implementation_log.md`、`delta_report.json` | Phase 4 手工循环，无专门脚本 |
| `experiment_execution_skill` | `results/raw_metrics.csv`、`logs/run.log`、`results/figures/*.png` | `scripts/plot_and_export.py` + Phase 5 手工步骤 |
| `artifact_packaging_skill` | `dist/artifact_bundle.zip`、`provenance_chain.json` | **完全无实现**（Phase 7 只做文件归位，不打制品包） |

**这意味着三件事**：① "中等风险需运行前审批"和"高风险逐条审批"目前靠模型自觉，没有机制保障；② registry 的 DAG（`requires_skills`）也不会被真正执行——阶段顺序实际由 `SKILL.md` 正文描述约束；③ 悬空技能名会让阅读者误以为有 10 个 skill 可用，实际只有 4 个有实体。

**两条可选修法**：
- **A. 让 registry 生效**（尚未做）：新增 `scripts/pipeline.py` 读取 registry，把 18 个审批点做成真正的 gate（读到需审批动作时暂停等确认），并为 6 个缺目录的技能补 `SKILL.md` 壳（指向现有脚本）。
- **B. 让 registry 诚实**：✅ **已采用**（见下）。

#### 已处置（2026-09-12，用户选定"标注诚实化"）

`skills/registry.yaml` 已改写为诚实版，**内容一条未删**，只把状态讲清楚：

| 改动 | 内容 |
|---|---|
| 文件头审计说明 | 明确写出：本文件是声明性文档、无代码读取、审批与 DAG 均未强制、需 `scripts/pipeline.py` 才具备强制力 |
| 新增 `implementation_status` | `implemented` 4 条（infrastructure_orchestration / version_management / statistical_verification / bilingual_report）／`declared-only` 5 条／`not-implemented` 1 条（artifact_packaging） |
| 新增 `implementation` 字段 | 无目录条目改为指向真实载体，如 `paper_parsing_skill → scripts/math_pdf_extract.py + literature_reader.py`；无脚本的写明"Phase 3 手工步骤" |
| 无目录条目的 `path` | 置为 `null` 并注明"无实体目录" |
| `metadata.approvals` | `enforcement: policy-only`、`declared_actions: 18`、`enforced_actions: 0` |
| `default_entrypoint` | 加注：该名称不在 skills 列表内、也无目录，**当前实际入口是仓库根 SKILL.md** |

校验：`yaml.safe_load` 解析通过；10 条技能、18 条审批动作、状态分布 `{implemented: 4, declared-only: 5, not-implemented: 1}` 均与原数据一致。

**仍未解决**：审批依然不强制（`enforced_actions: 0`）。要让"中风险需运行前审批"真正生效，仍需做 A 方案里的 `scripts/pipeline.py`。

### 4.3 其他已知（未处置）

| # | 问题 |
|---|---|
| Q3 | `SKILL.md` 称旧脚本在 `scripts/legacy/`，该目录不存在（`three_perspective_review.py` 仍在 `scripts/` 原位） |
| Q8 | *（顺带发现）* `scripts/__pycache__/trajectory_visualizer.cpython-314.pyc` 被误提交进 git，建议加入 `.gitignore` 并移除 |

