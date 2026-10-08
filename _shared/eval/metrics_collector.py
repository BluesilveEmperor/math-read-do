#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指标采集器：采集四分支量化指标并汇总到 dashboard.json。

采集指标：
    - 首响 token   : 主 SKILL.md 加载体积（字节数）
    - QEM 吞吐     : 运行 benchmark_qem.py 并解析输出（面/秒）
    - 测试覆盖率   : 运行 pytest --cov --cov-report=json 并解析行覆盖率
    - 跨分支一致性 : diff 四分支 SKILL.md 关键段（首部 frontmatter + 触发词）

用法::

    python -m _shared.eval.metrics_collector --branch obj
    python -m _shared.eval.metrics_collector --branch obj --output dashboard.json

所有外部命令失败均优雅降级为 ``status: "unavailable"``，不中断采集。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── 路径常量 ──────────────────────────────────────────────
EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parents[1]                       # 仓库根
REPORT_DIR = EVAL_DIR / "report"                      # 报告输出目录
DEFAULT_OUTPUT = REPORT_DIR / "dashboard.json"

# 四分支 worktree 常见路径（用于跨分支一致性 diff）
BRANCH_WORKTREES: dict[str, Path] = {
    "obj": REPO_ROOT,
    "main": REPO_ROOT.parent / "wt-main",
    "routine": REPO_ROOT.parent / "wt-routine",
    "financial": REPO_ROOT.parent / "wt-financial",
}


# ════════════════════════════════════════════════════════
#  指标采集函数
# ════════════════════════════════════════════════════════
def collect_first_token(branch: str, repo: Path = REPO_ROOT) -> dict[str, Any]:
    """采集首响 token：主 SKILL.md 的字节数与行数。

    Returns:
        ``{bytes, lines, status}``
    """
    skill_path = repo / "SKILL.md"
    if not skill_path.is_file():
        return {"bytes": None, "lines": None, "status": "SKILL.md 不存在"}
    try:
        text = skill_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"bytes": None, "lines": None, "status": f"读取失败: {exc}"}
    return {
        "bytes": len(text.encode("utf-8")),
        "lines": text.count("\n") + 1,
        "status": "ok",
    }


def collect_qem_throughput(branch: str, repo: Path = REPO_ROOT) -> dict[str, Any]:
    """采集 QEM 简化吞吐：运行 benchmark_qem.py 并解析输出。

    仅对 obj 分支有意义；其他分支返回 ``status: "skipped"``。

    Returns:
        ``{faces_per_sec, elapsed, raw_output, status}``
    """
    if branch != "obj":
        return {"faces_per_sec": None, "elapsed": None, "status": "skipped"}

    bench = repo / "scripts" / "benchmark_qem.py"
    if not bench.is_file():
        return {"faces_per_sec": None, "elapsed": None, "status": "benchmark_qem.py 不存在"}

    try:
        proc = subprocess.run(
            [sys.executable, str(bench)],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"faces_per_sec": None, "elapsed": None, "status": "超时（>120s）"}
    except Exception as exc:  # noqa: BLE001
        return {"faces_per_sec": None, "elapsed": None, "status": f"执行失败: {exc}"}

    raw = proc.stdout + proc.stderr
    # 尝试从输出中解析面/秒（兼容多种格式：faces/s, 面/秒, throughput）
    fps = _parse_throughput(raw)
    return {
        "faces_per_sec": fps,
        "elapsed": None,
        "raw_output": raw.strip()[:500] if raw else "",
        "status": "ok" if fps is not None else "解析失败",
    }


