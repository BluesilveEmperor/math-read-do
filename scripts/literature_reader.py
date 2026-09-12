#!/usr/bin/env python3
"""
文献阅读报告生成器 / Literature Reader Report Generator

从已解析的论文 Markdown 内容出发，生成结构化的中文审阅分析报告。
包含：论文结构导航、术语表、图表索引、三视角分析、复现指导。

用法:
  python literature_reader.py <parsed_md_path> --output-dir ./analysis \
      [--perspective student|advisor|reviewer|all] \
      [--paper-summary analysis/paper_summary.json] \
      [--template templates/literature_reader.template.md] \
      [--language zh|en|bilingual]

依赖:
  pip install openai jinja2
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

# Windows: force UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── 视角框架定义 ─────────────────────────────────────────────────────

STUDENT_PERSPECTIVE_SYSTEM = """你是一位数学/机器人/经济学/计算机科学领域的研究生，正在深入研读一篇学术论文。
你的任务是以学习理解为导向，用中文输出结构化的深度分析。

## 输出要求

1. **摘要**：精炼概括核心内容，点明核心模型/方法，标注来源页码
   - 格式：段落末尾添加 *(来源: p.X Abstract)*

2. **研究问题**：列出明确的 RQ 列表，未明确时标注"（推断）"
   - 格式：每个 RQ 标注来源，如 *(来源: p.1 §1, 第3段)*

3. **核心方法**：详细解释方法论，包含关键公式
   - 公式用 LaTeX 格式（$$...$$），标注公式编号和来源
   - 格式：**Eq.(N)** — 公式描述 *(来源: p.X §Y)*

4. **实验结果**：用表格呈现，包含四列：指标 | 论文声称值 | 来源 | 证据强度
   - 证据强度分为：强（有完整数据支持）、弱（数据不完整/缺失）、无（仅有定性描述）

5. **对复现的指导**：
   - 核心算法：方法名称 + 关键步骤
   - 关键超参数：列出所有超参数及其取值
   - 数据集：数据集名称 + 来源
   - 主要风险：复现中可能遇到的问题

## 写作风格
- 使用专业术语，首次出现时给出英文原文
- 每个论断必须标注具体来源（页码+章节）
- 忠实原文，不添加未在论文中出现的推测
- 公式必须准确引用，不可篡改符号定义"""

ADVISOR_PERSPECTIVE_SYSTEM = """你是一位经验丰富的数学/经济学/计算机科学导师，正在以指导评估为导向审阅一篇学术论文。
你的任务是评估该文献的学术价值和指导意义，判断其是否值得投入时间复现。用中文输出结构化分析。

## 输出要求

1. **文献定位**：发表信息、领域归属、学术影响、难度评级(1-5)、创新程度(1-5)
2. **研究问题与贡献评估**：问题重要性、主要贡献类型
3. **方法论评估**：方法合理性、先修知识要求、可复现性
4. **可复现性评估**：用表格呈现，包含三列：维度 | 状态 | 证据
   - 维度：代码公开、数据可用、环境说明、方法清晰度
   - 状态：✅ 公开 / ⚠️ 部分 / ❌ 缺失
   - 证据：具体出处（如 GitHub 链接在 p.1 脚注）
5. **指导建议**：推荐指数(1-5)、适合方向、先修知识、延伸方向

## 写作风格
- 评估时必须特别关注可复现性（代码/数据是否公开、环境信息是否完整）
- 每个判断必须标注依据来源
- 给出明确的推荐/不推荐结论及理由"""

REVIEWER_PERSPECTIVE_SYSTEM = """你是一位严格的审稿人，正在以同行评审导向评估一篇学术论文。
你的任务是做出专业的独立评判，重点关注论文的质量、严谨性和可信度。用中文输出结构化评审。

## 输出要求

1. **总体评价**：推荐意见 + 各维度评分(1-5) + 依据
   - 推荐意见：接收 / 小修 / 大修 / 拒稿
   - 维度：创新性、方法论、写作质量
   - 每个评分必须附具体依据

2. **研究问题与创新性评估**：新颖性、与已有文献关系、宣称vs实际贡献

3. **方法论评估**：模型设定合理性、识别策略、证明严谨性、数据和计算可靠性

4. **论证与证据评估**：结论是否被充分支持、过度推论、稳健性检验

