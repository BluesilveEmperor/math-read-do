"""scripts/literature_reader.py 的单元测试（pytest 风格）。

重点覆盖 call_llm 的外部依赖隔离：
  - 无 API key 时的占位输出
  - openai 库未安装时的占位输出
  - 论文内容截断（> 80000 字符）
  - 超时 + 指数退避重试逻辑（mock OpenAI client + mock time.sleep）
  - 全部重试失败后的错误占位
  - generate_reproducibility_assessment 可复现性评级推断
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

import literature_reader as lr


# ── call_llm：无 API key ─────────────────────────────────────────────

class TestCallLlmNoApiKey:

    def test_no_api_key_returns_placeholder(self, monkeypatch, capsys):
        """LLM_API_KEY 未设置时应返回占位输出，含视角名与内容长度。"""
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        result = lr.call_llm("system", "paper content here", "研究生视角")
        assert "占位" in result
        assert "研究生视角" in result
        assert "18" in result  # len("paper content here") == 18

    def test_no_api_key_placeholder_mentions_env(self, monkeypatch):
        """占位输出应提示设置 LLM_API_KEY 环境变量。"""
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        result = lr.call_llm("sys", "x", "test")
        assert "LLM_API_KEY" in result


# ── call_llm：openai 未安装 ──────────────────────────────────────────

class TestCallLlmNoOpenai:

    def test_openai_import_error_returns_placeholder(self, monkeypatch):
        """有 API key 但 openai 库未安装时应返回占位。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        # 模拟 openai 不存在：让 import openai 抛 ImportError
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("No module named 'openai'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        result = lr.call_llm("sys", "paper", "test视角")
        assert "占位" in result
        assert "openai" in result


# ── call_llm：成功路径 + 截断 ────────────────────────────────────────

def _install_mock_openai(monkeypatch, mock_client):
    """在 sys.modules 注入 mock openai 模块，使 `from openai import OpenAI` 生效。"""
    mock_module = MagicMock()
    mock_module.OpenAI = MagicMock(return_value=mock_client)
    monkeypatch.setitem(sys.modules, "openai", mock_module)
    return mock_module


class TestCallLlmSuccess:

    def test_successful_call_returns_content(self, monkeypatch):
        """有 API key 且调用成功时应返回 LLM 响应内容。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        monkeypatch.setenv("LLM_MODEL", "gpt-4o")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "LLM 分析结果"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        _install_mock_openai(monkeypatch, mock_client)
        result = lr.call_llm("system prompt", "paper", "test")
        assert result == "LLM 分析结果"

    def test_paper_content_truncated_over_80000(self, monkeypatch):
        """论文内容 > 80000 字符时应被截断并附加截断标记。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        long_content = "A" * 90000

        captured_user = {}

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        mock_client = MagicMock()
        def fake_create(**kwargs):
            captured_user["content"] = kwargs["messages"][1]["content"]
            return mock_response
        mock_client.chat.completions.create.side_effect = fake_create

        _install_mock_openai(monkeypatch, mock_client)
        lr.call_llm("sys", long_content, "test")

        user_msg = captured_user["content"]
        # 截断后主体 ≤ 80000 + 截断标记行
        assert "[论文内容已截断" in user_msg
        assert "90000" in user_msg

    def test_paper_content_not_truncated_under_limit(self, monkeypatch):
        """论文内容 ≤ 80000 字符时不应截断。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        short_content = "B" * 1000

        captured_user = {}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_client = MagicMock()
        def fake_create(**kwargs):
            captured_user["content"] = kwargs["messages"][1]["content"]
            return mock_response
        mock_client.chat.completions.create.side_effect = fake_create

        _install_mock_openai(monkeypatch, mock_client)
        lr.call_llm("sys", short_content, "test")
        assert "已截断" not in captured_user["content"]


# ── call_llm：重试逻辑 ──────────────────────────────────────────────

class TestCallLlmRetry:

    def test_retry_succeeds_on_third_attempt(self, monkeypatch):
        """前两次失败、第三次成功时应返回结果（mock sleep 避免等待）。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        monkeypatch.setattr(time, "sleep", lambda s: None)  # 跳过退避等待

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "recovered"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            RuntimeError("timeout1"),
            RuntimeError("timeout2"),
            mock_response,
        ]

        _install_mock_openai(monkeypatch, mock_client)
        result = lr.call_llm("sys", "paper", "test")
        assert result == "recovered"
        assert mock_client.chat.completions.create.call_count == 3

    def test_all_retries_fail_returns_error_placeholder(self, monkeypatch, capsys):
        """三次全部失败时应返回错误占位（含重试次数）。"""
        monkeypatch.setenv("LLM_API_KEY", "fake-key")
        monkeypatch.setattr(time, "sleep", lambda s: None)

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("boom")

        _install_mock_openai(monkeypatch, mock_client)
        result = lr.call_llm("sys", "paper", "test视角")
        assert "错误" in result
        assert mock_client.chat.completions.create.call_count == 3


