"""金样本矩阵回归测试
====================

覆盖 corpus/golden/ 登记的 18 个 intrinsic-simplification 稀疏矩阵：

- spot 系列（9 个，已入库）: 完整性自检（sha256/bytes）+ 按 kind 的数学性质断言
- dragon 系列（9 个，仅校验和登记）: ICE_GOLDEN_DRAGON_DIR 未设置时 SKIP，
  设置后对 sha256/bytes/dims/nnz/统计范围做全量校验

性质断言以实测为准（容差依据与已知现象见 corpus/golden/README.md）：

- 标量延拓 P: 每行行和=1（atol 1e-9）且取值 ∈ [0,1]
- Laplacian L: 行和≈0（atol 1e-10）、对角元<0、严格对称
  （注: 非对角元可为负——简化后内在三角化非 Delaunay，钝角 cotan 权重为负，
  "非对角≥0"断言已被实测推翻，按实测修正为对称性断言，见 README 已知现象 3）
- 质量矩阵 M: 纯对角且对角元>0
- 向量延拓 P(re,im): 非空行逐行条目模长之和=1（atol 1e-9）、
  复数行和模长 ≤ 1+1e-9（spot 有 30 行为上游跳过的空行，见 README 已知现象 2）
- 连接 Laplacian(re,im): re 对角>0 且对称、im 对角==0 且反对称
- 向量质量矩阵(re,im): re 纯对角且对角>0、im 全零

dragon 系列获取（未入库，体积考虑）
----------------------------------
dragon 系列 9 个 .spmat 矩阵文件单文件最大 1.4 MB+，整体不入库，仅以校验和登记。
数据来源: intrinsic-simplification (SIGGRAPH 2023) 实验导出，原始路径::

    <obj_exp>/ICE_Experiment_Logs/matrices/01_dragon_{prolongation,laplace,mass}.spmat
    <obj_exp>/ICE_Experiment_Logs/matrices/05_vector_{prolongation,mass}_{re,im}.spmat
    <obj_exp>/ICE_Experiment_Logs/matrices/05_connection_laplace_{re,im}.spmat

对应的输入网格为 dragon_fat.obj（15,746 顶点，见 corpus/MANIFEST.json）。
获取后通过环境变量 ICE_GOLDEN_DRAGON_DIR 指向 .spmat 所在目录即可启用全量校验::

    # pwsh
    $env:ICE_GOLDEN_DRAGON_DIR = "<obj_exp>/ICE_Experiment_Logs/matrices"
    python -m pytest tests/test_golden_matrices.py -v

    # bash
    export ICE_GOLDEN_DRAGON_DIR="<obj_exp>/ICE_Experiment_Logs/matrices"
    python -m pytest tests/test_golden_matrices.py -v

详见 corpus/golden/README.md「dragon 系列获取与用法」。
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

# 修改搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from corpus.spmat import parse_spmat

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = REPO_ROOT / "corpus" / "golden"
SPOT_DIR = GOLDEN_DIR / "spot"
CHECKSUMS_PATH = GOLDEN_DIR / "checksums.json"
DRAGON_ENV = "ICE_GOLDEN_DRAGON_DIR"

REQUIRED_FIELDS = {
    "filename", "series", "kind", "stage", "in_repo", "bytes", "sha256",
    "rows", "cols", "nnz", "value_min", "value_max", "rowsum_min", "rowsum_max", "notes",
}


def _load_checksums():
    with open(CHECKSUMS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["matrices"]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _max_asym(m):
    """max |L_ij - L_ji|（要求转置条目全覆盖，缺失即断言失败）。"""
    d = {}
    for r, c, v in zip(m.row_idx, m.col_idx, m.values):
        d[(int(r), int(c))] = float(v)
    worst = 0.0
    for (i, j), v in d.items():
        t = d.get((j, i))
        assert t is not None, f"缺少转置条目 ({j}, {i})"
        worst = max(worst, abs(v - t))
    return worst


def _max_antisym(m):
    """max |L_ij + L_ji|（反对称性偏差，要求转置条目全覆盖）。"""
    d = {}
    for r, c, v in zip(m.row_idx, m.col_idx, m.values):
        d[(int(r), int(c))] = float(v)
    worst = 0.0
    for (i, j), v in d.items():
        t = d.get((j, i))
        assert t is not None, f"缺少转置条目 ({j}, {i})"
        worst = max(worst, abs(v + t))
    return worst


CHECKSUMS = _load_checksums()
SPOT_ENTRIES = [m for m in CHECKSUMS if m["series"] == "spot"]
DRAGON_ENTRIES = [m for m in CHECKSUMS if m["series"] == "dragon"]


# ---------- 清单 schema ----------

def test_checksums_registry_schema():
    """checksums.json: 18 条、字段齐备、series/in_repo 标记自洽。"""
    assert len(CHECKSUMS) == 18
    filenames = [m["filename"] for m in CHECKSUMS]
    assert len(set(filenames)) == 18
    for m in CHECKSUMS:
        assert REQUIRED_FIELDS <= set(m.keys()), f"缺少字段: {m['filename']}"
    assert len(SPOT_ENTRIES) == 9
    assert len(DRAGON_ENTRIES) == 9
    assert all(m["in_repo"] for m in SPOT_ENTRIES)
    assert all(not m["in_repo"] for m in DRAGON_ENTRIES)


# ---------- spot 完整性自检 ----------

@pytest.mark.parametrize("entry", SPOT_ENTRIES, ids=lambda e: e["filename"])
def test_spot_file_integrity(entry):
    """spot 金样本文件与 checksums.json 的 bytes/sha256 逐字节一致。"""
    path = SPOT_DIR / entry["filename"]
    assert path.is_file(), f"金样本文件缺失: {path}"
    actual_bytes = path.stat().st_size
    assert actual_bytes == entry["bytes"], \
        f"{entry['filename']} bytes: 期望 {entry['bytes']}, 实际 {actual_bytes}"
    actual_sha = _sha256(path)
    assert actual_sha == entry["sha256"], \
        f"{entry['filename']} sha256: 期望 {entry['sha256']}, 实际 {actual_sha}"


# ---------- spot 性质断言 ----------

def test_spot_scalar_prolongation():
    """标量延拓: 每行行和=1（重心插值权重）且取值 ∈ [0,1]。"""
    m = parse_spmat(SPOT_DIR / "01_prolongation.spmat")
    assert np.allclose(m.row_sums(), 1.0, atol=1e-9)
    assert (m.values >= 0.0).all()
    assert (m.values <= 1.0).all()


def test_spot_laplacian():
    """Cotan Laplacian: 行和≈0、对角元<0、严格对称。"""
    m = parse_spmat(SPOT_DIR / "01_laplace.spmat")
    assert np.allclose(m.row_sums(), 0.0, atol=1e-10)
    assert (m.diag_values() < 0.0).all()
    assert _max_asym(m) == pytest.approx(0.0, abs=1e-12)


def test_spot_mass():
    """质量矩阵: 纯对角且对角元>0。"""
    m = parse_spmat(SPOT_DIR / "01_mass.spmat")
    assert m.rows == m.cols
    assert m.nnz == m.rows
    assert (m.row_idx == m.col_idx).all()
    assert (m.diag_values() > 0.0).all()


def test_spot_vector_prolongation_pair():
    """向量延拓 (re,im): 非空行逐行条目模长之和=1、复数行和模长 ≤ 1+容差。"""
    re = parse_spmat(SPOT_DIR / "05_spot_vprolong_re.spmat")
    im = parse_spmat(SPOT_DIR / "05_spot_vprolong_im.spmat")
    # re/im 同稀疏模式，逐条目配对为复数
    assert re.nnz == im.nnz
    assert (re.row_idx == im.row_idx).all()
    assert (re.col_idx == im.col_idx).all()
    # 非空行: 每行 Σ|entry| = 1（条目 = 重心权重 × 单位旋转传输系数）
    mod_sums = np.bincount(
        re.row_idx,
        weights=np.sqrt(re.values ** 2 + im.values ** 2),
        minlength=re.rows,
    )
    nonempty = np.unique(re.row_idx)
    # 30/2930 行为上游跳过的空行（切线空间对应失败, get_vertex_vector_prolongation.cpp:71）
    assert len(nonempty) == 2900
    assert np.allclose(mod_sums[nonempty], 1.0, atol=1e-9)
    # 复数行和模长 ≤ 1 + 1e-9
    csum = re.row_sums() + 1j * im.row_sums()
    assert (np.abs(csum) <= 1.0 + 1e-9).all()


def test_spot_connection_laplacian_pair():
    """连接 Laplacian (re,im): re 对角>0 且对称、im 对角==0 且反对称。"""
    re = parse_spmat(SPOT_DIR / "05_spot_claplace_re.spmat")
    im = parse_spmat(SPOT_DIR / "05_spot_claplace_im.spmat")
    assert (re.diag_values() > 0.0).all()
    assert (im.diag_values() == 0.0).all()
    assert _max_asym(re) == pytest.approx(0.0, abs=1e-12)
    assert _max_antisym(im) == pytest.approx(0.0, abs=1e-12)


def test_spot_vector_mass_pair():
    """向量质量矩阵 (re,im): re 纯对角且对角>0、im 全零。"""
    re = parse_spmat(SPOT_DIR / "05_spot_vmass_re.spmat")
    im = parse_spmat(SPOT_DIR / "05_spot_vmass_im.spmat")
    assert re.rows == re.cols
    assert re.nnz == re.rows
    assert (re.row_idx == re.col_idx).all()
    assert (re.diag_values() > 0.0).all()
    assert (im.values == 0.0).all()


# ---------- spmat 解析器（D9: 非法输入显式报错） ----------

def test_parse_spmat_rejects_blank_line(tmp_path):
    p = tmp_path / "bad_blank.spmat"
    p.write_text("1 1 0.5\n\n1 2 0.3\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad_blank\.spmat:2"):
        parse_spmat(p)


def test_parse_spmat_rejects_malformed_line(tmp_path):
    p = tmp_path / "bad_tok.spmat"
    p.write_text("1 1 0.5\nnot a triplet\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad_tok\.spmat:2"):
        parse_spmat(p)


def test_parse_spmat_rejects_zero_based_index(tmp_path):
    p = tmp_path / "bad_idx.spmat"
    p.write_text("0 1 0.5\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad_idx\.spmat:1"):
        parse_spmat(p)


# ---------- dragon 分支（外部数据，经 ICE_GOLDEN_DRAGON_DIR） ----------

def _dragon_dir():
    d = os.environ.get(DRAGON_ENV)
    if not d:
        pytest.skip(
            f"未设置 {DRAGON_ENV}: dragon 系列 9 个 .spmat 矩阵未入库（单文件最大 "
            f"1.4 MB+，体积考虑仅校验和登记）。\n"
            f"  获取方式: 从 intrinsic-simplification 实验数据目录拷贝 9 个 dragon "
            f".spmat 文件，来源路径:\n"
            f"    <obj_exp>/ICE_Experiment_Logs/matrices/"
            f"01_dragon_*.spmat, 05_vector_*.spmat, 05_connection_laplace_*.spmat\n"
            f"  启用全量校验:\n"
            f"    pwsh:  $env:{DRAGON_ENV} = '<obj_exp>\\ICE_Experiment_Logs\\matrices'\n"
            f"    bash:  export {DRAGON_ENV}='<obj_exp>/ICE_Experiment_Logs/matrices'\n"
            f"  详见 corpus/golden/README.md「dragon 系列获取与用法」。"
        )
    return Path(d)


@pytest.mark.parametrize("entry", DRAGON_ENTRIES, ids=lambda e: e["filename"])
def test_dragon_matrix_full_check(entry):
    """dragon 全量校验: sha256/bytes/dims/nnz + 取值与行和统计范围。"""
    ddir = _dragon_dir()
    path = ddir / entry["filename"]
    assert path.is_file(), \
        f"dragon 文件缺失: {path}（{DRAGON_ENV}={ddir}）"

    actual_bytes = path.stat().st_size
    assert actual_bytes == entry["bytes"], \
        f"{entry['filename']} bytes: 期望 {entry['bytes']}, 实际 {actual_bytes}"
    actual_sha = _sha256(path)
    assert actual_sha == entry["sha256"], \
        f"{entry['filename']} sha256: 期望 {entry['sha256']}, 实际 {actual_sha}"

    m = parse_spmat(path)
    assert m.rows == entry["rows"], \
        f"{entry['filename']} rows: 期望 {entry['rows']}, 实际 {m.rows}"
    assert m.cols == entry["cols"], \
        f"{entry['filename']} cols: 期望 {entry['cols']}, 实际 {m.cols}"
    assert m.nnz == entry["nnz"], \
        f"{entry['filename']} nnz: 期望 {entry['nnz']}, 实际 {m.nnz}"

    assert m.values.min() == pytest.approx(entry["value_min"], rel=1e-9, abs=1e-15), \
        f"{entry['filename']} value_min: 期望 {entry['value_min']}, 实际 {m.values.min()}"
    assert m.values.max() == pytest.approx(entry["value_max"], rel=1e-9, abs=1e-15), \
        f"{entry['filename']} value_max: 期望 {entry['value_max']}, 实际 {m.values.max()}"
    rs = m.row_sums()
    assert rs.min() == pytest.approx(entry["rowsum_min"], rel=1e-9, abs=1e-15), \
        f"{entry['filename']} rowsum_min: 期望 {entry['rowsum_min']}, 实际 {rs.min()}"
    assert rs.max() == pytest.approx(entry["rowsum_max"], rel=1e-9, abs=1e-15), \
        f"{entry['filename']} rowsum_max: 期望 {entry['rowsum_max']}, 实际 {rs.max()}"
