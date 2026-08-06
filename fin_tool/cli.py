"""CLI for the math-read-do-finance reproduction framework.

    python -m fin_tool.cli status                 # reproduction status table
    python -m fin_tool.cli show 07                # one experiment in detail
    python -m fin_tool.cli verdict --value 1.3274 --ref 1.3274 --tol 1e-4
    python -m fin_tool.cli metrics --pnl file.csv [--column PnL]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

from . import metrics as M
from . import registry as R

ICON = {R.DONE: "[OK]", R.PARTIAL: "[PART]", R.BLOCKED: "[BLOCK]"}


def cmd_status(args) -> int:
    if args.json:
        print(json.dumps({k: v.as_dict() for k, v in R.REGISTRY.items()},
                         ensure_ascii=False, indent=2))
        return 0
    print(f"{'ID':<4}{'Status':<9}{'Env':<12}{'Experiment':<38}Venue")
    print("-" * 100)
    for eid in sorted(R.REGISTRY):
        e = R.REGISTRY[eid]
        print(f"{e.eid:<4}{ICON[e.status]:<9}{e.env:<12}{e.name:<38}{e.venue}")
    s = R.summary()
    print("-" * 100)
    print(f"done={s[R.DONE]}  partial={s[R.PARTIAL]}  blocked={s[R.BLOCKED]}"
          f"  total={len(R.REGISTRY)}")
    return 0


def cmd_show(args) -> int:
    e = R.get(args.eid)
    if e is None:
        print(f"unknown experiment id: {args.eid}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(e.as_dict(), ensure_ascii=False, indent=2))
        return 0
    print(f"{e.eid} {e.name}  ({e.venue})")
    print(f"  status : {e.status}")
    print(f"  env    : {e.env}")
    for label, items in (("metrics", [f"{k} = {v}" for k, v in e.metrics.items()]),
                         ("artifacts", e.artifacts),
                         ("blockers", e.blockers),
                         ("fixes", e.fixes)):
        if items:
            print(f"  {label}:")
            for it in items:
                print(f"    - {it}")
    return 0


def cmd_verdict(args) -> int:
    v = M.verdict(args.value, args.ref, args.tol)
    err = M.relative_error(args.value, args.ref)
    print(json.dumps({"value": args.value, "reference": args.ref,
                      "rel_error": err, "tolerance": args.tol,
                      "verdict": v}, indent=2))
    return 0 if v in (M.PASS, M.APPROX) else 2


def _read_column(path: str, column: str | None) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return []
    header, body = rows[0], rows[1:]
    idx = 0
    if column is not None and column in header:
        idx = header.index(column)
    else:
        # no matching header -> assume the last numeric column
        try:
            float(header[-1])
            body = rows          # the "header" was already data
        except ValueError:
            pass
        idx = len(header) - 1
    out = []
    for r in body:
        if len(r) <= idx:
            continue
        try:
            out.append(float(r[idx]))
        except ValueError:
            continue
    return out


def cmd_metrics(args) -> int:
    series = _read_column(args.pnl, args.column)
    if not series:
        print(f"no numeric data found in {args.pnl}", file=sys.stderr)
        return 1
    cum = [sum(series[:i + 1]) for i in range(len(series))]
    lo, hi = M.bootstrap_ci(series, seed=args.seed)
    print(json.dumps({
        "n": len(series),
        "mean": sum(series) / len(series),
        "sharpe_annualized": M.sharpe_ratio(series),
        "sortino_annualized": M.sortino_ratio(series),
        "max_drawdown": M.max_drawdown(cum),
        "hedge_probability": M.hedge_probability(series),
        "mean_ci95": [lo, hi],
    }, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fin_tool",
                                description="math-read-do-finance CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="reproduction status of all 10 experiments")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("show", help="detail of one experiment")
    s.add_argument("eid")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("verdict", help="five-state verdict for one number")
    s.add_argument("--value", type=float, required=True)
    s.add_argument("--ref", type=float, required=True)
    s.add_argument("--tol", type=float, default=0.01)
    s.set_defaults(func=cmd_verdict)

    s = sub.add_parser("metrics", help="risk metrics of a PnL csv")
    s.add_argument("--pnl", required=True)
    s.add_argument("--column", default=None)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(func=cmd_metrics)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
