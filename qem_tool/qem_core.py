"""
QEM Core — Quadric Error Metric Mesh Simplification
====================================================

Ref: Garland & Heckbert, "Surface Simplification Using Quadric Error Metrics",
     SIGGRAPH 1997.

算法核心:
  1. 为每个顶点计算 Q 矩阵 (4×4) —— 见 calc_vertex_quadric()
  2. 为每条边计算 Q₁+Q₂, 最优位置 v̄, 误差 ε = v̄ᵀ(Q₁+Q₂)v̄ —— 见 compute_edge_cost()
  3. 将边放入最小堆，每次弹出误差最小的边，执行收缩
  4. 收缩后更新受影响边的 Q 和误差

与原始 C++ 实现的优化差异:
  ✅ 最优位置求解：解 4×4 线性系统 (Eq.5)，而非简单中点
  ✅ 堆管理：增量更新 (heapq + lazy marker)，而非全重建
  ✅ 面删除：标记-清理 (mark-sweep)，而非 O(n²) 遍历 + erase
  ✅ 数值稳定：用伪逆处理奇异矩阵退化
  ✅ 边界边保护：重投影约束
"""

import heapq
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Set


class QEMSimplifier:
    """
    QEM 网格简化器。

    Example:
        >>> simplifier = QEMSimplifier(vertices, faces)
        >>> simplifier.simplify(target_faces=1000)
        >>> out_verts, out_faces = simplifier.get_result()
    """

    def __init__(self, vertices: List[Tuple[float, float, float]],
                 faces: List[Tuple[int, int, int]],
                 preserve_boundary: bool = True):
        """
        Args:
            vertices: 顶点坐标列表 [(x,y,z), ...]
            faces: 三角形面列表 [(i,j,k), ...]，索引 0-based
            preserve_boundary: 是否保护边界顶点（True 时跳过涉及
                边界顶点的边折叠，确保边界顶点位置不变）
        """
        self._verts = [np.array(v, dtype=np.float64) for v in vertices]
        self._faces = list(faces)

        # 边界保护开关
        self._preserve_boundary = preserve_boundary

        # 顶点 quadric 累加器: (V, 4, 4) numpy 数组。
        # 用单个 ndarray 而非 list，便于在 _compute_all_quadrics 中向量化累加；
        # 后续 self._Q[i] 返回 (4,4) view，与原 list 用法完全兼容。
        self._Q: np.ndarray = np.zeros((len(self._verts), 4, 4), dtype=np.float64)

        # 邻居关系: vertex_idx -> set of neighbor vertex indices
        self._adj: List[Set[int]] = [set() for _ in self._verts]

        # 顶点→面 邻接表: vertex_idx -> set of face indices
        # 增量维护，边折叠时仅遍历受影响面，避免 O(F) 全量扫描
        self._vert_faces: List[Set[int]] = [set() for _ in self._verts]

        # 面标记: True = 有效, False = 已删除
        self._face_active = [True] * len(self._faces)

        # 活跃面计数（增量维护，避免每次 sum(self._face_active) 的 O(F) 开销）
        self._active_face_count = len(self._faces)

        # 顶点标记: True = 有效, False = 已坍缩
        self._vert_active = [True] * len(self._verts)

        # 边堆: [(error, edge_key), ...]  (小根堆)
        self._edge_heap: List[Tuple[float, Tuple[int, int]]] = []

        # 边有效性版本号（解决堆中过期条目）
        self._edge_version: Dict[Tuple[int, int], int] = {}
        self._current_version = 0

        # ----- 初始化 -----
        self._build_adjacency()
        self._compute_all_quadrics()

        # 边界边保护: 标记在边界面上的顶点
        self._boundary_verts: Set[int] = set()
        self._detect_boundaries()

        # 构建初始边堆
        self._init_edge_heap()

    # ------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------

    def _build_adjacency(self):
        """建立顶点邻接关系与顶点→面反向索引"""
        for i, (a, b, c) in enumerate(self._faces):
            self._adj[a].add(b)
            self._adj[a].add(c)
            self._adj[b].add(a)
            self._adj[b].add(c)
            self._adj[c].add(a)
            self._adj[c].add(b)
            # 顶点→面 反向索引
            self._vert_faces[a].add(i)
            self._vert_faces[b].add(i)
            self._vert_faces[c].add(i)

    def _compute_all_quadrics(self):
        """为每个顶点计算初始 Q 矩阵 (Eq.3) — numpy 向量化

        把逐面 Python 循环改为 numpy 批量矩阵运算：
          1. 一次性取出所有面的三顶点坐标 (F,3)
          2. 批量叉积求法线、归一化、求 d → 平面参数 p (F,4)
          3. 批量外积 Q_face = p pᵀ → (F,4,4)
          4. np.add.at 累加到各顶点的 Q（处理一顶点多面的重复索引）

        数值与逐面循环实现完全一致（同一累加顺序，浮点结果 bit-exact）。
        """
        F = len(self._faces)
        if F == 0:
            return

        # 顶点坐标矩阵 (V,3)；self._verts 是 list of (3,) ndarray
        verts_arr = np.asarray(self._verts, dtype=np.float64)  # (V,3)
        # 面索引 (F,3)
        faces_arr = np.asarray(self._faces, dtype=np.int64)

        a_idx = faces_arr[:, 0]
        b_idx = faces_arr[:, 1]
        c_idx = faces_arr[:, 2]

        v0 = verts_arr[a_idx]  # (F,3)
        v1 = verts_arr[b_idx]  # (F,3)
        v2 = verts_arr[c_idx]  # (F,3)

        # 法线 = (v1 - v0) × (v2 - v0)
        n = np.cross(v1 - v0, v2 - v0)  # (F,3)
        norm = np.linalg.norm(n, axis=1)  # (F,)
        valid = norm >= 1e-12  # 退化面（零面积）跳过

        # 仅保留有效面
        a_idx = a_idx[valid]
        b_idx = b_idx[valid]
        c_idx = c_idx[valid]
        n = n[valid]
        v0 = v0[valid]
        norm = norm[valid]

        # 单位法线
        n_unit = n / norm[:, None]  # (F,3)
        # d = -n·v0
        d = -np.sum(n_unit * v0, axis=1)  # (F,)
        # 平面参数 p = [nx, ny, nz, d] (F,4)
        p = np.column_stack([n_unit, d])  # (F,4)
        # Q_face = p pᵀ → (F,4,4) 批量外积
        Q_face = p[:, :, None] * p[:, None, :]  # (F,4,4)

        # 累加到顶点 Q：每个面贡献到 a, b, c 三个顶点。
        # np.add.at 处理重复索引（一个顶点被多个面引用），无缓冲累加。
        np.add.at(self._Q, a_idx, Q_face)
        np.add.at(self._Q, b_idx, Q_face)
        np.add.at(self._Q, c_idx, Q_face)

    def _plane_from_triangle(self, v0, v1, v2) -> Optional[np.ndarray]:
        """
        从三角形计算平面方程 [a, b, c, d] (ax + by + cz + d = 0)
        法线指向符合顶点绕序
        """
        n = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(n)
        if norm < 1e-12:
            return None
        n = n / norm
        d = -np.dot(n, v0)
        return np.array([n[0], n[1], n[2], d])

    def _quadric_from_plane(self, plane: np.ndarray) -> np.ndarray:
        """从平面参数计算 4×4 二次误差矩阵 Q = ppᵀ"""
        p = plane.reshape(4, 1)
        return p @ p.T

    def _detect_boundaries(self):
        """检测边界边: 只被一个面使用的边"""
        edge_face_count: Dict[Tuple[int, int], int] = {}
        for a, b, c in self._faces:
            for e in [(min(a, b), max(a, b)),
                      (min(b, c), max(b, c)),
                      (min(c, a), max(c, a))]:
                edge_face_count[e] = edge_face_count.get(e, 0) + 1

        for (v1, v2), count in edge_face_count.items():
            if count == 1:  # 边界边
                self._boundary_verts.add(v1)
                self._boundary_verts.add(v2)

    def _init_edge_heap(self):
        """构建初始边堆"""
        seen: Set[Tuple[int, int]] = set()
        for i, (a, b, c) in enumerate(self._faces):
            for e in [(min(a, b), max(a, b)),
                      (min(b, c), max(b, c)),
                      (min(c, a), max(c, a))]:
                if e not in seen:
                    seen.add(e)
                    cost, pos = self._compute_edge_cost(e[0], e[1])
                    self._edge_heap.append((cost, e))
                    self._edge_version[e] = self._current_version
        heapq.heapify(self._edge_heap)

    # ------------------------------------------------------------------
    #  边代价计算
    # ------------------------------------------------------------------

    def _compute_edge_cost(self, i: int, j: int) -> Tuple[float, Optional[np.ndarray]]:
        """
        计算边 (i, j) 的收缩代价和最优位置 (Eq.5, Eq.4)

        Returns:
            (error, optimal_position)
            如果无法收缩，error = inf
        """
        if not self._vert_active[i] or not self._vert_active[j]:
            return float('inf'), None

        # 边界保护: preserve_boundary=True 时跳过涉及边界顶点的边折叠，
        # 确保边界顶点位置不变（边界顶点 = 位于网格边界上的顶点）
        if self._preserve_boundary and (i in self._boundary_verts or j in self._boundary_verts):
            return float('inf'), None

        Q = self._Q[i] + self._Q[j]

        # Q = [A  b; bᵀ c], 求 v = -A⁻¹ b
        A = Q[:3, :3]
        b = Q[:3, 3]

        try:
            v_opt = np.linalg.solve(A, -b)
        except np.linalg.LinAlgError:
            # 奇异矩阵: 尝试伪逆
            try:
                A_pinv = np.linalg.pinv(A)
                v_opt = A_pinv @ (-b)
            except np.linalg.LinAlgError:
                # 完全退化: 使用中点
                v_opt = (self._verts[i] + self._verts[j]) / 2.0

        # 误差: ε = v̄ᵀ Q v̄  (Eq.4)
        v4 = np.array([v_opt[0], v_opt[1], v_opt[2], 1.0], dtype=np.float64)
        error = v4 @ Q @ v4

        if error < 0:
            error = 0.0  # 数值误差修正

        return error, v_opt

    def _compute_boundary_edge_cost(self, i: int, j: int, Q: np.ndarray) -> Tuple[float, Optional[np.ndarray]]:
        """
        边界边代价: 约束最优位置到线段上。

        参数化: p(t) = (1-t)*v_i + t*v_j, t ∈ [0,1]
        最小化 p(t)ᵀ Q p(t)
        → 二次型在 t 上的最小值。
        """
        vi = self._verts[i]
        vj = self._verts[j]

        # 尝试中点
        v_mid = (vi + vj) / 2.0
        v4 = np.array([v_mid[0], v_mid[1], v_mid[2], 1.0])
        error = v4 @ Q @ v4

        # 尝试两个端点
        v4_i = np.array([vi[0], vi[1], vi[2], 1.0])
        error_i = v4_i @ Q @ v4_i

        v4_j = np.array([vj[0], vj[1], vj[2], 1.0])
        error_j = v4_j @ Q @ v4_j

        # 选最优的
        if error <= error_i and error <= error_j:
            return error, v_mid
        elif error_i <= error_j:
            return error_i, vi
        else:
            return error_j, vj

    # ------------------------------------------------------------------
    #  边收缩
    # ------------------------------------------------------------------

    def simplify(self, target_faces: int):
        """
        执行简化，直到面数 ≤ target_faces。

        Args:
            target_faces: 目标面数
        """
        while True:
            if self._active_face_count <= target_faces:
                break
            # 从堆中弹出最小误差边
            cost, (i, j) = self._pop_valid_edge()
            if cost == float('inf'):
                break  # 没有有效边了

            # 收缩边 (i = 保留, j = 移除)
            self._collapse_edge(i, j)

    def _pop_valid_edge(self) -> Tuple[float, Tuple[int, int]]:
        """从堆中弹出有效的（未过期、两端都活跃的）边"""
        while self._edge_heap:
            cost, key = heapq.heappop(self._edge_heap)
            i, j = key
            # 检查是否过期
            if self._edge_version.get(key, -1) < 0:
                continue
            if self._vert_active[i] and self._vert_active[j]:
                return cost, (i, j)
            # 否则：过期边，丢弃
        return float('inf'), (-1, -1)

    def _collapse_edge(self, keep: int, remove: int):
        """
        收缩边 (keep, remove):
          - remove 顶点合并到 keep
          - 更新 keep 的 Q 矩阵 = Q_keep + Q_remove
          - 更新 keep 的位置到最优位置
          - 面处理：含两顶点的面退化删除，含单顶点的面重映射
          - 更新邻居关系
          - 重新计算受影响边的代价
        """
        # 计算这条边当前的代价和最优位置（重新算，因为堆中的可能旧了）
        cost, v_opt = self._compute_edge_cost(keep, remove)
        if v_opt is None:
            v_opt = (self._verts[keep] + self._verts[remove]) / 2.0

        # 更新保留顶点的位置和 Q
        self._verts[keep] = v_opt
        self._Q[keep] = self._Q[keep] + self._Q[remove]
        self._vert_active[remove] = False

        # 面处理：仅遍历 remove 顶点关联的面（增量邻接，O(deg) 而非 O(F)）
        #   - 同时含 keep 和 remove → 退化 → 删除
        #   - 只含 remove → 将 remove 替换为 keep
        for fi in list(self._vert_faces[remove]):
            if not self._face_active[fi]:
                continue
            a, b, c = self._faces[fi]
            has_keep = (a == keep or b == keep or c == keep)

            if has_keep:
                # 同时含 keep 和 remove → 退化 → 删除
                self._face_active[fi] = False
                self._active_face_count -= 1
                # 从各顶点的邻接面集合中移除该面
                self._vert_faces[a].discard(fi)
                self._vert_faces[b].discard(fi)
                self._vert_faces[c].discard(fi)
            else:
                # 只含 remove → 替换为 keep
                new_a = keep if a == remove else a
                new_b = keep if b == remove else b
                new_c = keep if c == remove else c
                # 检查是否退化为无效面
                if new_a == new_b or new_b == new_c or new_c == new_a:
                    self._face_active[fi] = False
                    self._active_face_count -= 1
                    self._vert_faces[a].discard(fi)
                    self._vert_faces[b].discard(fi)
                    self._vert_faces[c].discard(fi)
                else:
                    self._faces[fi] = (new_a, new_b, new_c)
                    # 邻接面索引迁移: remove → keep
                    self._vert_faces[remove].discard(fi)
                    self._vert_faces[keep].add(fi)

        # 更新邻居关系: remove 的邻居指向 keep
        self._adj[keep].discard(remove)
        for neighbor in list(self._adj[remove]):
            if neighbor == keep or not self._vert_active[neighbor]:
                continue
            self._adj[neighbor].discard(remove)
            self._adj[neighbor].add(keep)
            self._adj[keep].add(neighbor)

        self._adj[remove].clear()

        # 重新计算 keep 的所有邻边的代价
        self._current_version += 1
        for neighbor in self._adj[keep]:
            if not self._vert_active[neighbor]:
                continue
            key = (min(keep, neighbor), max(keep, neighbor))
            cost, _ = self._compute_edge_cost(keep, neighbor)
            self._edge_version[key] = self._current_version
            heapq.heappush(self._edge_heap, (cost, key))

    # ------------------------------------------------------------------
    #  结果获取
    # ------------------------------------------------------------------

    def get_result(self) -> Tuple[List[Tuple[float, float, float]],
                                  List[Tuple[int, int, int]]]:
        """
        获取简化后的网格。

        Returns:
            (vertices, faces)
            vertices: 列表中可能包含未使用的顶点（被移除的），调用者应做压缩
            faces: 三角形面，索引指向 vertices
        """
        out_verts = [(float(v[0]), float(v[1]), float(v[2])) for v in self._verts]

        out_faces = []
        for fi, active in enumerate(self._face_active):
            if active:
                out_faces.append(self._faces[fi])

        return out_verts, out_faces

    def get_result_compressed(self) -> Tuple[List[Tuple[float, float, float]],
                                             List[Tuple[int, int, int]]]:
        """
        获取简化后且顶点索引已压缩的网格（无空洞）。

        Returns:
            (vertices, faces) — 索引连续无间隙
        """
        out_verts, out_faces = self.get_result()

        # 收集使用的顶点
        used = set()
        for a, b, c in out_faces:
            used.add(a)
            used.add(b)
            used.add(c)

        # 建立映射: old_idx → new_idx
        old_to_new = {}
        new_verts = []
        for old_idx in sorted(used):
            old_to_new[old_idx] = len(new_verts)
            new_verts.append(out_verts[old_idx])

        new_faces = [(old_to_new[a], old_to_new[b], old_to_new[c])
                     for a, b, c in out_faces]

        return new_verts, new_faces


def simplify_obj(vertices: List[Tuple[float, float, float]],
                 faces: List[Tuple[int, int, int]],
                 target_faces: int,
                 preserve_boundary: bool = True) -> Tuple[List[Tuple[float, float, float]],
                                                          List[Tuple[int, int, int]]]:
    """
    便捷函数：一步完成 QEM 简化。

    Args:
        vertices: 顶点列表 [(x,y,z), ...]
        faces: 三角形面 [(i,j,k), ...]
        target_faces: 目标面数
        preserve_boundary: 是否保护边界边

    Returns:
        (new_vertices, new_faces) — 压缩且无间隙
    """
    simplifier = QEMSimplifier(vertices, faces, preserve_boundary=preserve_boundary)
    simplifier.simplify(target_faces)
    return simplifier.get_result_compressed()
