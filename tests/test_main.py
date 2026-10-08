#!/usr/bin/env python3
"""
Math-Read-Do Main Branch — Test Suite
测试核心功能：文献阅读报告生成、模板渲染、数据提取
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


class TestLiteratureReader(unittest.TestCase):
    """测试文献阅读报告生成器"""

    def setUp(self):
        """准备测试数据"""
        self.sample_paper = """# Sample Paper Title

## Abstract
This is a sample abstract for testing purposes.

## 1 Introduction
This paper introduces a novel method.

## 2 Method
The method is defined as:

$$x_{k+1} = f(x_k, u_k) \\tag{1}$$

where $x$ is the state and $u$ is the input.

## 3 Experiments
We evaluate on 3 datasets.

| Method | Accuracy | Time(ms) |
|--------|----------|----------|
| Ours   | 95.2%    | 12.3     |
| Baseline| 89.1%   | 15.7     |

## 4 Conclusion
This is the conclusion.
"""
        self.temp_dir = tempfile.mkdtemp()
        self.parsed_file = Path(self.temp_dir) / "parsed_text.md"
        self.parsed_file.write_text(self.sample_paper, encoding="utf-8")

    def tearDown(self):
        """清理测试数据"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_paper_structure(self):
        """测试论文结构解析"""
        from literature_reader import parse_paper_structure
        sections = parse_paper_structure(self.sample_paper)
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 0)
        # 检查是否识别了标题
        titles = [s["title"] for s in sections]
        self.assertTrue(any("Abstract" in t for t in titles))

    def test_extract_terminology(self):
        """测试术语提取"""
        from literature_reader import extract_terminology
        terms = extract_terminology(self.sample_paper)
        self.assertIsInstance(terms, list)

    def test_extract_figures_index(self):
        """测试图表索引提取"""
        from literature_reader import extract_figures_index
        figures = extract_figures_index(self.sample_paper)
        self.assertIsInstance(figures, list)

    def test_extract_key_formulas(self):
        """测试公式提取"""
        from literature_reader import extract_key_formulas
        formulas = extract_key_formulas(self.sample_paper)
        self.assertIsInstance(formulas, list)
        # 应该提取到至少一个公式
        self.assertGreater(len(formulas), 0)

    def test_simple_render_student_only(self):
        """测试仅研究生视角渲染（使用 _simple_render）"""
        from literature_reader import _simple_render
        data = {
            "PAPER_TITLE": "Test Paper",
            "AUTHORS": "Test Author",
            "VENUE": "Test Venue",
            "DOMAIN": "test",
            "PAPER_TYPE": "methods",
            "PAPER_TYPE_DESC": "方法论文",
            "DATE": "2025-01-01",
            "PERSPECTIVE": "student",
            "sections": [],
            "terminology": [],
            "figures": [],
            "key_formulas": [],
            "research_questions": [],
            "student_metrics": [],
            "STUDENT_ABSTRACT": "Test abstract",
            "STUDENT_METHODS": "Test methods",
            "REPRO_CORE_ALGORITHM": "Test algorithm",
            "REPRO_HYPERPARAMS": "Test params",
            "REPRO_DATASETS": "Test data",
            "REPRO_RISKS": "Test risks",
            "reviewer_mandatory": [],
            "reviewer_suggested": [],
        }
        result = _simple_render(data)
        self.assertIsInstance(result, str)
        self.assertIn("Test Paper", result)
        # 学生视角应该存在
        self.assertIn("研究生视角", result)

    def test_get_default_template(self):
        """测试默认模板获取"""
        from literature_reader import _get_default_template
        template = _get_default_template()
        self.assertIsInstance(template, str)
        self.assertIn("文献阅读", template)


class TestTemplateSystem(unittest.TestCase):
    """测试模板系统"""

    def test_all_templates_exist(self):
        """测试所有模板文件存在"""
        template_dir = PROJECT_ROOT / "templates"
        expected_templates = [
            "literature_reader.markleaf.md",
            "literature_reader.print.md",
            "literature_reader.retro-print.md",
            "literature_reader.sans.md",
            "literature_reader.serif.md",
            "literature_reader.magazine.md",
            "literature_reader.minimal.md",
            "literature_reader.notebook.md",
            "literature_reader.print-double.md",
        ]
        for template in expected_templates:
            self.assertTrue(
                (template_dir / template).exists(),
                f"Template missing: {template}"
            )

    def test_all_templates_have_css(self):
        """测试所有模板都包含 CSS"""
        template_dir = PROJECT_ROOT / "templates"
        templates = template_dir.glob("literature_reader.*.md")
        for template in templates:
            if template.name == "literature_reader.template.md":
                continue  # 跳过旧模板
            content = template.read_text(encoding="utf-8")
            self.assertIn("<style>", content, f"Missing <style> in {template.name}")
            self.assertIn("</style>", content, f"Missing </style> in {template.name}")

    def test_all_templates_have_perspective_conditional(self):
        """测试所有模板都有视角条件判断"""
        template_dir = PROJECT_ROOT / "templates"
        templates = template_dir.glob("literature_reader.*.md")
        for template in templates:
            if template.name == "literature_reader.template.md":
                continue
            content = template.read_text(encoding="utf-8")
            self.assertIn("PERSPECTIVE", content, f"Missing PERSPECTIVE check in {template.name}")


class TestDataExtraction(unittest.TestCase):
    """测试数据提取功能"""

    def test_argument_function_inference(self):
        """测试论证功能推断"""
        from literature_reader import infer_argument_function
        self.assertEqual(infer_argument_function("Introduction"), "gap → contribution")
        self.assertEqual(infer_argument_function("Method"), "contribution")
        self.assertEqual(infer_argument_function("Experiments"), "result")
        self.assertEqual(infer_argument_function("Discussion"), "limits")
        self.assertEqual(infer_argument_function("Related Work"), "background")


if __name__ == "__main__":
    unittest.main(verbosity=2)
