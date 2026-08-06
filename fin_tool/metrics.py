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

# five-state verdict
PASS = "pass"                 # |delta| within tolerance
APPROX = "approx"             # outside tolerance but within 3x tolerance
FAIL = "fail"                 # outside 3x tolerance
NOT_TESTABLE = "not_testable"  # reference value unavailable (licensed data etc.)
BLOCKED = "blocked"           # experiment could not be run at all


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
                 alpha: float = 0.05, seed: int = 0) -> Tuple[float, float]:
    """Percentile bootstrap CI for the mean. Deterministic given ``seed``."""
    x = np.asarray(sample, dtype=float)
    if x.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.RandomState(seed)
    means = x[rng.randint(0, x.size, size=(n_boot, x.size))].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(lo), float(hi))


def verdict(value: float, reference: float | None, tol: float = 0.01,
            runnable: bool = True) -> str:
    """Five-state verdict used by every report in this skill.

    ``tol`` is a *relative* tolerance; the reproduction bundle uses 0.01
    (1 %) by default and 0.0001 for the deterministic experiment 07.
    """
    if not runnable:
        return BLOCKED
    if reference is None or (isinstance(reference, float) and math.isnan(reference)):
        return NOT_TESTABLE
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
