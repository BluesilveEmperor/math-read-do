#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Phase 1 数据可得性分诊脚本 / Data Availability Triage.

将 SKILL.md 中 Phase 1 的散文式分诊流程代码化，使"数据先行"原则可执行、可回归。

输入：论文元数据 JSON（标题 / URL / 数据源列表）
输出：results/triage_report.json（每个数据源标记 available / needs_auth / missing + 建议）

用法:
    python scripts/data_triage.py --paper paper.json
    python scripts/data_triage.py --paper paper.json --output results/triage_report.json

数据源类型 (data_sources[].type):
    url       — 公开 URL，发 HTTP HEAD 探测可达性
    file      — 本地文件路径，检查是否存在
    licensed  — 商业授权数据（CRSP/WRDS/Bloomberg/ICAP），标记 needs_auth
    absent    — 论文与仓库均未提供，标记 missing
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

# 三态标记，与 SKILL.md Phase 1 的 open/licensed/absent 对齐
STATUS_AVAILABLE = "available"      # 公开可下载
STATUS_NEEDS_AUTH = "needs_auth"   # 商业授权，需凭证
STATUS_MISSING = "missing"         # 缺失，无法获取

# 处置建议（与 SKILL.md Phase 1 表格一致）
SUGGESTIONS = {
    STATUS_AVAILABLE: "公开可下载，正常复现，可与论文数值直接比对",
    STATUS_NEEDS_AUTH: "商业授权数据，生成合成替代（GBM/Heston），判决降级为 skip",
    STATUS_MISSING: "数据缺失，标记 skip，不启动训练",
}

# URL 探测超时（秒）；网络不可达时降级为 missing，不阻塞流程
_URL_TIMEOUT = 5.0


def _check_url(location: str) -> tuple[str, str]:
    """探测 URL 可达性，返回 (status, detail)。网络不可达时降级为 missing。"""
    try:
        req = urllib.request.Request(location, method="HEAD",
                                     headers={"User-Agent": "data_triage/1.0"})
        with urllib.request.urlopen(req, timeout=_URL_TIMEOUT) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return STATUS_AVAILABLE, f"HTTP HEAD {code} — 可达"
            return STATUS_MISSING, f"HTTP HEAD {code} — 异常状态码"
    except urllib.error.HTTPError as e:
        # 401/403 → 需授权；其他 HTTP 错误 → missing
        if e.code in (401, 403):
            return STATUS_NEEDS_AUTH, f"HTTP {e.code} — 需授权"
        return STATUS_MISSING, f"HTTP {e.code} — 不可达"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return STATUS_MISSING, f"网络不可达: {e}"


def _check_file(location: str) -> tuple[str, str]:
    """检查本地文件是否存在，返回 (status, detail)。"""
    if os.path.isfile(location):
        size = os.path.getsize(location)
        return STATUS_AVAILABLE, f"本地存在，{size} 字节"
    return STATUS_MISSING, f"本地不存在: {location}"


def _triage_source(src: dict[str, Any]) -> dict[str, Any]:
    """对单个数据源执行分诊，返回带 status/detail/suggestion 的记录。"""
    name = src.get("name", "unknown")
    src_type = src.get("type", "unknown")
    location = src.get("location", "")

    # licensed / absent 直接判定，无需探测
    if src_type == "licensed":
        status, detail = STATUS_NEEDS_AUTH, "商业授权数据，需凭证获取"
    elif src_type == "absent":
        status, detail = STATUS_MISSING, "论文与仓库均未提供"
    elif src_type == "url":
        status, detail = _check_url(location)
    elif src_type == "file":
        status, detail = _check_file(location)
    else:
        # 未知类型 → missing，避免误判为可用
        status, detail = STATUS_MISSING, f"未知数据源类型: {src_type}"

    return {
        "name": name,
        "type": src_type,
        "location": location,
        "status": status,
        "detail": detail,
        "suggestion": SUGGESTIONS[status],
    }


def run_triage(paper: dict[str, Any]) -> dict[str, Any]:
    """对论文元数据执行完整分诊，返回 triage_report 字典。"""
    sources = paper.get("data_sources", [])
    triaged = [_triage_source(s) for s in sources]

    summary = {
        STATUS_AVAILABLE: sum(1 for t in triaged if t["status"] == STATUS_AVAILABLE),
        STATUS_NEEDS_AUTH: sum(1 for t in triaged if t["status"] == STATUS_NEEDS_AUTH),
        STATUS_MISSING: sum(1 for t in triaged if t["status"] == STATUS_MISSING),
    }

    return {
        "title": paper.get("title", ""),
        "url": paper.get("url", ""),
        "triaged_at": datetime.now(timezone.utc).isoformat(),
        "sources": triaged,
        "summary": summary,
    }


def main(argv: list[str] | None = None) -> int:
    """命令行入口，返回退出码。"""
    parser = argparse.ArgumentParser(
        description="Phase 1 数据可得性分诊 / Data Availability Triage")
    parser.add_argument("--paper", required=True,
                        help="论文元数据 JSON 路径")
    parser.add_argument("--output", default="results/triage_report.json",
                        help="分诊报告输出路径（默认 results/triage_report.json）")
    args = parser.parse_args(argv)

    # 读取论文元数据
    if not os.path.isfile(args.paper):
        print(f"错误: 论文元数据文件不存在: {args.paper}", file=sys.stderr)
        return 1
    with open(args.paper, "r", encoding="utf-8") as f:
        paper = json.load(f)

    # 执行分诊
    report = run_triage(paper)

    # 落盘
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 摘要输出到 stdout
    print(f"分诊完成: {report['title']}")
    print(f"  available: {report['summary'][STATUS_AVAILABLE]}")
    print(f"  needs_auth: {report['summary'][STATUS_NEEDS_AUTH]}")
    print(f"  missing: {report['summary'][STATUS_MISSING]}")
    print(f"  报告已写入: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())