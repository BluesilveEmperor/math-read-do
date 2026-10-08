"""Financial reproduction metrics and the five-state verdict rule.

All functions are pure NumPy so they run in both reproduction environments
(``financial`` = TF 2.15 / Python 3.11 and ``sigtorch39`` = torch 1.9 /
Python 3.9, numpy < 2).
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple

import numpy as np

TRADING_DAYS = 252

# 统一五态判决枚举（跨四分支统一）
# pass      — 精确匹配/通过（误差 ≤ tol）
# approx    — 近似通过（tol < 误差 ≤ 3·tol）
# within_ci — 在置信区间内
# fail      — 不通过
# skip      — 跳过（条件不满足/无法判定）
PASS = "pass"                 # 精确匹配/通过
APPROX = "approx"             # 近似通过
WITHIN_CI = "within_ci"       # 在置信区间内
FAIL = "fail"                 # 不通过
SKIP = "skip"                 # 跳过

# 向后兼容别名（旧枚举值 → 统一枚举，保留常量名供现有代码使用）
NOT_TESTABLE = SKIP           # 旧 not_testable → skip
BLOCKED = SKIP                # 旧 blocked → skip

# 旧值常量（仅供迁移/映射使用）
NOT_TESTABLE_LEGACY = "not_testable"
BLOCKED_LEGACY = "blocked"

# 旧值 → 新值 映射表（跨分支统一）
VERDICT_LEGACY_MAP = {
    # financial 旧值
    "not_testable": SKIP,
    "blocked": SKIP,
    # main/routine 旧值
    "within_ci": WITHIN_CI,
    "close_outside_ci": APPROX,
    "outside_tolerance": FAIL,
    "static_check_failed": FAIL,
    # obj 旧值
    "within_tolerance": PASS,
    "close_outside": APPROX,
    "outside": FAIL,
}


def sharpe_ratio(returns: Sequence[float], annualize: bool = True,
                 periods: int = TRADING_DAYS) -> float:
    """Sharpe ratio of a return series (risk-free rate assumed 0).

    Fin-GAN reports the *annualized* variant, hence ``annualize=True``.
    """
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return float("nan")
    sd = r.std(ddof=1) if r.size > 1 else 0.0
    # a constant series has zero volatility up to float noise -> undefined Sharpe
    if sd <= 1e-15 * max(1.0, abs(float(r.mean()))):
        return float("nan")
    s = r.mean() / sd
    return float(s * math.sqrt(periods)) if annualize else float(s)


def sortino_ratio(returns: Sequence[float], periods: int = TRADING_DAYS) -> float:
    r = np.asarray(returns, dtype=float)
    downside = r[r < 0]
    if downside.size == 0:
        return float("inf")
    dd = downside.std(ddof=1) if downside.size > 1 else abs(float(downside[0]))
    if dd == 0:
        return float("inf")
    return float(r.mean() / dd * math.sqrt(periods))


def max_drawdown(pnl: Sequence[float]) -> float:
    """Maximum drawdown of a cumulative PnL curve (returned as a positive number)."""
    c = np.asarray(pnl, dtype=float)
    if c.size == 0:
        return float("nan")
    peak = np.maximum.accumulate(c)
    return float(np.max(peak - c))


def hedge_probability(pnl: Sequence[float], tol: float = 0.0) -> float:
    """Fraction of paths whose terminal hedging error is >= -tol.

    This is the ``hedge_prob`` figure of experiment 07 (Network Superhedging).
    """
    p = np.asarray(pnl, dtype=float)
    if p.size == 0:
        return float("nan")
    return float(np.mean(p >= -tol))


def relative_error(value: float, reference: float) -> float:
    """Relative error, falling back to absolute error when reference == 0."""
    if reference == 0:
        return abs(value)
    return abs(value - reference) / abs(reference)


def bootstrap_ci(sample: Sequence[float], n_boot: int = 2000,
                 alpha: float = 0.05, seed: int = 0,
                 max_samples: int = 10000,
                 max_memory_mb: float = 500.0) -> Tuple[float, float]:
    """Percentile bootstrap CI for the mean. Deterministic given ``seed``.

    内存保护（避免大样本 OOM）：
    - 当样本数超过 ``max_samples`` 时，随机下采样至 ``max_samples``；
    - 当预估峰值内存超过 ``max_memory_mb`` 时，分块计算，逐块释放。
    小样本（不触发任何降级）时数值结果与原实现完全一致。

    内存估算：每个元素约 16 字节（int64 索引 + float64 采样数据）。
    """
    x = np.asarray(sample, dtype=float)
    if x.size == 0:
        return (float("nan"), float("nan"))

    rng = np.random.RandomState(seed)

    # 每个元素约 16 字节（int64 索引 + float64 采样数据）
    _bytes_per_element = 16
    estimated_mb = n_boot * x.size * _bytes_per_element / (1024 * 1024)

    needs_downsample = x.size > max_samples
    needs_chunking = estimated_mb > max_memory_mb

    if not needs_downsample and not needs_chunking:
        # 小样本：原算法，数值完全不变
        means = x[rng.randint(0, x.size, size=(n_boot, x.size))].mean(axis=1)
    else:
        # 大样本降级：先下采样控制样本量
        if needs_downsample:
            chosen = rng.choice(x.size, size=max_samples, replace=False)
            x = x[chosen]

        # 分块计算，每块峰值内存控制在 max_memory_mb 以内
        max_rows = max(1, int(max_memory_mb * 1024 * 1024
                              / (x.size * _bytes_per_element)))
        means_parts: list = []
        remaining = n_boot
        while remaining > 0:
            chunk = min(max_rows, remaining)
            idx = rng.randint(0, x.size, size=(chunk, x.size))
            means_parts.append(x[idx].mean(axis=1))
            remaining -= chunk
        means = np.concatenate(means_parts)

    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(lo), float(hi))


def verdict(value: float, reference: float | None, tol: float = 0.01,
            runnable: bool = True) -> str:
    """统一五态判决（跨四分支统一枚举）。

    返回值: pass / approx / within_ci / fail / skip
    - skip: 条件不满足（不可运行或无参考值）
    - pass: 误差 ≤ tol
    - approx: tol < 误差 ≤ 3·tol
    - fail: 误差 > 3·tol

    ``tol`` is a *relative* tolerance; the reproduction bundle uses 0.01
    (1 %) by default and 0.0001 for the deterministic experiment 07.
    """
    if not runnable:
        return SKIP  # 旧 BLOCKED → skip
    if reference is None or (isinstance(reference, float) and math.isnan(reference)):
        return SKIP  # 旧 NOT_TESTABLE → skip
    err = relative_error(value, reference)
    if err <= tol:
        return PASS
    if err <= 3 * tol:
        return APPROX
    return FAIL


def verdict_table(rows: Iterable[tuple]) -> list:
    """rows: (name, value, reference, tol) -> list of dicts with verdicts."""
    out = []
    for name, value, reference, tol in rows:
        out.append({
            "name": name,
            "value": value,
            "reference": reference,
            "rel_error": (None if reference is None
                          else relative_error(value, reference)),
            "tolerance": tol,
            "verdict": verdict(value, reference, tol),
        })
    return out
