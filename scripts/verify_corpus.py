#!/usr/bin/env python3
"""
语料校验脚本 — 校验网格副本与 corpus/MANIFEST.json 登记是否逐字节一致
====================================================================

用法:
    python scripts/verify_corpus.py --mesh-dir <dir>                        # 校验模式（默认）
    python scripts/verify_corpus.py --mesh-dir <dir> --regen                # 重算派生字段并回写清单
    python scripts/verify_corpus.py --mesh-dir <dir> --manifest other.json  # 指定清单路径

校验模式（默认）:
  对清单每条记录检查 文件存在 / bytes / sha256，逐项输出 PASS/FAIL（含期望值与实际值）；
  缺失文件 = FAIL；目录中未登记的文件 = WARN 列表；
  退出码 0 当且仅当全部检查 PASS（可被 CI 判断）。

--regen 模式:
  重算派生字段（bytes/sha256/vertices/faces/euler/boundary_edges/uv 及拓扑判定）
  并回写 MANIFEST.json；手工字段（source/stages/notes）原样保留；
  拓扑判定规则: boundary_edges>0 → with_boundary(genus null)；
               euler==2 → closed_sphere(genus 0)；否则 closed_genus(genus=(2-euler)/2)。
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "corpus" / "MANIFEST.json"

DERIVED_FIELDS = ["bytes", "sha256", "vertices", "faces", "euler", "boundary_edges", "uv"]
MANUAL_FIELDS = ["source", "stages", "notes"]


def sha256_of(path: Path) -> str:
    """计算文件内容的 SHA-256（分块读取，兼容大文件）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_mesh_stats(path: Path) -> dict:
    """从 OBJ 文件计算派生字段: 顶点/面数、边统计、Euler 示性数、边界边数、UV 有无。"""
    vertices = 0
    faces = 0
    vt_lines = 0
    edge_count = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                vertices += 1
            elif line.startswith("vt "):
                vt_lines += 1
            elif line.startswith("f "):
                faces += 1
                vids = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                n = len(vids)
                for i in range(n):
                    a = vids[i]
                    b = vids[(i + 1) % n]
                    e = (a, b) if a < b else (b, a)
                    edge_count[e] = edge_count.get(e, 0) + 1
    edges = len(edge_count)
    boundary_edges = sum(1 for c in edge_count.values() if c == 1)
    euler = vertices - edges + faces
    return {
        "bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "vertices": vertices,
        "faces": faces,
        "euler": euler,
        "boundary_edges": boundary_edges,
        "uv": vt_lines > 0,
    }


def classify_topology(boundary_edges: int, euler: int):
    """拓扑分类与亏格推导（人工覆核过的确定性规则，--regen 沿用）。"""
    if boundary_edges > 0:
        return "with_boundary", None
    if euler == 2:
        return "closed_sphere", 0
    return "closed_genus", (2 - euler) // 2


def load_manifest(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_unregistered(mesh_dir: Path, registered: set) -> list:
    """列出目录中未登记的文件。"""
    return sorted(p.name for p in mesh_dir.iterdir() if p.is_file() and p.name not in registered)


def cmd_verify(manifest_path: Path, mesh_dir: Path) -> int:
    """校验模式: 逐条记录检查 文件存在/bytes/sha256，返回退出码。"""
    manifest = load_manifest(manifest_path)
    meshes = manifest.get("meshes", [])
    print(f"清单: {manifest_path}")
    print(f"语料目录: {mesh_dir}")
    print(f"登记网格数: {len(meshes)}")
    print("-" * 72)

    all_pass = True
    for entry in meshes:
        name = entry.get("filename", "<missing filename>")
        path = mesh_dir / name
        print(f"[{name}]")

        if not path.exists():
            print(f"  FAIL 存在性: 文件缺失 (期望 {path})")
            all_pass = False
            continue

        ok = True
        actual_bytes = path.stat().st_size
        if actual_bytes != entry.get("bytes"):
            print(f"  FAIL bytes: 期望 {entry.get('bytes')}, 实际 {actual_bytes}")
            ok = False
        else:
            print(f"  PASS bytes: {actual_bytes}")

        actual_sha = sha256_of(path)
        if actual_sha != entry.get("sha256"):
            print(f"  FAIL sha256: 期望 {entry.get('sha256')}")
            print(f"              实际 {actual_sha}")
            ok = False
        else:
            print(f"  PASS sha256: {actual_sha}")

        if not ok:
            all_pass = False

    unregistered = list_unregistered(mesh_dir, {e.get("filename") for e in meshes})
    print("-" * 72)
    if unregistered:
        print(f"WARN 目录中存在 {len(unregistered)} 个未登记文件:")
        for name in unregistered:
            print(f"  WARN 未登记: {name}")
    else:
        print("未登记文件: 无")

    if all_pass:
        print("结果: 全部 PASS")
        return 0
    print("结果: 存在 FAIL 项")
    return 1


def cmd_regen(manifest_path: Path, mesh_dir: Path) -> int:
    """重算模式: 重算派生字段并回写清单（保留手工字段），输出变更摘要。"""
    manifest = load_manifest(manifest_path)
    meshes = manifest.get("meshes", [])
    changes = []
    errors = []

    for entry in meshes:
        name = entry.get("filename", "<missing filename>")
        path = mesh_dir / name
        if not path.exists():
            errors.append(f"缺少文件，跳过重算: {path}")
            continue
        derived = derive_mesh_stats(path)
        topology, genus = classify_topology(derived["boundary_edges"], derived["euler"])
        for field in DERIVED_FIELDS:
            if entry.get(field) != derived[field]:
                changes.append(f"[{name}] {field}: {entry.get(field)!r} -> {derived[field]!r}")
                entry[field] = derived[field]
        if entry.get("topology") != topology or entry.get("genus") != genus:
            changes.append(
                f"[{name}] topology/genus: "
                f"{entry.get('topology')!r}/{entry.get('genus')!r} -> {topology!r}/{genus!r}"
            )
            entry["topology"] = topology
            entry["genus"] = genus
        # 手工字段（source/stages/notes）原样保留，不做任何改动

    for err in errors:
        print(f"ERROR {err}")

    unregistered = list_unregistered(mesh_dir, {e.get("filename") for e in meshes})
    for name in unregistered:
        print(f"WARN 未登记文件（未加入清单，如需登记请手工补充条目）: {name}")

    if changes:
        print(f"变更摘要（{len(changes)} 项）:")
        for c in changes:
            print(f"  {c}")
    else:
        print("变更摘要: 派生字段无变化")

    if errors:
        return 1

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"已回写: {manifest_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="网格语料清单校验/重算工具")
    parser.add_argument("--mesh-dir", required=True, help="网格语料目录（必选）")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                        help=f"清单路径（默认 {DEFAULT_MANIFEST}）")
    parser.add_argument("--regen", action="store_true",
                        help="重算派生字段并回写清单（默认为校验模式）")
    args = parser.parse_args()

    mesh_dir = Path(args.mesh_dir)
    manifest_path = Path(args.manifest)

    if not mesh_dir.is_dir():
        print(f"ERROR 语料目录不存在: {mesh_dir}")
        return 2
    if not manifest_path.is_file():
        print(f"ERROR 清单文件不存在: {manifest_path}")
        return 2

    if args.regen:
        return cmd_regen(manifest_path, mesh_dir)
    return cmd_verify(manifest_path, mesh_dir)


if __name__ == "__main__":
    sys.exit(main())
