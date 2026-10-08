"""scripts/math_pdf_extract.py 的单元测试（pytest 风格）。

重点覆盖 MinerU 超时降级路径：
  - extract_with_pymupdf：MinerU 不可用/超时时降级到 PyMuPDF，输出 markdown 格式
  - estimate_pdf_pages：PDF 页数估算
  - get_token：配置文件不存在时 sys.exit(1)
  - report_quota：日用量记录与余额计算
  - _load_daily_usage / _save_daily_usage
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import math_pdf_extract as mpe


# ── extract_with_pymupdf 降级路径 ───────────────────────────────────

class TestExtractWithPyMuPDF:

    def test_pymupdf_not_installed_returns_1(self, tmp_path, monkeypatch, capsys):
        """fitz 未安装时应返回 1 并提示安装。"""
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "fitz":
                raise ImportError("No module named 'fitz'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        rc = mpe.extract_with_pymupdf(pdf_path, tmp_path)
        assert rc == 1
        err = capsys.readouterr().err
        assert "PyMuPDF" in err

    def test_pymupdf_extracts_markdown(self, tmp_path, monkeypatch):
        """fitz 可用时应提取文本并生成 markdown（含标题与降级说明）。"""
        pdf_path = tmp_path / "paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")

        # mock fitz.open 返回 mock doc
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "First page content."
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Second page."
        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page1, mock_page2]))
        mock_doc.close = MagicMock()

        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc

        monkeypatch.setitem(sys.modules, "fitz", mock_fitz)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        rc = mpe.extract_with_pymupdf(pdf_path, out_dir)
        assert rc == 0
        md_path = out_dir / "paper.md"
        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")
        assert "paper" in content
        assert "降级提取" in content
        assert "First page content" in content
        assert "Second page" in content
        assert "第 1 页" in content
        assert "第 2 页" in content

    def test_pymupdf_empty_pages(self, tmp_path, monkeypatch):
        """空页（无文本）不应出现在输出中。"""
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        mock_page = MagicMock()
        mock_page.get_text.return_value = "   "  # 仅空白
        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc
        monkeypatch.setitem(sys.modules, "fitz", mock_fitz)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        rc = mpe.extract_with_pymupdf(pdf_path, out_dir)
        assert rc == 0
        content = (out_dir / "empty.md").read_text(encoding="utf-8")
        assert "降级提取" in content  # 头部仍在
        assert "第 1 页" not in content  # 空页被跳过


# ── estimate_pdf_pages ───────────────────────────────────────────────

class TestEstimatePdfPages:

    def test_pdf_with_page_type_markers(self, tmp_path):
        """含多个 /Type /Page 标记的 PDF 应返回该计数。"""
        pdf_path = tmp_path / "p.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n/Type /Page\n/Type /Page\n/Type /Page\n/Type /Page\n/Type /Page\n/Type /Page\n")
        pages = mpe.estimate_pdf_pages(str(pdf_path))
        assert pages == 6

    def test_pdf_with_count_field(self, tmp_path):
        """含 /Count 字段的 PDF 应返回该值。"""
        pdf_path = tmp_path / "c.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n/Count 42\n")
        pages = mpe.estimate_pdf_pages(str(pdf_path))
        assert pages == 42

    def test_empty_file_returns_at_least_one(self, tmp_path):
        """空文件应返回至少 1（max(..., 1) 兜底）。"""
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_bytes(b"")
        assert mpe.estimate_pdf_pages(str(pdf_path)) >= 1

    def test_minimal_pdf_returns_at_least_1(self, tmp_path):
        """无明确页标记的 PDF 至少返回 1。"""
        pdf_path = tmp_path / "min.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 minimal")
        pages = mpe.estimate_pdf_pages(str(pdf_path))
        assert pages >= 1


# ── get_token ────────────────────────────────────────────────────────

class TestGetToken:

    def test_no_config_file_exits(self, monkeypatch, tmp_path, capsys):
        """配置文件不存在时应 sys.exit(1)。"""
        fake_home = tmp_path / "fakehome"
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        with pytest.raises(SystemExit) as exc:
            mpe.get_token()
        assert exc.value.code == 1

    def test_valid_token_returned(self, monkeypatch, tmp_path):
        """配置文件含有效 token 时应返回该 token。"""
        fake_home = tmp_path / "fakehome"
        (fake_home / ".mineru").mkdir(parents=True)
        (fake_home / ".mineru" / "config.yaml").write_text(
            "token: 'my-secret-key'\n", encoding="utf-8"
        )
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        # yaml 可能未安装，走 fallback 解析
        token = mpe.get_token()
        assert token == "my-secret-key"

    def test_empty_token_exits(self, monkeypatch, tmp_path):
        """配置文件中 token 为空时应 sys.exit(1)。"""
        fake_home = tmp_path / "fakehome"
        (fake_home / ".mineru").mkdir(parents=True)
        (fake_home / ".mineru" / "config.yaml").write_text(
            "token: ''\n", encoding="utf-8"
        )
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        with pytest.raises(SystemExit):
            mpe.get_token()


# ── report_quota / daily_usage ───────────────────────────────────────

class TestQuota:

    def test_load_daily_usage_missing_file(self, monkeypatch, tmp_path):
        """用量文件不存在时返回空字典。"""
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "no.json")
        assert mpe._load_daily_usage() == {}

    def test_save_and_load_roundtrip(self, monkeypatch, tmp_path):
        """保存后再加载应一致。"""
        qf = tmp_path / "usage.json"
        monkeypatch.setattr(mpe, "QUOTA_FILE", qf)
        mpe._save_daily_usage({"2024-01-01": {"pages": 10, "files": 1}})
        loaded = mpe._load_daily_usage()
        assert loaded["2024-01-01"]["pages"] == 10

    def test_report_quota_returns_tuple(self, monkeypatch, tmp_path):
        """report_quota 应返回 (used, remaining) 且 remaining ≥ 0。"""
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")
        used, remaining = mpe.report_quota(used_pages=50)
        assert used == 50
        assert remaining == mpe.DAILY_QUOTA_PAGES - 50
        assert remaining >= 0

    def test_report_quota_accumulates(self, monkeypatch, tmp_path):
        """多次调用应累加当日用量。"""
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")
        mpe.report_quota(used_pages=100)
        used, remaining = mpe.report_quota(used_pages=200)
        assert used == 300
        assert remaining == mpe.DAILY_QUOTA_PAGES - 300

    def test_report_quota_clamps_remaining_zero(self, monkeypatch, tmp_path):
        """超出限额时 remaining 应钳制为 0。"""
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")
        used, remaining = mpe.report_quota(used_pages=mpe.DAILY_QUOTA_PAGES + 500)
        assert remaining == 0

# ── main() 端到端（mock MinerU / get_token）─────────────────────────

class TestMainEntry:

    def _run_main(self, argv):
        old = sys.argv
        sys.argv = argv
        try:
            rc = mpe.main()
            rc = 0 if rc is None else rc
        except SystemExit as e:
            rc = e.code if e.code is not None else 0
        finally:
            sys.argv = old
        return rc

    def test_main_mineru_success(self, monkeypatch, tmp_path):
        """MinerU 正常解析路径：mock get_token + MinerU，验证返回 0。"""
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 /Type /Page /Type /Page")
        out_dir = tmp_path / "out"

        monkeypatch.setattr(mpe, "get_token", lambda: "fake-token")
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")

        # mock mineru 模块
        mock_result = MagicMock()
        mock_result.state = "done"
        mock_result.error = None
        mock_result.progress = MagicMock()
        mock_result.progress.total_pages = 2
        mock_result.save_markdown = MagicMock()

        mock_client = MagicMock()
        mock_client.extract.return_value = mock_result
        mock_client.close = MagicMock()

        mock_mineru_module = MagicMock()
        mock_mineru_module.MinerU = MagicMock(return_value=mock_client)
        monkeypatch.setitem(sys.modules, "mineru", mock_mineru_module)

        rc = self._run_main(["mpe", str(pdf_path), "--output-dir", str(out_dir)])
        assert rc == 0
        mock_result.save_markdown.assert_called_once()

    def test_main_mineru_timeout_fallback_pymupdf(self, monkeypatch, tmp_path):
        """MinerU 超时时应降级到 PyMuPDF（mock fitz + 立即超时）。"""
        import concurrent.futures
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        out_dir = tmp_path / "out"

        monkeypatch.setattr(mpe, "get_token", lambda: "fake-token")
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")

        # mock mineru 模块（client 不会被真正调用，因为 future 立即超时）
        mock_client = MagicMock()
        mock_client.close = MagicMock()
        mock_mineru_module = MagicMock()
        mock_mineru_module.MinerU = MagicMock(return_value=mock_client)
        monkeypatch.setitem(sys.modules, "mineru", mock_mineru_module)

        # mock fitz 供降级路径
        mock_page = MagicMock()
        mock_page.get_text.return_value = "fallback text"
        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc
        monkeypatch.setitem(sys.modules, "fitz", mock_fitz)

        # mock ThreadPoolExecutor 让 future.result 立即抛 TimeoutError
        mock_future = MagicMock()
        mock_future.result.side_effect = concurrent.futures.TimeoutError()
        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        mock_pool.submit = MagicMock(return_value=mock_future)
        monkeypatch.setattr(concurrent.futures, "ThreadPoolExecutor",
                            lambda **kw: mock_pool)

        rc = self._run_main(["mpe", str(pdf_path), "--output-dir", str(out_dir)])
        # 超时降级后 extract_with_pymupdf 返回 0
        assert rc == 0
        md_file = out_dir / "doc.md"
        assert md_file.exists()

    def test_main_mineru_parse_error(self, monkeypatch, tmp_path):
        """MinerU 返回 state != done 时应 sys.exit(1)。"""
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        out_dir = tmp_path / "out"

        monkeypatch.setattr(mpe, "get_token", lambda: "fake-token")
        monkeypatch.setattr(mpe, "QUOTA_FILE", tmp_path / "q.json")

        mock_result = MagicMock()
        mock_result.state = "error"
        mock_result.error = "parse failed"
        mock_result.progress = None

        mock_client = MagicMock()
        mock_client.extract.return_value = mock_result
        mock_client.close = MagicMock()
        mock_mineru_module = MagicMock()
        mock_mineru_module.MinerU = MagicMock(return_value=mock_client)
        monkeypatch.setitem(sys.modules, "mineru", mock_mineru_module)

        rc = self._run_main(["mpe", str(pdf_path), "--output-dir", str(out_dir)])
        assert rc == 1

    def test_main_pdf_not_exists(self, monkeypatch, tmp_path):
        """PDF 文件不存在时应 sys.exit(1)。"""
        monkeypatch.setattr(mpe, "get_token", lambda: "fake-token")
        mock_mineru_module = MagicMock()
        monkeypatch.setitem(sys.modules, "mineru", mock_mineru_module)
        rc = self._run_main(["mpe", str(tmp_path / "no.pdf"),
                             "--output-dir", str(tmp_path / "o")])
        assert rc == 1

    def test_main_quota_error_resets_usage(self, monkeypatch, tmp_path):
        """解析错误含 quota 时应重置本地用量计数。"""
        pdf_path = tmp_path / "doc.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        out_dir = tmp_path / "out"
        qf = tmp_path / "q.json"
        qf.write_text('{"old": "data"}', encoding="utf-8")

        monkeypatch.setattr(mpe, "get_token", lambda: "fake-token")
        monkeypatch.setattr(mpe, "QUOTA_FILE", qf)

        mock_result = MagicMock()
        mock_result.state = "error"
        mock_result.error = "quota exceeded"
        mock_result.progress = None

        mock_client = MagicMock()
        mock_client.extract.return_value = mock_result
        mock_client.close = MagicMock()
        mock_mineru_module = MagicMock()
        mock_mineru_module.MinerU = MagicMock(return_value=mock_client)
        monkeypatch.setitem(sys.modules, "mineru", mock_mineru_module)

        rc = self._run_main(["mpe", str(pdf_path), "--output-dir", str(out_dir)])
        assert rc == 1
        # 用量应被重置为 {}
        assert qf.read_text(encoding="utf-8").strip() == "{}"