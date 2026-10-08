"""scripts/verify_qem.py 的单元测试（pytest 风格）。

覆盖：
  - check_degenerate_faces / check_duplicate_faces / check_manifold
  - _sample_surface_points 采样正确性
  - hausdorff_distance 向量化版本 vs naive 对比
  - 空网格 / 单面网格边界情况
  - main() 端到端验证流程
"""

import io
import os
import sys
import math
import random
import contextlib
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from verify_qem import (
    check_degenerate_faces,
    check_duplicate_faces,
    check_manifold,
    _sample_surface_points,
    _max_min_dist_naive,
    _max_min_dist_vectorized,
    hausdorff_distance,
)
from tests.fixtures import CUBE_OBJ, TETRA_OBJ, PLANE_OBJ


def _write_fixture(tmp_path, content, name="model.obj"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


# ── 退化面 / 重复面 / 流形检查 ───────────────────────────────────────

class TestFaceChecks:

    def test_no_degenerate_faces(self):
        """正常面列表无退化面。"""
        assert check_degenerate_faces([(0, 1, 2), (2, 3, 0)]) == 0

    def test_degenerate_face_detected(self):
        """含重复顶点的面应被计数。"""
        assert check_degenerate_faces([(0, 0, 2), (1, 2, 1)]) == 2

    def test_no_duplicate_faces(self):
        """无重复面返回 0。"""
        assert check_duplicate_faces([(0, 1, 2), (0, 2, 3)]) == 0

    def test_duplicate_face_detected(self):
        """排序后相同的面视为重复。"""
        assert check_duplicate_faces([(0, 1, 2), (2, 0, 1)]) == 1

    def test_manifold_ok(self):
        """每条边最多被 2 个面共享 → 无 bad edges。"""
        # 四面体闭合网格，每条边恰好 2 面
        faces = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
        assert check_manifold(faces) == []

    def test_non_manifold_detected(self):
        """一条边被 3 个面共享 → 返回 bad edge。"""
        faces = [(0, 1, 2), (0, 1, 3), (0, 1, 4)]
        bad = check_manifold(faces)
        assert len(bad) >= 1
        assert all(c > 2 for _, c in bad)


# ── 采样正确性 ────────────────────────────────────────────────────────

class TestSampleSurfacePoints:

    def test_sample_count(self):
        """采样数量应等于请求的 samples。"""
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        rng = random.Random(42)
        pts = _sample_surface_points(verts, faces, 50, rng=rng)
        assert len(pts) == 50
        for p in pts:
            assert len(p) == 3

    def test_sample_points_on_triangle(self):
        """采样点应落在三角形面内（重心坐标非负且和为 1）。"""
        verts = [(0, 0, 0), (2, 0, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        rng = random.Random(7)
        pts = _sample_surface_points(verts, faces, 100, rng=rng)
        for px, py, pz in pts:
            # 三角形在 z=0 平面，x>=0, y>=0, x+y<=2
            assert pz == pytest.approx(0, abs=1e-9)
            assert px >= -1e-9
            assert py >= -1e-9
            assert px + py <= 2 + 1e-9

    def test_sample_deterministic_with_seed(self):
        """相同 rng seed 应产生相同采样点。"""
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        pts1 = _sample_surface_points(verts, faces, 20, rng=random.Random(1))
        pts2 = _sample_surface_points(verts, faces, 20, rng=random.Random(1))
        assert pts1 == pts2


# ── Hausdorff 距离：向量化 vs naive ──────────────────────────────────

class TestHausdorffDistance:

    def test_vectorized_matches_naive(self):
        """向量化最近邻与朴素实现数值一致。"""
        sampled = [(0, 0, 0), (1, 0, 0), (0.5, 0.5, 0), (0.2, 0.3, 0.1)]
        v2 = [(0.1, 0.1, 0.0), (0.9, 0.0, 0.0), (0.5, 0.5, 0.0)]
        naive = _max_min_dist_naive(sampled, v2)
        vec = _max_min_dist_vectorized(sampled, v2)
        assert vec == pytest.approx(naive, rel=1e-9, abs=1e-12)

    def test_vectorized_matches_naive_random(self):
        """随机数据上向量化与 naive 一致。"""
        rng = random.Random(123)
        sampled = [(rng.random(), rng.random(), rng.random()) for _ in range(80)]
        v2 = [(rng.random(), rng.random(), rng.random()) for _ in range(40)]
        naive = _max_min_dist_naive(sampled, v2)
        vec = _max_min_dist_vectorized(sampled, v2)
        assert vec == pytest.approx(naive, rel=1e-7, abs=1e-10)

    def test_empty_v2_returns_zero(self):
        """空 v2 时向量化实现应返回 0.0。"""
        assert _max_min_dist_vectorized([(0, 0, 0)], []) == 0.0

    def test_hausdorff_nonnegative_and_bounded(self):
        """Hausdorff 距离非负，且不超过采样点到最远顶点的距离。

        注：hausdorff_distance 采样网格1表面点，到网格2的**顶点集**求最近邻，
        因此相同网格时距离 = 面内点到角点的最大距离，不为 0。
        """
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        h = hausdorff_distance(verts, faces, verts, faces, samples=200)
        assert h >= 0
        # 单位直角三角形面内点到顶点距离 ≤ sqrt(2)
        assert h <= math.sqrt(2) + 1e-9

    def test_hausdorff_far_target_large_distance(self):
        """v2 为远处单点时，Hausdorff 距离应约为采样点到该点的距离。"""
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        # v2 是一个在 (10,10,10) 的单点
        v2 = [(10, 10, 10)]
        h = hausdorff_distance(verts, faces, v2, [(0, 1, 2)], samples=300)
        # 面上任意点到 (10,10,10) 的距离 ≥ sqrt(9^2+9^2+9^2) ≈ 15.59
        assert h >= 15.0
        assert h <= 18.0


# ── 边界情况 ──────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_single_face_hausdorff(self):
        """单面网格 Hausdorff 距离可计算。"""
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        v2 = [(0.5, 0.5, 0)]
        h = hausdorff_distance(verts, faces, v2, [(0, 0, 0)], samples=50)
        assert h >= 0

    def test_empty_sampled_naive(self):
        """空采样点 naive 返回 0。"""
        assert _max_min_dist_naive([], [(0, 0, 0)]) == 0.0


# ── main() 端到端 ────────────────────────────────────────────────────

class TestVerifyMain:

    def _run_main(self, argv):
        from verify_qem import main
        old = sys.argv
        sys.argv = argv
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = main()
            rc = 0 if rc is None else rc
        except SystemExit as e:
            rc = e.code if e.code is not None else 0
        finally:
            sys.argv = old
        return rc, buf.getvalue()

    def test_verify_cube_passes(self, tmp_path):
        """立方体简化后验证应通过（无退化/重复面）。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["verify", "-i", path, "--faces", "6"])
        assert rc == 0
        assert "VERIFICATION PASSED" in out

    def test_verify_with_ratio(self, tmp_path):
        """--ratio 参数验证。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["verify", "-i", path, "--ratio", "0.5"])
        assert rc == 0

    def test_verify_check_hausdorff(self, tmp_path):
        """--check-hausdorff 应输出 Hausdorff 距离行。

        cube 简化到 6 面时 Hausdorff 可能超过 10% bbox 导致验证失败，
        这里只断言 Hausdorff 距离被计算并输出，不强制 rc==0。
        """
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["verify", "-i", path, "--faces", "6",
                                  "--check-hausdorff"])
        assert "Hausdorff dist" in out

    def test_verify_missing_target_errors(self, tmp_path):
        """未指定 --faces/--ratio 应报错退出。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["verify", "-i", path])
        assert rc != 0