5. **具体修改意见**：按重要程度分类
   - **强制性修改**：必须修改才能接收
   - **建议性修改**：建议修改可提升质量
   - 每条意见必须附具体来源页码

6. **写作与呈现质量**：结构、数学符号、图表、引用

## 写作风格
- 每条批评必须有具体依据，标注来源页码
- 负面评价必须伴随改进建议
- 保持专业、客观、建设性的语气"""


# ── 论文结构解析 ───────────────────────────────────────────────────

def parse_paper_structure(content: str) -> list:
    """从解析后的 Markdown 中提取论文结构（标题层级+页码）。"""
    sections = []
    lines = content.split('\n')

    current_page = 1
    for line in lines:
        # 尝试检测页码标记 (MinerU 输出中常见的页码格式)
        page_match = re.match(r'(?:<!--\s*)?[Pp]age\s*(\d+)(?:\s*-->)?', line.strip())
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # 检测标题
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            # 清理 Markdown 格式
            title = re.sub(r'\*\*|\*|__|_', '', title).strip()
            if title and level <= 3:
                sections.append({
                    "title": title,
                    "level": level,
                    "page": current_page,
                    "function": infer_argument_function(title),
                    "summary": ""
                })

    return sections


def infer_argument_function(title: str) -> str:
    """根据章节标题推断论证功能。"""
    title_lower = title.lower()

    # Gap 信号
    gap_keywords = ['introduction', 'introduction', '背景', '引言', 'motivation',
                    '问题', 'problem', 'challenge']
    if any(kw in title_lower for kw in gap_keywords):
        return "gap → contribution"

    # Contribution 信号
    contrib_keywords = ['method', 'approach', 'algorithm', 'model', 'framework',
                        '方法', '算法', '模型', '框架', '设计', 'architecture']
    if any(kw in title_lower for kw in contrib_keywords):
        return "contribution"

    # Result 信号
    result_keywords = ['experiment', 'result', 'evaluation', '实验', '结果',
                       '评估', 'evaluation', 'ablation']
    if any(kw in title_lower for kw in result_keywords):
        return "result"

    # Limits 信号
    limit_keywords = ['discussion', 'limitation', 'future', '讨论', '局限',
                      '展望', 'conclusion', '结论']
    if any(kw in title_lower for kw in limit_keywords):
        return "limits"

    # Background
    bg_keywords = ['related', 'background', 'preliminary', 'related work',
                   '相关', '综述', '基础', '预备']
    if any(kw in title_lower for kw in bg_keywords):
        return "background"

    return "—"


# ── 术语提取 ───────────────────────────────────────────────────────

def extract_terminology(content: str) -> list:
    """从论文内容中提取关键术语。"""
    terminology = []

    # 需要过滤的常见词和章节标题
    filter_words = {
        'abstract', 'introduction', 'related work', 'method', 'methods',
        'experiment', 'experiments', 'result', 'results', 'discussion',
        'conclusion', 'conclusions', 'acknowledgment', 'references',
        'appendix', 'supplementary', 'figure', 'table', 'section',
        'problem formulation', 'network architecture', 'training',
        'main results', 'generalization', 'sampling-based methods',
        'learning-based methods', 'deep rapidly', 'random tree star',
        'robot path planning', 'path length', 'convergence time',
        'formulation', 'architecture',
    }

    # 检测缩写定义模式：中文（English, ABBR）或 English (ABBR)
    abbr_patterns = [
        r'([A-Za-z][A-Za-z0-9\-\s]{1,30})\s*[（(]([A-Z][A-Z0-9\-]+)[）)]',  # English (ABBR)
        r'([一-龥]{2,20})\s*[（(]([A-Za-z][A-Za-z0-9\-]+)[）)]',               # 中文 (English)
    ]

    seen_terms = set()
    for pattern in abbr_patterns:
        matches = re.findall(pattern, content)
        for full, abbr in matches:
            full = full.strip()
            abbr = abbr.strip()
            if abbr not in seen_terms and len(abbr) >= 2 and abbr.lower() not in filter_words:
                seen_terms.add(abbr)
                terminology.append({
                    "term": abbr,
                    "full_name": full,
                    "translation": "",
                    "first_appearance": "",
                    "notes": ""
                })

    # 检测首字母大写的专有名词（连续2-3个词）
    tech_pattern = r'\b([A-Z][a-z]+(?:[-\s][A-Z][a-z]+){1,2})\b'
    tech_matches = re.findall(tech_pattern, content)
    for term in set(tech_matches):
        term_lower = term.lower().strip()
        if term not in seen_terms and term_lower not in filter_words and len(term) > 3:
            # 过滤掉句首的普通大写词
            if term_lower not in {'this paper', 'in this', 'we present', 'we propose', 'we show'}:
                seen_terms.add(term)
                terminology.append({
                    "term": term,
                    "full_name": term,
                    "translation": "",
                    "first_appearance": "",
                    "notes": "专业术语，需确认译法"
                })

    return terminology[:30]  # 限制数量


# ── 图表索引 ───────────────────────────────────────────────────────

def extract_figures_index(content: str) -> list:
    """从论文内容中提取图表索引。"""
    figures = []

    # 检测图片引用 ![...](...)
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(img_pattern, content):
        caption = match.group(1).strip()
        path = match.group(2).strip()
        if caption:
            figures.append({
                "id": f"Fig.{len(figures) + 1}",
                "caption_zh": caption if any('\u4e00' <= c <= '\u9fff' for c in caption) else "",
                "caption_en": caption if not any('\u4e00' <= c <= '\u9fff' for c in caption) else "",
                "page": 0,
                "related_section": "",
                "image_path": path
            })

    # 检测表格标记
    table_pattern = r'(?:表|Table)\s*(\d+)[：:.]?\s*(.+)'
    for match in re.finditer(table_pattern, content, re.IGNORECASE):
        table_num = match.group(1)
        caption = match.group(2).strip()
        figures.append({
            "id": f"Table {table_num}",
            "caption_zh": caption,
            "caption_en": "",
            "page": 0,
            "related_section": "",
            "image_path": ""
        })

    return figures


# ── 关键公式提取 ──────────────────────────────────────────────────

def extract_key_formulas(content: str) -> list:
    """从论文内容中提取关键公式。"""
    formulas = []

    # 检测独立公式块 $$...$$ (支持跨行)
    formula_pattern = r'\$\$\s*(.*?)\s*\$\$'
    for i, match in enumerate(re.finditer(formula_pattern, content, re.DOTALL)):
        latex = match.group(1).strip()
        # 清理 LaTeX 中的转义字符
        latex = latex.replace('\\$', '$').replace('\\#', '#').replace('\\&', '&')
        if len(latex) > 3:  # 过滤太短的
            formulas.append({
                "label": f"Eq.({i + 1})",
                "latex": latex,
                "description": "",
                "source": ""
            })

    # 也检测行内公式 $...$ (排除 $$)
    inline_pattern = r'(?<!\$)\$(?!\$)(\S[^$]*?)\$(?!\$)'
    for match in re.finditer(inline_pattern, content):
        latex = match.group(1).strip()
        if len(latex) > 3:
            formulas.append({
                "label": f"Eq.{len(formulas) + 1}",
                "latex": latex,
                "description": "",
                "source": ""
            })

    return formulas[:15]  # 限制数量


# ── LLM 调用 ──────────────────────────────────────────────────────

def call_llm(system_prompt: str, paper_content: str, perspective_name: str) -> str:
    """调用 LLM 进行分析。优先使用环境变量配置的 LLM 端点。"""
    api_key = os.environ.get("LLM_API_KEY", "")
    api_base = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL", "gpt-4o")

    if not api_key:
        print(f"  ⚠ LLM_API_KEY 未设置，使用占位分析（perspective: {perspective_name}）", file=sys.stderr)
        placeholder = (
            f"# [{perspective_name}] 审阅报告（占位）\n\n"
            f"> LLM_API_KEY 未配置，无法完成实际分析。\n"
            f"> 请设置环境变量 LLM_API_KEY，或手动根据以下框架分析。\n\n"
            f"论文内容长度: {len(paper_content)} 字符\n\n"
            f"**说明**: 请按对应视角框架手动完成审阅。\n"
        )
        return placeholder

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=api_base)

        # 截断论文内容以防超过上下文窗口 (取前 80000 字符)
        truncated = paper_content[:80000]
        if len(paper_content) > 80000:
            truncated += "\n\n[论文内容已截断，完整内容共 {} 字符]".format(len(paper_content))

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析以下论文内容：\n\n{truncated}"}
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except ImportError:
        print(f"  ⚠ openai 库未安装，使用占位分析", file=sys.stderr)
        return (
            f"# [{perspective_name}] 审阅报告（占位）\n\n"
            f"> 需要安装 openai 库: pip install openai\n"
            f"论文内容长度: {len(paper_content)} 字符\n"
        )
    except Exception as e:
        print(f"  ❌ LLM 调用失败: {e}", file=sys.stderr)
        return (
            f"# [{perspective_name}] 审阅报告（错误）\n\n"
            f"> LLM 调用出错: {e}\n"
        )


# ── 可复现性评估 ──────────────────────────────────────────────────

def generate_reproducibility_assessment(advisor_report: str, paper_summary_path: str) -> dict:
    """从导师视角报告中提取可复现性评估，写入 JSON 供 G0 门禁使用。"""
    assessment = {
        "reproducibility_rating": "unknown",
        "code_available": False,
        "data_available": False,
        "environment_specified": False,
        "methodology_clarity": "unknown",
        "estimated_effort": "unknown",
        "recommendation": "proceed",
        "risk_flags": [],
    }

    advisor_lower = advisor_report.lower()

    # 代码可用性
    if "code" in advisor_lower or "github" in advisor_lower or "repository" in advisor_lower:
        assessment["code_available"] = True

    # 数据可用性
    if "data" in advisor_lower and ("available" in advisor_lower or "public" in advisor_lower or "open" in advisor_lower):
        assessment["data_available"] = True

    # 环境说明
    if "environment" in advisor_lower or "requirements" in advisor_lower or "docker" in advisor_lower:
        assessment["environment_specified"] = True

    # 可复现性评级推断
    if assessment["code_available"] and assessment["data_available"] and assessment["environment_specified"]:
        assessment["reproducibility_rating"] = "high"
        assessment["recommendation"] = "proceed"
    elif assessment["code_available"] and assessment["data_available"]:
        assessment["reproducibility_rating"] = "medium"
        assessment["recommendation"] = "proceed_with_caution"
        assessment["risk_flags"].append("environment_not_specified")
    elif assessment["code_available"]:
        assessment["reproducibility_rating"] = "low"
        assessment["recommendation"] = "needs_confirmation"
        assessment["risk_flags"].append("data_not_available")
        assessment["risk_flags"].append("environment_not_specified")
    else:
        assessment["reproducibility_rating"] = "very_low"
        assessment["recommendation"] = "needs_human_approval"
        assessment["risk_flags"].append("code_not_available")
        assessment["risk_flags"].append("data_not_available")
        assessment["risk_flags"].append("environment_not_specified")

    # 读取已有 paper_summary 补充信息
    if paper_summary_path and Path(paper_summary_path).exists():
        try:
            summary = json.loads(Path(paper_summary_path).read_text(encoding="utf-8"))
            assessment["domain"] = summary.get("domain", "unknown")
            assessment["paper_title"] = summary.get("title", "unknown")
        except Exception:
            pass

    # 写入文件
    output_path = Path(paper_summary_path).parent / "reproducibility_assessment.json" if paper_summary_path else Path("analysis/reproducibility_assessment.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(assessment, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✅ 可复现性评估已写入: {output_path}")

    return assessment


# ── 模板渲染 ──────────────────────────────────────────────────────

def select_template_interactive():
    """交互式选择模板。返回选中的模板路径。"""
    # 非交互式终端不得静默默认，必须让用户显式指定
    if not sys.stdin.isatty():
        print(
            "  ❌ 模板必须由用户选择，但当前不是交互式终端。\n"
            "     请显式指定: --template templates/literature_reader.<风格>.md",
            file=sys.stderr,
        )
        return None

    # 模板目录：优先使用脚本所在目录的 templates/，其次当前目录
    script_dir = Path(__file__).parent.parent
    template_dir = script_dir / "templates"
    if not template_dir.exists():
        template_dir = Path("templates")

    templates = sorted(template_dir.glob("literature_reader.*.md"))
    # 过滤掉旧版 template.md
    templates = [t for t in templates if t.stem != "literature_reader.template"]

    if not templates:
        print(f"  ❌ 未找到任何模板文件 (搜索路径: {template_dir})")
        return None

    print("\n" + "=" * 50)
    print("📋 可用模板列表")
    print("=" * 50)

    # 模板名称映射（按推荐顺序排列）
    name_map = {
        "markleaf": "LaTeX 风格（推荐）",
        "print": "印刷品",
        "retro-print": "铅字印刷",
        "sans": "无衬线",
        "serif": "衬线",
        "magazine": "杂志",
        "minimal": "极简",
        "notebook": "手记",
        "print-double": "双色印刷",
    }

    # 按推荐顺序排序模板
    order = ["markleaf", "print", "retro-print", "sans", "serif", "magazine", "minimal", "notebook", "print-double"]
    templates_sorted = []
    for name in order:
        for t in templates:
            if t.stem.replace("literature_reader.", "") == name:
                templates_sorted.append(t)
                break
    # 添加未在顺序列表中的其他模板
    for t in templates:
        if t not in templates_sorted:
            templates_sorted.append(t)
    templates = templates_sorted

    for i, t in enumerate(templates, 1):
        # 提取模板名称（literature_reader.xxx.md -> xxx）
        name = t.stem.replace("literature_reader.", "")
        desc = name_map.get(name, name)
        print(f"  {i}. {desc} ({name})")

    print("=" * 50)

    while True:
        try:
            choice = input("\n请选择模板编号 (1-{}，默认 1): ".format(len(templates)))
            if choice.strip() == "":
                idx = 0
            else:
                idx = int(choice) - 1
            if 0 <= idx < len(templates):
                selected = templates[idx]
                name = selected.stem.replace("literature_reader.", "")
                desc = name_map.get(name, name)
                print(f"\n  ✅ 已选择: {desc}")
                return str(selected)
            else:
                print(f"  ⚠️ 请输入 1-{len(templates)} 之间的数字")
        except EOFError:
            print(
                "\n  ❌ 输入流已结束（非交互环境），无法获取模板选择。\n"
                "     请显式指定: --template templates/literature_reader.<风格>.md",
                file=sys.stderr,
            )
            return None
        except ValueError:
            print(f"  ⚠️ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n  ❌ 已取消")
            return None


def select_perspective_interactive():
    """交互式选择审阅视角。返回视角字符串，取消则返回 None。

    视角属"必须询问"项：不设默认值，不得代为选择。
    """
    if not sys.stdin.isatty():
        print(
            "  ❌ 审阅视角必须由用户选择，但当前不是交互式终端。\n"
            "     请显式指定: --perspective student|advisor|reviewer|all",
            file=sys.stderr,
        )
        return None

    options = [
        ("student", "研究生视角 — 学习理解导向（读懂论文、吃透方法）"),
        ("advisor", "导师视角 — 指导评估导向（判断学术价值与复现可行性）"),
        ("reviewer", "审稿人视角 — 同行评审导向（批判性审查）"),
        ("all", "三方全出 — 三个视角 + 交叉对比（要进复现流程选这个）"),
    ]

    print("\n" + "=" * 50)
    print("🎓 请选择审阅视角")
    print("=" * 50)
    for i, (_, desc) in enumerate(options, 1):
        print(f"  {i}. {desc}")
    print("=" * 50)

    while True:
        try:
            choice = input(f"\n请选择视角编号 (1-{len(options)}，无默认): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                value, desc = options[int(choice) - 1]
                print(f"\n  ✅ 已选择: {desc}")
                return value
            print(f"  ⚠️ 请输入 1-{len(options)} 之间的数字")
        except EOFError:
            print(
                "\n  ❌ 输入流已结束（非交互环境），无法获取视角选择。\n"
                "     请显式指定: --perspective student|advisor|reviewer|all",
                file=sys.stderr,
            )
            return None
        except ValueError:
            print("  ⚠️ 请输入有效的数字", file=sys.stderr)
        except KeyboardInterrupt:
            print("\n\n  ❌ 已取消")
            return None


def render_report(template_path: str, data: dict) -> str:
    """使用 Jinja2 渲染报告模板。"""
    try:
        from jinja2 import Environment, FileSystemLoader, BaseLoader

        if Path(template_path).exists():
            template_dir = str(Path(template_path).parent)
            template_name = Path(template_path).name
            env = Environment(
                loader=FileSystemLoader(template_dir),
                keep_trailing_newline=True,
                trim_blocks=True,      # 去除块后的第一个换行
                lstrip_blocks=True,    # 去除块前的前导空白
            )
            template = env.get_template(template_name)
        else:
            # 回退：使用字符串模板
            env = Environment(loader=BaseLoader())
            template = env.from_string(_get_default_template())

        return template.render(**data)
    except ImportError:
        print("  ⚠ jinja2 未安装，使用简单字符串替换", file=sys.stderr)
        return _simple_render(data)


def _simple_render(data: dict) -> str:
    """简单的字符串替换渲染（不依赖 Jinja2 时的回退方案）。"""
    # 构建基础报告
    lines = []
    lines.append(f"# 文献阅读：{data.get('PAPER_TITLE', 'Unknown')}")
    lines.append("")
    lines.append(f"> **论文**: {data.get('PAPER_TITLE', '')}")
    lines.append(f"> **作者**: {data.get('AUTHORS', '')}")
    lines.append(f"> **发表**: {data.get('VENUE', '')}")
    lines.append(f"> **领域**: {data.get('DOMAIN', '')}")
    lines.append(f"> **审阅日期**: {data.get('DATE', '')}")
    lines.append(f"> **审阅视角**: {data.get('PERSPECTIVE', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 研究生视角
    if data.get('STUDENT_ABSTRACT'):
        lines.append("## 4. 研究生视角")
        lines.append("")
        lines.append("> 🎓 以学习理解为导向 — 深度理解论文核心方法")
        lines.append("")
        lines.append("### 4.1 摘要")
        lines.append("")
        lines.append(data.get('STUDENT_ABSTRACT', ''))
        lines.append("")

    # 导师视角
    if data.get('ADVISOR_CONTRIBUTION'):
        lines.append("## 5. 导师视角")
        lines.append("")
        lines.append("> 🎓 以指导评估为导向 — 判断学术价值与复现可行性")
        lines.append("")
        lines.append("### 5.2 可复现性评估")
        lines.append("")
        lines.append(data.get('ADVISOR_CONTRIBUTION', ''))
        lines.append("")

    # 审稿人视角
    if data.get('REVIEWER_ORIGINALITY'):
        lines.append("## 6. 审稿人视角")
        lines.append("")
        lines.append("> 🎯 以同行评审为导向 — 批判性审查")
        lines.append("")
        lines.append(data.get('REVIEWER_ORIGINALITY', ''))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*审阅生成于 {data.get('DATE', '')} by Math-Read-Do Literature Reader Engine*")

    return '\n'.join(lines)


def _get_default_template() -> str:
    """返回默认模板字符串（当模板文件不存在时使用）。"""
    return """# 文献阅读：{{PAPER_TITLE}}

