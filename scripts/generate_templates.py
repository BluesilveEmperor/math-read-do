#!/usr/bin/env python3
"""Generate all literature reader template variants."""

import os

# Read the base template (latex version)
with open('templates/literature_reader.markleaf.md', 'r', encoding='utf-8') as f:
    base = f.read()

# Extract the content part (after the style block)
style_end = base.find('</style>')
if style_end != -1:
    content_part = base[style_end + 8:]
else:
    content_part = base

# Define all typography variants
variants = {
    'print': {
        'font_main': '"Times New Roman", "宋体-简", "方正书宋_GBK", "宋体", serif',
        'font_head': '"Helvetica", "方正黑体_GBK", "黑体", sans-serif',
        'font_mono': '"Courier New", monospace',
        'h1_size': '24px',
        'h1_align': 'center',
        'h1_line': '3',
        'table_border': '1px solid #1a1a1a',
        'table_radius': '0',
        'quote_border': '1px solid #1a1a1a',
        'quote_radius': '0',
        'quote_bg': 'transparent',
        'card_border': '1.5px solid #1a1a1a',
        'card_radius': '0',
        'card_bg': 'transparent',
        'p_indent': '2em',
        'card_student_border': '#333333',
        'card_advisor_border': '#555555',
        'card_reviewer_border': '#777777',
    },
    'retro-print': {
        'font_main': 'KingHwaOldSong, "宋体-简", "宋体", serif',
        'font_head': '"汇文港黑", "黑体", sans-serif',
        'font_mono': '"朝华打字机", "Courier New", monospace',
        'h1_size': '24px',
        'h1_align': 'center',
        'h1_line': '3',
        'table_border': '1px solid #1a1a1a',
        'table_radius': '0',
        'quote_border': '1px dashed #1a1a1a',
        'quote_radius': '0',
        'quote_bg': 'transparent',
        'card_border': '1.5px solid #1a1a1a',
        'card_radius': '0',
        'card_bg': 'transparent',
        'p_indent': '2em',
        'card_student_border': '#333333',
        'card_advisor_border': '#555555',
        'card_reviewer_border': '#777777',
    },
    'sans': {
        'font_main': '"SF Pro Display", "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif',
        'font_head': '"SF Pro Display", "Microsoft YaHei", sans-serif',
        'font_mono': '"SF Mono", "Consolas", monospace',
        'h1_size': '28.8px',
        'h1_align': 'center',
        'h1_line': '1.4',
        'table_border': '0',
        'table_radius': '6px',
        'quote_border': '2px solid #e7e7ef',
        'quote_radius': '6px',
        'quote_bg': '#f8f9fa',
        'card_border': '2px solid #e7e7ef',
        'card_radius': '8px',
        'card_bg': '#f8f9fa',
        'p_indent': '0',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
    'serif': {
        'font_main': 'serif, "Source Han Serif CN", "Noto Serif CJK CN"',
        'font_head': 'serif, "Source Han Serif CN"',
        'font_mono': 'Consolas, monospace',
        'h1_size': '32px',
        'h1_align': 'left',
        'h1_line': '1.3',
        'table_border': '1px solid #e7e7ef',
        'table_radius': '4px',
        'quote_border': '3px solid #e7e7ef',
        'quote_radius': '0',
        'quote_bg': 'transparent',
        'card_border': '2px solid #e7e7ef',
        'card_radius': '6px',
        'card_bg': '#f8f9fa',
        'p_indent': '0',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
    'magazine': {
        'font_main': 'Georgia, serif',
        'font_head': 'Georgia, serif',
        'font_mono': 'Consolas, monospace',
        'h1_size': '35.2px',
        'h1_align': 'center',
        'h1_line': '1.4',
        'table_border': '0',
        'table_radius': '0',
        'quote_border': '4px solid #0079f3',
        'quote_radius': '0',
        'quote_bg': '#f2f1f5',
        'card_border': '2px solid #0079f3',
        'card_radius': '0',
        'card_bg': '#f2f1f5',
        'p_indent': '0',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
    'minimal': {
        'font_main': '"Segoe UI", "Microsoft YaHei", sans-serif',
        'font_head': '"Segoe UI", "Microsoft YaHei", sans-serif',
        'font_mono': '"Segoe UI Mono", Consolas, monospace',
        'h1_size': '32px',
        'h1_align': 'left',
        'h1_line': '1.4',
        'table_border': '0',
        'table_radius': '0',
        'quote_border': '0',
        'quote_radius': '0',
        'quote_bg': 'transparent',
        'card_border': '2px solid #e7e7ef',
        'card_radius': '8px',
        'card_bg': '#f8f9fa',
        'p_indent': '0',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
    'notebook': {
        'font_main': '"霞鹜文楷", "楷体", "KaiTi", "Comic Sans MS", cursive',
        'font_head': '"霞鹜文楷", "楷体", "KaiTi", cursive',
        'font_mono': '"Cascadia Code", "Consolas", monospace',
        'h1_size': '25.6px',
        'h1_align': 'center',
        'h1_line': '1.4',
        'table_border': '0',
        'table_radius': '0',
        'quote_border': '3px dotted #0284f9',
        'quote_radius': '0',
        'quote_bg': 'transparent',
        'card_border': '2px solid #0284f9',
        'card_radius': '0',
        'card_bg': 'transparent',
        'p_indent': '0',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
    'print-double': {
        'font_main': '"Times New Roman", "宋体-简", "方正书宋_GBK", "宋体", serif',
        'font_head': '"Helvetica", "方正黑体_GBK", "黑体", sans-serif',
        'font_mono': '"Courier New", monospace',
        'h1_size': '24px',
        'h1_align': 'center',
        'h1_line': '3',
        'table_border': '1.5px solid #0079f3',
        'table_radius': '0',
        'quote_border': '1.5px solid #0079f3',
        'quote_radius': '0',
        'quote_bg': '#f2f1f5',
        'card_border': '1.5px solid #0079f3',
        'card_radius': '0',
        'card_bg': '#f2f1f5',
        'p_indent': '2em',
        'card_student_border': '#0969da',
        'card_advisor_border': '#1a7f37',
        'card_reviewer_border': '#8250df',
    },
}

# CSS template
CSS_TEMPLATE = """<style>
:root {{
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-hover: #f2f1f5;
  --bg-selected: #e7e7ef;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --theme-dark: #0079f3;
}}

.markdown-preview.markdown-preview {{
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: {font_main};
  font-size: 16px;
  line-height: 1.8;
  text-align: justify;
  max-width: 820px;
  margin: 0 auto;
  padding: 2em 2.5em;
}}

.markdown-preview.markdown-preview h1 {{
  font-family: {font_head};
  font-size: {h1_size};
  font-weight: bold;
  text-align: {h1_align};
  line-height: {h1_line};
  margin-top: 1.5em;
  margin-bottom: 0.8em;
}}

.markdown-preview.markdown-preview h2 {{
  font-family: {font_head};
  font-size: 1.4em;
  font-weight: bold;
  margin-top: 1.5em;
  margin-bottom: 0.6em;
  padding-bottom: 0.25em;
  border-bottom: 1px solid var(--bg-selected);
}}

.markdown-preview.markdown-preview h3 {{
  font-family: {font_head};
  font-size: 1.1em;
  font-weight: bold;
  margin-top: 1.3em;
  margin-bottom: 0.5em;
}}

.markdown-preview.markdown-preview p {{
  margin: 0.6em 0;
  text-indent: {p_indent};
}}

.markdown-preview.markdown-preview strong,
.markdown-preview.markdown-preview b {{
  font-family: {font_head};
  font-weight: bold;
}}

.markdown-preview.markdown-preview em,
.markdown-preview.markdown-preview i {{
  font-style: italic;
}}

.markdown-preview.markdown-preview a {{
  color: var(--theme-dark);
  text-decoration: none;
}}

.markdown-preview.markdown-preview hr {{
  width: 10em;
  height: 1px;
  margin: 2em auto;
  background: var(--text-primary);
  border: 0;
}}

.markdown-preview.markdown-preview ul,
.markdown-preview.markdown-preview ol {{
  padding-left: 1.5em;
}}

.markdown-preview.markdown-preview li > p {{
  margin: 0;
  text-indent: 0 !important;
}}

.markdown-preview.markdown-preview table {{
  width: auto;
  min-width: 50%;
  margin: 1em auto;
  border: {table_border};
  border-collapse: collapse;
  background: transparent;
}}

.markdown-preview.markdown-preview th,
.markdown-preview.markdown-preview td {{
  border: {table_border};
  background: transparent;
  padding: 5px 12px;
}}

.markdown-preview.markdown-preview th {{
  font-weight: 600;
}}

.markdown-preview.markdown-preview table p {{
  text-indent: 0;
  margin: 0;
}}

.markdown-preview.markdown-preview blockquote {{
  margin: 0.8em 0;
  padding: 0.5em 1em;
  border: {quote_border};
  border-radius: {quote_radius};
  background: {quote_bg};
  font-style: normal;
}}

.markdown-preview.markdown-preview blockquote p {{
  text-indent: 0;
}}

.markdown-preview.markdown-preview code,
.markdown-preview.markdown-preview pre code {{
  font-family: {font_mono};
  font-size: 0.9em;
}}

.markdown-preview.markdown-preview pre {{
  border: 1px solid var(--bg-selected);
  border-radius: 4px;
  padding: 0.8em 1em;
  margin: 1em 0;
  overflow-x: auto;
}}

.markdown-preview.markdown-preview .perspective-card {{
  margin: 1.5em 0;
  padding: 0;
  border: {card_border};
  border-radius: {card_radius};
  overflow: hidden;
  background: {card_bg};
}}

.markdown-preview.markdown-preview .perspective-card > blockquote:first-child {{
  margin: 0;
  padding: 0.5em 1em;
  border: 0;
  border-radius: 0;
  font-weight: 600;
  font-size: 1.05em;
}}

.markdown-preview.markdown-preview .perspective-card > *:not(:first-child) {{
  padding-left: 1em;
  padding-right: 1em;
}}

.markdown-preview.markdown-preview .perspective-card > :last-child {{
  padding-bottom: 1em;
}}

.markdown-preview.markdown-preview .perspective-card.student {{
  border-color: {card_student_border};
}}

.markdown-preview.markdown-preview .perspective-card.advisor {{
  border-color: {card_advisor_border};
}}

.markdown-preview.markdown-preview .perspective-card.reviewer {{
  border-color: {card_reviewer_border};
}}

.markdown-preview.markdown-preview .katex-display {{
  margin: 1.2em 0;
  padding: 0.8em 1em;
  border-left: 3px solid var(--theme-dark);
  background: var(--bg-secondary);
  border-radius: 0 4px 4px 0;
  overflow-x: auto;
}}

.markdown-preview.markdown-preview > blockquote:first-of-type {{
  background: var(--bg-secondary);
  border: 1px solid var(--bg-selected);
  border-radius: 6px;
  padding: 1em 1.2em;
}}

@media print {{
  .markdown-preview.markdown-preview {{
    max-width: 100%;
    padding: 0;
    font-size: 12pt;
  }}
}}
</style>"""

# Generate each variant
os.makedirs('templates', exist_ok=True)
for name, v in variants.items():
    css = CSS_TEMPLATE.format(**v)
    full_template = css + '\n' + content_part
    filename = f'templates/literature_reader.{name}.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_template)
    print(f'Created: {filename}')

print(f'\nDone! Generated {len(variants)} templates.')
