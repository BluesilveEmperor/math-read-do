"""Tests for math-read-do-obj: QEM Core Algorithm"""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool.qem_core import QEMSimplifier, simplify_obj
from qem_tool.obj_io import load_obj, compute_face_normals
from tests.fixtures import CUBE_OBJ, TETRA_OBJ, SPHERE_OBJ


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


if __name__ == '__main__':
    unittest.main()
