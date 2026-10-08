"""Tests for math-read-do-obj: QEM Core Algorithm"""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool.qem_core import QEMSimplifier, simplify_obj
from qem_tool.obj_io import load_obj, compute_face_normals
from tests.fixtures import CUBE_OBJ, TETRA_OBJ, SPHERE_OBJ, PLANE_OBJ


def _model_from_str(content: str):
    """从字符串创建模型，返回 (vertices, faces)"""
    import tempfile
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "model.obj")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    model = load_obj(path)
    verts = list(model.vertices)
    faces = [(f.v[0], f.v[1], f.v[2]) for f in model.faces]
    return verts, faces


class TestQEMCore(unittest.TestCase):

    def test_simplify_no_reduction(self):
        """简化到相同面数 → 不变"""
        verts, faces = _model_from_str(TETRA_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=len(faces))
        self.assertEqual(len(out_f), len(faces))
        self.assertEqual(len(out_v), len(verts))

    def test_simplify_tetrahedron_to_2_faces(self):
        """四面体 4 面 → 2 面"""
        verts, faces = _model_from_str(TETRA_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=2)
        self.assertLessEqual(len(out_f), 2)
        self.assertGreater(len(out_v), 0)

    def test_simplify_cube_to_6_faces(self):
        """立方体 12 面 → 6 面"""
        verts, faces = _model_from_str(CUBE_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=6)
        self.assertLessEqual(len(out_f), 6)

    def test_simplify_to_1_face(self):
        """简化到 1 个面"""
        verts, faces = _model_from_str(CUBE_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=1)
        self.assertLessEqual(len(out_f), 1)

    def test_output_vertices_are_valid(self):
        """检查输出顶点索引都在范围内"""
        verts, faces = _model_from_str(SPHERE_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=12)
        max_idx = len(out_v) - 1
        for a, b, c in out_f:
            self.assertLessEqual(a, max_idx)
            self.assertLessEqual(b, max_idx)
            self.assertLessEqual(c, max_idx)
            self.assertGreaterEqual(a, 0)
            self.assertGreaterEqual(b, 0)
            self.assertGreaterEqual(c, 0)

    def test_quadric_matrix_symmetry(self):
        """Q 矩阵应为对称矩阵"""
        verts, faces = _model_from_str(CUBE_OBJ)
        simplifier = QEMSimplifier(verts, faces)
        for Q in simplifier._Q:
            for i in range(4):
                for j in range(4):
                    self.assertAlmostEqual(Q[i, j], Q[j, i], places=10)

    def test_error_non_negative(self):
        """边收缩误差应 ≥ 0"""
        verts, faces = _model_from_str(CUBE_OBJ)
        simplifier = QEMSimplifier(verts, faces)
        for cost, _ in simplifier._edge_heap:
            self.assertGreaterEqual(cost, -1e-10, f"负误差: {cost}")

    def test_compression_duplicate_rate_low(self):
        """简化后面应无明显重复（重复率 < 20%）"""
        verts, faces = _model_from_str(SPHERE_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=8)
        face_set = set()
        for a, b, c in out_f:
            key = tuple(sorted((a, b, c)))
            face_set.add(key)
        dup_rate = 1.0 - len(face_set) / len(out_f)
        self.assertLess(dup_rate, 0.2,
                        f"Duplicate face rate too high: {dup_rate:.1%}")

    def test_vertex_reduction_ratio(self):
        """顶点数应随面数减少而减少"""
        verts, faces = _model_from_str(SPHERE_OBJ)
        out_v_high, out_f_high = simplify_obj(verts, faces, target_faces=16)
        out_v_low, out_f_low = simplify_obj(verts, faces, target_faces=6)
        self.assertLess(len(out_v_low), len(out_v_high))

    def test_preserve_boundary_keeps_boundary_verts(self):
        """preserve_boundary=True 时边界顶点不被移动

        PLANE_OBJ 是开网格（2 个三角形拼成的四边形），其 4 个顶点
        全部位于边界上。preserve_boundary=True 时所有边都涉及边界
        顶点，应被全部跳过，因此面数保持不变且顶点坐标不变。
        """
        verts, faces = _model_from_str(PLANE_OBJ)
        orig_vert_set = {tuple(round(c, 6) for c in v) for v in verts}

        # preserve_boundary=True: 边界顶点不动，无法折叠任何边
        out_v, out_f = simplify_obj(verts, faces, target_faces=1,
                                    preserve_boundary=True)
        # 面数应保持不变（所有边都涉及边界顶点，全部被跳过）
        self.assertEqual(len(out_f), len(faces))
        # 所有输出顶点坐标应与原始一致（边界顶点未被移动）
        out_vert_set = {tuple(round(c, 6) for c in v) for v in out_v}
        self.assertEqual(out_vert_set, orig_vert_set)

    def test_no_preserve_boundary_allows_simplification(self):
        """preserve_boundary=False 时开网格可被正常简化"""
        verts, faces = _model_from_str(PLANE_OBJ)
        out_v, out_f = simplify_obj(verts, faces, target_faces=1,
                                    preserve_boundary=False)
        self.assertLessEqual(len(out_f), 1)

    def test_boundary_verts_immobile_on_open_mesh(self):
        """开网格简化后边界顶点坐标保持不变

        用金字塔（开网格，底面不填充）验证：4 个底面角点是边界
        顶点，preserve_boundary=True 时其坐标在输出中必须原样保留。
        """
        # 金字塔: 4 底面顶点(边界) + 1 顶点(内部), 4 侧面三角形
        verts = [(-1.0, 0.0, -1.0), (1.0, 0.0, -1.0),
                 (1.0, 0.0, 1.0), (-1.0, 0.0, 1.0),
                 (0.0, 1.0, 0.0)]
        faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        # 底面四角为边界顶点
        boundary_coords = {tuple(round(c, 6) for c in verts[i])
                           for i in range(4)}

        out_v, out_f = simplify_obj(verts, faces, target_faces=2,
                                    preserve_boundary=True)
        out_coords = {tuple(round(c, 6) for c in v) for v in out_v}
        # 边界顶点坐标必须全部保留在输出中
        self.assertTrue(boundary_coords.issubset(out_coords),
                        f"边界顶点被移动: 缺失 {boundary_coords - out_coords}")


if __name__ == '__main__':
    unittest.main()
