# RFC 001: algos 插件化注册表（Algo Plugin Registry）

- **状态（Status）**: Draft（设计依据文档，未实现）
- **日期（Date）**: 2026-10-01
- **范围（Scope）**: obj 分支从"单算法范本（qem_tool）"向"多算法基准平台"演进的第一步设计依据
- **关联（Related）**: `algos/registry.yaml`（骨架）、`corpus/MANIFEST.json`、`corpus/golden/checksums.json`、SKILL.md Phase 7（G9 门禁）

## 0. 背景与动机

obj 分支当前把 QEM 实现固定在 `qem_tool/` 包内，SKILL.md 的"适配新算法"指引是"整体替换 qem_tool"——对单一算法可用，但接入第二个算法（ICE：Surface Simplification Using Intrinsic Error Metrics）时会产生两个问题：

1. **入口不统一**：每个算法一个顶层包，CLI/测试/报告无从按统一方式发现与调用；
2. **数据资产无主**：金样本矩阵（`corpus/golden/`）与语料清单（`corpus/MANIFEST.json`）是按算法产出族登记的，缺少"算法 ↔ 数据 ↔ 验证"的声明式关联。

本 RFC 提出一个**最小**注册表 schema（`algos/registry.yaml`）与配套策略：QEM 作为首个 `active` 条目，ICE 作为 `planned` 占位。**本 RFC 只定义 schema 与迁移路径，不实现任何加载器，也不实际迁移代码**（见 §5 非目标）。

## 1. 设计点一：registry schema 字段与 status 语义

### 1.1 条目字段（AlgoRegistryEntry）

```yamlc
schema_version: 1
algorithms:
  - name: str            # 唯一标识（小写、下划线，作为 registry 主键）
    paper_ref: str       # 论文引用（作者/年份/题名/出处）
    entry: str | null    # CLI 入口（相对仓库根的路径）；planned 阶段为 null
    params: map          # 参数模式（参数名 → 默认值示例；空 map 表示待定）
    capabilities: [str]  # 能力声明（小写动词短语，如 simplify）
    status: active       # active | planned
```

### 1.2 status 语义

| status | 语义 | 准入条件 |
|--------|------|---------|
| `active` | 条目指向**可运行**的 CLI 入口；`pytest tests/` 有其专属回归测试；其涉及的金样本断言全绿 | entry 非空且文件存在；测试与数据齐备 |
| `planned` | 设计占位：论文已知、接入路径已定，但代码未落库 | entry 必须为 `null`；接入时必须先升为 active 的准入检查 |

不允许第三种状态（如 `deprecated`）——降级路径待真实案例出现后再补充，避免过度设计。

### 1.3 版本化策略

- `schema_version`（文件级）：schema 结构变更时 +1。**仅加可选字段** → 不加版本（旧消费者忽略新字段即可）；**改字段语义/删字段/改必填性** → +1 并在 RFC 中登记变更记录。
- 条目级不设版本：条目演进（如 qem 的 entry 从 `qem_tool/cli.py` 迁至 `algos/qem/cli.py`）通过 §2 的三阶段迁移保证兼容，不引入条目内版本号。
- 追加（additive）变更合入时须跑一遍 `yaml.safe_load` 冒烟 + 金样本测试（现状即 SC-005 的验证方式）。

## 2. 设计点二：qem_tool → algos/qem 迁移路径（三阶段）

现状：QEM 实现位于 `qem_tool/`（`cli.py` / `qem_core.py` / `obj_io.py`），测试直接 `import qem_tool`。目标形态：算法包收敛到 `algos/<name>/`，`obj_io.py` 留在框架层。

迁移按三阶段执行，每阶段独立 commit、`pytest tests/` 全绿才进入下一阶段：

| 阶段 | 动作 | 兼容性 |
|------|------|--------|
| **① 复制** | 新建 `algos/qem/`，把 `qem_core.py`/`cli.py` 复制过去（import 路径改写）；`qem_tool/` 原样保留 | 双路径并存，`registry.yaml` 的 entry 仍指旧路径 |
| **② shim 重导出** | `qem_tool/qem_core.py`/`cli.py` 变为 shim：`from algos.qem.qem_core import *`（显式列名重导出）；`registry.yaml` entry 切到 `algos/qem/cli.py`；测试逐步切换到新路径，旧路径保留一组 shim 冒烟测试 | 外部消费者（SKILL.md 示例命令、历史脚本）不破坏 |
| **③ 删除旧路径** | 至少一个完整发布周期后，删除 `qem_tool/` 下的算法文件（`obj_io.py` 是否上提到框架层另行决策）；删除 shim 冒烟测试 | Breaking change，须在 SKILL.md 与 RFC 变更记录中显式公告 |

