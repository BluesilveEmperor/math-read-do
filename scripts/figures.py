#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figures · math-read-do 论文插图唯一用户门面（方案 docs/figures-feature-plan.md §2.3）

用法：
  python scripts/figures.py list [--json]
  python scripts/figures.py doctor
  python scripts/figures.py render <framework|route|model|system|structure|experiment>
        --stage <draft|confirmed|final>
        [--preset <paper|paper-dark|blueprint-print|brutalism|playful|neumorphism|memphis|glass|bauhaus|apple>]
        [--motion <off|hover|flow|tour>] [--lang <zh-CN|en>] [--column <single|double>]
        [--format <html|pdf|eps>] [--quality <standard|showcase>] [--spec <path>]
        [--declined <a,b,c>] [--code-verified] [--force-rewrite] [--out <path>] [--json]
  python scripts/figures.py init-reading <literature_reading.json> [render 公共参数...]
  python scripts/figures.py route-draft <literature_reading.json> [render 公共参数...]
  python scripts/figures.py route-supplement <delta_report.json> --spec <new.json> [--force-rewrite] [--json]

设计要点（docs/figures-feature-plan.md）：
- 出图前必问清单做成**代码约束**：任一必问项既未指定也未弃权 → exit 2 并列出缺失项（§2.4 / T15）
- figures.py 是唯一允许触碰渲染内核的入口（§6），保证门禁不可规避
- 渲染内核内嵌于 scripts/figuregen/engine/（源自 paperfig，MIT，见 NOTICE.md），Node ≥ 18
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from figuregen import gates as G          # noqa: E402
from figuregen import manifest as MF      # noqa: E402
from figuregen import presets as P        # noqa: E402
from figuregen import state as ST         # noqa: E402

ENGINE = os.path.join(HERE, "figuregen", "engine", "bin", "paperfig.mjs")
TEMPLATES_DIR = os.path.join(HERE, "figuregen", "templates")
SPECS_REL = os.path.join("figures", "specs")
OUT_REL = os.path.join("figures", "out")
DATA_REL = os.path.join("figures", "data")

# 渲染产物体积约 0.65MB/张（字体子集已内嵌），全部保留
KNOWN_LIMITS = [
    "PDF/EPS 导出：内核目前是 Phase 2 桩，本次仅交付 HTML（自包含，字体子集已内嵌）",
    "visual-check（浏览器级目检）：内核同样是 Phase 2 桩，视觉确认需人工打开 HTML",
]


# ─────────────────────────── 基础设施 ───────────────────────────

def find_node():
    exe = shutil.which("node")
    if exe:
        return exe
    return None


def node_version(node_exe):
    try:
        out = subprocess.check_output([node_exe, "--version"], stderr=subprocess.STDOUT)
        return out.decode("utf-8", "replace").strip()
    except Exception as e:
        return "unknown (%s)" % e


