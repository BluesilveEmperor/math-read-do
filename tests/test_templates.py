#!/usr/bin/env python3
"""Test all 9 literature reader templates - Fixed version."""
import sys
sys.path.insert(0, 'scripts')

from pathlib import Path

# 内置测试论文
paper = r'''# Topology-Driven Parallel Trajectory Optimization in Dynamic Environments

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

from literature_reader import (
    parse_paper_structure,
    extract_terminology,
    extract_figures_index,
    extract_key_formulas,
)

# 提取数据
sections = parse_paper_structure(paper)
terminology = extract_terminology(paper)
figures = extract_figures_index(paper)
formulas = extract_key_formulas(paper)

print(f'Extracted: {len(sections)} sections, {len(terminology)} terms, {len(figures)} figures, {len(formulas)} formulas')

# 测试数据
data = {
    'PAPER_TITLE': 'T-MPC Test',
    'AUTHORS': 'Test Author',
    'VENUE': 'IEEE TRO 2025',
    'DOMAIN': 'robotics',
    'PAPER_TYPE': 'methods',
    'PAPER_TYPE_DESC': 'method paper',
    'DATE': '2025-01-01',
    'PERSPECTIVE': 'student',
    'sections': sections,
    'terminology': terminology,
    'figures': figures,
    'key_formulas': formulas,
    'research_questions': [{'question': 'RQ1: test', 'source': 'p.1'}],
    'student_metrics': [
        {'name': 'Duration', 'value': '13.0s', 'source': 'p.7', 'evidence_strength': 'strong'},
    ],
    'STUDENT_ABSTRACT': 'Test abstract.',
    'STUDENT_METHODS': 'Test methods.',
    'REPRO_CORE_ALGORITHM': 'T-MPC framework',
    'REPRO_HYPERPARAMS': 'N=30, P=4',
    'REPRO_DATASETS': 'Simulation',
    'REPRO_RISKS': 'FORCES Pro commercial',
    'reviewer_mandatory': [],
    'reviewer_suggested': [],
}

# 测试所有模板
templates = sorted(Path('templates').glob('literature_reader.*.md'))
print(f'\nTesting {len(templates)} templates:')

passed = 0
failed = 0
for tmpl in templates:
    name = tmpl.name
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(
            loader=FileSystemLoader(str(tmpl.parent)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(tmpl.name)
        result = template.render(**data)
        
        has_style = '<style>' in result
        has_css = 'perspective-card' in result
        has_table = '|---' in result
        
        # 只计算 ## 开头的 section headers（不包括 CSS 注释）
        import re
        headers = re.findall(r'^## 研究生视角$', result, re.MULTILINE)
        has_student = len(headers) > 0
        
        status = 'OK' if (has_style and has_css and has_table) else 'WARN'
        if status == 'OK':
            passed += 1
        else:
            failed += 1
        print(f'  [{status}] {name:45} style={has_style} css={has_css} table={has_table} student={has_student}')
    except Exception as e:
        failed += 1
        print(f'  [FAIL] {name:45} Error: {str(e)[:80]}')

print(f'\nResults: {passed} OK, {failed} WARN/FAIL out of {len(templates)}')

# 额外测试：验证视角条件逻辑
print('\n--- Testing perspective conditional logic ---')
for perspective in ['student', 'advisor', 'reviewer', 'all']:
    data['PERSPECTIVE'] = perspective
    tmpl = Path('templates/literature_reader.markleaf.md')
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(
            loader=FileSystemLoader(str(tmpl.parent)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(tmpl.name)
        result = template.render(**data)
        
        # 只计算 ## 开头的 section headers
        import re
        student_headers = re.findall(r'^## 研究生视角$', result, re.MULTILINE)
        advisor_headers = re.findall(r'^## 导师视角$', result, re.MULTILINE)
        reviewer_headers = re.findall(r'^## 审稿人视角$', result, re.MULTILINE)
        cross_headers = re.findall(r'^## 视角交叉对比$', result, re.MULTILINE)
        
        has_student = len(student_headers) > 0
        has_advisor = len(advisor_headers) > 0
        has_reviewer = len(reviewer_headers) > 0
        has_cross = len(cross_headers) > 0
        
        expected_student = perspective in ['student', 'all']
        expected_advisor = perspective in ['advisor', 'all']
        expected_reviewer = perspective in ['reviewer', 'all']
        expected_cross = perspective == 'all'
        
        ok = (has_student == expected_student and
              has_advisor == expected_advisor and
              has_reviewer == expected_reviewer and
              has_cross == expected_cross)
        
        status = 'OK' if ok else 'FAIL'
        print(f'  [{status}] perspective={perspective:10} student={has_student:5} advisor={has_advisor:5} reviewer={has_reviewer:5} cross={has_cross:5}')
    except Exception as e:
        print(f'  [FAIL] perspective={perspective:10} Error: {str(e)[:60]}')

print('\nDone')
