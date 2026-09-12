#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figuregen · 图状态机

状态：draft（初稿/预计）→ confirmed（结构已定）→ final（已过门禁，可入稿）
规则：
1. 状态**只升不降**（允许重跑同级）；
2. spec 一经修改，自动降回 draft 并要求重跑门禁（防"改了图沿用旧 final"）。
"""

import hashlib
import json

STAGES = ("draft", "confirmed", "final")
STAGE_CN = {"draft": "初稿", "confirmed": "已确认", "final": "最终版"}

# draft 标题自动加的标注（方案 §5）；「（预计流程）」来自实验流程图门禁
STAGE_LABEL_SUFFIX = {"draft": "（初稿）", "confirmed": "", "final": ""}
KNOWN_SUFFIXES = ["（初稿）", "（预计流程）"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_spec(path):
    """读 spec 并返回 (dict, bytes, sha256)。"""
    with open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8-sig")), raw, sha256_bytes(raw)


def stage_rank(stage):
    if stage not in STAGES:
        raise ValueError("非法阶段 %r，合法值 %s" % (stage, list(STAGES)))
    return STAGES.index(stage)


def resolve_stage(requested, record, spec_sha):
    """按状态机裁决本次渲染允许到达的阶段。

    返回 (stage, note)：
    - 无记录（新图）             → 允许 requested
    - spec 未变                  → 允许 requested（只升不降）
    - spec 已变                  → 一律降回 draft，note 说明原因
    """
    if record is None:
        return requested, None
    if record.get("spec_sha256") != spec_sha:
        return "draft", ("spec 已修改，状态自动降回 draft（原 %s），需重跑门禁" % record.get("stage"))
    prev = record.get("stage", "draft")
    if stage_rank(requested) > stage_rank(prev):
        return requested, None
    if stage_rank(requested) < stage_rank(prev):
        # 只升不降：请求比已登记的低，不回退已达到的状态，按登记值执行
        return prev, ("状态只升不降：已登记 %s，本次请求 %s，按 %s 执行" % (prev, requested, prev))
    return requested, None


def title_with_stage(title, stage, suffix_override=None):
    """draft 阶段给标题加「（初稿）」类标注（方案 §5 标题处理）。

    标题已带任一已知阶段标注（如实验流程图的「（预计流程）」）时不再叠加。
    """
    suffix = suffix_override if suffix_override is not None else STAGE_LABEL_SUFFIX.get(stage, "")
    if not suffix:
        return title
    known = [s for s in KNOWN_SUFFIXES + [suffix] if s]
    if any(title.endswith(s) for s in known):
        return title
    return "%s%s" % (title, suffix)
