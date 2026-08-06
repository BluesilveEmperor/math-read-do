import math

import numpy as np
import pytest

from fin_tool import metrics as M


def test_sharpe_zero_mean():
    r = [0.01, -0.01, 0.01, -0.01]
    assert abs(M.sharpe_ratio(r)) < 1e-12


def test_sharpe_annualization_factor():
    rng = np.random.RandomState(0)
    r = rng.normal(0.001, 0.01, 500)
    daily = M.sharpe_ratio(r, annualize=False)
    ann = M.sharpe_ratio(r)
    assert ann == pytest.approx(daily * math.sqrt(252), rel=1e-12)


def test_sharpe_constant_series_is_nan():
    assert math.isnan(M.sharpe_ratio([0.01] * 10))


def test_sortino_no_downside_is_inf():
    assert M.sortino_ratio([0.01, 0.02, 0.03]) == float("inf")


def test_max_drawdown():
    cum = [0, 1, 3, 2, 5, 1]
    assert M.max_drawdown(cum) == pytest.approx(4.0)


def test_hedge_probability():
    assert M.hedge_probability([1.0, -1.0, 0.0, 2.0]) == pytest.approx(0.75)


def test_relative_error_zero_reference():
    assert M.relative_error(0.5, 0.0) == pytest.approx(0.5)


def test_verdict_five_states():
    assert M.verdict(1.0, 1.0, 0.01) == M.PASS
    assert M.verdict(1.02, 1.0, 0.01) == M.APPROX
    assert M.verdict(1.5, 1.0, 0.01) == M.FAIL
    assert M.verdict(1.0, None, 0.01) == M.NOT_TESTABLE
    assert M.verdict(1.0, 1.0, 0.01, runnable=False) == M.BLOCKED


def test_verdict_matches_experiment_07():
    # 07 Network Superhedging reproduced exactly at tol=1e-4
    assert M.verdict(1.3274, 1.3274, 1e-4) == M.PASS
    assert M.verdict(0.4072, 0.4072, 1e-4) == M.PASS
    assert M.verdict(2.0952, 2.0952, 1e-4) == M.PASS
    assert M.verdict(0.9966, 0.9966, 1e-4) == M.PASS


def test_bootstrap_ci_is_deterministic_and_brackets_mean():
    rng = np.random.RandomState(1)
    x = rng.normal(1.0, 0.1, 300)
    a = M.bootstrap_ci(x, seed=42)
    b = M.bootstrap_ci(x, seed=42)
    assert a == b
    assert a[0] < x.mean() < a[1]


def test_verdict_table_shape():
    rows = [("price", 1.3274, 1.3274, 1e-4), ("prob", 0.41, 0.4072, 1e-4)]
    t = M.verdict_table(rows)
    assert [r["verdict"] for r in t] == [M.PASS, M.FAIL]
