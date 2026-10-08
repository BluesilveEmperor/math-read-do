"""cli.py 的单元测试。

重点验证 cmd_metrics 中累积收益的计算由 O(n²) 列表推导改为
np.cumsum (O(n)) 后数值结果保持不变，以及端到端 CLI 行为正确。
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from fin_tool import cli
from fin_tool import metrics as M


def _write_pnl_csv(path: Path, values, header=("Date", "PnL")):
    """把一组 PnL 数值写成带表头的 CSV。"""
    lines = [",".join(header)]
    for i, v in enumerate(values):
        lines.append(f"2024-01-{i + 1:02d},{v}")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. cumsum 数值等价性：np.cumsum 必须与原 O(n²) 算法逐项相等
# ---------------------------------------------------------------------------
def test_cumsum_matches_naive_quadratic():
    """np.cumsum 应与原先 O(n²) 的 [sum(series[:i+1]) for i in range(n)] 完全一致。"""
    rng = np.random.RandomState(0)
    series = rng.normal(0.001, 0.01, 500).tolist()
    naive = [sum(series[:i + 1]) for i in range(len(series))]  # 原 O(n²) 实现
    fast = np.cumsum(series).tolist()                            # 新 O(n) 实现
    assert fast == pytest.approx(naive, rel=1e-12, abs=1e-15)


def test_cumsum_empty_series():
    """空序列的 cumsum 应为空数组，与原实现一致。"""
    assert np.cumsum([]).tolist() == []


def test_cumsum_single_element():
    """单元素序列的 cumsum 应为该元素本身。"""
    assert np.cumsum([3.5]).tolist() == [3.5]


# ---------------------------------------------------------------------------
# 2. cmd_metrics 端到端：输出 JSON 结构与关键数值正确
# ---------------------------------------------------------------------------
def test_cmd_metrics_end_to_end(tmp_path):
    """构造 PnL CSV，运行 cmd_metrics，校验输出字段与 max_drawdown 一致。"""
    values = [0.01, -0.02, 0.03, 0.04, -0.01, 0.02]
    csv_path = tmp_path / "pnl.csv"
    _write_pnl_csv(csv_path, values)

    args = type("A", (), {"pnl": str(csv_path), "column": "PnL", "seed": 0})()
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.cmd_metrics(args)
    assert rc == 0

    out = json.loads(buf.getvalue())
    assert out["n"] == len(values)
    assert out["mean"] == pytest.approx(sum(values) / len(values))

    # max_drawdown 应基于累积收益曲线计算
    cum = np.cumsum(values)
    assert out["max_drawdown"] == pytest.approx(M.max_drawdown(cum))


def test_cmd_metrics_no_data_returns_error(tmp_path):
    """空 CSV 应返回非零退出码。"""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("Date,PnL\n", encoding="utf-8")

    args = type("A", (), {"pnl": str(csv_path), "column": "PnL", "seed": 0})()
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        rc = cli.cmd_metrics(args)
    assert rc == 1
    assert "no numeric data" in buf.getvalue()


# ---------------------------------------------------------------------------
# 3. 性能 sanity check：cumsum 在大数组上远快于 O(n²)（仅断言结果一致，不卡时）
# ---------------------------------------------------------------------------
def test_cumsum_large_array_correct():
    """大数组上 np.cumsum 结果与朴素实现一致（确保重构未改变语义）。"""
    n = 2000
    rng = np.random.RandomState(42)
    series = rng.normal(0.0, 1.0, n)
    naive = np.array([series[:i + 1].sum() for i in range(n)])
    fast = np.cumsum(series)
    assert fast == pytest.approx(naive, rel=1e-10, abs=1e-10)

# ===========================================================================
# 4. cmd_status / cmd_show / cmd_verdict 命令覆盖
# ===========================================================================
def test_cmd_status_text(tmp_path, capsys):
    """cmd_status 文本模式应输出表头与实验列表。"""
    args = type("A", (), {"json": False})()
    rc = cli.cmd_status(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "ID" in out
    assert "done=" in out


def test_cmd_status_json(capsys):
    """cmd_status --json 应输出合法 JSON 且含 10 个实验。"""
    args = type("A", (), {"json": True})()
    rc = cli.cmd_status(args)
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 10
    assert "01" in data


def test_cmd_show_existing(capsys):
    """cmd_show 已知 eid 应输出实验详情。"""
    args = type("A", (), {"eid": "07", "json": False})()
    rc = cli.cmd_show(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "07" in out
    assert "Network Superhedging" in out


def test_cmd_show_json(capsys):
    """cmd_show --json 输出合法 JSON。"""
    args = type("A", (), {"eid": "01", "json": True})()
    rc = cli.cmd_show(args)
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["eid"] == "01"


def test_cmd_show_unknown_returns_error(capsys):
    """未知 eid 应返回 1 并输出错误。"""
    args = type("A", (), {"eid": "99", "json": False})()
    rc = cli.cmd_show(args)
    err = capsys.readouterr().err
    assert rc == 1
    assert "unknown" in err


def test_cmd_verdict_pass(capsys):
    """value 与 ref 接近时 verdict=pass，rc=0。"""
    args = type("A", (), {"value": 1.0, "ref": 1.0, "tol": 0.01})()
    rc = cli.cmd_verdict(args)
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["verdict"] == M.PASS


def test_cmd_verdict_fail(capsys):
    """value 与 ref 偏差大时 verdict=fail，rc=2。"""
    args = type("A", (), {"value": 1.0, "ref": 2.0, "tol": 0.01})()
    rc = cli.cmd_verdict(args)
    out = capsys.readouterr().out
    assert rc == 2
    data = json.loads(out)
    assert data["verdict"] == M.FAIL


def test_cmd_verdict_approx(capsys):
    """偏差在 tol~3*tol 之间时 verdict=approx，rc=0。"""
    args = type("A", (), {"value": 1.02, "ref": 1.0, "tol": 0.01})()
    rc = cli.cmd_verdict(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["verdict"] == M.APPROX
    assert rc == 0


# ===========================================================================
# 5. _read_column 边界覆盖
# ===========================================================================
def test_read_column_no_header_treats_all_as_data(tmp_path):
    """无表头（首行即数据）时应把所有行当数据。"""
    csv_path = tmp_path / "noheader.csv"
    csv_path.write_text("1.0\n2.0\n3.0\n", encoding="utf-8")
    col = cli._read_column(str(csv_path), None)
    assert col == [1.0, 2.0, 3.0]


def test_read_column_skips_non_numeric_rows(tmp_path):
    """非数值行应被跳过。"""
    csv_path = tmp_path / "mixed.csv"
    csv_path.write_text("Date,PnL\n2024-01-01,1.0\nbad,N/A\n2024-01-03,2.0\n",
                        encoding="utf-8")
    col = cli._read_column(str(csv_path), "PnL")
    assert col == [1.0, 2.0]


def test_read_column_unknown_column_falls_back_last(tmp_path):
    """列名不匹配时回退到最后一列。"""
    csv_path = tmp_path / "fb.csv"
    csv_path.write_text("A,B,C\n1,2,3\n4,5,6\n", encoding="utf-8")
    col = cli._read_column(str(csv_path), "Z")
    assert col == [3.0, 6.0]


def test_read_column_empty_file(tmp_path):
    """空文件返回空列表。"""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")
    assert cli._read_column(str(csv_path), None) == []


def test_read_column_short_rows_skipped(tmp_path):
    """列数不足的行应被跳过。"""
    csv_path = tmp_path / "short.csv"
    csv_path.write_text("A,B\n1,2\n3\n4,5\n", encoding="utf-8")
    col = cli._read_column(str(csv_path), "B")
    assert col == [2.0, 5.0]


# ===========================================================================
# 6. cmd_metrics NaN / 大数据 / bootstrap 内存保护
# ===========================================================================
def test_cmd_metrics_with_nan_rows(tmp_path, capsys):
    """含非数值文本的行应被跳过，剩余数值正常计算。"""
    csv_path = tmp_path / "nan.csv"
    csv_path.write_text("Date,PnL\n1,0.01\n2,N/A\n3,0.02\n", encoding="utf-8")
    args = type("A", (), {"pnl": str(csv_path), "column": "PnL", "seed": 0})()
    rc = cli.cmd_metrics(args)
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["n"] == 2  # 非数值行被跳过


def test_cmd_metrics_large_dataset_no_timeout(tmp_path, capsys):
    """n=10000+ 大数据集应在合理时间内完成不超时。"""
    import time
    n = 12000
    rng = np.random.RandomState(0)
    values = rng.normal(0.001, 0.01, n)
    _write_pnl_csv(tmp_path / "big.csv", values.tolist())
    args = type("A", (), {
        "pnl": str(tmp_path / "big.csv"), "column": "PnL", "seed": 0
    })()
    t0 = time.time()
    rc = cli.cmd_metrics(args)
    elapsed = time.time() - t0
    capsys.readouterr()  # 清空
    assert rc == 0
    assert elapsed < 30.0  # 30s 内完成


def test_bootstrap_ci_downsample_large_sample():
    """超过 max_samples 时触发下采样，仍返回有限区间。"""
    rng = np.random.RandomState(1)
    big = rng.normal(0, 1, 15000).tolist()
    lo, hi = M.bootstrap_ci(big, n_boot=500, seed=0, max_samples=5000)
    assert math.isfinite(lo)
    assert math.isfinite(hi)
    assert lo <= hi


def test_bootstrap_ci_chunking_large_memory():
    """预估内存超限时触发分块，结果仍为有限区间且 lo<=hi。"""
    # n_boot * size * 16 / 1MB > max_memory_mb 触发分块
    rng = np.random.RandomState(2)
    sample = rng.normal(0, 1, 2000).tolist()
    lo, hi = M.bootstrap_ci(sample, n_boot=2000, seed=0,
                            max_memory_mb=0.5)  # 极小内存阈值强制分块
    assert math.isfinite(lo)
    assert math.isfinite(hi)
    assert lo <= hi


def test_bootstrap_ci_empty_returns_nan():
    """空样本返回 (nan, nan)。"""
    lo, hi = M.bootstrap_ci([])
    assert math.isnan(lo)
    assert math.isnan(hi)


# ===========================================================================
# 7. main() 入口与 build_parser
# ===========================================================================
def test_build_parser_has_subcommands():
    """build_parser 应注册 status/show/verdict/metrics 子命令。"""
    parser = cli.build_parser()
    actions = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
    # subparsers 的 choices 应含四个命令
    for sub in actions:
        if "status" in sub.choices:
            assert set(["status", "show", "verdict", "metrics"]).issubset(sub.choices)
            return
    pytest.fail("未找到子命令注册")


def test_main_status_returns_zero():
    """main(['status']) 应返回 0。"""
    assert cli.main(["status"]) == 0


def test_main_verdict_fail_returns_two():
    """main verdict 失败时返回 2。"""
    assert cli.main(["verdict", "--value", "1.0", "--ref", "5.0"]) == 2


def test_main_show_unknown_returns_one():
    """main show 未知 id 返回 1。"""
    assert cli.main(["show", "99"]) == 1