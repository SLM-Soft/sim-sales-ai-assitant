from __future__ import annotations

import base64
import html
import os
from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright


PdfSpecDict = Dict[str, Any]
_FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
_FONT_REGULAR = os.path.join(_FONTS_DIR, "Roboto-Regular.ttf")
_FONT_BOLD = os.path.join(_FONTS_DIR, "Roboto-Bold.ttf")


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _escape(value: Any) -> str:
    return html.escape(_safe_str(value))


def _font_data_uri(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:font/ttf;base64,{encoded}"


def _render_section_body(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and all(line.startswith(("-", "*")) for line in lines):
        items = [_escape(line.lstrip("-* ").strip()) for line in lines]
        return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"
    return "<p>" + "<br/>".join(_escape(line) for line in text.splitlines()) + "</p>"


def _render_meta_line(author: str, language: str) -> str:
    meta_parts = []
    if author:
        meta_parts.append(f"Author: {_escape(author)}")
    if language:
        meta_parts.append(f"Language: {_escape(language)}")
    return " | ".join(meta_parts)


def _render_table(table: Dict[str, Any]) -> str:
    title = _safe_str(table.get("title") or "")
    headers: List[str] = table.get("headers") or []
    rows: List[List[str]] = table.get("rows") or []

    header_html = ""
    if headers:
        header_cells = "".join(f"<th>{_escape(h)}</th>" for h in headers)
        header_html = f"<thead><tr>{header_cells}</tr></thead>"

    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{_escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")

    title_html = f"<div class=\"table-title\">{_escape(title)}</div>" if title else ""
    return (
        "<div class=\"table-block\">"
        f"{title_html}"
        "<div class=\"table-wrap\">"
        f"<table>{header_html}<tbody>{''.join(body_rows)}</tbody></table>"
        "</div>"
        "</div>"
    )


def _render_html(spec: PdfSpecDict) -> str:
    title = _safe_str(spec.get("title") or "Business Report")
    subtitle = _safe_str(spec.get("subtitle") or "")
    author = _safe_str(spec.get("author") or "")
    language = _safe_str(spec.get("language") or "")
    footer = _safe_str(spec.get("footer") or "")

    sections: List[Dict[str, Any]] = spec.get("sections") or []
    tables: List[Dict[str, Any]] = spec.get("tables") or []

    font_regular = _font_data_uri(_FONT_REGULAR)
    font_bold = _font_data_uri(_FONT_BOLD)

    font_face = ""
    if font_regular:
        font_face += (
            "@font-face { font-family: 'RobotoEmbed'; font-weight: 400; "
            f"src: url('{font_regular}') format('truetype'); }}"
        )
    if font_bold:
        font_face += (
            "@font-face { font-family: 'RobotoEmbed'; font-weight: 700; "
            f"src: url('{font_bold}') format('truetype'); }}"
        )

    meta_line = _render_meta_line(author, language)

    section_blocks = []
    for section in sections:
        sec_title = _safe_str(section.get("title") or "")
        sec_body = _safe_str(section.get("body") or "")
        if not (sec_title or sec_body):
            continue
        section_blocks.append(
            "<section class=\"card\">"
            f"<h2>{_escape(sec_title) if sec_title else ''}</h2>"
            f"{_render_section_body(sec_body) if sec_body else ''}"
            "</section>"
        )

    table_blocks = [_render_table(tbl) for tbl in tables or []]

    return f"""
<!doctype html>
<html lang="{_escape(language or 'en')}">
  <head>
    <meta charset="utf-8" />
    <style>
      {font_face}
      :root {{
        --red: #c1121f;
        --black: #111111;
        --white: #ffffff;
        --gray: #f4f5f7;
        --border: #e3e5e8;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        padding: 0;
        font-family: {"'RobotoEmbed', Arial, sans-serif" if font_regular else "Arial, sans-serif"};
        color: var(--black);
        background: var(--white);
      }}
      .page {{
        padding: 28px 32px 40px;
      }}
      .hero {{
        border-radius: 18px;
        padding: 26px 28px;
        background: linear-gradient(135deg, #111111 0%, #1b1b1b 100%);
        color: var(--white);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
      }}
      .hero::after {{
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 180px;
        height: 180px;
        background: var(--red);
        border-radius: 50%;
        opacity: 0.9;
      }}
      .hero h1 {{
        margin: 0 0 8px;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.4px;
      }}
      .hero p {{
        margin: 0;
        max-width: 520px;
        font-size: 14px;
        line-height: 1.5;
        color: #f0f0f0;
      }}
      .meta {{
        margin-top: 12px;
        font-size: 12px;
        opacity: 0.9;
      }}
      .grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 16px;
      }}
      .card {{
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px 20px;
        background: var(--gray);
      }}
      .card h2 {{
        margin: 0 0 8px;
        font-size: 16px;
        color: var(--black);
      }}
      .card p {{
        margin: 0;
        font-size: 13px;
        line-height: 1.6;
      }}
      .card ul {{
        margin: 8px 0 0 18px;
        padding: 0;
        font-size: 13px;
        line-height: 1.6;
      }}
      .table-block {{
        margin-top: 16px;
      }}
      .table-title {{
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 8px;
        color: var(--black);
      }}
      .table-wrap {{
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        background: var(--white);
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
      }}
      th {{
        background: var(--red);
        color: var(--white);
        text-align: left;
        padding: 8px 10px;
        font-weight: 700;
      }}
      td {{
        padding: 8px 10px;
        border-bottom: 1px solid var(--border);
        vertical-align: top;
      }}
      tr:nth-child(even) td {{
        background: #fafafa;
      }}
      .footer {{
        margin-top: 24px;
        font-size: 11px;
        color: #5c5c5c;
        text-align: center;
      }}
    </style>
  </head>
  <body>
    <div class="page">
      <header class="hero">
        <h1>{_escape(title)}</h1>
        <p>{_escape(subtitle) if subtitle else ""}</p>
        {f"<div class=\"meta\">{meta_line}</div>" if meta_line else ""}
      </header>
      <main class="grid">
        {''.join(section_blocks)}
        {''.join(table_blocks)}
      </main>
      {f"<div class=\"footer\">{_escape(footer)}</div>" if footer else ""}
    </div>
  </body>
</html>
"""


def build_pdf_from_spec(spec: PdfSpecDict) -> bytes:
    html_doc = _render_html(spec)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_doc, wait_until="networkidle")
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "18mm", "bottom": "20mm", "left": "16mm", "right": "16mm"},
        )
        browser.close()
    return pdf_bytes
