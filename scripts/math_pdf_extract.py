#!/usr/bin/env python3
"""
MinerU Open SDK — 将本地 PDF 文件转换为 Markdown（使用 mineru-open-sdk 的 extract 模式）。
读取 ~/.mineru/config.yaml 获取 token，支持 Precision Extract。
每次操作结束后自动报告当日 API 用量。

用法:
  python math_pdf_extract.py <pdf_path> [--output-dir <dir>] [--model vlm]

依赖:
  pip install mineru-open-sdk
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import date, timedelta

# ── Windows GBK 编码兼容 ─────────────────────────────────────────────
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        import io
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ── 配置读取 ──────────────────────────────────────────────────────────

def get_token():
    """从 ~/.mineru/config.yaml 读取 token。"""
    config_path = Path.home() / ".mineru" / "config.yaml"
    if not config_path.exists():
        print("ERROR: 配置文件不存在: ~/.mineru/config.yaml", file=sys.stderr)
        print(file=sys.stderr)
        print("请创建 ~/.mineru/config.yaml，内容为：", file=sys.stderr)
        print("  token: '你的API密钥'", file=sys.stderr)
        print(file=sys.stderr)
        print("如果还没有密钥，请前往 https://mineru.net/apiManage/token 注册获取。", file=sys.stderr)
        sys.exit(1)

    try:
        try:
            import yaml
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except ImportError:
            text = config_path.read_text(encoding="utf-8")
            token = None
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("token:"):
                    token = line.split(":", 1)[1].strip().strip("'\"")
                    break
            config = {"token": token} if token else {}

        token = config.get("token", "")
        if not token:
            print("ERROR: ~/.mineru/config.yaml 中未找到有效的 token", file=sys.stderr)
            print("请确保文件包含: token: '你的API密钥'", file=sys.stderr)
            sys.exit(1)
        return token
    except Exception as e:
        print(f"ERROR: 读取配置文件失败: {e}", file=sys.stderr)
        print("请检查 ~/.mineru/config.yaml 格式是否正确", file=sys.stderr)
        sys.exit(1)


# ── 日用量跟踪 ──────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
QUOTA_FILE = SKILL_DIR / "daily_usage.json"
DAILY_QUOTA_PAGES = 2000


def _load_daily_usage() -> dict:
    if QUOTA_FILE.exists():
        try:
            return json.loads(QUOTA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_daily_usage(usage: dict):
    QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUOTA_FILE.write_text(
        json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def report_quota(used_pages: int = 0):
    """记录本次用量并报告当日余额。返回 (used_today, remaining_pages)。"""
    usage = _load_daily_usage()
    today = date.today().isoformat()

    today_entry = usage.get(today, {"pages": 0, "files": 0})
    today_entry["pages"] += used_pages
    today_entry["files"] += 1
    usage[today] = today_entry

    cutoff = (date.today() - timedelta(days=30)).isoformat()
    for k in list(usage.keys()):
        if k < cutoff:
            del usage[k]

    _save_daily_usage(usage)

    used = today_entry["pages"]
    files = today_entry["files"]
    remaining = max(0, DAILY_QUOTA_PAGES - used)

    print(f"\n📊 ── 当日 MinerU API 用量 ────────────────────")
    print(f"   已用页数:         {used}")
    print(f"   剩余可处理页数:    {remaining}（日限额 {DAILY_QUOTA_PAGES} 页）")
    print(f"   已处理文件数:      {files}")
    print(f"   📌 注: 超出限额后解析优先级会降低，但仍可继续使用")
    print(f"──────────────────────────────────────────────\n")

    return used, remaining


# ── 获取 PDF 页数（估算） ───────────────────────────────────────────

def estimate_pdf_pages(pdf_path: str) -> int:
    path = Path(pdf_path)
    try:
        content = path.read_bytes()
        import re
        page_refs = content.count(b"/Type /Page")
        if page_refs > 5:
            return page_refs
        matches = re.findall(rb"/Count\s+(\d+)", content)
        if matches:
            return max(int(m) for m in matches)
        return max(content.count(b"/Page\n"), content.count(b"/Page\r"), 1)
    except Exception:
        return 0


# ── 主函数 ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MinerU Open SDK — PDF → Markdown 转换（Precision Extract）"
    )
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument(
        "--output-dir", default="./math-output",
        help="输出目录（默认 ./math-output）"
    )
    parser.add_argument(
        "--model", default="vlm", choices=["pipeline", "vlm", "html"],
        help="模型版本（默认 vlm）"
    )
    parser.add_argument(
        "--ocr", action="store_true",
        help="启用 OCR（默认关闭）"
    )
    parser.add_argument(
        "--language", default="en",
        help="文档语言（英文论文默认 en，中文论文用 ch）"
    )
    parser.add_argument(
        "--no-formula", action="store_false", dest="formula",
        help="禁用公式识别（默认开启）"
    )
    parser.add_argument(
        "--no-table", action="store_false", dest="table",
        help="禁用表格识别（默认开启）"
    )
    parser.add_argument(
        "--pages", default=None,
        help="页码范围，如 '1-10,15'"
    )

    args = parser.parse_args()

    token = get_token()

    try:
        from mineru import MinerU
    except ImportError:
        print("ERROR: 需要安装 mineru-open-sdk", file=sys.stderr)
        print("请执行: pip install mineru-open-sdk", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(args.pdf_path).resolve()
    if not pdf_path.exists():
        print(f"ERROR: 文件不存在: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    page_count = estimate_pdf_pages(str(pdf_path))
    if page_count:
        print(f"📄 PDF 预估页数: {page_count}")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    client = MinerU(token=token)
    try:
        print(f"📤 正在上传并解析: {pdf_path.name}")
        result = client.extract(
            source=str(pdf_path),
            model=args.model,
            ocr=args.ocr or None,
            formula=args.formula,
            table=args.table,
            language=args.language,
            pages=args.pages,
        )

        if result.state != "done":
            error_msg = result.error or "未知错误"
            print(f"❌ 解析失败: {error_msg}", file=sys.stderr)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                _save_daily_usage({})
                print("   ⚠ 已重置本地日用量计数，请重试", file=sys.stderr)
            sys.exit(1)

        md_path = output_dir / f"{pdf_path.stem}.md"
        result.save_markdown(str(md_path), with_images=True)
        print(f"✅ 转换完成: {md_path}")

        actual_pages = page_count
        if result.progress and result.progress.total_pages:
            actual_pages = max(actual_pages, result.progress.total_pages)

        report_quota(used_pages=actual_pages)

        return 0

    except Exception as e:
        print(f"❌ 处理失败: {e}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