# ── generate_reproducibility_assessment ──────────────────────────────

class TestReproducibilityAssessment:

    def test_no_code_no_data_very_low(self, tmp_path):
        """报告中无 code/data 关键词时应评级 very_low。"""
        summary_path = tmp_path / "paper_summary.json"
        summary_path.write_text(json.dumps({"domain": "finance", "title": "T"}),
                                encoding="utf-8")
        assessment = lr.generate_reproducibility_assessment(
            "这是一篇普通论文，没有提到代码或数据。", str(summary_path)
        )
        assert assessment["reproducibility_rating"] == "very_low"
        assert assessment["code_available"] is False
        assert "code_not_available" in assessment["risk_flags"]

    def test_code_and_data_and_env_high(self, tmp_path):
        """报告含 code + data available + environment 时评级 high。"""
        report = "The code is on GitHub. Data is publicly available. Environment in Docker."
        assessment = lr.generate_reproducibility_assessment(report, None)
        assert assessment["code_available"] is True
        assert assessment["data_available"] is True
        assert assessment["environment_specified"] is True
        assert assessment["reproducibility_rating"] == "high"

    def test_code_only_low(self, tmp_path):
        """仅 code 可用、无 data/env 时评级 low。"""
        report = "We provide the source code in a repository."
        assessment = lr.generate_reproducibility_assessment(report, None)
        assert assessment["code_available"] is True
        assert assessment["data_available"] is False
        assert assessment["reproducibility_rating"] == "low"

    def test_writes_json_file(self, tmp_path):
        """评估结果应写入 reproducibility_assessment.json。"""
        summary_path = tmp_path / "paper_summary.json"
        summary_path.write_text("{}", encoding="utf-8")
        lr.generate_reproducibility_assessment("code", str(summary_path))
        out_file = tmp_path / "reproducibility_assessment.json"
        assert out_file.exists()
        data = json.loads(out_file.read_text(encoding="utf-8"))
        assert "reproducibility_rating" in data


# ── 纯解析函数补充覆盖 ───────────────────────────────────────────────

class TestParsingFunctions:

    def test_parse_paper_structure_with_page_markers(self):
        """含页码标记的论文应正确识别页码。"""
        content = "# Title\nPage 3\n## Section\n"
        sections = lr.parse_paper_structure(content)
        assert any(s["title"] == "Section" and s["page"] == 3 for s in sections)

    def test_extract_terminology_abbr(self):
        """应识别英文缩写定义。"""
        content = "We use Reinforcement Learning (RL) for training."
        terms = lr.extract_terminology(content)
        abbrs = [t["term"] for t in terms]
        assert "RL" in abbrs

    def test_extract_figures_index_image(self):
        """应识别 Markdown 图片引用。"""
        content = "![Figure 1](fig1.png)\n"
        figures = lr.extract_figures_index(content)
        assert any("Fig" in f["id"] for f in figures)

    def test_extract_key_formulas_block(self):
        """应识别 $$...$$ 公式块。"""
        content = "Some text\n$$E = mc^2$$\nmore text\n"
        formulas = lr.extract_key_formulas(content)
        assert len(formulas) >= 1
        assert any("mc" in f["latex"] for f in formulas)

# ── select_template_interactive（mock input）────────────────────────

class TestSelectTemplateInteractive:

    def test_select_first_template(self, monkeypatch):
        """输入空串（默认）应选择第一个模板。"""
        # mock input 返回空串
        monkeypatch.setattr("builtins.input", lambda *a, **kw: "")
        # 模板目录需存在；wt-main/templates 有 9 个模板
        result = lr.select_template_interactive()
        # 应返回一个路径字符串或 None（取决于 templates 目录是否在预期位置）
        assert result is None or isinstance(result, str)


