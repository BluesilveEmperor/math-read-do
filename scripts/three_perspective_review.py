#!/usr/bin/env python3
"""
三方视角审阅执行器 / Three-Perspective Review Executor

从已解析的论文 Markdown 内容出发，依次按研究生、导师、审稿人三个身份
框架对论文进行深度分析，产出结构化审阅文件和可复现性评估。

用法:
  python three_perspective_review.py <marked_md_path> --output-dir ./analysis

依赖:
  pip install openai  (或其他 LLM 客户端)
"""
import os
import sys
import json
import argparse
from pathlib import Path


# ── 视角框架定义 ─────────────────────────────────────────────────────

STUDENT_PERSPECTIVE_SYSTEM = """你是一位数学/经济学领域的研究生，正在以学习理解为导向深入研读一篇学术论文。
你的任务是从论文中提取核心知识，帮助自己（和读者）理解、消化和吸收文献内容。

请按以下框架分析：
1. **摘要** — 精炼概括核心内容，点明核心模型/方法
2. **文献综述** — 理论根基、关键文献、研究空白
3. **研究问题** — 明确的 RQ 列表，未明确时标注"（推断）"
4. **研究方法** — 理论模型、实证策略、数据来源、关键变量
5. **研究结果** — 主要发现、核心数据/统计结果
6. **讨论与评价** — 从学习者角度的诚实评估、对自己的启发
7. **关键公式与概念** — 列出核心数学/经济公式及定义

要求：忠实原文，使用专业术语，关键公式必须准确引用。"""

ADVISOR_PERSPECTIVE_SYSTEM = """你是一位经验丰富的数学/经济学导师，正在以指导评估为导向审阅一篇学术论文。
你的任务是评估该文献的学术价值和指导意义，判断其是否值得投入时间复现。

请按以下框架分析：
1. **文献定位** — 发表信息、领域归属、学术影响、难度评级(1-5)、创新程度(1-5)
2. **研究问题与贡献评估** — 问题重要性、主要贡献类型
3. **方法论评估（适合指导的角度）** — 方法合理性、先修知识要求、可复现性
4. **结果可信度评估** — 稳健性、潜在问题、争议点
5. **教学与指导建议** — 推荐指数(1-5)、建议阅读方式、延伸材料
6. **对学生研究的启发** — 拓展方向、切入点、警惕信号

要求：评估时必须特别关注可复现性（代码/数据是否公开、环境信息是否完整）。
在方法论评估部分给出明确的可复现性评级。"""

REVIEWER_PERSPECTIVE_SYSTEM = """你是一位严格的审稿人，正在以同行评审导向评估一篇学术论文。
你的任务是做出专业的独立评判，重点关注论文的质量、严谨性和可信度。

请按以下框架评审：
1. **总体评价** — 推荐意见（接收/小修/大修/拒稿）、评分（创新性/方法论/写作质量各1-5）
2. **研究问题与创新性评估** — 新颖性、与已有文献关系、宣称vs实际贡献的落差
3. **方法论评估** — 模型设定合理性、识别策略（经济学）、证明严谨性（数学）、数据和计算可靠性
4. **论证与证据评估** — 结论是否被充分支持、过度推论、稳健性检验
5. **具体修改意见** — 按重要程度列出：[强制性修改]、[建议性修改]、[细节修正]
6. **写作与呈现质量** — 结构、数学符号、图表、引用
7. **总结与建议** — 最终推荐意见、接收条件、给作者的建设性建议

要求：每条批评必须有具体依据，负面评价必须伴随改进建议。"""


# ── 主函数 ──────────────────────────────────────────────────────────

def read_markdown(md_path: str) -> str:
    path = Path(md_path)
    if not path.exists():
        print(f"ERROR: 文件不存在: {md_path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def write_report(output_dir: str, filename: str, content: str):
    path = Path(output_dir) / filename
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ 写入: {path}")
    return str(path)


def call_llm(system_prompt: str, paper_content: str, perspective_name: str) -> str:
    """调用 LLM 进行审阅分析。优先使用环境变量配置的 LLM 端点。"""
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


def main():
    parser = argparse.ArgumentParser(
        description="三方视角审阅执行器 — 研究生/导师/审稿人分析"
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
        help="指定视角: student(研究生)/advisor(导师)/reviewer(审稿人)/all(三方)"
    )
    parser.add_argument(
        "--language", default="ch",
        choices=["en", "ch", "bilingual"],
        help="输出语言: en(英文)/ch(中文)/bilingual(中英双列)"
    )

    args = parser.parse_args()

    paper_content = read_markdown(args.paper_md)
    paper_stem = Path(args.paper_md).stem
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    perspective = args.perspective or "all"

    print(f"\n📖 论文: {args.paper_md}")
    print(f"📐 视角: {perspective}")
    print(f"{'='*50}")

    results = {}

    # ── 研究生视角 ──────────────────────────────────────────────────
    if perspective in ("student", "all"):
        print(f"\n🎓 [1/3] 研究生视角 — 学习理解分析中...")
        student_report = call_llm(
            STUDENT_PERSPECTIVE_SYSTEM, paper_content, "研究生视角"
        )
        student_file = write_report(
            output_dir, f"{paper_stem}_student_review.md", student_report
        )
        results["student"] = student_file

    # ── 导师视角 ──────────────────────────────────────────────────
    if perspective in ("advisor", "all"):
        print(f"\n🎓 [2/3] 导师视角 — 指导评估分析中...")
        advisor_report = call_llm(
            ADVISOR_PERSPECTIVE_SYSTEM, paper_content, "导师视角"
        )
        advisor_file = write_report(
            output_dir, f"{paper_stem}_advisor_review.md", advisor_report
        )
        results["advisor"] = advisor_file

        # 从导师视角产出可复现性评估
        summary_path = args.paper_summary
        if not summary_path:
            summary_path = str(output_dir / "paper_summary.json")
        generate_reproducibility_assessment(advisor_report, summary_path)

    # ── 审稿人视角 ──────────────────────────────────────────────────
    if perspective in ("reviewer", "all"):
        print(f"\n🎯 [3/3] 审稿人视角 — 同行评审分析中...")
        reviewer_report = call_llm(
            REVIEWER_PERSPECTIVE_SYSTEM, paper_content, "审稿人视角"
        )
        reviewer_file = write_report(
            output_dir, f"{paper_stem}_reviewer_review.md", reviewer_report
        )
        results["reviewer"] = reviewer_file

    # ── 产出摘要 ──────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"✅ 三方视角审阅完成!")
    print(f"输出目录: {output_dir.resolve()}")
    for k, v in results.items():
        print(f"  - {k}: {v}")

    # 写入审阅清单
    manifest = {
        "paper": paper_stem,
        "perspective": perspective,
        "outputs": results,
        "reproducibility_assessment": str(
            output_dir / "reproducibility_assessment.json"
        )
    }
    manifest_path = output_dir / "review_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  清单: {manifest_path}")


if __name__ == "__main__":
    main()