> **论文**: {{PAPER_TITLE}}
> **作者**: {{AUTHORS}}
> **发表**: {{VENUE}}
> **领域**: {{DOMAIN}}
> **审阅日期**: {{DATE}}
> **审阅视角**: {{PERSPECTIVE}}

---

## 4. 研究生视角

> 🎓 以学习理解为导向 — 深度理解论文核心方法

### 4.1 摘要

{{STUDENT_ABSTRACT}}
*(来源: p.1 Abstract)*

---

## 5. 导师视角

> 🎓 以指导评估为导向 — 判断学术价值与复现可行性

### 5.2 可复现性评估

| 维度 | 状态 | 证据 |
|------|------|------|
| 代码公开 | {{ADVISOR_CODE_AVAIL}} | {{ADVISOR_CODE_EVIDENCE}} |
| 数据可用 | {{ADVISOR_DATA_AVAIL}} | {{ADVISOR_DATA_EVIDENCE}} |
| 环境说明 | {{ADVISOR_ENV_SPEC}} | {{ADVISOR_ENV_EVIDENCE}} |
| **总体评级** | **{{ADVISOR_REPRO_RATING}}** | — |

---

## 6. 审稿人视角

> 🎯 以同行评审为导向 — 批判性审查

{{REVIEWER_ORIGINALITY}}

