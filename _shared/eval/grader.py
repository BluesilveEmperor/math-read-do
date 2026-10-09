#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""评分器：按 assertions[] + rubric 对评测用例机判。

工作流：
    1. 加载 ``test-prompts.json``，按分支过滤用例
    2. 对每例：跑 skill（subprocess）→ 收集产物 → 逐条 assertions 断言 → rubric 加权打分
    3. 输出每例 ``{case_id, passed, score, evidence}`` 及汇总统计

用法::

    # 默认 dry-run 模式：不实际执行 skill，仅对已有产物做断言
    python -m _shared.eval.grader --branch obj

    # 执行模式：通过 subprocess 调用 skill 命令
    python -m _shared.eval.grader --branch obj --execute --skill-cmd "python cli.py"

    # 指定产物根目录与输出文件
    python -m _shared.eval.grader --branch obj --workdir ./results --output report.json

断言类型：
    - ``file_exists``  : 检查文件是否存在
    - ``json_field``   : 加载 JSON，检查字段值在指定集合中
    - ``exit_code``    : 检查子进程退出码
    - ``text_contains``: 检查输出文本包含子串
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ── 路径常量 ──────────────────────────────────────────────
EVAL_DIR = Path(__file__).resolve().parent          # _shared/eval/
TEST_PROMPTS = EVAL_DIR / "test-prompts.json"        # 统一评测集
# 仓库根：_shared/eval → _shared → 仓库根（parents[1]）
REPO_ROOT = EVAL_DIR.parents[1]


# ════════════════════════════════════════════════════════
#  数据加载
# ════════════════════════════════════════════════════════
def load_cases(branch: str | None = None) -> list[dict[str, Any]]:
    """加载评测用例，可按分支过滤。

    Args:
        branch: 分支名（main/routine/financial/obj），None 表示加载全部。

    Returns:
        用例字典列表，每个含 id/branch/prompt/expected/assertions/rubric 等字段。
    """
    with open(TEST_PROMPTS, encoding="utf-8") as f:
        cases = json.load(f)
    if branch is not None:
        cases = [c for c in cases if c.get("branch") == branch]
    return cases


# ════════════════════════════════════════════════════════
#  Skill 执行
# ════════════════════════════════════════════════════════
def run_skill(
    prompt: str,
    skill_cmd: str | None = None,
    workdir: Path | None = None,
    timeout: int = 300,
    execute: bool = False,
) -> dict[str, Any]:
    """通过 subprocess 运行 skill（模拟触发）。

    Args:
        prompt:    用户提示词。
        skill_cmd: 实际执行的命令模板（含 ``{prompt}`` 占位符）。
        workdir:   子进程工作目录。
        timeout:   子进程超时秒数。
        execute:   是否真正执行 subprocess；False 时返回模拟结果（dry-run）。

    Returns:
        执行上下文字典，含 exit_code / stdout / stderr / elapsed。
    """
    cwd = str(workdir) if workdir else str(REPO_ROOT)

    if not execute or not skill_cmd:
        # dry-run：不调用外部进程，假定成功退出
        return {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "elapsed": 0.0,
            "mode": "dry-run",
        }

    # 组装命令：将 {prompt} 替换为实际提示词
    cmd = skill_cmd.replace("{prompt}", prompt)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed": round(elapsed, 3),
            "mode": "execute",
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"超时（>{timeout}s）",
            "elapsed": float(timeout),
            "mode": "timeout",
        }
    except Exception as exc:  # noqa: BLE001 — 采集所有异常供诊断
        return {
            "exit_code": -2,
            "stdout": "",
            "stderr": str(exc),
            "elapsed": 0.0,
            "mode": "error",
        }


# ════════════════════════════════════════════════════════
#  断言检查器
# ════════════════════════════════════════════════════════
def _resolve_path(path_str: str, workdir: Path | None) -> Path:
    """将断言中的相对路径解析为绝对路径。

    优先相对于 workdir，其次相对于仓库根。
    """
    p = Path(path_str)
    if p.is_absolute():
        return p
    base = workdir if workdir else REPO_ROOT
    return base / p


