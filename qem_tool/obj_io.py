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

    def _to_float(token, lineno, what):
        """把 token 转 float，失败时抛出带中文消息和行号的 ValueError。"""
        try:
            return float(token)
        except (ValueError, TypeError):
            raise ValueError(
                f"第 {lineno} 行: {what} 字段不是合法数字: {token!r}"
            )

    with open(path, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if not parts:
                continue

            keyword = parts[0]

            if keyword == 'v':
                # 顶点至少需要 x y z 三个坐标
                if len(parts) < 4:
                    raise ValueError(
                        f"第 {lineno} 行: 顶点(v)缺少坐标分量，"
                        f"期望 'v x y z'，实际只有 {len(parts) - 1} 个字段: {line!r}"
                    )
                x = _to_float(parts[1], lineno, "顶点 x")
                y = _to_float(parts[2], lineno, "顶点 y")
                z = _to_float(parts[3], lineno, "顶点 z")
                model.vertices.append((x, y, z))

            elif keyword == 'vt':
                # 纹理坐标至少需要 u
                if len(parts) < 2:
                    raise ValueError(
                        f"第 {lineno} 行: 纹理坐标(vt)缺少 u 分量: {line!r}"
                    )
                u = _to_float(parts[1], lineno, "纹理 u")
                v = _to_float(parts[2], lineno, "纹理 v") if len(parts) > 2 else 0.0
                model.texcoords.append((u, v))

            elif keyword == 'vn':
                # 法线需要 x y z 三个分量
                if len(parts) < 4:
                    raise ValueError(
                        f"第 {lineno} 行: 法线(vn)缺少分量，"
                        f"期望 'vn x y z'，实际只有 {len(parts) - 1} 个字段: {line!r}"
                    )
                x = _to_float(parts[1], lineno, "法线 x")
                y = _to_float(parts[2], lineno, "法线 y")
                z = _to_float(parts[3], lineno, "法线 z")
                model.normals.append((x, y, z))

            elif keyword == 'f':
                # 解析面顶点索引 (1-based in file)
                face_verts = _parse_face_vertices(parts[1:], lineno)
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

    # 统一校验面引用的顶点/纹理/法线索引是否越界。
    # 放在末尾校验以兼容顶点定义在面之后的非标准但实际存在的 OBJ 文件。
    _validate_indices(model, path)

    return model


def _validate_indices(model: OBJModel, path: str) -> None:
    """校验所有面引用的顶点/纹理/法线索引都在合法范围内，越界则抛出 ValueError。"""
    n_v = len(model.vertices)
    n_vt = len(model.texcoords)
    n_vn = len(model.normals)
    for fi, face in enumerate(model.faces):
        for slot, idx in zip(('v[0]', 'v[1]', 'v[2]'), face.v):
            if idx < 0 or idx >= n_v:
                raise ValueError(
                    f"文件 {os.path.basename(path)}: 第 {fi + 1} 个面引用了"
                    f"不存在的顶点索引 {idx + 1}（1-based），"
                    f"顶点总数为 {n_v}（合法范围 1..{n_v}），字段 {slot}"
                )
        if face.vt is not None:
            for slot, idx in zip(('vt[0]', 'vt[1]', 'vt[2]'), face.vt):
                if idx < 0 or idx >= n_vt:
                    raise ValueError(
                        f"文件 {os.path.basename(path)}: 第 {fi + 1} 个面引用了"
                        f"不存在的纹理坐标索引 {idx + 1}（1-based），"
                        f"纹理坐标总数为 {n_vt}（合法范围 1..{n_vt}），字段 {slot}"
                    )
        if face.vn is not None:
            for slot, idx in zip(('vn[0]', 'vn[1]', 'vn[2]'), face.vn):
                if idx < 0 or idx >= n_vn:
                    raise ValueError(
                        f"文件 {os.path.basename(path)}: 第 {fi + 1} 个面引用了"
                        f"不存在的法线索引 {idx + 1}（1-based），"
                        f"法线总数为 {n_vn}（合法范围 1..{n_vn}），字段 {slot}"
                    )


def _parse_face_vertices(tokens: List[str], lineno: int = 0) -> List[Tuple[int, Optional[int], Optional[int]]]:
    """
    解析面顶点, 返回 [(v, vt, vn), ...] (0-based)

    支持格式:
      f v1 v2 v3
      f v1/vt1 v2/vt2 v3/vt3
      f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
      f v1//vn1 v2//vn2 v3//vn3

    非数字字段会抛出带中文消息和行号的 ValueError。
    """
    def _to_int(token, what):
        try:
            return int(token)
        except (ValueError, TypeError):
            raise ValueError(
                f"第 {lineno} 行: 面{what}索引不是合法整数: {token!r}"
            )

    result = []
    for token in tokens:
        subs = token.split('/')
        v = _to_int(subs[0], "顶点") - 1  # OBJ 1-based → 0-based
        vt = _to_int(subs[1], "纹理") - 1 if len(subs) > 1 and subs[1] != '' else None
        vn = _to_int(subs[2], "法线") - 1 if len(subs) > 2 and subs[2] != '' else None
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
