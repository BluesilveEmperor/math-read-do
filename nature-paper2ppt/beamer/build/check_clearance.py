#!/usr/bin/env python
"""Quantify the takeaway-panel vs footer clearance on the figure page.

The figure slide is the one layout where content and chrome compete for the
same vertical space, and the failure (panel sitting on top of the footer) is
easy to miss by eye at preview resolution. This measures it instead.

Usage:  python check_clearance.py [beamer_dir]
Exit code is 1 if any theme has a non-positive clearance.
"""
import os
import sys

import pymupdf


def find_figure_page(doc):
    """Index of the slide carrying a \naturefigurepage.

    Identified by the source line ('Source:'), which only that layout emits,
    so this keeps working if the demo's page order changes.
    """
    for i, page in enumerate(doc):
        text = page.get_text()
        if "Source:" in text:
            return i
    return None


def footer_top(page):
    """Topmost y of the footer text within the bottom 8 mm of the page."""
    limit = page.rect.height - 8 * 72 / 25.4
    ys = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            y0 = line["bbox"][1]
            if y0 >= limit:
                ys.append(y0)
    return min(ys) if ys else None


def panel_bottom(page):
    """Lowest y of the tinted takeaway panel.

    The panel is a filled rectangle of roughly text width and 5-15 mm tall;
    the size window filters out the many hairlines and rules on the slide.
    """
    ys = []
    for d in page.get_drawings():
        r = d["rect"]
        if not d.get("fill"):
            continue
        if 100 < r.width < 420 and 5 < r.height < 40:
            ys.append(r.y1)
    return max(ys) if ys else None


def main():
    beamer = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    build = os.path.join(beamer, "build")

    print(f"{'theme':8} {'page':>5} {'panel_y1':>9} {'footer_y0':>10} "
          f"{'clearance':>10}  status")
    bad = 0
    for theme in ("slate", "navy", "ink", "paper"):
        pdf = os.path.join(build, f"demo-{theme}.pdf")
        if not os.path.exists(pdf):
            print(f"{theme:8} {'-':>5} {'-':>9} {'-':>10} {'-':>10}  MISSING")
            bad += 1
            continue
        doc = pymupdf.open(pdf)
        idx = find_figure_page(doc)
        if idx is None:
            print(f"{theme:8} {'-':>5} {'-':>9} {'-':>10} {'-':>10}  NO FIG PAGE")
            bad += 1
            continue
        page = doc[idx]
        panel = panel_bottom(page)
        foot = footer_top(page)
        if panel is None or foot is None:
            print(f"{theme:8} {idx + 1:>5} {str(panel):>9} {str(foot):>10} "
                  f"{'-':>10}  UNDETECTED")
            bad += 1
            continue
        clearance = foot - panel
        ok = clearance > 0
        if not ok:
            bad += 1
        print(f"{theme:8} {idx + 1:>5} {panel:>9.1f} {foot:>10.1f} "
              f"{clearance:>10.1f}  {'OK' if ok else 'OVERLAP'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