**shim 策略约束**：shim 只做重导出，不保留任何实现副本；shim 存续期内 `registry.yaml` 的 entry 已指向新路径，旧路径仅为兼容存续。

**本 RFC 不执行任何阶段**——三阶段是 E1（QEM 迁移执行特性）的实施依据。

## 3. 设计点三：ICE adapter（status: planned 占位）

ICE 参考实现是 C++（obj_exp `ICE_Experiment_Logs` 的上游 intrinsic-simplification 工程），adapter 形态按优先级：

1. **subprocess wrapper（优先）**：Python 侧 `algos/ice/` 仅封装 CLI 调用（构造参数 → `subprocess.run` → 解析 stdout/产物文件）。优点：不碰 C++ 内存管理、失败隔离、与实验日志的调用方式一致（金样本矩阵即其产物）。
2. **FFI（后备）**：仅当 subprocess 成为性能瓶颈（如批量基准测试）且上游提供稳定 C ABI 时考虑；需额外评估构建链与跨平台成本，届时另立 RFC。

**planned 占位含义**（对齐 §1.2）：registry 中 ice 条目 `entry: null`、`status: planned`；`capabilities` 预声明 `simplify` 与 `intrinsic_field_transport`（对应 05_multigrid 的向量延拓/连接拉普拉斯产物族）；`params` 留空 map。接入时（E2）需满足 active 准入：wrapper CLI 可运行、金样本测试覆盖（dragon 系列见 §4）、G9 走查通过。

## 4. 设计点四：金样本/语料版本化

金样本与语料清单是算法回归测试的数据契约，版本化策略如下：

- **schema_version 锚定**：`corpus/golden/checksums.json` 与 `corpus/MANIFEST.json` 各自带 `schema_version`（当前均为 1）；schema 变更规则同 §1.3。
- **sha256 锚定**：每个数据条目以 `sha256`（+ bytes）唯一锚定内容；任何"同一名字但内容变了"的数据变更必须显式更新 checksums 并在金样本 README 登记原因（禁止静默替换）。
- **in_repo / 外部数据**：spot 系列 9 矩阵入仓（`in_repo: true`）；dragon 系列 9 矩阵因体积不入仓（`in_repo: false`），测试默认 SKIP，设置环境变量 `ICE_GOLDEN_DRAGON_DIR` 指向本地目录后自动启用全量校验（获取方式见 `corpus/golden/README.md`，来源为 obj_exp `ICE_Experiment_Logs/matrices/` 的 `ICE_Experiment_Logs.7z` 快照）。
- **算法 ↔ 数据关联**：金样本按产物族（kind）断言，kind 命名与 ICE 的 stage 产物一一对应；qem 侧迁移后（§2 阶段②）应在 registry 条目的 params 中登记基准参数，使"算法版本 + 参数 + 数据 sha256"三元组可复现。
- **已知现象登记**：不满足强断言但确认非回归的现象（如 dragon vprolong 行偏差 ≈8.9e-2、上游空行 HACK）登记于金样本 README 的"已知现象"，与断言解耦——版本化的是断言 + 现象清单两者。

## 5. 非目标（Non-Goals）

- **不实现 registry 加载器**：`registry.yaml` 当前仅供人与文档消费；任何代码消费（CLI 发现算法、按 capabilities 调度）待第二个 active 条目出现后再设计。
- **不实际迁移 qem_tool**：§2 仅定义路径；执行属 E1。
- **不接入 ICE**：§3 仅定义 adapter 形态；执行属 E2。
- **不引入构建系统/打包变更**：registry 骨架不影响现有 `pip install`/import 体系。

## 6. 变更记录（Changelog）

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-10-01 | r1 | 初版：四设计点 + registry 骨架 schema（schema_version: 1，qem active + ice planned） |
