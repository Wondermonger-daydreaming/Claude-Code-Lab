#!/usr/bin/env python3
"""Convert the spectral separatrix paper markdown to a printable HTML with MathJax."""

import re
import markdown
from pathlib import Path

PAPER = Path(__file__).parent / "spectral-separatrix-draft.md"
OUT = Path(__file__).parent / "spectral-separatrix-draft.html"

# Read markdown
md_text = PAPER.read_text()

# Protect LaTeX math blocks from markdown parser
# Replace $$ ... $$ with placeholders
math_blocks = []
def save_display_math(m):
    math_blocks.append(m.group(0))
    return f"DISPLAYMATH{len(math_blocks)-1}ENDMATH"

def save_inline_math(m):
    math_blocks.append(m.group(0))
    return f"INLINEMATH{len(math_blocks)-1}ENDMATH"

# Display math first (greedy)
md_text = re.sub(r'\$\$(.+?)\$\$', save_display_math, md_text, flags=re.DOTALL)
# Inline math
md_text = re.sub(r'\$([^\$\n]+?)\$', save_inline_math, md_text)

# Convert markdown to HTML
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

# Restore math
for i, block in enumerate(math_blocks):
    html_body = html_body.replace(f"DISPLAYMATH{i}ENDMATH", block)
    html_body = html_body.replace(f"INLINEMATH{i}ENDMATH", block)

# Build full HTML document
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Goldstone Modes and the Coexistence Saddle</title>
<script>
MathJax = {{
  tex: {{
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']],
  }},
  svg: {{ fontCache: 'global' }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<style>
  @media print {{
    body {{ font-size: 11pt; }}
    h1 {{ font-size: 16pt; }}
    h2 {{ font-size: 14pt; page-break-before: auto; }}
    h3 {{ font-size: 12pt; }}
    .no-print {{ display: none; }}
  }}
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    max-width: 750px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.6;
    color: #1a1a1a;
  }}
  h1 {{
    font-size: 1.5em;
    text-align: center;
    margin-bottom: 0.3em;
    line-height: 1.3;
  }}
  h2 {{
    font-size: 1.25em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.2em;
    margin-top: 2em;
  }}
  h3 {{ font-size: 1.1em; margin-top: 1.5em; }}
  h4 {{ font-size: 1.0em; font-style: italic; margin-top: 1.2em; }}
  p {{ text-align: justify; margin: 0.8em 0; }}
  table {{
    border-collapse: collapse;
    margin: 1em auto;
    font-size: 0.9em;
  }}
  th, td {{
    border: 1px solid #999;
    padding: 4px 10px;
    text-align: left;
  }}
  th {{ background: #f0f0f0; }}
  strong {{ font-weight: 600; }}
  hr {{ border: none; border-top: 1px solid #ccc; margin: 2em 0; }}
  blockquote {{
    border-left: 3px solid #ccc;
    margin: 1em 0;
    padding: 0.5em 1em;
    color: #444;
    font-style: italic;
  }}
  .figure-caption {{
    text-align: center;
    font-size: 0.9em;
    color: #333;
    margin: 1em 2em;
    line-height: 1.4;
  }}
  /* Style figure captions that start with "Figure N." */
  p > strong:first-child {{
    color: #000;
  }}
</style>
</head>
<body>
{html_body}
<div class="no-print" style="margin-top:3em; padding:1em; background:#f9f9f9; border:1px solid #ddd; font-size:0.9em;">
<strong>Print instructions:</strong> Open this file in your browser, then Ctrl+P (or Cmd+P) → Save as PDF.
MathJax must finish rendering before printing (wait for all equations to appear).
</div>
</body>
</html>
"""

OUT.write_text(html)
print(f"Written: {OUT}")
print(f"Open in browser: file:///{OUT.resolve()}")
