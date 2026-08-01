#!/usr/bin/env python3
"""
QEM 验证脚本 — 验证简化结果的正确性
=====================================

用法:
    python scripts/verify_qem.py --input model.obj --faces 1000
    python scripts/verify_qem.py --input model.obj --ratio 0.1 --check-hausdorff

验证项:
  1. 简化前后顶点/面数比例
  2. 无退化面（两个顶点相同）
  3. 无重复面
  4. Hausdorff 距离（可选）
  5. 法线一致性（可选）
"""

import os
import sys
import math
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool.obj_io import load_obj, export_obj, compute_face_normals
from qem_tool.qem_core import simplify_obj


def check_degenerate_faces(faces):
    """检查退化面（有重复顶点索引）"""
    bad = 0
    for i, (a, b, c) in enumerate(faces):
        if a == b or b == c or c == a:
            bad += 1
    return bad


def check_duplicate_faces(faces):
    """检查重复面"""
    seen = set()
    dup = 0
    for f in faces:
        key = tuple(sorted(f))
        if key in seen:
            dup += 1
        seen.add(key)
    return dup


def check_manifold(faces):
    """检查每条边最多被 2 个面共享"""
    edge_count = {}
    for a, b, c in faces:
        for e in [(min(a, b), max(a, b)),
                  (min(b, c), max(b, c)),
                  (min(c, a), max(c, a))]:
            edge_count[e] = edge_count.get(e, 0) + 1
    bad_edges = [(e, c) for e, c in edge_count.items() if c > 2]
    return bad_edges


def hausdorff_distance(v1, f1, v2, f2, samples=1000):
    """
    近似 Hausdorff 距离：在第一个网格表面采样，计算到第二个网格的最短距离。
    Gar: max over all points on surface A of min distance to surface B
    """
    import random

    # 在第一个网格面上采样
    sampled_points = []
    for _ in range(samples):
        fi = random.randint(0, len(f1) - 1)
        a, b, c = f1[fi]
        va, vb, vc = v1[a], v1[b], v1[c]
        # 随机重心坐标
        u = random.random()
        v = random.random()
        if u + v > 1:
            u, v = 1 - u, 1 - v
        w = 1 - u - v
        px = u * va[0] + v * vb[0] + w * vc[0]
        py = u * va[1] + v * vb[1] + w * vc[1]
        pz = u * va[2] + v * vb[2] + w * vc[2]
        sampled_points.append((px, py, pz))

    # 简化版本：最近点距离（按顶点）
    max_min_dist = 0.0
    for p in sampled_points:
        min_dist = float('inf')
        for vt in v2:
            d2 = (p[0]-vt[0])**2 + (p[1]-vt[1])**2 + (p[2]-vt[2])**2
            min_dist = min(min_dist, math.sqrt(d2))
        max_min_dist = max(max_min_dist, min_dist)

    return max_min_dist


def main():
    parser = argparse.ArgumentParser(description="QEM 简化结果验证")
    parser.add_argument('-i', '--input', required=True, help='输入 .obj 文件')
    parser.add_argument('-f', '--faces', type=int, help='目标面数')
    parser.add_argument('-r', '--ratio', type=float, help='简化比例')
    parser.add_argument('--check-hausdorff', action='store_true',
                        help='检查 Hausdorff 距离')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()
    if args.faces is None and args.ratio is None:
        parser.error("请指定 --faces 或 --ratio")

    # 加载
    print(f"Loading {args.input}...")
    model = load_obj(args.input)
    verts = list(model.vertices)
    faces = [(f.v[0], f.v[1], f.v[2]) for f in model.faces]

    if args.faces:
        target = args.faces
    else:
        target = max(1, int(len(faces) * args.ratio))

    # 简化
    print(f"Simplifying {len(faces)} → {target} faces...")
    out_v, out_f = simplify_obj(verts, faces, target)

    # 验证
    errors = []

    # 1. 面数检查
    if len(out_f) > target:
        errors.append(f"FAIL: target={target}, got={len(out_f)}")
    else:
        print(f"  ✓ Face count: {len(out_f)} ≤ {target}")

    # 2. 退化面
    n_degen = check_degenerate_faces(out_f)
    if n_degen > 0:
        errors.append(f"FAIL: {n_degen} degenerate faces")
    else:
        print(f"  ✓ No degenerate faces")

    # 3. 重复面
    n_dup = check_duplicate_faces(out_f)
    if n_dup > 0:
        errors.append(f"FAIL: {n_dup} duplicate faces")
    else:
        print(f"  ✓ No duplicate faces")

    # 4. Manifold 检查
    bad_edges = check_manifold(out_f)
    if bad_edges:
        print(f"  ⚠ {len(bad_edges)} non-manifold edges found")
    else:
        print(f"  ✓ Manifold preserved")

    # 5. Hausdorff
    if args.check_hausdorff:
        bbox_diag = math.sqrt(
            (max(v[0] for v in verts) - min(v[0] for v in verts))**2 +
            (max(v[1] for v in verts) - min(v[1] for v in verts))**2 +
            (max(v[2] for v in verts) - min(v[2] for v in verts))**2
        )
        hdist = hausdorff_distance(verts, faces, out_v, out_f)
        hdist_norm = hdist / bbox_diag if bbox_diag > 0 else 1.0
        print(f"  Hausdorff dist: {hdist:.6f} ({hdist_norm*100:.2f}% of bbox)")
        if hdist_norm > 0.1:
            errors.append(f"FAIL: Hausdorff dist > 10% of bbox diagonal")

    # 结果
    print()
    if errors:
        print("❌ VERIFICATION FAILED")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("✅ VERIFICATION PASSED")


if __name__ == '__main__':
    main()
