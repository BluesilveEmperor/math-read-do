#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figuregen · figures/manifest.json 读写与校验（方案 §5）

manifest 是图状态机 + SHA-256 收据的注册表（Phase 7 归位时一并移入
`实验复刻结果汇总/论文插图（含规格）/`）。

校验说明：`schemas/figure_manifest.schema.json` 是声明文档；本模块用显式规则校验
（不引入 jsonschema 依赖），规则与 schema 一致。
"""

import json
import os
import time

from . import presets as P

MANIFEST_REL = os.path.join("figures", "manifest.json")

FIGURE_REQUIRED = ["id", "type", "stage", "gate", "spec", "output_html", "quality"]
FIGURE_ID_RE_RULE = "id 必须匹配 ^[a-z][a-z0-9_-]*$"


def default_manifest(paper=""):
    return {
        "schema_version": P.MANIFEST_SCHEMA_VERSION,
        "paper": paper,
        "engine": {
            "internal": "figuregen",
            "version": P.ENGINE_VERSION,
            "upstream_commit": P.ENGINE_UPSTREAM_COMMIT,
        },
        "global_motion": "off",
        "figures": [],
    }


def manifest_path(root):
    return os.path.join(root, MANIFEST_REL)


def load(root):
    p = manifest_path(root)
    if not os.path.exists(p):
        return default_manifest()
    try:
        with open(p, "rb") as fh:
            m = json.loads(fh.read().decode("utf-8-sig"))
    except Exception as e:
        raise ValueError("figures/manifest.json 不是合法 JSON：%s" % e)
    if not isinstance(m, dict) or not isinstance(m.get("figures"), list):
        raise ValueError("figures/manifest.json 结构不合法（缺少 figures 列表）")
    return m


def save(root, manifest):
    p = manifest_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    manifest["updated"] = now
    tmp = p + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    if os.path.exists(p):
        os.replace(tmp, p)
    else:
        os.rename(tmp, p)
    return p


def get(manifest, fig_id):
    for rec in manifest.get("figures") or []:
        if rec.get("id") == fig_id:
            return rec
    return None


def put(manifest, record):
    for i, rec in enumerate(manifest.get("figures") or []):
        if rec.get("id") == record.get("id"):
            manifest["figures"][i] = record
            return
    manifest.setdefault("figures", []).append(record)


def _is_str(x):
    return isinstance(x, str) and x != ""


def _valid_id(fid):
    if not isinstance(fid, str) or not fid:
        return False
    if not (fid[0].isalpha() and fid[0].islower()):
        return False
    return all(c.islower() or c.isdigit() or c in "_-" for c in fid)


def validate(manifest):
    """显式规则校验（与 schemas/figure_manifest.schema.json 一致）。返回错误列表。"""
    errs = []
    if manifest.get("schema_version") != P.MANIFEST_SCHEMA_VERSION:
        errs.append("schema_version 必须为 %r" % P.MANIFEST_SCHEMA_VERSION)
    if not isinstance(manifest.get("paper"), str):
        errs.append("paper 必须是字符串（可为空：尚未读取论文标题时）")
    eng = manifest.get("engine") or {}
    if eng.get("internal") != "figuregen":
        errs.append("engine.internal 必须为 figuregen")
    if not _is_str(eng.get("upstream_commit")):
        errs.append("engine.upstream_commit 必须记录内嵌基线 commit")
    if manifest.get("global_motion") not in P.MOTIONS:
        errs.append("global_motion 必须是 %s 之一" % sorted(P.MOTIONS))
    seen = set()
    for rec in manifest.get("figures") or []:
        fid = rec.get("id")
        for k in FIGURE_REQUIRED:
            if not _is_str(rec.get(k)):
                errs.append("figure %r 缺少必填字段 %s" % (fid, k))
        if fid in seen:
            errs.append("figure id 重复：%r" % fid)
        seen.add(fid)
        if fid and not _valid_id(fid):
            errs.append("figure %r %s" % (fid, FIGURE_ID_RE_RULE))
        if rec.get("type") not in P.DIAGRAM_TYPES:
            errs.append("figure %r type 非法：%r" % (fid, rec.get("type")))
        if rec.get("stage") not in P.STAGES:
            errs.append("figure %r stage 非法：%r" % (fid, rec.get("stage")))
        if rec.get("gate") not in P.GATES.values():
            errs.append("figure %r gate 非法：%r" % (fid, rec.get("gate")))
        if rec.get("quality") not in ("standard", "showcase"):
            errs.append("figure %r quality 非法" % fid)
        sha = rec.get("sha256") or {}
        if not (_is_str(sha.get("spec")) and _is_str(sha.get("html"))):
            errs.append("figure %r 缺少 sha256.spec / sha256.html 收据" % fid)
        checks = rec.get("checks")
        if not isinstance(checks, dict) or "errors" not in checks:
            errs.append("figure %r 缺少 checks（11 项几何自证检查结果）" % fid)
        elif int(checks.get("errors", 0)) > 0:
            errs.append("figure %r 的检查存在 error，不允许登记为已交付" % fid)
    return errs
