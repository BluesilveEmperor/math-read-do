#!/usr/bin/env python3
"""
QEM 性能基准测试
=================

测试不同规模网格的简化性能。

用法:
    python scripts/benchmark_qem.py --input model.obj
    python scripts/benchmark_qem.py --input model.obj --ratios 0.5 0.2 0.1 0.05
    python scripts/benchmark_qem.py --input model.obj --faces-list 1000 500 100
"""

import os
import sys
import time
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool.obj_io import load_obj
from qem_tool.qem_core import simplify_obj


def benchmark(verts, faces, target_faces, name=""):
    """单次基准测试"""
    t0 = time.time()
    out_v, out_f = simplify_obj(verts, faces, target_faces)
    elapsed = time.time() - t0

    reduction = (1 - len(out_f) / len(faces)) * 100
    rate = len(faces) / elapsed if elapsed > 0 else 0

    label = f"[{name}] " if name else ""
    print(f"{label}{len(faces):>8,} → {len(out_f):>8,} faces "
          f"({reduction:5.1f}%)  "
          f"{elapsed:8.3f}s  {rate:>10,.0f} faces/s")

    return {
        "input_faces": len(faces),
        "output_faces": len(out_f),
        "input_verts": len(verts),
        "output_verts": len(out_v),
        "time_sec": elapsed,
        "faces_per_sec": rate,
        "reduction_pct": reduction,
    }


def main():
    parser = argparse.ArgumentParser(description="QEM 性能基准测试")
    parser.add_argument('-i', '--input', required=True, help='输入 .obj 文件')
    parser.add_argument('-r', '--ratios', nargs='+', type=float,
                        default=[0.5, 0.2, 0.1, 0.05, 0.01],
                        help='简化比例列表')
    parser.add_argument('-f', '--faces-list', nargs='+', type=int,
                        help='目标面数列表（替代 --ratios）')
    args = parser.parse_args()

    # 加载
    print(f"Loading {args.input}...")
    model = load_obj(args.input)
    verts = list(model.vertices)
    faces = [(f.v[0], f.v[1], f.v[2]) for f in model.faces]
    print(f"  Verts: {len(verts)}, Faces: {len(faces)}")
    print()

    # 目标值
    if args.faces_list:
        targets = args.faces_list
    else:
        targets = [max(1, int(len(faces) * r)) for r in args.ratios]

    targets = sorted(set(t for t in targets if t < len(faces)), reverse=True)

    if not targets:
        print("No valid targets (all ≥ original face count)")
        return

    print(f"{'Test':>12} {'Input':>10} {'Output':>10} {'Reduc':>7}  "
          f"{'Time':>9} {'Rate':>12}")
    print("-" * 70)

    results = []
    for i, target in enumerate(targets):
        result = benchmark(verts, faces, target, name=f"Run {i+1}")
        results.append(result)

    print()
    print("Summary:")
    print(f"  Total time: {sum(r['time_sec'] for r in results):.3f}s")
    print(f"  Avg rate:   "
          f"{sum(r['faces_per_sec'] for r in results) / len(results):,.0f} faces/s")


if __name__ == '__main__':
    main()