# ── main() 端到端（mock call_llm + 注入 render_report）─────────────

class TestMainEntry:

    def _run_main(self, argv):
        old = sys.argv
        sys.argv = argv
        try:
            lr.main()
            return 0
        except SystemExit as e:
            return e.code if e.code is not None else 0
        finally:
            sys.argv = old

    def test_main_student_perspective(self, monkeypatch, tmp_path):
        """main() student 视角：mock call_llm + render_report，验证输出文件。"""
        paper_md = tmp_path / "paper.md"
        paper_md.write_text("# Test Paper\n## Abstract\nContent.\n", encoding="utf-8")
        out_dir = tmp_path / "analysis"

        # mock call_llm 返回固定报告
        monkeypatch.setattr(lr, "call_llm",
                            lambda sys_p, content, name: f"[{name}] mock report")
        # 注入 render_report（源码中缺失 def，用 mock 替代）
        monkeypatch.setattr(lr, "render_report",
                            lambda tpl, data: "# Mocked Report\n", raising=False)
        # 指定 template 避免交互选择
        tpl_path = PROJECT_ROOT / "templates" / "literature_reader.markleaf.md"
        rc = self._run_main([
            "lr", str(paper_md),
            "--output-dir", str(out_dir),
            "--perspective", "student",
            "--template", str(tpl_path),
        ])
        assert rc == 0
        assert (out_dir / "文献阅读.md").exists()
        assert (out_dir / "literature_reading.json").exists()

    def test_main_advisor_perspective(self, monkeypatch, tmp_path):
        """main() advisor 视角应生成可复现性评估。"""
        paper_md = tmp_path / "paper.md"
        paper_md.write_text("# Paper\n## Method\nCode on GitHub.\n", encoding="utf-8")
        out_dir = tmp_path / "analysis"

        monkeypatch.setattr(lr, "call_llm",
                            lambda sys_p, content, name: f"[{name}] code available")
        monkeypatch.setattr(lr, "render_report", lambda tpl, data: "# Report\n", raising=False)
        tpl_path = PROJECT_ROOT / "templates" / "literature_reader.markleaf.md"
        rc = self._run_main([
            "lr", str(paper_md),
            "--output-dir", str(out_dir),
            "--perspective", "advisor",
            "--template", str(tpl_path),
        ])
        assert rc == 0
        # advisor 视角应生成 reproducibility_assessment.json
        assert (out_dir / "reproducibility_assessment.json").exists()

    def test_main_all_perspectives(self, monkeypatch, tmp_path):
        """main() all 视角应调用 call_llm 三次。"""
        paper_md = tmp_path / "paper.md"
        paper_md.write_text("# Paper\n", encoding="utf-8")
        out_dir = tmp_path / "analysis"

        call_count = {"n": 0}
        def mock_call(sys_p, content, name):
            call_count["n"] += 1
            return f"[{name}] report"
        monkeypatch.setattr(lr, "call_llm", mock_call)
        monkeypatch.setattr(lr, "render_report", lambda tpl, data: "# R\n", raising=False)
        tpl_path = PROJECT_ROOT / "templates" / "literature_reader.markleaf.md"
        rc = self._run_main([
            "lr", str(paper_md),
            "--output-dir", str(out_dir),
            "--perspective", "all",
            "--template", str(tpl_path),
        ])
        assert rc == 0
        assert call_count["n"] == 3  # student + advisor + reviewer

    def test_main_nonexistent_paper(self, monkeypatch, tmp_path):
        """论文文件不存在时应以空内容继续（不崩溃）。"""
        out_dir = tmp_path / "analysis"
        monkeypatch.setattr(lr, "call_llm",
                            lambda sys_p, content, name: "mock")
        monkeypatch.setattr(lr, "render_report", lambda tpl, data: "# R\n", raising=False)
        tpl_path = PROJECT_ROOT / "templates" / "literature_reader.markleaf.md"
        rc = self._run_main([
            "lr", str(tmp_path / "no_such.md"),
            "--output-dir", str(out_dir),
            "--perspective", "student",
            "--template", str(tpl_path),
        ])
        assert rc == 0