def check_file_exists(assertion: dict[str, Any], ctx: dict[str, Any]) -> bool:
    """断言：文件存在。"""
    path = _resolve_path(assertion["path"], ctx.get("workdir"))
    return path.is_file()


def check_json_field(assertion: dict[str, Any], ctx: dict[str, Any]) -> bool:
    """断言：JSON 文件中指定字段的值在给定集合内。

    assertion 字段：
        - path:  JSON 文件路径
        - field: 要检查的字段名
        - in:    允许值列表（可选；若缺省则仅检查字段存在）
    """
    path = _resolve_path(assertion["path"], ctx.get("workdir"))
    if not path.is_file():
        return False
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    field = assertion["field"]
    if field not in data:
        return False
    allowed = assertion.get("in")
    if allowed is None:
        return True  # 仅检查字段存在
    return data[field] in allowed


def check_exit_code(assertion: dict[str, Any], ctx: dict[str, Any]) -> bool:
    """断言：子进程退出码等于期望值。"""
    expected = assertion.get("eq", 0)
    return ctx.get("exit_code") == expected


def check_text_contains(assertion: dict[str, Any], ctx: dict[str, Any]) -> bool:
    """断言：文本文件或 stdout 包含指定子串。

    assertion 字段：
        - path:   文件路径（可选；若缺省则检查 stdout）
        - needle: 要查找的子串
    """
    needle = assertion["needle"]
    path_str = assertion.get("path")
    if path_str:
        path = _resolve_path(path_str, ctx.get("workdir"))
        if not path.is_file():
            return False
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
    else:
        text = ctx.get("stdout", "")
    return needle in text


# 断言类型 → 检查函数的分发表
ASSERTION_CHECKERS: dict[str, Any] = {
    "file_exists": check_file_exists,
    "json_field": check_json_field,
    "exit_code": check_exit_code,
    "text_contains": check_text_contains,
}


# ════════════════════════════════════════════════════════
#  用例评估
# ════════════════════════════════════════════════════════
def evaluate_case(
    case: dict[str, Any],
    skill_cmd: str | None = None,
    workdir: Path | None = None,
    timeout: int = 300,
    execute: bool = False,
) -> dict[str, Any]:
    """评估单个用例：跑 skill → 逐条断言 → rubric 加权打分。

    Returns:
        ``{case_id, branch, passed, score, evidence, assertions_detail}``
    """
    # 1. 执行 skill，收集上下文
    run_ctx = run_skill(
        prompt=case["prompt"],
        skill_cmd=skill_cmd,
        workdir=workdir,
        timeout=timeout,
        execute=execute,
    )
    ctx: dict[str, Any] = {
        "exit_code": run_ctx["exit_code"],
        "stdout": run_ctx["stdout"],
        "stderr": run_ctx["stderr"],
        "workdir": workdir,
    }

    # 2. 逐条断言求值
    assertions = case.get("assertions", [])
    assertion_results: list[dict[str, Any]] = []
    for i, a in enumerate(assertions):
        checker = ASSERTION_CHECKERS.get(a["type"])
        if checker is None:
            assertion_results.append({
                "index": i,
                "type": a["type"],
                "passed": False,
                "error": f"未知断言类型: {a['type']}",
            })
            continue
        try:
            passed = bool(checker(a, ctx))
        except Exception as exc:  # noqa: BLE001
            passed = False
            assertion_results.append({
                "index": i,
                "type": a["type"],
                "passed": False,
                "error": str(exc),
            })
            continue
        assertion_results.append({
            "index": i,
            "type": a["type"],
            "passed": passed,
        })

    all_passed = all(r["passed"] for r in assertion_results) if assertion_results else True

    # 3. rubric 加权打分
    #    每项 rubric 可通过 "assertion_index" 关联到具体断言；
    #    若未指定，则该项通过当且仅当全部断言通过。
    rubric = case.get("rubric", [])
    total_weight = 0.0
    earned_weight = 0.0
    rubric_detail: list[dict[str, Any]] = []
    for item in rubric:
        weight = float(item.get("weight", 1))
        idx = item.get("assertion_index")
        if idx is not None and 0 <= idx < len(assertion_results):
            item_passed = assertion_results[idx]["passed"]
        else:
            item_passed = all_passed
        total_weight += weight
        if item_passed:
            earned_weight += weight
        rubric_detail.append({
            "item": item.get("item", ""),
            "weight": weight,
            "passed": item_passed,
        })

    score = round(earned_weight / total_weight * 100, 2) if total_weight > 0 else 100.0

    return {
        "case_id": case["id"],
        "branch": case.get("branch", "unknown"),
        "prompt": case["prompt"],
        "passed": all_passed,
        "score": score,
        "evidence": {
            "exit_code": run_ctx["exit_code"],
            "mode": run_ctx["mode"],
            "elapsed": run_ctx["elapsed"],
            "stderr": run_ctx["stderr"] if run_ctx["stderr"] else None,
        },
        "assertions_detail": assertion_results,
        "rubric_detail": rubric_detail,
    }