def run_kernel(args, node_exe):
    """调用内嵌内核，返回 (returncode, stdout文本, stderr文本)。"""
    cmd = [node_exe, ENGINE] + args
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (p.returncode,
            p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def parse_json_loose(text):
    """内核 --json 输出可能夹杂 stderr 行；取第一个 { 到最后一个 }。"""
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(text[i:j + 1])
    except Exception:
        return None


def die(msg, code=1):
    sys.stderr.write("figures: %s\n" % msg)
    sys.exit(code)


# ─────────────────────────── list / doctor ───────────────────────────

def cmd_list(args):
    root = os.path.abspath(args.root)
    mf = MF.load(root)
    rows = []
    for t in P.DIAGRAM_TYPES:
        rec = MF.get(mf, "fig-" + t)
        rows.append({
            "type": t,
            "cn": P.DIAGRAM_TYPES_CN[t],
            "gate": P.GATES[t],
            "registered": rec is not None,
            "stage": (rec or {}).get("stage"),
            "spec": (rec or {}).get("spec"),
            "output_html": (rec or {}).get("output_html"),
            "checks": (rec or {}).get("checks"),
        })
    if getattr(args, "json", False):
        print(json.dumps({"root": root, "figures": rows,
                          "warnings": KNOWN_LIMITS}, ensure_ascii=False, indent=2))
        return 0
    print("论文插图（六类）· 工作目录: %s" % root)
    print("门禁: none=无  soft_code_verified=代码跑通后 final  requires_experiment_data=实验数据齐备才可 final")
    print("")
    print("  类型        名称            门禁                        状态      产物")
    for r in rows:
        print("  %-10s  %-14s  %-26s  %-8s  %s" % (
            r["type"], r["cn"], r["gate"],
            r["stage"] or "未出图",
            r["output_html"] or "-"))
    print("")
    print("已知限制:")
    for w in KNOWN_LIMITS:
        print("  - " + w)
    return 0


def cmd_doctor(args):
    node = find_node()
    if not node:
        die("未找到 node。论文插图内核需要 Node >= 18：https://nodejs.org/ （Windows 安装后重开终端）。", 1)
    code, out, err = run_kernel(["doctor"], node)
    sys.stdout.write(out)
    if err:
        sys.stderr.write(err)
    return code


# ─────────────────────────── 必问项校验（§2.4）───────────────────────────

def check_ask_items(args, asked_type):
    """§2.4：缺任一必问项且未弃权 → 返回缺失列表（否则返回 (declined, values)）。"""
    provided = {
        "preset": args.preset is not None,
        "motion": args.motion is not None,
        "lang": args.lang is not None,
        "column": args.column is not None,
        "format": (args.format is not None or args.pdf or args.eps),
        "stage": args.stage is not None,
    }
    declined = []
    for d in (args.declined or "").split(","):
        d = d.strip().lower()
        if d:
            if d not in P.ASK_ITEMS:
                die("--declined 含未知项 %r（合法：%s）" % (d, ", ".join(P.ASK_ITEMS)), 2)
            declined.append(d)
    missing = [k for k in P.ASK_ITEMS if not provided[k] and k not in declined]
    if missing:
        lines = ["出图前必问项缺失（方案 §2.4）：图的细节由用户定，数学流程不得默默决定任何一项。", ""]
        for k in missing:
            lines.append("  - %s (%s)" % (P.ASK_ITEM_CN[k], k))
        lines.append("")
        lines.append("请先向用户问清这些项再出图；用户明确弃权时用 --declined <项,项> 显式声明，")
        lines.append("例如：--declined preset,motion（将按推荐默认交付，并在交付说明中写明）。")
        return {"missing": missing, "lines": lines}
    values = {
        "preset": args.preset or P.DECLINE_FALLBACK["preset"],
        "motion": args.motion or P.DECLINE_FALLBACK["motion"],
        "lang": args.lang or P.DECLINE_FALLBACK["lang"],
        "column": args.column or P.DECLINE_FALLBACK["column"],
        "format": ("pdf" if args.pdf else "eps" if args.eps else (args.format or "html")),
        "stage": args.stage,
    }
    return {"missing": None, "declined": declined, "values": values}


def validate_values(values):
    bad = []
    if values["preset"] not in P.VISUAL_PRESETS:
        bad.append("preset=%r（合法：%s）" % (values["preset"], ", ".join(P.VISUAL_PRESETS)))
    if values["motion"] not in P.MOTIONS:
        bad.append("motion=%r（合法：%s）" % (values["motion"], ", ".join(P.MOTIONS)))
    if values["lang"] not in P.LANGS:
        bad.append("lang=%r（合法：%s）" % (values["lang"], ", ".join(P.LANGS)))
    if values["column"] not in P.COLUMNS:
        bad.append("column=%r（合法：%s）" % (values["column"], ", ".join(P.COLUMNS)))
    if values["format"] not in P.FORMATS:
        bad.append("format=%r（合法：%s）" % (values["format"], ", ".join(P.FORMATS)))
    if values["stage"] not in P.STAGES:
        bad.append("stage=%r（合法：%s）" % (values["stage"], ", ".join(P.STAGES)))
    return bad


# ─────────────────────────── render 主流程 ───────────────────────────

def build_spec_from_template(diag_type, values, paper_title):
    """读骨架并按必问项答案填充 meta；返回 (spec dict, 来源路径)。"""
    src = os.path.join(TEMPLATES_DIR, diag_type + ".json")
    if not os.path.exists(src):
        die("缺少 %s 的 spec 骨架：%s" % (diag_type, src), 1)
    spec = json.loads(open(src, "rb").read().decode("utf-8"))
    meta = spec.setdefault("meta", {})
    meta["locale"] = values["lang"]
    meta["visual_preset"] = values["preset"]
    meta["motion"] = values["motion"]
    meta["column"] = values["column"]
    meta["quality_profile"] = "showcase"
    meta["language"] = {"mode": "zh-CN" if values["lang"] == "zh-CN" else "off"}
    if paper_title:
        meta["subtitle"] = meta.get("subtitle", "") + ("｜论文：%s" % paper_title)
    return spec, src


def write_spec(spec, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(json.dumps(spec, ensure_ascii=False, indent=2).encode("utf-8"))
    return dest


def cmd_render(args):
    root = os.path.abspath(args.root)
    node = find_node()
    if not node:
        die("未找到 node。论文插图内核需要 Node >= 18：https://nodejs.org/ 安装后重开终端。", 1)
    if args.type not in P.DIAGRAM_TYPES:
        die("未知图类型 %r（合法：%s）" % (args.type, ", ".join(P.DIAGRAM_TYPES)), 2)

    chk = check_ask_items(args, args.type)
    if chk.get("missing") is not None:
        for line in chk["lines"]:
            sys.stderr.write(line + "\n")
        sys.exit(2)
    declined, values = chk["declined"], chk["values"]
    bad = validate_values(values)
    if bad:
        die("；".join(bad), 2)

    paper_title = read_paper_title(root)
    if args.spec:
        spec_path = os.path.abspath(args.spec)
        spec = json.loads(open(spec_path, "rb").read().decode("utf-8-sig"))
        src = spec_path
    else:
        spec, src = build_spec_from_template(args.type, values, paper_title)

    gate_name = P.GATES[args.type]
    gate_res = G.run_gate(gate_name, values["stage"], root)
    if not gate_res.ok:
        sys.stderr.write("figures: 门禁拒绝（%s / %s）\n  %s\n" %
                         (args.type, gate_name, gate_res.blocked_reason))
        sys.exit(1)

    mf = MF.load(root)
    fig_id = "fig-" + args.type
    rec = MF.get(mf, fig_id)
    spec_sha = ST.sha256_bytes(json.dumps(spec, ensure_ascii=False, indent=2).encode("utf-8"))
    stage, st_note = ST.resolve_stage(values["stage"], rec, spec_sha)

    if args.code_verified and values["stage"] == "final" and gate_name == "soft_code_verified":
        gate_res = G.GateResult(ok=True, note="用户已显式确认代码跑通（--code-verified）")

    if gate_res.stage_cap and ST.stage_rank(stage) > ST.stage_rank(gate_res.stage_cap):
        stage = gate_res.stage_cap

    title_suffix = gate_res.label_suffix or ST.STAGE_LABEL_SUFFIX.get(stage, "")
    if title_suffix:
        spec["meta"]["title"] = ST.title_with_stage(spec["meta"]["title"], stage, title_suffix)
    spec["meta"]["motion"] = values["motion"]
    spec["meta"]["column"] = values["column"]
    spec["meta"]["visual_preset"] = values["preset"]

    spec_dest = os.path.join(root, SPECS_REL, args.type + ".json")
    write_spec(spec, spec_dest)

    out_html = os.path.join(root, OUT_REL, args.type + ".html")
    os.makedirs(os.path.dirname(out_html), exist_ok=True)

    kargs = ["deliver", args.type, spec_dest, out_html, "--quality", "showcase", "--json"]
    if values["motion"]:
        kargs += ["--motion", values["motion"]]
    code, out, err = run_kernel(kargs, node)
    result = parse_json_loose(out) or parse_json_loose(err)
    if code != 0 or not result or not result.get("ok"):
        sys.stderr.write("figures: 内核渲染失败（exit=%d）\n" % code)
        for d in (result or {}).get("diagnostics") or []:
            sys.stderr.write("  [%s] %s: %s — %s\n" % (d.get("severity"), d.get("rule"),
                                                       d.get("subject"), d.get("evidence")))
        if not result:
            sys.stderr.write(err[-1200:] + "\n")
        sys.exit(1)

    checks = result.get("checks") or {}
    rec = {
        "id": fig_id,
        "type": args.type,
        "stage": stage,
        "gate": gate_name,
        "spec": os.path.relpath(spec_dest, root).replace("\\", "/"),
        "output_html": os.path.relpath(out_html, root).replace("\\", "/"),
        "output_pdf": None,
        "quality": "showcase",
        "checks": {"passed": int(checks.get("total", 11)) - int(checks.get("errors", 0)) - int(checks.get("warnings", 0)),
                   "total": int(checks.get("total", 11)),
                   "errors": int(checks.get("errors", 0)),
                   "warnings": int(checks.get("warnings", 0))},
        "sha256": {"spec": (result.get("spec") or {}).get("sha256", spec_sha),
                   "html": (result.get("html") or {}).get("sha256", "")},
        # spec_sha256 是"内容身份"：不含量级标题后缀的 spec 摘要，供状态机判断 spec 是否被改过
        "spec_sha256": spec_sha,
        "data_source": (os.path.join(DATA_REL, "experiment_counts.json").replace("\\", "/")
                        if gate_name == "requires_experiment_data" and values["stage"] == "final" else None),
        "label_suffix": title_suffix or None,
        "declined": declined,
        "notes": [n for n in [gate_res.note, st_note] if n],
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    }
    mf["global_motion"] = values["motion"]
    if not MF.get(mf, fig_id):
        mf.setdefault("figures", []).append(rec)
    else:
        MF.put(mf, rec)
    errs = MF.validate(mf)
    if errs:
        die("manifest 校验失败：" + "；".join(errs), 1)
    MF.save(root, mf)

    notes = []
    notes += P.declined_notes(declined)
    if values["format"] in ("pdf", "eps"):
        notes.append("输出格式 %s：内核尚未实现（Phase 2 桩），本次交付自包含 HTML；"
                     "PDF/EPS 可由该 HTML 经浏览器打印获得" % values["format"])
    if gate_res.stage_cap:
        notes.append(gate_res.note or "")
    if st_note:
        notes.append(st_note)
    notes += [gate_res.note] if gate_res.note and not gate_res.stage_cap else []

    if getattr(args, "json", False):
        print(json.dumps({"ok": True, "root": root, "figure": rec,
                          "notes": [n for n in notes if n],
                          "limits": KNOWN_LIMITS}, ensure_ascii=False, indent=2))
        return 0

    print("✅ %s 已交付（%s / %s）" % (P.DIAGRAM_TYPES_CN[args.type], args.type, stage))
    print("   HTML : %s（%.1f KB，字体子集已内嵌，可离线打开）" %
          (os.path.relpath(out_html, root), os.path.getsize(out_html) / 1024.0))
    print("   检查 : %d/%d 通过，errors=%d，warnings=%d" %
          (rec["checks"]["passed"], rec["checks"]["total"], rec["checks"]["errors"], rec["checks"]["warnings"]))
    print("   收据 : spec sha256=%s… / html sha256=%s…" %
          (rec["sha256"]["spec"][:12], rec["sha256"]["html"][:12]))
    if notes:
        print("   说明 :")
        for n in notes:
            if n:
                print("     - " + n)
    print("   门禁 : %s（本图 %s）" % (gate_name, stage))
    return 0


def read_paper_title(root):
    p = os.path.join(root, "analysis", "literature_reading.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.loads(open(p, "rb").read().decode("utf-8"))
    except Exception:
        return ""
    for k in ("paper_title", "title", "paper"):
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


# ─────────────────────── init-reading / route-draft / supplement ───────────────────────

def cmd_init_reading(args):
    """Phase 1.5：阅读阶段默认产出三张 —— framework(final) + route(draft) + structure(final)。"""
    total = 0
    for t, stage in (("framework", "final"), ("route", "draft"), ("structure", "final")):
        ns = argparse.Namespace(**{**vars(args), "type": t, "stage": stage,
                                   "spec": None, "code_verified": False, "force_rewrite": False})
        code = cmd_render(ns)
        total += code
        if code != 0:
            return code
    return 0


def cmd_route_draft(args):
    ns = argparse.Namespace(**{**vars(args), "type": "route", "stage": "draft",
                               "spec": None, "code_verified": False, "force_rewrite": False})
    return cmd_render(ns)


def cmd_route_supplement(args):
    """Phase 4.0：已有路线图 → 追加模式（方案 §7）。禁删节点、禁改主路径方向、新边必须带 label。"""
    root = os.path.abspath(args.root)
    mf = MF.load(root)
    rec = MF.get(mf, "fig-route")
    if rec is None:
        sys.stderr.write("figures: 尚无技术路线图，请先 route-draft 出初稿（补充模式只对已有初稿生效）。\n")
        sys.exit(1)
    old_spec_path = os.path.join(root, rec["spec"])
    if not os.path.exists(old_spec_path):
        sys.stderr.write("figures: 已登记的路线图 spec 不存在：%s\n" % rec["spec"])
        sys.exit(1)
    old = json.loads(open(old_spec_path, "rb").read().decode("utf-8-sig"))
    new = json.loads(open(os.path.abspath(args.spec), "rb").read().decode("utf-8-sig"))

    old_ids = [m["id"] for m in old.get("modules") or []]
    new_ids = [m["id"] for m in new.get("modules") or []]
    problems = []
    removed = [i for i in old_ids if i not in new_ids]
    if removed and not args.force_rewrite:
        problems.append("删除了既有节点：%s（补充模式禁删；需重画请显式 --force-rewrite）" % "、".join(removed))

    def conn_pairs(spec):
        return set((c["from"], c["to"]) for c in (spec.get("connections") or []))

    old_pairs, new_pairs = conn_pairs(old), conn_pairs(new)
    lost = old_pairs - new_pairs
    if lost and not args.force_rewrite:
        problems.append("删除/改向了既有连线：%s（主路径不得改向）" %
                        "、".join("%s→%s" % p for p in sorted(lost)))

    added_labels = []
    for c in (new.get("connections") or []):
        pair = (c.get("from"), c.get("to"))
        if pair not in old_pairs:
            if not (c.get("label") or "").strip():
                problems.append("新增连线 %s→%s 缺少 label（结果标注要写清是什么结果）" % pair)
            else:
                added_labels.append("%s→%s（%s）" % (c["from"], c["to"], c["label"]))

    if problems and not args.force_rewrite:
        sys.stderr.write("figures: 补充模式校验未通过\n")
        for p in problems:
            sys.stderr.write("  - %s\n" % p)
        sys.stderr.write("补充模式只允许追加；需重画请显式 --force-rewrite。\n")
        sys.exit(1)

    sys.stderr.write("figures: 补充模式%s\n" % ("（--force-rewrite 显式重画）" if args.force_rewrite else "校验通过"))
    for a in added_labels:
        sys.stderr.write("  + 新增结果连线：%s\n" % a)
    ns = argparse.Namespace(**{**vars(args), "type": "route", "stage": None, "spec": args.spec,
                               "code_verified": False, "force_rewrite": args.force_rewrite})
    if ns.stage is None:
        ns.stage = (MF.get(MF.load(root), "fig-route") or {}).get("stage", "draft")
    return cmd_render(ns)


# ─────────────────────────── 参数解析 ───────────────────────────

def build_parser():
    ap = argparse.ArgumentParser(prog="figures.py",
                                 description="math-read-do 论文插图（六类图）唯一入口")
    ap.add_argument("--root", default=".", help="工作目录（figures/ 的父目录，默认当前目录）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("list", help="列出六类图与状态")
    sub.add_parser("doctor", help="检查渲染内核环境（Node/schema/字体子集）")

    pr = sub.add_parser("render", help="渲染一类图")
    pr.add_argument("type", nargs="?", default=None, help="framework|route|model|system|structure|experiment")
    pr.add_argument("--spec", help="自定义 spec 路径（默认用内置骨架）")
    pr.add_argument("--stage", help="draft|confirmed|final")
    pr.add_argument("--preset", help="视觉预设（10 种，见 figuregen.presets）")
    pr.add_argument("--motion", help="off|hover|flow|tour")
    pr.add_argument("--lang", help="zh-CN|en")
    pr.add_argument("--column", help="single|double")
    pr.add_argument("--format", help="html|pdf|eps")
    pr.add_argument("--pdf", action="store_true", help="等价 --format pdf")
    pr.add_argument("--eps", action="store_true", help="等价 --format eps")
    pr.add_argument("--quality", choices=["standard", "showcase"], default="showcase")
    pr.add_argument("--declined", help="用户明确弃权的必问项（逗号分隔）")
    pr.add_argument("--code-verified", action="store_true", help="用户确认代码已跑通（soft 门禁放行 final）")
    pr.add_argument("--force-rewrite", action="store_true", help="补充模式下显式重画（绕过追加校验）")
    pr.add_argument("--out", help="输出 HTML 路径（默认 figures/out/<type>.html）")

    for name, help_text in (("init-reading", "Phase 1.5：默认产出 framework(final)+route(draft)+structure(final)"),
                            ("route-draft", "Phase 4.0：出技术路线图初稿")):
        p2 = sub.add_parser(name, help=help_text)
        p2.add_argument("reading", nargs="?", help="analysis/literature_reading.json（可选）")
        p2.add_argument("--preset"); p2.add_argument("--motion"); p2.add_argument("--lang")
        p2.add_argument("--column"); p2.add_argument("--format")
        p2.add_argument("--pdf", action="store_true"); p2.add_argument("--eps", action="store_true")
        p2.add_argument("--quality", choices=["standard", "showcase"], default="showcase")
        p2.add_argument("--declined"); p2.add_argument("--out")

    p3 = sub.add_parser("route-supplement", help="Phase 4.0：路线图补充模式（禁删节点/禁改主路径）")
    p3.add_argument("delta", nargs="?", help="implementation/delta_report.json（可选）")
    p3.add_argument("--spec", required=True, help="补充后的新 spec 路径")
    p3.add_argument("--preset"); p3.add_argument("--motion"); p3.add_argument("--lang")
    p3.add_argument("--column"); p3.add_argument("--format")
    p3.add_argument("--pdf", action="store_true"); p3.add_argument("--eps", action="store_true")
    p3.add_argument("--quality", choices=["standard", "showcase"], default="showcase")
    p3.add_argument("--declined"); p3.add_argument("--force-rewrite", action="store_true"); p3.add_argument("--out")
    return ap


def add_missing_common_fields(args):
    if not hasattr(args, "preset"):
        args.preset = None
    if not hasattr(args, "motion"):
        args.motion = None
    if not hasattr(args, "lang"):
        args.lang = None
    if not hasattr(args, "column"):
        args.column = None
    if not hasattr(args, "format"):
        args.format = None
    if not hasattr(args, "pdf"):
        args.pdf = False
    if not hasattr(args, "eps"):
        args.eps = False
    if not hasattr(args, "declined"):
        args.declined = None
    if not hasattr(args, "code_verified"):
        args.code_verified = False
    if not hasattr(args, "force_rewrite"):
        args.force_rewrite = False
    if not hasattr(args, "quality"):
        args.quality = "showcase"
    if not hasattr(args, "out"):
        args.out = None
    if not hasattr(args, "spec"):
        args.spec = None
    if not hasattr(args, "stage"):
        args.stage = None
    if not hasattr(args, "type"):
        args.type = None
    return args


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    args = add_missing_common_fields(args)
    if not getattr(args, "cmd", None):
        ap.print_help()
        return 0
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "doctor":
        return cmd_doctor(args)
    if args.cmd == "render":
        if not args.type:
            die("render 需要图类型（framework|route|model|system|structure|experiment）", 2)
        return cmd_render(args)
    if args.cmd == "init-reading":
        return cmd_init_reading(args)
    if args.cmd == "route-draft":
        return cmd_route_draft(args)
    if args.cmd == "route-supplement":
        return cmd_route_supplement(args)
    die("未知子命令 %r" % args.cmd, 2)


if __name__ == "__main__":
    sys.exit(main())
