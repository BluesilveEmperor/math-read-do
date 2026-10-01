#!/usr/bin/env python
"""Render a PDF's pages to PNG and report basic facts.

Used by build.sh. Kept as a real file rather than an inline -c snippet because
the deck path is injected through a shell variable, and raw Windows paths with
backslashes or spaces make inline Python fragile.

Usage:  python pdf_tools.py <pdf> <out_dir> <stem> [dpi]
Prints a single summary line on stdout.
"""
import os
import sys


def load_pdf(path):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    return fitz.open(path)


def main():
    if len(sys.argv) < 4:
        print("usage: pdf_tools.py <pdf> <out_dir> <stem> [dpi]")
        return 2

    pdf_path = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])
    stem = sys.argv[3]
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 150

    if not os.path.exists(pdf_path):
        print(f"MISSING {pdf_path}")
        return 1

    doc = load_pdf(pdf_path)
    n = doc.page_count

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for i, page in enumerate(doc):
            page.get_pixmap(dpi=dpi).save(os.path.join(out_dir, f"{stem}-{i + 1:02d}.png"))

    # Report the rendered aspect ratio so a wrong paper size is caught here
    # rather than after a figure has already been laid out against it.
    r = doc[0].rect
    ratio = r.width / r.height if r.height else 0

    print(f"pages={n} ratio={ratio:.3f}{' rendered' if out_dir else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
