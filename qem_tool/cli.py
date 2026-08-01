#!/usr/bin/env python3
"""
QEM CLI — 命令行网格简化工具
=============================

用法:
    python -m qem_tool.cli --input model.obj --output simplified.obj --faces 1000
    python -m qem_tool.cli --input model.obj --output simplified.obj --ratio 0.1
    python -m qem_tool.cli --input model.obj --info            # 只显示网格信息

示例:
    # 将 bunny.obj 简化为 2000 个面
    python -m qem_tool.cli -i bunny.obj -o bunny_simple.obj -f 2000

    # 简化为原始面数的 10%
    python -m qem_tool.cli -i bunny.obj -o bunny_10pct.obj -r 0.1

    # 查看网格信息
    python -m qem_tool.cli -i bunny.obj --info
"""

import argparse
import math
import sys
import time
import os

# 确保可以从包外直接运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qem_tool.obj_io import OBJModel, Face, load_obj, export_obj, compute_face_normals
from qem_tool.qem_core import simplify_obj


def get_mesh_info(vertices, faces):
    """计算网格统计信息"""
    if not vertices or not faces:
        return {}

    # 包围盒
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    bbox_min = (min(xs), min(ys), min(zs))
    bbox_max = (max(xs), max(ys), max(zs))
    bbox_diag = math.sqrt((bbox_max[0]-bbox_min[0])**2 +
                          (bbox_max[1]-bbox_min[1])**2 +
                          (bbox_max[2]-bbox_min[2])**2)

    # 面平均面积
    total_area = 0.0
    for a, b, c in faces:
        v0, v1, v2 = vertices[a], vertices[b], vertices[c]
        u = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
        v = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
        cx = u[1]*v[2] - u[2]*v[1]
        cy = u[2]*v[0] - u[0]*v[2]
        cz = u[0]*v[1] - u[1]*v[0]
        total_area += 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)

    return {
        "vertices": len(vertices),
        "faces": len(faces),
        "edges": len(faces) * 3 // 2,
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "bbox_diagonal": bbox_diag,
        "total_surface_area": total_area,
        "avg_face_area": total_area / len(faces) if faces else 0,
    }


def print_mesh_info(info: dict, label: str = ""):
    """格式化打印网格信息"""
    prefix = f"[{label}] " if label else ""
    print(f"{prefix}Mesh Information:")
    print(f"  Vertices: {info['vertices']}")
    print(f"  Faces:    {info['faces']}")
    print(f"  BBox:     {info['bbox_min']} → {info['bbox_max']}")
    print(f"  Diagonal: {info['bbox_diagonal']:.4f}")
    print(f"  Surface:  {info['total_surface_area']:.4f}")
    print(f"  Avg Face: {info['avg_face_area']:.6f}")


def main():
    parser = argparse.ArgumentParser(
        description="QEM 网格简化工具 — Surface Simplification Using Quadric Error Metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i bunny.obj -o simplified.obj --faces 2000
  %(prog)s -i bunny.obj -o simplified.obj --ratio 0.1
  %(prog)s -i bunny.obj --info
  %(prog)s -i bunny.obj -o out.obj --faces 500 --no-boundary
        """)

    parser.add_argument('-i', '--input', required=True,
                        help='输入 .obj 文件路径')
    parser.add_argument('-o', '--output',
                        help='输出 .obj 文件路径')
    parser.add_argument('-f', '--faces', type=int,
                        help='目标面数（与 --ratio 二选一）')
    parser.add_argument('-r', '--ratio', type=float,
                        help='简化比例，如 0.1 = 保留 10%% 面（与 --faces 二选一）')
    parser.add_argument('--info', action='store_true',
                        help='只显示网格信息，不简化')
    parser.add_argument('--no-boundary', action='store_true',
                        help='不保护边界边（默认保护）')
    parser.add_argument('--precision', type=int, default=8,
                        help='OBJ 导出数值精度（默认 8 位小数）')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='输出详细信息')

    args = parser.parse_args()

    # ── 验证参数 ──
    if args.faces is None and args.ratio is None and not args.info:
        parser.error("请指定 --faces 或 --ratio（或使用 --info 仅查看信息）")
    if args.faces is not None and args.ratio is not None:
        parser.error("--faces 和 --ratio 不能同时使用")
    if args.faces is not None and args.faces < 1:
        parser.error("目标面数必须 ≥ 1")
    if args.ratio is not None and (args.ratio <= 0 or args.ratio > 1):
        parser.error("简化比例必须在 (0, 1] 范围内")

    # ── 加载模型 ──
    if not os.path.exists(args.input):
        print(f"[ERROR] 文件不存在: {args.input}")
        sys.exit(1)

    print(f"Loading: {args.input}")
    model = load_obj(args.input)

    vertices = list(model.vertices)
    faces = [(f.v[0], f.v[1], f.v[2]) for f in model.faces]
    texcoords = list(model.texcoords)

    orig_info = get_mesh_info(vertices, faces)
    print_mesh_info(orig_info, "Original")

    if args.info:
        return

    # ── 计算目标面数 ──
    if args.faces is not None:
        target_faces = args.faces
    else:
        target_faces = max(1, int(len(faces) * args.ratio))

    if target_faces >= len(faces):
        print(f"[WARN] 目标面数 ({target_faces}) ≥ 原始面数 ({len(faces)})，无需简化")
        if args.output:
            export_obj(model, args.output)
            print(f"Copied (unchanged): {args.output}")
        return

    print(f"\nTarget faces: {target_faces} "
          f"(reduction: {len(faces)} → {target_faces}, "
          f"{-100*(1-target_faces/len(faces)):.1f}%)")

    # ── 执行简化 ──
    print("Simplifying...")
    t0 = time.time()
    out_verts, out_faces = simplify_obj(
        vertices, faces, target_faces,
        preserve_boundary=not args.no_boundary
    )
    elapsed = time.time() - t0

    out_info = get_mesh_info(out_verts, out_faces)
    print_mesh_info(out_info, "Simplified")
    print(f"\nTime: {elapsed:.3f}s")

    # ── 导出 ──
    if args.output:
        out_model = OBJModel()
        out_model.vertices = out_verts
        # 简化后纹理坐标不传递（语义已变）
        # 重建法线
        out_normals = compute_face_normals(out_verts,
                                           [Face(v=f) for f in out_faces])
        out_model.normals = out_normals

        for (a, b, c) in out_faces:
            if out_normals:
                out_model.faces.append(Face(v=(a, b, c), vn=(a, b, c)))
            else:
                out_model.faces.append(Face(v=(a, b, c)))

        export_obj(out_model, args.output)
        print(f"Exported: {args.output}")

    # ── 简化报告 ──
    print("\n" + "=" * 50)
    print("SIMPLIFICATION REPORT")
    print("=" * 50)
    print(f"  Input:    {os.path.basename(args.input)}")
    print(f"  Faces:    {len(faces)} → {len(out_faces)} "
          f"({-100*(1-len(out_faces)/len(faces)):.1f}%)")
    print(f"  Verts:    {len(vertices)} → {len(out_verts)}")
    print(f"  Time:     {elapsed:.3f}s")
    print(f"  Rate:     {len(faces)/elapsed:.0f} faces/s")
    print("=" * 50)


if __name__ == '__main__':
    main()