def grade_branch(
    branch: str,
    skill_cmd: str | None = None,
    workdir: Path | None = None,
    timeout: int = 300,
    execute: bool = False,
) -> dict[str, Any]:
    """对指定分支的所有用例评分并汇总。

    Returns:
        汇总字典 ``{total, passed, failed, score_avg, by_branch, cases}``
    """
    cases = load_cases(branch)
    results = [
        evaluate_case(c, skill_cmd=skill_cmd, workdir=workdir, timeout=timeout, execute=execute)
        for c in cases
    ]

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    score_avg = round(sum(r["score"] for r in results) / total, 2) if total else 0.0

    # 按分支细分（虽然已按单分支过滤，仍保留结构供全量运行时使用）
    by_branch: dict[str, dict[str, int | float]] = {}
    for r in results:
        b = r["branch"]
        slot = by_branch.setdefault(b, {"total": 0, "passed": 0, "failed": 0, "score_avg": 0.0})
        slot["total"] += 1
        if r["passed"]:
            slot["passed"] += 1
        else:
            slot["failed"] += 1
    for b, slot in by_branch.items():
        slot["score_avg"] = round(
            sum(r["score"] for r in results if r["branch"] == b) / slot["total"], 2
        ) if slot["total"] else 0.0

    return {
        "branch": branch,
        "total": total,
        "passed": passed,
        "failed": failed,
        "score_avg": score_avg,
        "by_branch": by_branch,
        "cases": results,
    }


# ════════════════════════════════════════════════════════
#  命令行入口
# ════════════════════════════════════════════════════════
def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="python -m _shared.eval.grader",
        description="评测评分器：按 assertions + rubric 对用例机判打分",
    )
    parser.add_argument(
        "--branch", default="obj",
        help="目标分支（main/routine/financial/obj），默认 obj",
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="实际执行 skill（subprocess）；缺省为 dry-run 仅检查已有产物",
    )
    parser.add_argument(
        "--skill-cmd", default=None,
        help="skill 执行命令模板，用 {prompt} 占位（如 'python cli.py \"{prompt}\"'）",
    )
    parser.add_argument(
        "--workdir", default=None,
        help="产物根目录，断言中的相对路径基于此解析；缺省为仓库根",
    )
    parser.add_argument(
        "--timeout", type=int, default=300,
        help="子进程超时秒数，默认 300",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="结果输出 JSON 路径；缺省打印到 stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """命令行入口，返回退出码。"""
    args = build_parser().parse_args(argv)
    workdir = Path(args.workdir).resolve() if args.workdir else None

    summary = grade_branch(
        branch=args.branch,
        skill_cmd=args.skill_cmd,
        workdir=workdir,
        timeout=args.timeout,
        execute=args.execute,
    )

    output_text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"结果已写入 {out_path}", file=sys.stderr)
    else:
        print(output_text)

    # 全部通过返回 0，否则返回 1（供 CI 判定）
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())