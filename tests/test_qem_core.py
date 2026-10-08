"""routine 分支适配版 — QEM 核心算法测试。

routine 分支定位为「跨语言栈例行复现」，不含 qem_tool / QEM 几何简化栈，
因此本测试在 routine 分支整体跳过。完整实现见 obj 分支
(math-read-do/tests/test_qem_core.py)。
"""

import unittest

import pytest

# routine 分支无 qem_tool 模块，模块级跳过
pytestmark = pytest.mark.skip(
    reason="routine 分支不含 qem_tool/QEM 栈，QEM 核心测试在 obj 分支运行"
)


class TestQEMCore(unittest.TestCase):
    """QEM 核心算法测试占位（routine 分支跳过）。"""

    def test_simplify_no_reduction(self):
        """简化到相同面数 — routine 分支跳过。"""

    def test_simplify_cube_to_6_faces(self):
        """立方体简化 — routine 分支跳过。"""

    def test_quadric_matrix_symmetry(self):
        """Q 矩阵对称性 — routine 分支跳过。"""


if __name__ == "__main__":
    unittest.main()