---

*审阅生成于 {{DATE}} by Math-Read-Do Literature Reader Engine*
"""


# ── 主函数 ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="文献阅读报告生成器 — 结构化中文审阅分析"
    )
    parser.add_argument(
        "paper_md",
        help="论文解析后的 Markdown 文件路径"
    )
    parser.add_argument(
        "--output-dir", default="./analysis",
        help="输出目录（默认 ./analysis）"
    )
    parser.add_argument(
        "--paper-summary", default=None,
        help="paper_summary.json 路径（可选，用于补充可复现性评估）"
    )
    parser.add_argument(
        "--perspective", default=None,
        choices=["student", "advisor", "reviewer", "all"],
        help="指定视角: student(研究生)/advisor(导师)/reviewer(审稿人)/all(三方)；未指定则交互询问"
    )
    parser.add_argument(
        "--template", default=None,
        help="模板文件路径（默认询问用户选择）"
    )
    parser.add_argument(
        "--language", default="zh",
        choices=["en", "zh", "bilingual"],
        help="输出语言: en(英文)/zh(中文)/bilingual(中英双语)"
    )

    args = parser.parse_args()

    # ── 模板选择 ──────────────────────────────────────────────────
    template_path = args.template
    if template_path is None:
        template_path = select_template_interactive()
        if template_path is None:
            sys.exit(1)

    # ── 视角选择（必须询问，不得代选）────────────────────────────
    perspective = args.perspective
    if perspective is None:
        perspective = select_perspective_interactive()
        if perspective is None:
            sys.exit(1)

    paper_content = Path(args.paper_md).read_text(encoding="utf-8") if Path(args.paper_md).exists() else ""
    paper_stem = Path(args.paper_md).stem
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📖 论文: {args.paper_md}")
    print(f"📐 视角: {perspective}")
    print(f"📂 输出: {output_dir.resolve()}")
    print(f"{'='*50}")

    # ── 步骤 1: 解析论文结构 ──────────────────────────────────────
    print(f"\n📑 [1/5] 解析论文结构...")
    sections = parse_paper_structure(paper_content)
    print(f"  ✅ 识别 {len(sections)} 个章节")

    # ── 步骤 2: 提取术语 ──────────────────────────────────────────
    print(f"\n📚 [2/5] 提取术语表...")
    terminology = extract_terminology(paper_content)
    print(f"  ✅ 识别 {len(terminology)} 个术语")

    # ── 步骤 3: 提取图表索引 ──────────────────────────────────────
    print(f"\n📊 [3/5] 提取图表索引...")
    figures = extract_figures_index(paper_content)
    print(f"  ✅ 识别 {len(figures)} 个图表/表格")

    # ── 步骤 4: 提取关键公式 ──────────────────────────────────────
    print(f"\n🔢 [4/5] 提取关键公式...")
    key_formulas = extract_key_formulas(paper_content)
    print(f"  ✅ 识别 {len(key_formulas)} 个公式")

    # ── 步骤 5: 三视角分析 ────────────────────────────────────────
    print(f"\n🎓 [5/5] 三视角分析...")

    # perspective 已在 main() 顶部解析（缺省时由用户交互选择，不设默认值）
    if "advisor" not in (perspective, "all"):
        print(
            "  ⚠️ 未包含导师视角 → 不会产出 reproducibility_assessment.json，"
            "G01 门禁将无法通过，无法进入复现流程（Phase 2+）。\n"
            "     如需复现，请改用 --perspective advisor 或 all。",
            file=sys.stderr,
        )
    results = {}

    student_report = ""
    advisor_report = ""
    reviewer_report = ""

    if perspective in ("student", "all"):
        print(f"\n  🎓 [1/3] 研究生视角 — 学习理解分析中...")
        student_report = call_llm(
            STUDENT_PERSPECTIVE_SYSTEM, paper_content, "研究生视角"
        )
        results["student"] = student_report

    if perspective in ("advisor", "all"):
        print(f"\n  🎓 [2/3] 导师视角 — 指导评估分析中...")
        advisor_report = call_llm(
            ADVISOR_PERSPECTIVE_SYSTEM, paper_content, "导师视角"
        )
        results["advisor"] = advisor_report

        # 从导师视角产出可复现性评估
        summary_path = args.paper_summary
        if not summary_path:
            summary_path = str(output_dir / "paper_summary.json")
        generate_reproducibility_assessment(advisor_report, summary_path)

    if perspective in ("reviewer", "all"):
        print(f"\n  🎯 [3/3] 审稿人视角 — 同行评审分析中...")
        reviewer_report = call_llm(
            REVIEWER_PERSPECTIVE_SYSTEM, paper_content, "审稿人视角"
        )
        results["reviewer"] = reviewer_report

    # ── 渲染最终报告 ──────────────────────────────────────────────
    print(f"\n📝 渲染最终报告...")

    # 准备模板数据
    template_data = {
        "PAPER_TITLE": paper_stem,
        "AUTHORS": "",
        "VENUE": "",
        "DOMAIN": "",
        "PAPER_TYPE": "",
        "PAPER_TYPE_DESC": "",
        "DATE": datetime.now().strftime("%Y-%m-%d"),
        "PERSPECTIVE": perspective,
        "sections": sections,
        "terminology": terminology,
        "figures": figures,
        "key_formulas": key_formulas,
        "research_questions": [],
        "student_metrics": [],
        "STUDENT_ABSTRACT": results.get("student", ""),
        "STUDENT_METHODS": "",
        "REPRO_CORE_ALGORITHM": "",
        "REPRO_HYPERPARAMS": "",
        "REPRO_DATASETS": "",
        "REPRO_RISKS": "",
        "ADVISOR_VENUE": "",
        "ADVISOR_DOMAIN": "",
        "ADVISOR_DIFFICULTY": "",
        "ADVISOR_INNOVATION": "",
        "ADVISOR_CONTRIBUTION": results.get("advisor", ""),
        "ADVISOR_CODE_AVAIL": "",
        "ADVISOR_CODE_EVIDENCE": "",
        "ADVISOR_DATA_AVAIL": "",
        "ADVISOR_DATA_EVIDENCE": "",
        "ADVISOR_ENV_SPEC": "",
        "ADVISOR_ENV_EVIDENCE": "",
        "ADVISOR_CLARITY": "",
        "ADVISOR_CLARITY_EVIDENCE": "",
        "ADVISOR_REPRO_RATING": "",
        "ADVISOR_RECOMMENDATION": "",
        "ADVISOR_SUITABLE": "",
        "ADVISOR_PREREQUISITES": "",
        "ADVISOR_EXTENSIONS": "",
        "REVIEWER_RECOMMENDATION": "",
        "REVIEWER_RECOMMENDATION_RATIONALE": "",
        "REVIEWER_INNOVATION": "",
        "REVIEWER_INNOVATION_RATIONALE": "",
        "REVIEWER_METHODOLOGY": "",
        "REVIEWER_METHODOLOGY_RATIONALE": "",
        "REVIEWER_WRITING": "",
        "REVIEWER_WRITING_RATIONALE": "",
        "REVIEWER_ORIGINALITY": results.get("reviewer", ""),
        "reviewer_mandatory": [],
        "reviewer_suggested": [],
        "CROSS_STRENGTH_STUDENT": "",
        "CROSS_STRENGTH_ADVISOR": "",
        "CROSS_STRENGTH_REVIEWER": "",
        "CROSS_CONCERN_STUDENT": "",
        "CROSS_CONCERN_ADVISOR": "",
        "CROSS_CONCERN_REVIEWER": "",
        "CROSS_METHOD_STUDENT": "",
        "CROSS_METHOD_ADVISOR": "",
        "CROSS_METHOD_REVIEWER": "",
    }

    # 渲染（template_path 已在 main() 顶部解析：显式 --template 或用户交互选择结果）
    if not Path(template_path).exists():
        print(
            f"  ⚠️ 模板文件不存在: {template_path}，回退到内置默认模板",
            file=sys.stderr,
        )
    rendered_report = render_report(template_path, template_data)

    # 写入最终报告
    report_path = output_dir / "文献阅读.md"
    report_path.write_text(rendered_report, encoding="utf-8")
    print(f"  ✅ 报告已写入: {report_path}")

    # 写入结构化 JSON（供下游消费）
    structured_data = {
        "paper": {
            "title": paper_stem,
            "source_path": str(args.paper_md),
        },
        "sections": sections,
        "terminology": terminology,
        "figures": figures,
        "key_formulas": key_formulas,
        "perspectives": {
            "student": results.get("student", ""),
            "advisor": results.get("advisor", ""),
            "reviewer": results.get("reviewer", ""),
        },
        "generated_at": datetime.now().isoformat(),
    }
    json_path = output_dir / "literature_reading.json"
    json_path.write_text(
        json.dumps(structured_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✅ 结构化数据已写入: {json_path}")

    # ── 产出摘要 ──────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"✅ 文献阅读报告生成完成!")
    print(f"输出目录: {output_dir.resolve()}")
    print(f"  - 报告: {report_path.name}")
    print(f"  - 数据: {json_path.name}")
    print(f"  - 章节: {len(sections)}")
    print(f"  - 术语: {len(terminology)}")
    print(f"  - 图表: {len(figures)}")
    print(f"  - 公式: {len(key_formulas)}")


if __name__ == "__main__":
    main()
