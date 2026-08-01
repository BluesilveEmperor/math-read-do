"""
OBJ File Reader/Writer — 纯 Python，无外部依赖
==============================================

Spec: https://en.wikipedia.org/wiki/Wavefront_.obj_file

支持的格式:
  - 顶点:        v x y z
  - 纹理坐标:    vt u v
  - 法线:        vn x y z
  - 面:          f v1 v2 v3          (仅顶点索引)
                 f v1/vt1 v2/vt2 v3/vt3         (含纹理)
                 f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3  (含纹理+法线)
                 f v1//vn1 v2//vn2 v3//vn3       (仅法线)
  - 组:          g group_name
  - 对象:        o object_name

输出约定: 索引从 0 开始（内部），导出时自动 +1 转为 OBJ 格式
"""

import math
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Face:
    """三角形面，索引 0-based"""
    v: Tuple[int, int, int]           # 顶点索引
    vt: Optional[Tuple[int, int, int]] = None  # 纹理坐标索引
    vn: Optional[Tuple[int, int, int]] = None  # 法线索引


@dataclass
class OBJModel:
    """内存中的 .obj 模型表示"""
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    texcoords: List[Tuple[float, float]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)
    faces: List[Face] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    object_name: str = ""

    def num_faces(self) -> int:
        return len(self.faces)

    def num_vertices(self) -> int:
        return len(self.vertices)

    def bounds(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Return (min, max) corners of bounding box"""
        if not self.vertices:
            return (0, 0, 0), (0, 0, 0)
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def center(self) -> Tuple[float, float, float]:
        """Return center of bounding box"""
        lo, hi = self.bounds()
        return ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2)


def load_obj(path: str) -> OBJModel:
    """
    加载 .obj 文件。索引从 1-based (文件格式) 转为 0-based (内存格式)。

    与原始 C++ 实现的差异（优化点）:
      1. 支持空行/注释（以 # 开头）
      2. 支持四边形面自动三角化
      3. 支持 f v1 v2 v3 和 f v1/vt1/vn1等多种格式
      4. 健壮的空格/制表符处理
    """
    model = OBJModel()
    base_dir = os.path.dirname(path)

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if not parts:
                continue

            keyword = parts[0]

            if keyword == 'v':
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                model.vertices.append((x, y, z))

            elif keyword == 'vt':
                u = float(parts[1])
                v = float(parts[2]) if len(parts) > 2 else 0.0
                model.texcoords.append((u, v))

            elif keyword == 'vn':
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                model.normals.append((x, y, z))

            elif keyword == 'f':
                # 解析面顶点索引 (1-based in file)
                face_verts = _parse_face_vertices(parts[1:])
                # 三角化: 如果 > 3 个顶点，拆成 triangle fan
                for i in range(1, len(face_verts) - 1):
                    v = (face_verts[0][0], face_verts[i][0], face_verts[i + 1][0])
                    vt = None
                    vn = None
                    # 检查纹理坐标一致性
                    if all(fv[1] is not None for fv in [face_verts[0], face_verts[i], face_verts[i + 1]]):
                        vt = (face_verts[0][1], face_verts[i][1], face_verts[i + 1][1])
                    if all(fv[2] is not None for fv in [face_verts[0], face_verts[i], face_verts[i + 1]]):
                        vn = (face_verts[0][2], face_verts[i][2], face_verts[i + 1][2])
                    model.faces.append(Face(v=v, vt=vt, vn=vn))

            elif keyword == 'o':
                model.object_name = parts[1] if len(parts) > 1 else ""

            elif keyword == 'g':
                model.groups = parts[1:]

    return model


def _parse_face_vertices(tokens: List[str]) -> List[Tuple[int, Optional[int], Optional[int]]]:
    """
    解析面顶点, 返回 [(v, vt, vn), ...] (0-based)

    支持格式:
      f v1 v2 v3
      f v1/vt1 v2/vt2 v3/vt3
      f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
      f v1//vn1 v2//vn2 v3//vn3
    """
    result = []
    for token in tokens:
        subs = token.split('/')
        v = int(subs[0]) - 1  # OBJ 1-based → 0-based
        vt = int(subs[1]) - 1 if len(subs) > 1 and subs[1] != '' else None
        vn = int(subs[2]) - 1 if len(subs) > 2 and subs[2] != '' else None
        result.append((v, vt, vn))
    return result


def export_obj(model: OBJModel, path: str) -> None:
    """
    导出为 .obj 文件。索引 0-based → 1-based。

    与原始 C++ exportToOBJ 的差异（优化点）:
      1. 输出法线 vn 和纹理坐标 vt（原版只输出 v 和 f）
      2. 输出结构化分组 (o / g)
      3. 数值精度控制
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# Generated by QEM Simplification Tool\n")
        f.write(f"# Vertices: {len(model.vertices)}, Faces: {len(model.faces)}\n")
        f.write(f"\n")

        if model.object_name:
            f.write(f"o {model.object_name}\n")

        # 顶点
        for v in model.vertices:
            f.write(f"v {v[0]:.8f} {v[1]:.8f} {v[2]:.8f}\n")

        # 纹理坐标
        for vt in model.texcoords:
            f.write(f"vt {vt[0]:.8f} {vt[1]:.8f}\n")

        # 法线
        for vn in model.normals:
            f.write(f"vn {vn[0]:.8f} {vn[1]:.8f} {vn[2]:.8f}\n")

        # 面 (OBJ 索引从 1 开始)
        has_vt = any(face.vt is not None for face in model.faces)
        has_vn = any(face.vn is not None for face in model.faces)

        for face in model.faces:
            if has_vt and has_vn:
                f.write(f"f {face.v[0]+1}/{face.vt[0]+1}/{face.vn[0]+1} "
                        f"{face.v[1]+1}/{face.vt[1]+1}/{face.vn[1]+1} "
                        f"{face.v[2]+1}/{face.vt[2]+1}/{face.vn[2]+1}\n")
            elif has_vt:
                f.write(f"f {face.v[0]+1}/{face.vt[0]+1} "
                        f"{face.v[1]+1}/{face.vt[1]+1} "
                        f"{face.v[2]+1}/{face.vt[2]+1}\n")
            elif has_vn:
                f.write(f"f {face.v[0]+1}//{face.vn[0]+1} "
                        f"{face.v[1]+1}//{face.vn[1]+1} "
                        f"{face.v[2]+1}//{face.vn[2]+1}\n")
            else:
                f.write(f"f {face.v[0]+1} {face.v[1]+1} {face.v[2]+1}\n")


def build_indexed_model(model: OBJModel) -> Tuple[List[Tuple[float, float, float]],
                                                   List[Tuple[float, float]],
                                                   List[Tuple[float, float, float]],
                                                   List[int]]:
    """
    将 OBJModel 转为索引化三角网格。

    Returns:
        (positions, texcoords, normals, indices)
        indices 是三角形顶点索引 (每 3 个一组)
        当模型无法提供纹理/法线时，返回空列表
    """
    positions = list(model.vertices)
    texcoords = list(model.texcoords) if model.texcoords else []
    normals = list(model.normals) if model.normals else []

    # 法线不存在时生成默认法线
    if not normals and positions:
        normals = [(0.0, 1.0, 0.0)] * len(positions)

    indices = []
    for face in model.faces:
        indices.extend([face.v[0], face.v[1], face.v[2]])

    return positions, texcoords, normals, indices


def compute_face_normals(vertices: List[Tuple[float, float, float]],
                         faces: List[Face]) -> List[Tuple[float, float, float]]:
    """
    计算每个面的法线（使用面法线加权平均为顶点法线）。

    如果不提供顶点法线，可以用这个方法生成。
    """
    # 面法线
    face_normals = []
    for face in faces:
        v0 = vertices[face.v[0]]
        v1 = vertices[face.v[1]]
        v2 = vertices[face.v[2]]
        n = _cross(_sub(v1, v0), _sub(v2, v0))
        n_len = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
        if n_len > 1e-12:
            n = (n[0] / n_len, n[1] / n_len, n[2] / n_len)
        face_normals.append(n)

    # 顶点法线（面法线加权平均）
    vertex_normals = [(0.0, 0.0, 0.0)] * len(vertices)
    counts = [0.0] * len(vertices)

    for i, face in enumerate(faces):
        area = _triangle_area(vertices[face.v[0]], vertices[face.v[1]], vertices[face.v[2]])
        for idx in face.v:
            vertex_normals[idx] = _add(vertex_normals[idx],
                                       (face_normals[i][0] * area,
                                        face_normals[i][1] * area,
                                        face_normals[i][2] * area))
            counts[idx] += area

    for i in range(len(vertex_normals)):
        if counts[i] > 0:
            vertex_normals[i] = (vertex_normals[i][0] / counts[i],
                                 vertex_normals[i][1] / counts[i],
                                 vertex_normals[i][2] / counts[i])
            n_len = math.sqrt(vertex_normals[i][0]**2 + vertex_normals[i][1]**2 + vertex_normals[i][2]**2)
            if n_len > 1e-12:
                vertex_normals[i] = (vertex_normals[i][0] / n_len,
                                     vertex_normals[i][1] / n_len,
                                     vertex_normals[i][2] / n_len)

    return vertex_normals


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def _triangle_area(v0, v1, v2):
    a = _sub(v1, v0)
    b = _sub(v2, v0)
    c = _cross(a, b)
    return 0.5 * math.sqrt(c[0]**2 + c[1]**2 + c[2]**2)
