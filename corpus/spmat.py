#!/usr/bin/env python3
"""
稀疏三元组 (.spmat) 解析库
==========================

.spmat 文件格式: 每行一个三元组 "row col value"（空白分隔），
索引为 1-based（MATLAB 兼容），解析后转为 0-based 内部表示。

来源: intrinsic-simplification 实验导出的稀疏矩阵
（ICE_Experiment_Logs/matrices/，登记见 corpus/golden/checksums.json）。
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class SpmatData:
    """解析后的稀疏矩阵: 维度 + COO 三元组（0-based）。"""

    rows: int                 # 行数（= 文件中最大行索引）
    cols: int                 # 列数（= 文件中最大列索引）
    nnz: int                  # 条目数（= 有效三元组行数，含显式零）
    row_idx: np.ndarray       # shape (nnz,), int64, 0-based
    col_idx: np.ndarray       # shape (nnz,), int64, 0-based
    values: np.ndarray        # shape (nnz,), float64

    def row_sums(self) -> np.ndarray:
        """每行元素和，shape (rows,)。无条目的行和为 0。"""
        return np.bincount(self.row_idx, weights=self.values, minlength=self.rows)

    def diag_values(self) -> np.ndarray:
        """对角条目（row == col）的值组成的数组。"""
        mask = self.row_idx == self.col_idx
        return self.values[mask]

    def offdiag_min(self) -> float:
        """非对角条目的最小值；不存在非对角条目时返回 nan。"""
        mask = self.row_idx != self.col_idx
        if not np.any(mask):
            return float("nan")
        return float(self.values[mask].min())


def parse_spmat(path) -> SpmatData:
    """
    解析 .spmat 文件（每行 "row col value"，1-based 索引）。

    空行或无法解析的行抛 ValueError（含文件名与行号），绝不静默跳过——
    金样本被静默截断会造成假阴性。
    """
    path = Path(path)
    row_list = []
    col_list = []
    val_list = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(
                    f"{path.name}:{lineno}: 非法行（期望 'row col value' 三元组）: {line.strip()!r}"
                )
            try:
                r = int(parts[0])
                c = int(parts[1])
                v = float(parts[2])
            except ValueError as exc:
                raise ValueError(
                    f"{path.name}:{lineno}: 无法解析三元组 {line.strip()!r} ({exc})"
                ) from None
            if r < 1 or c < 1:
                raise ValueError(
                    f"{path.name}:{lineno}: 索引必须为 1-based 正整数: {line.strip()!r}"
                )
            row_list.append(r - 1)
            col_list.append(c - 1)
            val_list.append(v)
    if not row_list:
        raise ValueError(f"{path.name}: 文件不含任何三元组")
    row_idx = np.asarray(row_list, dtype=np.int64)
    col_idx = np.asarray(col_list, dtype=np.int64)
    values = np.asarray(val_list, dtype=np.float64)
    return SpmatData(
        rows=int(row_idx.max()) + 1,
        cols=int(col_idx.max()) + 1,
        nnz=len(values),
        row_idx=row_idx,
        col_idx=col_idx,
        values=values,
    )