def _parse_throughput(text: str) -> float | None:
    """从 benchmark 输出文本中提取吞吐数值（面/秒）。"""
    # 匹配 "1234.5 faces/s" / "1234.5 面/秒" / "throughput: 1234.5"
    patterns = [
        r"([\d.]+)\s*faces/s",
        r"([\d.]+)\s*面/秒",
        r"throughput\s*[:=]\s*([\d.]+)",
        r"([\d.]+)\s*faces\s*/\s*s",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                continue
    return None


def collect_coverage(branch: str, repo: Path = REPO_ROOT) -> dict[str, Any]:
    """采集测试覆盖率：运行 pytest --cov 并解析 JSON 报告。

    Returns:
        ``{line_rate, num_statements, num_missing, status}``
    """
    cov_json = repo / "coverage.json"
    # 先尝试运行 pytest
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "--cov", "--cov-report=json",
             "-q", "--no-header", "-p", "no:cacheprovider"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {"line_rate": None, "status": "pytest 超时（>180s）"}
    except Exception as exc:  # noqa: BLE001
        return {"line_rate": None, "status": f"pytest 执行失败: {exc}"}

    # 解析 coverage.json
    if not cov_json.is_file():
        return {"line_rate": None, "status": "coverage.json 未生成（可能无测试或 pytest 未安装）"}

    try:
        with open(cov_json, encoding="utf-8") as f:
            cov = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {"line_rate": None, "status": f"coverage.json 解析失败: {exc}"}

    totals = cov.get("totals", {})
    line_rate = totals.get("percent_covered")
    if line_rate is None:
        line_rate = totals.get("line_rate")
        if line_rate is not None:
            line_rate = round(line_rate * 100, 2)
    return {
        "line_rate": round(line_rate, 2) if line_rate is not None else None,
        "num_statements": totals.get("num_statements"),
        "num_missing": totals.get("missing_lines"),
        "status": "ok",
    }


def collect_cross_branch_consistency() -> dict[str, Any]:
    """采集跨分支一致性：diff 四分支 SKILL.md 的关键段。

    比较各分支 SKILL.md 的 frontmatter（name/description）与触发词段，
    检测是否存在分叉。worktree 不存在的分支标记为 ``status: "worktree 不存在"``。

    Returns:
        ``{branches_checked, frontmatter_diff, trigger_diff, status}``
    """
    results: dict[str, Any] = {"branches_checked": {}, "status": "ok"}

    # 提取各分支 SKILL.md 的关键段
    segments: dict[str, dict[str, str | None]] = {}
    for bname, wpath in BRANCH_WORKTREES.items():
        skill = wpath / "SKILL.md"
        if not skill.is_file():
            results["branches_checked"][bname] = "worktree 不存在"
            continue
        try:
            text = skill.read_text(encoding="utf-8", errors="replace")
        except OSError:
            results["branches_checked"][bname] = "读取失败"
            continue
        results["branches_checked"][bname] = f"{len(text.encode('utf-8'))} bytes"
        segments[bname] = {
            "frontmatter": _extract_frontmatter(text),
            "triggers": _extract_triggers(text),
        }

    # 比较关键段：以 obj 为基准，检测其他分支是否一致
    base = segments.get("obj")
    if base is None:
        results["status"] = "obj 基准缺失，无法比较"
        return results

    frontmatter_diff: dict[str, bool] = {}
    trigger_diff: dict[str, bool] = {}
    for bname, seg in segments.items():
        if bname == "obj":
            continue
        frontmatter_diff[bname] = seg["frontmatter"] != base["frontmatter"]
        trigger_diff[bname] = seg["triggers"] != base["triggers"]

    results["frontmatter_diff"] = frontmatter_diff
    results["trigger_diff"] = trigger_diff
    return results


def _extract_frontmatter(text: str) -> str | None:
    """提取 SKILL.md 的 YAML frontmatter（首个 ``---`` 块）。"""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end].strip()


def _extract_triggers(text: str) -> str | None:
    """提取 SKILL.md 的 Triggers/触发词段。"""
    m = re.search(r"(Triggers\s*/\s*触发词.*?)(?:\n---|\n## |\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else None


# ════════════════════════════════════════════════════════
#  汇总采集
# ════════════════════════════════════════════════════════
def collect_all(branch: str, repo: Path = REPO_ROOT) -> dict[str, Any]:
    """采集指定分支的全部指标并汇总。

    Returns:
        包含各指标子字典的汇总字典。
    """
    return {
        "branch": branch,
        "first_token": collect_first_token(branch, repo),
        "qem_throughput": collect_qem_throughput(branch, repo),
        "coverage": collect_coverage(branch, repo),
        "cross_branch_consistency": collect_cross_branch_consistency(),
    }


# ════════════════════════════════════════════════════════
#  命令行入口
# ════════════════════════════════════════════════════════
def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="python -m _shared.eval.metrics_collector",
        description="指标采集器：采集首响 token / QEM 吞吐 / 覆盖率 / 跨分支一致性",
    )
    parser.add_argument(
        "--branch", default="obj",
        help="目标分支（main/routine/financial/obj），默认 obj",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help=f"输出 JSON 路径；缺省为 {DEFAULT_OUTPUT.relative_to(REPO_ROOT)}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """命令行入口，返回退出码。"""
    args = build_parser().parse_args(argv)
    dashboard = collect_all(args.branch)

    output_path = Path(args.output).resolve() if args.output else DEFAULT_OUTPUT
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"指标已写入 {output_path}", file=sys.stderr)
    # 同时打印简要摘要到 stdout
    ft = dashboard["first_token"]
    cov = dashboard["coverage"]
    qem = dashboard["qem_throughput"]
    print(f"[{args.branch}] 首响 token: {ft['bytes']} bytes | "
          f"覆盖率: {cov.get('line_rate')}% | "
          f"QEM 吞吐: {qem.get('faces_per_sec')} faces/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())