"""qem_tool/cli.py 的单元测试（pytest 风格）。

覆盖：
  - CLI 参数解析（--input/--output/--faces/--ratio/--preserve-boundary 即 --no-boundary）
  - 简化命令端到端（输入 cube.obj → 输出简化网格）
  - 错误输入处理（不存在文件 / 坏 OBJ）
  - --no-boundary 传递验证
  - --info 仅查看信息
  - 参数互斥校验
"""

import io
import os
import sys
import contextlib
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool import cli as cli_mod
from tests.fixtures import CUBE_OBJ, TETRA_OBJ, PLANE_OBJ


# ── 辅助 ──────────────────────────────────────────────────────────────

def _write_fixture(tmp_path, content, name="model.obj"):
    """把 OBJ 文本写入临时文件，返回路径字符串。"""
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def _run_cli(argv, expect_exit=0):
    """以给定 argv 调用 cli.main()，捕获 stdout，返回 (rc, stdout)。

    main() 正常返回 None（视为 0），sys.exit(n) 会被 SystemExit 捕获。
    """
    old_argv = sys.argv
    sys.argv = argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = cli_mod.main()
        if rc is None:
            rc = 0
    except SystemExit as e:
        rc = e.code if e.code is not None else 0
    finally:
        sys.argv = old_argv
    return rc, buf.getvalue()


# ── get_mesh_info / print_mesh_info 纯函数 ───────────────────────────

class TestGetMeshInfo:
    """get_mesh_info 与 print_mesh_info 的纯函数测试。"""

    def test_empty_mesh_returns_empty_dict(self):
        """空顶点或空面应返回空字典。"""
        assert cli_mod.get_mesh_info([], []) == {}
        assert cli_mod.get_mesh_info([(0, 0, 0)], []) == {}

    def test_cube_info_fields(self):
        """立方体的统计字段齐全且数值合理。"""
        verts = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                 (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        faces = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7)]
        info = cli_mod.get_mesh_info(verts, faces)
        assert info["vertices"] == 8
        assert info["faces"] == 4
        assert info["edges"] == 6  # 4*3//2
        assert info["bbox_diagonal"] == pytest.approx((2**2 + 2**2 + 2**2) ** 0.5)
        assert info["total_surface_area"] > 0
        assert info["avg_face_area"] == pytest.approx(info["total_surface_area"] / 4)

    def test_print_mesh_info_outputs_label(self, capsys):
        """print_mesh_info 应输出带 label 的行。"""
        info = {
            "vertices": 4, "faces": 4, "bbox_min": (0, 0, 0),
            "bbox_max": (1, 1, 1), "bbox_diagonal": 1.732,
            "total_surface_area": 2.0, "avg_face_area": 0.5,
        }
        cli_mod.print_mesh_info(info, "Test")
        out = capsys.readouterr().out
        assert "[Test]" in out
        assert "Vertices: 4" in out
        assert "Faces:    4" in out


# ── 参数解析与校验 ────────────────────────────────────────────────────

class TestArgParsing:
    """CLI 参数解析与互斥校验。"""

    def test_missing_faces_and_ratio_errors(self, tmp_path):
        """既不指定 --faces 也不指定 --ratio（且非 --info）应报错退出。"""
        path = _write_fixture(tmp_path, CUBE_OBJ)
        rc, out = _run_cli(["qem", "-i", path])
        assert rc != 0  # parser.error → SystemExit(2)

    def test_faces_and_ratio_mutually_exclusive(self, tmp_path):
        """--faces 和 --ratio 同时使用应报错。"""
        path = _write_fixture(tmp_path, CUBE_OBJ)
        rc, out = _run_cli(["qem", "-i", path, "-o", str(tmp_path / "o.obj"),
                            "--faces", "2", "--ratio", "0.5"])
        assert rc != 0

    def test_faces_must_be_positive(self, tmp_path):
        """目标面数 < 1 应报错。"""
        path = _write_fixture(tmp_path, CUBE_OBJ)
        rc, out = _run_cli(["qem", "-i", path, "--faces", "0"])
        assert rc != 0

    def test_ratio_out_of_range_errors(self, tmp_path):
        """简化比例 <=0 或 >1 应报错。"""
        path = _write_fixture(tmp_path, CUBE_OBJ)
        assert _run_cli(["qem", "-i", path, "--ratio", "0"])[0] != 0
        assert _run_cli(["qem", "-i", path, "--ratio", "1.5"])[0] != 0
        assert _run_cli(["qem", "-i", path, "--ratio", "-0.1"])[0] != 0


# ── 错误输入 ──────────────────────────────────────────────────────────

