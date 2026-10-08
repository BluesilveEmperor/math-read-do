"""routine 分支适配版 — OBJ I/O 测试。

routine 分支定位为「跨语言栈例行复现」，不含 qem_tool / obj 几何简化栈，
因此本测试在 routine 分支整体跳过。完整实现见 obj 分支
(math-read-do/tests/test_obj_io.py)。
"""

import unittest

import pytest

# routine 分支无 qem_tool 模块，模块级跳过
pytestmark = pytest.mark.skip(
    reason="routine 分支不含 qem_tool/obj 栈，OBJ I/O 测试在 obj 分支运行"
)


class TestObjIO(unittest.TestCase):
    """OBJ I/O 测试占位（routine 分支跳过）。"""

    def test_load_cube(self):
        """加载立方体 — routine 分支跳过。"""

    def test_load_plane_with_uv(self):
        """加载带纹理坐标的平面 — routine 分支跳过。"""

    def test_export_and_reimport(self):
        """导出后再导入 — routine 分支跳过。"""


if __name__ == "__main__":
    unittest.main()