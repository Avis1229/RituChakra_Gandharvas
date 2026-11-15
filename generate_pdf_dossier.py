#!/usr/bin/env python3
"""
RituChakra: Presentation & Technical Dossier PDF Generator
Converts rituchakra_presentation_master_dossier.md into a publication-grade,
beautifully styled A4 PDF using Headless Chrome, KaTeX for LaTeX math,
and Mermaid.js for vector architecture diagrams.
"""

import os
import re
import subprocess
import markdown

DOSSIER_MD = "/home/goku/.gemini/antigravity/brain/3830b98e-cd97-45ba-ac0b-6d62689ba0b1/rituchakra_presentation_master_dossier.md"
OUTPUT_HTML = "/home/goku/RituChakra_Gandharvas/RituChakra_Presentation_Dossier.html"
OUTPUT_PDF = "/home/goku/RituChakra_Gandharvas/RituChakra_Presentation_Dossier.pdf"

def build_pdf():
    print(f"Reading markdown source: {DOSSIER_MD}")
    with open(DOSSIER_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Pre-process Mermaid blocks so they render properly in HTML
    # replace ```mermaid ... ``` with <div class="mermaid">...</div>
    def mermaid_repl(match):
        return f'<div class="mermaid">\n{match.group(1).strip()}\n</div>'
    
    md_processed = re.sub(r'```mermaid\s+(.*?)```', mermaid_repl, md_text, flags=re.DOTALL)

    # Convert Markdown to HTML
    html_body = markdown.markdown(
        md_processed,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )

    # Post-process headers to add clean page-breaks before major parts
    html_body = html_body.replace('<h1>Part ', '<h1 class="page-break">Part ')

    # Embed HTML in styled template with print-ready A4 styling, KaTeX, and Mermaid
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>RituChakra — NASA Space Apps Challenge 2026 Presentation & Technical Dossier</title>
  
  <!-- KaTeX for crisp mathematical formulas -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

  <!-- Mermaid for clean vector diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'neutral',
      flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }}
    }});
  </script>

  <style>
    @page {{
      size: A4;
      margin: 18mm 16mm 18mm 16mm;
      @bottom-right {{
        content: counter(page);
      }}
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.55;
      color: #0F172A;
      background: #FFFFFF;
      margin: 0;
      padding: 0;
    }}

    /* Header & Branding Banner */
    .dossier-header {{
      background: linear-gradient(135deg, #0B3D91 0%, #032055 100%);
      color: #FFFFFF;
      padding: 16px 20px;
      border-radius: 4px;
      margin-bottom: 24px;
      border-left: 6px solid #059669;
    }}
    .dossier-header h1 {{
      margin: 0 0 4px 0;
      font-size: 18pt;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #FFFFFF;
    }}
    .dossier-header .subtitle {{
      font-size: 10pt;
      opacity: 0.9;
      font-weight: 500;
    }}
    .dossier-header .meta {{
      font-size: 8.5pt;
      margin-top: 8px;
      color: #CBD5E1;
      display: flex;
      gap: 16px;
    }}

    /* Headings */
    h1 {{
      font-size: 16pt;
      font-weight: 800;
      color: #0B3D91;
      border-bottom: 2px solid #E2E8F0;
      padding-bottom: 6px;
      margin-top: 26px;
      margin-bottom: 12px;
    }}
    h1.page-break {{
      page-break-before: always;
      margin-top: 10px;
    }}
    h2 {{
      font-size: 13pt;
      font-weight: 700;
      color: #0B3D91;
      margin-top: 20px;
      margin-bottom: 8px;
    }}
    h3 {{
      font-size: 11pt;
      font-weight: 700;
      color: #059669;
      margin-top: 16px;
      margin-bottom: 6px;
    }}
    h4 {{
      font-size: 10pt;
      font-weight: 700;
      color: #0F172A;
      margin-top: 12px;
      margin-bottom: 4px;
    }}

    p {{
      margin: 0 0 8px 0;
    }}

    /* Lists */
    ul, ol {{
      margin: 4px 0 10px 0;
      padding-left: 20px;
    }}
    li {{
      margin-bottom: 4px;
    }}

    /* Tables */
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 16px 0;
      font-size: 9pt;
      page-break-inside: avoid;
    }}
    th {{
      background: #F1F5F9;
      color: #0B3D91;
      font-weight: 700;
      text-align: left;
      padding: 8px 10px;
      border: 1px solid #CBD5E1;
      text-transform: uppercase;
      font-size: 8pt;
      letter-spacing: 0.04em;
    }}
    td {{
      padding: 7px 10px;
      border: 1px solid #E2E8F0;
      vertical-align: top;
    }}
    tr:nth-child(even) td {{
      background: #F8FAFC;
    }}

    /* Blockquotes & Callouts */
    blockquote {{
      background: #F8FAFC;
      border-left: 4px solid #059669;
      margin: 10px 0;
      padding: 10px 14px;
      font-size: 9.5pt;
      color: #1E293B;
      border-radius: 0 4px 4px 0;
      page-break-inside: avoid;
    }}
    blockquote p:last-child {{
      margin-bottom: 0;
    }}

    /* Code & Formulas */
    code {{
      background: #F1F5F9;
      color: #0B3D91;
      padding: 1px 4px;
      border-radius: 3px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 9pt;
    }}
    pre {{
      background: #0F172A;
      color: #F8FAFC;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
      font-size: 8.5pt;
      line-height: 1.4;
      margin: 10px 0;
      page-break-inside: avoid;
    }}
    pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
    }}

    /* Mermaid Diagrams */
    .mermaid {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 4px;
      padding: 14px;
      margin: 14px 0;
      text-align: center;
      page-break-inside: avoid;
    }}

    /* KaTeX Display Math */
    .katex-display {{
      margin: 10px 0;
      padding: 6px 0;
    }}

    /* Horizontal Rules */
    hr {{
      border: 0;
      border-top: 1px solid #E2E8F0;
      margin: 18px 0;
    }}

    /* Footer Note */
    .doc-footer {{
      margin-top: 30px;
      padding-top: 10px;
      border-top: 1px solid #E2E8F0;
      font-size: 8pt;
      color: #64748B;
      text-align: center;
      page-break-inside: avoid;
    }}
  </style>