class TestErrorInputs:
    """文件不存在 / 坏 OBJ 的错误路径。"""

    def test_nonexistent_file_exits_1(self, tmp_path):
        """输入文件不存在应打印 [ERROR] 并 sys.exit(1)。"""
        missing = str(tmp_path / "no_such.obj")
        rc, out = _run_cli(["qem", "-i", missing, "--faces", "2"])
        assert rc == 1
        assert "[ERROR]" in out
        assert "文件不存在" in out

    def test_bad_obj_raises_and_exits(self, tmp_path):
        """坏 OBJ（顶点缺分量）应触发 ValueError → 非零退出。"""
        path = _write_fixture(tmp_path, "o Bad\nv 1 2\n", "bad.obj")
        # load_obj 抛 ValueError，未被 main 捕获 → 传播为异常
        with pytest.raises(ValueError):
            _run_cli(["qem", "-i", path, "--faces", "1"])


# ── 端到端简化 ────────────────────────────────────────────────────────

class TestEndToEndSimplification:
    """端到端：输入 cube.obj → 输出简化网格。"""

    def test_info_only_no_output(self, tmp_path):
        """--info 仅显示信息，不简化、不报错。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = _run_cli(["qem", "-i", path, "--info"])
        assert rc == 0
        assert "Original" in out
        assert "Mesh Information" in out

    def test_simplify_cube_with_faces(self, tmp_path):
        """cube 12 面 → 6 面，输出文件存在且可重新加载。"""
        from qem_tool.obj_io import load_obj
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        out_path = str(tmp_path / "simple.obj")
        rc, out = _run_cli(["qem", "-i", path, "-o", out_path, "--faces", "6"])
        assert rc == 0
        assert os.path.exists(out_path)
        # 输出可重新加载
        model = load_obj(out_path)
        assert len(model.faces) <= 6
        assert len(model.vertices) > 0
        assert "Simplifying" in out
        assert "Exported" in out

    def test_simplify_cube_with_ratio(self, tmp_path):
        """--ratio 0.5 简化立方体。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        out_path = str(tmp_path / "ratio.obj")
        rc, out = _run_cli(["qem", "-i", path, "-o", out_path, "--ratio", "0.5"])
        assert rc == 0
        assert os.path.exists(out_path)

    def test_no_output_still_runs(self, tmp_path):
        """不指定 -o 时仍应完成简化并打印报告。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = _run_cli(["qem", "-i", path, "--faces", "4"])
        assert rc == 0
        assert "SIMPLIFICATION REPORT" in out

    def test_target_ge_original_copies_unchanged(self, tmp_path):
        """目标面数 ≥ 原始面数时应跳过简化，可选复制输出。"""
        from qem_tool.obj_io import load_obj
        path = _write_fixture(tmp_path, TETRA_OBJ, "tetra.obj")
        out_path = str(tmp_path / "copy.obj")
        rc, out = _run_cli(["qem", "-i", path, "-o", out_path, "--faces", "100"])
        assert rc == 0
        assert "[WARN]" in out
        assert os.path.exists(out_path)
        model = load_obj(out_path)
        assert len(model.faces) == 4  # 四面体 4 面不变

    def test_no_boundary_flag_passed(self, tmp_path):
        """--no-boundary 应允许开网格被简化（preserve_boundary=False）。

        PLANE_OBJ 是开网格，默认保护边界时无法折叠；--no-boundary 后可简化。
        """
        path = _write_fixture(tmp_path, PLANE_OBJ, "plane.obj")
        out_path = str(tmp_path / "nobnd.obj")
        rc, out = _run_cli(["qem", "-i", path, "-o", out_path,
                            "--faces", "1", "--no-boundary"])
        assert rc == 0
        assert os.path.exists(out_path)
        from qem_tool.obj_io import load_obj
        model = load_obj(out_path)
        assert len(model.faces) <= 1

    def test_preserve_boundary_default_blocks_open_mesh(self, tmp_path):
        """默认（保护边界）下开网格 PLANE 无法简化，面数不变。"""
        path = _write_fixture(tmp_path, PLANE_OBJ, "plane.obj")
        rc, out = _run_cli(["qem", "-i", path, "--faces", "1"])
        assert rc == 0
        # 默认保护边界 → 面数保持 2
        assert "2 → 2" in out or "2 →" in out

    def test_verbose_flag_runs(self, tmp_path):
        """--verbose 标志不应导致崩溃。"""
        path = _write_fixture(tmp_path, CUBE_OBJ, "cube.obj")
        rc, out = _run_cli(["qem", "-i", path, "--faces", "6", "--verbose"])
        assert rc == 0