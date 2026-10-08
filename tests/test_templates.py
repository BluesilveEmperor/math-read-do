#!/usr/bin/env python3
"""9 种文献阅读模板的真正单元测试（pytest 风格，带 assert）。

验证项：
  - 9 个模板文件全部存在
  - 每个模板能被 Jinja2 加载并渲染，渲染结果非空
  - 渲染结果含 <style> 块、perspective-card CSS 类、表格分隔符
  - 视角条件逻辑：student/advisor/reviewer/all 四种视角下对应章节出现/隐藏符合预期
"""
import sys
import re
from pathlib import Path

import pytest

# 定位仓库根（本文件在 tests/ 下），使测试不依赖 cwd
ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
sys.path.insert(0, str(ROOT / "scripts"))

# 内置测试论文
PAPER = r'''# Topology-Driven Parallel Trajectory Optimization in Dynamic Environments

## Abstract
This paper presents T-MPC, a topology-driven trajectory optimization strategy.

## I. INTRODUCTION
Ground robots navigating in complex dynamic environments must compute collision-free trajectories.

## II. RELATED WORK
Motion planning methods can be divided into local and global planning methods.

## III. PROBLEM FORMULATION
We consider discrete-time nonlinear robot dynamics

$$x_{k+1} = f(x_k, u_k) \tag{1}$$

where $x$ is the state and $u$ is the input.

## IV. TOPOLOGY-DRIVEN MODEL PREDICTIVE CONTROL
### A. Guidance Planner
The guidance planner computes homotopy distinct trajectories.

### B. Local Planner
$$\min J = w_c J_c + w_l J_l + w_v J_v \tag{13}$$

## V. SIMULATION RESULTS
### A. Implementation
We validate our framework in simulation.

| Method | Duration(s) | Safety(%) |
|--------|-------------|-----------|
| T-MPC++ | 13.0 | 100 |
| LMPCC | 13.8 | 96 |

## VI. REAL-WORLD EXPERIMENTS
We demonstrate our planner in the real world.

## VII. DISCUSSION
The method has limitations in dynamic environments.

## VIII. CONCLUSION
T-MPC achieves state-of-the-art performance.
'''


def _build_data(perspective: str = "student") -> dict:
    """构造模板渲染所需数据。"""
    from literature_reader import (
        parse_paper_structure,
        extract_terminology,
        extract_figures_index,
        extract_key_formulas,
    )

    sections = parse_paper_structure(PAPER)
    terminology = extract_terminology(PAPER)
    figures = extract_figures_index(PAPER)
    formulas = extract_key_formulas(PAPER)

    return {
        "PAPER_TITLE": "T-MPC Test",
        "AUTHORS": "Test Author",
        "VENUE": "IEEE TRO 2025",
        "DOMAIN": "robotics",
        "PAPER_TYPE": "methods",
        "PAPER_TYPE_DESC": "method paper",
        "DATE": "2025-01-01",
        "PERSPECTIVE": perspective,
        "sections": sections,
        "terminology": terminology,
        "figures": figures,
        "key_formulas": formulas,
        "research_questions": [{"question": "RQ1: test", "source": "p.1"}],
        "student_metrics": [
            {"name": "Duration", "value": "13.0s", "source": "p.7", "evidence_strength": "strong"},
        ],
        "STUDENT_ABSTRACT": "Test abstract.",
        "STUDENT_METHODS": "Test methods.",
        "REPRO_CORE_ALGORITHM": "T-MPC framework",
        "REPRO_HYPERPARAMS": "N=30, P=4",
        "REPRO_DATASETS": "Simulation",
        "REPRO_RISKS": "FORCES Pro commercial",
        "reviewer_mandatory": [],
        "reviewer_suggested": [],
    }


def _render(template_name: str, data: dict) -> str:
    """用 Jinja2 渲染指定模板。"""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    return template.render(**data)


# 期望的 9 个模板文件名
EXPECTED_TEMPLATES = [
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


def test_all_nine_templates_exist():
    """验证 9 种排版风格模板文件全部存在（允许额外的基础模板如 template.md）。"""
    actual = sorted(p.name for p in TEMPLATES_DIR.glob("literature_reader.*.md"))
    for name in EXPECTED_TEMPLATES:
        assert (TEMPLATES_DIR / name).is_file(), f"模板文件缺失: {name}"
        assert name in actual, f"{name} 未被 templates/ 目录 glob 匹配"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES)
def test_template_renders_nonempty(template_name):
    """每个模板渲染结果非空。"""
    pytest.importorskip("jinja2")
    data = _build_data("student")
    result = _render(template_name, data)
    assert result, f"{template_name} 渲染结果为空"
    assert len(result) > 100, f"{template_name} 渲染结果过短（{len(result)} 字符），可能渲染异常"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES)
def test_template_has_style_and_card_and_table(template_name):
    """每个模板渲染结果含 <style> 块、perspective-card CSS 类、表格分隔符。"""
    pytest.importorskip("jinja2")
    data = _build_data("student")
    result = _render(template_name, data)
    assert "<style>" in result, f"{template_name} 缺少 <style> 块"
    assert "perspective-card" in result, f"{template_name} 缺少 perspective-card CSS 类"
    assert "|---" in result, f"{template_name} 缺少表格分隔符 '|---'"


@pytest.mark.parametrize(
    "perspective,expect_student,expect_advisor,expect_reviewer,expect_cross",
    [
        ("student", True, False, False, False),
        ("advisor", False, True, False, False),
        ("reviewer", False, False, True, False),
        ("all", True, True, True, True),
    ],
)
def test_perspective_conditional(
    perspective, expect_student, expect_advisor, expect_reviewer, expect_cross
):
    """验证视角条件逻辑：每种视角下对应章节出现/隐藏符合预期。"""
    pytest.importorskip("jinja2")
    data = _build_data(perspective)
    result = _render("literature_reader.markleaf.md", data)

    has_student = bool(re.findall(r"^## 研究生视角$", result, re.MULTILINE))
    has_advisor = bool(re.findall(r"^## 导师视角$", result, re.MULTILINE))
    has_reviewer = bool(re.findall(r"^## 审稿人视角$", result, re.MULTILINE))
    has_cross = bool(re.findall(r"^## 视角交叉对比$", result, re.MULTILINE))

    assert has_student == expect_student, (
        f"perspective={perspective}: 研究生视角 期望 {expect_student} 实际 {has_student}"
    )
    assert has_advisor == expect_advisor, (
        f"perspective={perspective}: 导师视角 期望 {expect_advisor} 实际 {has_advisor}"
    )
    assert has_reviewer == expect_reviewer, (
        f"perspective={perspective}: 审稿人视角 期望 {expect_reviewer} 实际 {has_reviewer}"
    )
    assert has_cross == expect_cross, (
        f"perspective={perspective}: 视角交叉对比 期望 {expect_cross} 实际 {has_cross}"
    )
