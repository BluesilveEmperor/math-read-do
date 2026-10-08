"""scripts/benchmark_qem.py 的单元测试（pytest 风格）。

覆盖：
  - benchmark() 单次基准计时功能
  - 多面数比例测试
  - main() 端到端（ratios / faces-list）
  - 无有效目标时的早退
"""

import io
import os
import sys
import contextlib

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from benchmark_qem import benchmark, main
from tests.fixtures import CUBE_OBJ, TETRA_OBJ


def _write_fixture(tmp_path, content, name="model.obj"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


# ── benchmark() 单次基准 ─────────────────────────────────────────────

class TestBenchmarkFunction:

    def test_benchmark_returns_result_dict(self, capsys, tmp_path):
        """benchmark 应返回含完整字段的结果字典（用真实立方体）。"""
        from qem_tool.obj_io import load_obj
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        model = load_obj(path)
        verts = list(model.vertices)
        faces = [(f.v[0], f.v[1], f.v[2]) for f in model.faces]
        result = benchmark(verts, faces, target_faces=6, name="unit")
        assert result["input_faces"] == 12
        assert result["output_faces"] <= 6
        assert result["input_verts"] == 8
        assert result["output_verts"] > 0
        assert result["time_sec"] >= 0
        assert result["reduction_pct"] >= 0
        captured = capsys.readouterr().out
        assert "[unit]" in captured

    def test_benchmark_zero_time_rate(self, capsys):
        """elapsed=0 时 rate 应为 0（防除零，实际很难触发，这里测字段存在）。"""
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        faces = [(0, 1, 2)]
        result = benchmark(verts, faces, target_faces=1)
        assert "faces_per_sec" in result
        assert result["faces_per_sec"] >= 0


# ── main() 端到端 ────────────────────────────────────────────────────

class TestBenchmarkMain:

    def _run_main(self, argv):
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

    def test_main_with_ratios(self, tmp_path):
        """默认 ratios 列表运行基准测试。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["bench", "-i", path, "--ratios", "0.5", "0.25"])
        assert rc == 0
        assert "Summary" in out
        assert "Avg rate" in out

    def test_main_with_faces_list(self, tmp_path):
        """--faces-list 指定目标面数列表。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["bench", "-i", path,
                                  "--faces-list", "8", "6", "4"])
        assert rc == 0
        assert "Summary" in out

    def test_main_no_valid_targets(self, tmp_path):
        """所有目标 ≥ 原始面数时应早退并提示。"""
        path = _write_fixture(tmp_path, TETRA_OBJ, "tetra.obj")
        rc, out = self._run_main(["bench", "-i", path,
                                  "--faces-list", "100", "200"])
        assert rc == 0
        assert "No valid targets" in out

    def test_main_dedup_and_sort_targets(self, tmp_path):
        """重复/无序目标应去重并降序排列后运行。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = self._run_main(["bench", "-i", path,
                                  "--faces-list", "4", "6", "4"])
        assert rc == 0
        assert "Summary" in out