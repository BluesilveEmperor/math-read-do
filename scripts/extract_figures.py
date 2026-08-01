#!/usr/bin/env python3
"""
extract_figures.py - 论文图表提取脚本（出版级 / Publication-Grade）
从 PDF 精确裁剪图表区域，用于复现报告插图。

专为凸优化/路径规划类论文设计（如 FastPathPlanning TRO2024）：
- 支持按页码+坐标精确裁剪
- 支持多 DPI 输出（300/600）
- 自动生成裁剪区域可视化（调试用）
- 支持子图拆分（如 Fig 1 top/bottom）

用法:
    python extract_figures.py <pdf_path> --output-dir results/figures/ [--dpi 300] [--regions regions.json]
    python extract_figures.py <pdf_path> --list-pages  # 仅列出各页尺寸

依赖:
    pip install PyMuPDF Pillow

示例 regions.json:
[
    {"page": 0, "x0": 42, "y0": 38, "x1": 574, "y1": 210, "name": "fig02_preprocessing.png"},
    {"page": 0, "x0": 42, "y0": 250, "x1": 574, "y1": 490, "name": "fig01_path.png"}
]
"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)


def list_page_sizes(pdf_path):
    """列出 PDF 各页尺寸"""
    doc = fitz.open(pdf_path)
    print(f"PDF: {pdf_path}")
    print(f"Pages: {len(doc)}")
    print("-" * 50)
    for i, page in enumerate(doc):
        r = page.rect
        print(f"  Page {i+1}: {r.width:.0f} x {r.height:.0f} pts "
              f"({r.width/72:.1f} x {r.height/72:.1f} in)")
    doc.close()


def auto_detect_figures(pdf_path, pages=None):
    """自动检测图片块位置（启发式）"""
    doc = fitz.open(pdf_path)
    figures = []
    
    target_pages = pages if pages else range(len(doc))
    for p in target_pages:
        if p >= len(doc):
            continue
        page = doc[p]
        blocks = page.get_text("dict")["blocks"]
        img_blocks = [b for b in blocks if b["type"] == 1]
        
        for i, ib in enumerate(img_blocks):
            r = ib["bbox"]
            figures.append({
                "page": p,
                "x0": r[0], "y0": r[1], "x1": r[2], "y1": r[3],
                "name": f"page{p+1}_img{i+1}.png",
                "size": f"{r[2]-r[0]:.0f}x{r[3]-r[1]:.0f}"
            })
    
    doc.close()
    return figures


def extract_regions(pdf_path, regions, output_dir, dpi=300):
    """按指定区域提取图片"""
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    
    scale = dpi / 72.0
    results = []
    
    print(f"DPI: {dpi} (scale: {scale:.2f}x)")
    print(f"Output: {output_dir}")
    print("-" * 50)
    
    for reg in regions:
        page_num = reg["page"]
        if page_num >= len(doc):
            print(f"⚠️  Page {page_num+1} 超出范围，跳过")
            continue
        
        page = doc[page_num]
        clip = fitz.Rect(reg["x0"], reg["y0"], reg["x1"], reg["y1"])
        pix = page.get_pixmap(dpi=dpi, clip=clip)
        
        out_path = os.path.join(output_dir, reg["name"])
        pix.save(out_path)
        results.append({
            "file": out_path,
            "size": f"{pix.width}x{pix.height}",
            "source": f"page {page_num+1}"
        })
        print(f"  ✅ {reg['name']}: {pix.width}x{pix.height} "
              f"(from page {page_num+1}, clip [{reg['x0']:.0f},{reg['y0']:.0f},{reg['x1']:.0f},{reg['y1']:.0f}])")
    
    doc.close()
    return results


def generate_debug_overlay(pdf_path, regions, output_path, dpi=150):
    """生成裁剪区域叠加可视化（调试用）"""
    from PIL import Image, ImageDraw, ImageFont
    
    doc = fitz.open(pdf_path)
    scale = dpi / 72.0
    
    # 只处理有裁剪区域的页面
    pages_with_regions = {}
    for r in regions:
        pages_with_regions.setdefault(r["page"], []).append(r)
    
    images = []
    for page_num in sorted(pages_with_regions.keys()):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        draw = ImageDraw.Draw(img)
        
        for r in pages_with_regions[page_num]:
            x0, y0, x1, y1 = r["x0"]*scale, r["y0"]*scale, r["x1"]*scale, r["y1"]*scale
            draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
            draw.text((x0, y0-20), r.get("name", ""), fill="red")
        
        images.append(img)
    
    doc.close()
    
    if images:
        # 垂直拼接
        total_h = sum(img.height for img in images)
        max_w = max(img.width for img in images)
        combined = Image.new("RGB", (max_w, total_h), "white")
        y = 0
        for img in images:
            combined.paste(img, (0, y))
            y += img.height
        combined.save(output_path)
        print(f"  Debug overlay: {output_path}")


def load_regions_from_json(path):
    """从 JSON 文件加载裁剪区域"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="论文图表精确提取工具 / Publication-Grade Figure Extraction")
    parser.add_argument("pdf", help="PDF 文件路径")
    parser.add_argument("--output-dir", default="results/figures/", help="输出目录")
    parser.add_argument("--dpi", type=int, default=300, help="DPI (默认 300)")
    parser.add_argument("--regions", help="裁剪区域 JSON 文件")
    parser.add_argument("--list-pages", action="store_true", help="仅列出各页尺寸")
    parser.add_argument("--auto-detect", action="store_true", help="自动检测图片块")
    parser.add_argument("--debug-overlay", help="生成裁剪区域叠加可视化")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}")
        sys.exit(1)
    
    if args.list_pages:
        list_page_sizes(args.pdf)
        sys.exit(0)
    
    if args.auto_detect:
        figs = auto_detect_figures(args.pdf)
        print(json.dumps(figs, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    # 加载裁剪区域
    if args.regions:
        regions = load_regions_from_json(args.regions)
    else:
        # 默认使用 FastPathPlanning 的裁剪区域
        regions = [
            {"page": 0, "x0": 42, "y0": 40, "x1": 574, "y1": 310, "name": "fig01_top.png"},
            {"page": 0, "x0": 42, "y0": 340, "x1": 574, "y1": 490, "name": "fig01_bot.png"},
            {"page": 4, "x0": 38, "y0": 30, "x1": 574, "y1": 210, "name": "fig02.png"},
            {"page": 5, "x0": 38, "y0": 30, "x1": 574, "y1": 207, "name": "fig03.png"},
            {"page": 6, "x0": 38, "y0": 30, "x1": 574, "y1": 211, "name": "fig04.png"},
            {"page": 6, "x0": 301, "y0": 250, "x1": 611, "y1": 372, "name": "fig05.png"},
            {"page": 9, "x0": 38, "y0": 30, "x1": 574, "y1": 228, "name": "fig06.png"},
            {"page": 11, "x0": 42, "y0": 55, "x1": 574, "y1": 315, "name": "fig07.png"},
            {"page": 11, "x0": 301, "y0": 55, "x1": 611, "y1": 315, "name": "fig08.png"},
            {"page": 12, "x0": 295, "y0": 30, "x1": 611, "y1": 305, "name": "fig09.png"},
        ]
    
    results = extract_regions(args.pdf, regions, args.output_dir, args.dpi)
    
    if args.debug_overlay:
        generate_debug_overlay(args.pdf, regions, args.debug_overlay)
    
    print(f"\n✅ 共提取 {len(results)} 张图表")
