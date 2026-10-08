# -*- coding: utf-8 -*-
"""Phase 1 数据可得性分诊脚本的基础测试。

通过 sys.path 导入 scripts/data_triage.py，避免依赖包安装。
URL 探测用 unittest.mock 模拟，测试不依赖真实网络。
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

# 将 scripts 目录加入 sys.path 以导入 data_triage
_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(_SCRIPTS_DIR))

import data_triage as T  # noqa: E402


# --- 纯逻辑分诊（不触网） ---


class TestTriageLogic(unittest.TestCase):
    """licensed / absent / file / 未知类型 的纯逻辑分诊。"""

    def test_licensed_marks_needs_auth(self):
        """商业授权数据源标记为 needs_auth。"""
        src = {"name": "CRSP", "type": "licensed", "location": "WRDS"}
        out = T._triage_source(src)
        self.assertEqual(out["status"], T.STATUS_NEEDS_AUTH)
        self.assertIn("合成替代", out["suggestion"])

    def test_absent_marks_missing(self):
        """论文与仓库均未提供的数据源标记为 missing。"""
        src = {"name": "Bloomberg SPX", "type": "absent", "location": ""}
        out = T._triage_source(src)
        self.assertEqual(out["status"], T.STATUS_MISSING)

    def test_file_exists_marks_available(self):
        """本地存在的文件标记为 available。"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            f.write(b"date,price\n2024-01-01,100\n")
            path = f.name
        try:
            src = {"name": "local", "type": "file", "location": path}
            out = T._triage_source(src)
            self.assertEqual(out["status"], T.STATUS_AVAILABLE)
            self.assertIn("本地存在", out["detail"])
        finally:
            os.unlink(path)

    def test_file_missing_marks_missing(self):
        """本地不存在的文件标记为 missing。"""
        src = {"name": "ghost", "type": "file", "location": "nonexistent_12345.csv"}
        out = T._triage_source(src)
        self.assertEqual(out["status"], T.STATUS_MISSING)

    def test_unknown_type_marks_missing(self):
        """未知数据源类型标记为 missing，避免误判为可用。"""
        src = {"name": "weird", "type": "telepathy", "location": "????"}
        out = T._triage_source(src)
        self.assertEqual(out["status"], T.STATUS_MISSING)


# --- URL 探测（mock 网络） ---


class TestUrlCheck(unittest.TestCase):
    """URL 可达性探测，用 mock 模拟网络响应。"""

    def test_url_reachable_marks_available(self):
        """HTTP 200 的 URL 标记为 available。"""
        fake_resp = mock.MagicMock()
        fake_resp.getcode.return_value = 200
        fake_resp.__enter__ = mock.MagicMock(return_value=fake_resp)
        fake_resp.__exit__ = mock.MagicMock(return_value=False)
        with mock.patch("urllib.request.urlopen", return_value=fake_resp):
            status, detail = T._check_url("https://example.com/data")
        self.assertEqual(status, T.STATUS_AVAILABLE)

    def test_url_403_marks_needs_auth(self):
        """HTTP 403 的 URL 标记为 needs_auth。"""
        import urllib.error
        err = urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            status, _ = T._check_url("https://example.com/secret")
        self.assertEqual(status, T.STATUS_NEEDS_AUTH)

    def test_url_unreachable_marks_missing(self):
        """网络不可达时降级为 missing，不抛异常。"""
        with mock.patch("urllib.request.urlopen",
                        side_effect=urllib.error.URLError("no network")):
            status, detail = T._check_url("https://invalid.invalid/x")
        self.assertEqual(status, T.STATUS_MISSING)
        self.assertIn("网络不可达", detail)


# --- 完整分诊流程 ---


class TestRunTriage(unittest.TestCase):
    """run_triage 端到端流程与输出格式。"""

    def _make_paper(self):
        return {
            "title": "Test Paper",
            "url": "https://example.com",
            "data_sources": [
                {"name": "CRSP", "type": "licensed", "location": "WRDS"},
                {"name": "missing_data", "type": "absent", "location": ""},
            ],
        }

    def test_summary_counts_match_sources(self):
        """summary 计数与 sources 状态一致。"""
        report = T.run_triage(self._make_paper())
        s = report["summary"]
        self.assertEqual(s[T.STATUS_NEEDS_AUTH], 1)
        self.assertEqual(s[T.STATUS_MISSING], 1)
        self.assertEqual(s[T.STATUS_AVAILABLE], 0)
        self.assertEqual(len(report["sources"]), 2)

    def test_report_has_required_fields(self):
        """报告包含 title / triaged_at / sources / summary 字段。"""
        report = T.run_triage(self._make_paper())
        for key in ("title", "url", "triaged_at", "sources", "summary"):
            self.assertIn(key, report)
        for src in report["sources"]:
            for key in ("name", "type", "location", "status", "detail", "suggestion"):
                self.assertIn(key, src)

    def test_empty_data_sources(self):
        """无数据源时返回空列表与零计数。"""
        report = T.run_triage({"title": "Empty", "data_sources": []})
        self.assertEqual(report["sources"], [])
        self.assertEqual(sum(report["summary"].values()), 0)


# --- 命令行接口 ---


class TestCli(unittest.TestCase):
    """命令行入口 main()。"""

    def test_cli_writes_report_and_returns_zero(self):
        """CLI 正常执行并写入报告文件，返回 0。"""
        paper = {"title": "CLI Test", "data_sources": [
            {"name": "x", "type": "absent", "location": ""}]}
        with tempfile.TemporaryDirectory() as d:
            paper_path = os.path.join(d, "paper.json")
            out_path = os.path.join(d, "out.json")
            with open(paper_path, "w", encoding="utf-8") as f:
                json.dump(paper, f)
            rc = T.main(["--paper", paper_path, "--output", out_path])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            self.assertEqual(report["title"], "CLI Test")

    def test_cli_missing_paper_file_returns_one(self):
        """论文文件不存在时返回 1。"""
        rc = T.main(["--paper", "no_such_file_99999.json"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()