#!/usr/bin/env python
"""Build a four-theme side-by-side contact sheet from the rendered previews.

Reads build/preview/demo-<theme>-NN.png and writes
build/compare/themes-contact-sheet.png: one row per theme, one column per page,
each cell labelled with the theme name.

Usage:  python compare_sheet.py [beamer_dir]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

THEMES = ["slate", "navy", "ink", "paper"]
CAPTION = {
    "slate": "slate - grey-blue monochrome",
    "navy": "navy - deep blue + warm accent",
    "ink": "ink - near-black, figure-first",
    "paper": "paper - warm white, serif headings",
}


def load_font(size):
    """A CJK-capable system font, falling back to PIL's bitmap default."""
    for cand in (
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ):
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except OSError:
                continue
    return ImageFont.load_default()


def main():
    beamer = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    preview = os.path.join(beamer, "build", "preview")
    out_dir = os.path.join(beamer, "build", "compare")
    os.makedirs(out_dir, exist_ok=True)

    # Collect the pages that actually exist, so the sheet adapts if a theme
    # gains or loses a slide.
    pages = {}
    for t in THEMES:
        found = []
        for i in range(1, 40):
            p = os.path.join(preview, f"demo-{t}-{i:02d}.png")
            if not os.path.exists(p):
                break
            found.append(p)
        if not found:
            print(f"ERROR: no previews for theme '{t}' in {preview}", file=sys.stderr)
            return 1
        pages[t] = found

    ncols = max(len(v) for v in pages.values())
    nrows = len(THEMES)

    sample = Image.open(pages["slate"][0])
    cell_w, cell_h = sample.size
    label_w = 210          # left gutter holding the theme name
    header_h = 46          # top strip holding column numbers
    pad = 8

    sheet_w = label_w + ncols * (cell_w + pad) + pad
    sheet_h = header_h + nrows * (cell_h + pad) + pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    f_head = load_font(15)
    f_cell = load_font(17)
    f_name = load_font(19)

    # Column headers: 01..NN
    for c in range(ncols):
        x = label_w + c * (cell_w + pad) + pad
        draw.text((x, 14), f"{c + 1:02d}", fill=(120, 120, 120), font=f_head)

    for r, theme in enumerate(THEMES):
        y = header_h + r * (cell_h + pad)
        draw.text((12, y + 18), CAPTION[theme], fill=(30, 30, 30), font=f_name)
        for c, path in enumerate(pages[theme]):
            img = Image.open(path).convert("RGB")
            x = label_w + c * (cell_w + pad) + pad
            sheet.paste(img, (x, y))
            draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1],
                           outline=(205, 205, 205), width=1)

    out = os.path.join(out_dir, "themes-contact-sheet.png")
    sheet.save(out)
    print(f"wrote {out}  {sheet_w}x{sheet_h}  {ncols} cols x {nrows} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
