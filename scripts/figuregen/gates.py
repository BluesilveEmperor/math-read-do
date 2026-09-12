#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figuregen · 定稿门禁（方案 §4.3 / §6）

三类门禁：
- none                     framework / structure / route      无门禁
- soft_code_verified       model / system                     final 需代码已跑通的证据；
                                                              否则停在 confirmed 并要求确认
- requires_experiment_data experiment（硬门禁）               final 必须有
                                                              figures/data/experiment_counts.json
                                                              且字段完整、能对上真实实验产物

为什么只有实验流程图必须等实验后：那张图的每个数字和分支是**实验的事实记录**，
不是设计意图；其余五张图的主体是设计，设计阶段即成立。
"""

import json
import os

# 实验流程图 final 必须具备的字段（方案 §6）
EXPERIMENT_REQUIRED_FIELDS = [
    "initial_n",      # 初始样本/数据量
    "excluded",       # [{"n": int, "reason": str}] 排除数量与原因（PRISMA 要求逐条具名）
    "included_n",     # 最终纳入
    "groups",         # [{"name": str, "n": int, "allocation": str}] 分组与每组 n
    "attrition",      # [{"n": int, "reason": str, "type": "lost|withdrawn|excluded"}]
    "analyzed_n",     # 进入分析的人数
    "metrics",        # 评价指标
]

EXPERIMENT_DATA_REL = os.path.join("figures", "data", "experiment_counts.json")

# soft_code_verified 接受的证据（任一即可）
SOFT_EVIDENCE = (
    os.path.join("results", "raw_metrics.csv"),
    os.path.join("implementation", "delta_report.json"),
)


class GateResult(object):
    """门禁结果。stage_cap=None 表示不限；notes 是要写进交付说明/manifest 的说明。"""

    def __init__(self, ok=True, stage_cap=None, note=None, label_suffix=None, blocked_reason=None):
        self.ok = ok
        self.stage_cap = stage_cap
        self.note = note
        self.label_suffix = label_suffix
        self.blocked_reason = blocked_reason

    def __repr__(self):
        return "GateResult(ok=%s, stage_cap=%s)" % (self.ok, self.stage_cap)


def gate_none(stage, root):
    return GateResult(ok=True)


def gate_soft_code_verified(stage, root):
    """model / system：final 需要代码已跑通的证据，否则停在 confirmed 并要求确认。"""
    if stage != "final":
        return GateResult(ok=True)
    for rel in SOFT_EVIDENCE:
        if os.path.exists(os.path.join(root, rel)):
            return GateResult(ok=True, note="soft_code_verified 证据：%s" % rel)
    if os.path.exists(os.path.join(root, EXPERIMENT_DATA_REL)):
        return GateResult(ok=True, note="soft_code_verified 证据：实验数据文件已就位")
    return GateResult(
        ok=True,
        stage_cap="confirmed",
        note=("soft_code_verified 未满足：代码尚未跑通（需要以下任一证据：%s）。"
              "本次停在 confirmed；确认代码跑通后重跑 --stage final，"
              "或显式加 --code-verified 由你确认后放行。"
              % " 或 ".join(SOFT_EVIDENCE)),
    )


def gate_experiment(stage, root):
    """experiment：唯一硬门禁（方案 §6）。final 阶段缺数据 → 直接拒绝。"""
    if stage != "final":
        return GateResult(ok=True, label_suffix="（预计流程）")

    data_path = os.path.join(root, EXPERIMENT_DATA_REL)
    if not os.path.exists(data_path):
        return GateResult(
            ok=False,
            blocked_reason=("最终版实验流程图必须基于真实实验数据：缺少 %s。"
                            "计划阶段请改用 --stage draft 输出预计流程图。" % EXPERIMENT_DATA_REL),
        )
    try:
        with open(data_path, "rb") as fh:
            counts = json.loads(fh.read().decode("utf-8-sig"))
    except Exception as e:
        return GateResult(ok=False, blocked_reason="experiment_counts.json 不是合法 JSON：%s" % e)

    missing = [f for f in EXPERIMENT_REQUIRED_FIELDS if not counts.get(f)]
    if missing:
        return GateResult(
            ok=False,
            blocked_reason=("实验数据不完整，缺少字段：%s。这些数字不能靠推测编造，"
                            "请等实验跑完、数据整理完再定稿。" % "、".join(missing)),
        )
    if not counts.get("raw_metrics_sha256"):
        return GateResult(ok=False, blocked_reason="未记录 results/raw_metrics.csv 哈希：无法证明数字来自真实实验产物。")

    groups = counts.get("groups") or []
    total = sum(g.get("n", 0) for g in groups if isinstance(g, dict))
    if total > counts.get("included_n", 0):
        return GateResult(ok=False, blocked_reason="分组人数合计（%d）超过纳入人数（%d），数据自相矛盾。"
                          % (total, counts.get("included_n", 0)))

    kind = counts.get("flow_diagram_kind")
    if kind in ("PRISMA", "CONSORT"):
        bad = [i for i, e in enumerate(counts.get("excluded") or []) if not e.get("reason")]
        if bad:
            return GateResult(ok=False, blocked_reason="%s 流程图要求每条排除都必须写明原因与篇数（第 %s 条缺失）。"
                              % (kind, "、".join(str(i + 1) for i in bad)))

    return GateResult(ok=True, note="experiment_counts.json 完整（raw_metrics sha256 已记录）")


GATE_FN = {
    "none": gate_none,
    "soft_code_verified": gate_soft_code_verified,
    "requires_experiment_data": gate_experiment,
}

# 别名：测试与调用方常用门禁名直接命名
gate_requires_experiment_data = gate_experiment


def run_gate(gate_name, stage, root):
    fn = GATE_FN.get(gate_name)
    if fn is None:
        return GateResult(ok=False, blocked_reason="未知门禁 %r" % gate_name)
    return fn(stage, root)
