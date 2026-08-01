"""Tests for math-read-do-obj: OBJ I/O"""

import os
import tempfile
import unittest

# 修改搜索路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qem_tool.obj_io import load_obj, export_obj, OBJModel, Face
from tests.fixtures import CUBE_OBJ, PLANE_OBJ, TETRA_OBJ


class TestObjIO(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _write_fixture(self, content, name="test.obj"):
        path = os.path.join(self.tmpdir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_load_cube(self):
        """加载立方体: 8 个顶点，12 个面"""
        path = self._write_fixture(CUBE_OBJ, "cube.obj")
        model = load_obj(path)
        self.assertEqual(len(model.vertices), 8)
        self.assertEqual(len(model.faces), 12)
        self.assertEqual(len(model.normals), 6)

    def test_load_plane_with_uv(self):
        """加载带纹理坐标的平面"""
        path = self._write_fixture(PLANE_OBJ, "plane.obj")
        model = load_obj(path)
        self.assertEqual(len(model.vertices), 4)
        self.assertEqual(len(model.faces), 2)
        self.assertEqual(len(model.texcoords), 4)
        # 检查纹理坐标
        for face in model.faces:
            self.assertIsNotNone(face.vt)

    def test_load_tetrahedron_no_uv_no_normals(self):
        """加载纯顶点/面的四面体"""
        path = self._write_fixture(TETRA_OBJ, "tetra.obj")
        model = load_obj(path)
        self.assertEqual(len(model.vertices), 4)
        self.assertEqual(len(model.faces), 4)
        for face in model.faces:
            self.assertIsNone(face.vt)
            self.assertIsNone(face.vn)

    def test_export_and_reimport(self):
        """导出后再导入，数据一致"""
        path = self._write_fixture(CUBE_OBJ, "cube.obj")
        model = load_obj(path)

        out_path = os.path.join(self.tmpdir, "reimport.obj")
        export_obj(model, out_path)

        model2 = load_obj(out_path)
        self.assertEqual(len(model2.vertices), 8)
        self.assertEqual(len(model2.faces), 12)
        # 顶点坐标一致
        for v1, v2 in zip(model.vertices, model2.vertices):
            self.assertAlmostEqual(v1[0], v2[0], places=6)
            self.assertAlmostEqual(v1[1], v2[1], places=6)
            self.assertAlmostEqual(v1[2], v2[2], places=6)

    def test_obj_object_name(self):
        """检查对象名"""
        path = self._write_fixture(CUBE_OBJ, "cube.obj")
        model = load_obj(path)
        self.assertEqual(model.object_name, "Cube")

    def test_compute_face_normals(self):
        """面法线计算"""
        from qem_tool.obj_io import compute_face_normals
        path = self._write_fixture(TETRA_OBJ, "tetra.obj")
        model = load_obj(path)
        normals = compute_face_normals(model.vertices, model.faces)
        self.assertEqual(len(normals), 4)
        for n in normals:
            # 法线应是单位向量
            length = (n[0]**2 + n[1]**2 + n[2]**2) ** 0.5
            self.assertAlmostEqual(length, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