</head>
<body>

  <div class="dossier-header">
    <h1>RituChakra (Field Shift)</h1>
    <div class="subtitle">NASA Space Apps Challenge 2026 — Track: Adapting Farms with NASA Earth Observations</div>
    <div class="meta">
      <span><b>Team:</b> Gandharvas</span>
      <span><b>Authors:</b> Sarthak, Aadya, Ahqaf, Vivek, Lal Shivam, Trisha, Avi</span>
      <span><b>Status:</b> Fully Operational & Validated (36/36 Tests)</span>
    </div>
  </div>

  {html_body}

  <div class="doc-footer">
    RituChakra: Field Shift • NASA Space Apps Challenge 2026 • Team Gandharvas • Developed with Python, NASA POWER, SMAP & ESA Sentinel-1
  </div>

  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      if (typeof renderMathInElement === "function") {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: "$$", right: "$$", display: true}},
            {{left: "$", right: "$", display: false}}
          ],
          throwOnError: false
        }});
      }}
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Wrote intermediate HTML: {OUTPUT_HTML}")

    # Render HTML to PDF via Headless Chrome
    chrome_cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=3500",
        f"--print-to-pdf={OUTPUT_PDF}",
        OUTPUT_HTML
    ]
    print(f"Rendering PDF with command: {' '.join(chrome_cmd)}")
    result = subprocess.run(chrome_cmd, capture_output=True, text=True)
    
    if os.path.exists(OUTPUT_PDF) and os.path.getsize(OUTPUT_PDF) > 0:
        pdf_size_kb = os.path.getsize(OUTPUT_PDF) / 1024
        print(f"SUCCESS: PDF generated cleanly at {OUTPUT_PDF} ({pdf_size_kb:.1f} KB)")
        return True
    else:
        print(f"ERROR: PDF generation failed. Chrome stdout: {result.stdout}, stderr: {result.stderr}")
        return False

if __name__ == "__main__":
    build_pdf()

