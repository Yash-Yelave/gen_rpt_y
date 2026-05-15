from __future__ import annotations

import html
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .theme import load_theme

THEME = load_theme()
PALETTE = THEME["palette"]
BRAND_NAME = THEME["brand_name"]
REPORT_LABEL = THEME.get("report_label", "Strategic Intelligence")
FONT_FAMILY = THEME.get("font_family", "Helvetica Neue, Helvetica, Arial, sans-serif")
PAGE_FORMAT = os.getenv("REPORT_PAGE_FORMAT", "A4").upper()
PAGE_W, PAGE_H = (8.27, 11.69) if PAGE_FORMAT == "A4" else (6.93, 9.84)
PAD_X, PAD_TOP, PAD_BOTTOM = (0.45, 0.40, 0.32) if PAGE_FORMAT == "A4" else (0.32, 0.32, 0.26)

CSS = f"""
@page {{ size:{PAGE_W}in {PAGE_H}in; margin:0; }}

:root {{
    --accent:  {PALETTE['accent']};
    --accent2: {PALETTE.get('bright_blue', PALETTE['accent'])};
    --ink:     {PALETTE['ink']};
    --muted:   {PALETTE['subtle']};
    --line:    {PALETTE['line']};
    --paper:   {PALETTE['paper']};
    --panel:   {PALETTE['panel']};
    --dark:    #0B1929;
    --mid:     #4A5568;
}}

* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:{PAGE_W}in; background:#fff; }}
body {{
    font-family:"Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size:10pt;
    line-height:1.70;
    color:var(--ink);
    word-spacing:normal;
    letter-spacing:normal;
    text-rendering:auto;
}}

/* Page shell */
.page {{
    width:{PAGE_W}in;
    height:{PAGE_H}in;
    position:relative;
    background:var(--paper);
    padding:{PAD_TOP}in {PAD_X}in {PAD_BOTTOM}in {PAD_X}in;
    page-break-after:always;
    overflow:hidden;
}}
.content-area {{ margin-top:0.30in; }}

/* Running head — stable table layout avoids flex collision */
.run-head {{
    position:absolute;
    top:0.14in;
    left:{PAD_X}in;
    right:{PAD_X}in;
    border-bottom:0.6pt solid var(--line);
    padding-bottom:0.04in;
    display:table;
    width:{PAGE_W - PAD_X * 2}in;
}}
.run-head-inner {{
    display:table;
    width:100%;
}}
.run-head-brand {{
    display:table-cell;
    font-size:6.5pt;
    font-weight:700;
    letter-spacing:0.06em;
    text-transform:uppercase;
    color:var(--accent);
    vertical-align:bottom;
    white-space:nowrap;
}}
.run-head-label {{
    display:table-cell;
    text-align:right;
    font-size:6.5pt;
    color:var(--muted);
    letter-spacing:0;
    font-weight:500;
    white-space:nowrap;
    vertical-align:bottom;
}}
.logo-fixed {{
    height:0.20in;
    width:auto;
    object-fit:contain;
    vertical-align:bottom;
}}

/* Running foot — table layout for stability */
.run-foot {{
    position:absolute;
    bottom:0.12in;
    left:{PAD_X}in;
    right:{PAD_X}in;
    border-top:0.6pt solid var(--line);
    padding-top:0.05in;
    display:table;
    width:{PAGE_W - PAD_X * 2}in;
}}
.run-foot-left {{
    display:table-cell;
    font-size:6.5pt;
    color:var(--muted);
    letter-spacing:0;
    font-weight:400;
    white-space:nowrap;
}}
.run-foot-pg {{
    display:table-cell;
    text-align:right;
    font-size:6.5pt;
    color:var(--muted);
    font-weight:600;
    letter-spacing:0;
    white-space:nowrap;
}}

/* Type hierarchy — tracking applied with editorial restraint */
h1 {{ font-size:22pt; line-height:1.12; font-weight:300; color:var(--dark); letter-spacing:-0.015em; margin-bottom:0.16in; }}
h2 {{ font-size:17pt; line-height:1.20; font-weight:600; color:var(--ink); letter-spacing:-0.005em; margin-bottom:0.10in; }}
h3 {{ font-size:13pt; line-height:1.28; font-weight:600; color:var(--ink); letter-spacing:0; margin-bottom:0.07in; }}

/* Small institutional label — tracking appropriate here */
.chapter-label {{
    display:block;
    font-size:6.5pt;
    font-weight:700;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:var(--accent);
    margin-bottom:0.06in;
    padding-bottom:0.05in;
    border-bottom:2pt solid var(--accent2);
    width:0.60in;
}}
.section-title {{
    font-size:17pt;
    font-weight:600;
    line-height:1.18;
    color:var(--dark);
    letter-spacing:-0.010em;
    margin-bottom:0.07in;
    margin-top:0.04in;
}}
.lead {{
    font-size:10.5pt;
    line-height:1.58;
    color:var(--mid);
    font-weight:400;
    margin-bottom:0.14in;
    font-style:italic;
    border-left:2.5pt solid var(--accent2);
    padding-left:0.12in;
}}
p {{ margin:0 0 0.13in; font-size:10pt; line-height:1.72; color:var(--ink); letter-spacing:0; }}
ul, ol {{ margin:0 0 0.13in 0.17in; padding:0; }}
li {{ font-size:10pt; line-height:1.68; margin-bottom:0.06in; color:var(--ink); letter-spacing:0; }}

/* Section layout */
.section-grid {{
    display:grid;
    grid-template-columns:1.15fr 0.85fr;
    gap:0.26in;
    align-items:start;
    margin-top:0.08in;
}}
.section-grid-flip {{
    display:grid;
    grid-template-columns:0.85fr 1.15fr;
    gap:0.26in;
    align-items:start;
    margin-top:0.08in;
}}

/* Visuals */
.section-visual {{
    width:100%;
    height:3.70in;
    object-fit:cover;
    display:block;
    border:0.6pt solid var(--line);
    page-break-inside:avoid;
}}
.chart-inline {{
    width:100%;
    max-height:3.70in;
    object-fit:contain;
    display:block;
    page-break-inside:avoid;
}}
.visual-empty {{
    height:3.70in;
    background:var(--panel);
    border:0.6pt solid var(--line);
}}

/* Executive highlights */
.highlights-label {{
    font-size:7pt;
    font-weight:700;
    letter-spacing:0.06em;
    text-transform:uppercase;
    color:var(--accent);
    margin-bottom:0.12in;
    padding-bottom:0.05in;
    border-bottom:0.6pt solid var(--line);
}}
.highlight-grid {{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:0.09in 0.13in;
    margin-top:0.05in;
}}
.highlight-card {{
    border-left:3pt solid var(--accent);
    background:#FAFBFC;
    padding:0.09in 0.11in;
    min-height:0.60in;
    page-break-inside:avoid;
}}
.highlight-card .num {{
    font-size:7pt;
    font-weight:700;
    color:var(--accent);
    letter-spacing:0.02em;
    margin-bottom:0.025in;
}}
.highlight-card .text {{
    font-size:8.5pt;
    line-height:1.52;
    color:var(--ink);
    letter-spacing:0;
}}

/* Insight panel */
.insight-panel {{
    background:#F2F6FB;
    border-left:3pt solid var(--accent);
    padding:0.11in 0.13in;
    margin:0.12in 0 0.10in;
    page-break-inside:avoid;
}}
.insight-head {{
    font-size:7pt;
    font-weight:700;
    letter-spacing:0.06em;
    text-transform:uppercase;
    color:var(--accent);
    margin-bottom:0.06in;
}}
.insight-panel ul {{ margin:0; }}
.insight-panel li {{ font-size:8.5pt; line-height:1.58; margin-bottom:0.04in; letter-spacing:0; }}

/* TOC */
.toc-head {{
    font-size:7pt;
    font-weight:700;
    letter-spacing:0.06em;
    text-transform:uppercase;
    color:var(--accent);
    margin-bottom:0.14in;
    padding-bottom:0.06in;
    border-bottom:0.6pt solid var(--line);
}}
.toc-list {{ list-style:none; margin:0; padding:0; }}
.toc-list li {{
    font-size:10pt;
    line-height:1.52;
    margin-bottom:0.08in;
    padding-left:0.14in;
    border-left:1.5pt solid var(--line);
    color:var(--ink);
}}
.toc-num {{
    display:block;
    font-size:6.5pt;
    font-weight:700;
    color:var(--accent);
    letter-spacing:0.07em;
    margin-bottom:0.01in;
}}

/* Disclaimer / refs */
.disclaimer-text, .small-note {{
    font-size:8.5pt;
    line-height:1.55;
    color:var(--muted);
}}
.small-note {{ margin-top:0.08in; }}
.reference-note {{
    border-top:0.6pt solid var(--line);
    padding-top:0.10in;
    margin-top:0.18in;
    font-size:8.5pt;
    line-height:1.55;
    color:var(--muted);
}}

/* Cover */
.cover {{
    padding:0;
    background-size:cover;
    background-position:center top;
}}
.cover-overlay {{
    position:absolute;
    inset:0;
    background:linear-gradient(108deg, rgba(6,20,44,.95) 0%, rgba(6,20,44,.80) 50%, rgba(6,20,44,.35) 100%);
    z-index:1;
}}
.cover-panel {{
    position:absolute;
    left:0.52in;
    bottom:1.00in;
    width:5.60in;
    z-index:3;
}}
.cover-brand {{
    display:block;
    font-size:7pt;
    font-weight:700;
    letter-spacing:0.10em;
    text-transform:uppercase;
    color:rgba(255,255,255,0.55);
    margin-bottom:0.18in;
}}
.cover-rule {{
    width:0.38in;
    height:2.5pt;
    background:var(--accent2);
    margin-bottom:0.18in;
}}
.cover-title {{
    font-size:28pt;
    line-height:1.08;
    font-weight:300;
    color:#ffffff;
    letter-spacing:-0.015em;
    margin-bottom:0.16in;
}}
.cover-sub {{
    font-size:8pt;
    color:rgba(255,255,255,0.55);
    font-weight:400;
    letter-spacing:0.04em;
    text-transform:uppercase;
    margin-bottom:0.26in;
}}
.cover-divider {{
    width:100%;
    height:0.5pt;
    background:rgba(255,255,255,0.15);
    margin-bottom:0.16in;
}}
/* Cover metadata — table layout prevents label/value collision */
.cover-meta {{
    display:table;
    border-collapse:separate;
    border-spacing:0.30in 0;
}}
.cover-meta-item {{
    display:table-cell;
    vertical-align:top;
    padding-right:0.30in;
}}
.cover-meta-label {{
    display:block;
    font-size:6pt;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:rgba(255,255,255,0.35);
    margin-bottom:0.03in;
    white-space:nowrap;
}}
.cover-meta-value {{
    display:block;
    font-size:8pt;
    color:rgba(255,255,255,0.75);
    font-weight:500;
    white-space:nowrap;
    letter-spacing:0;
}}

/* Compact profile */
.profile-compact {{ font-size:9pt; }}
.profile-compact p, .profile-compact li {{ font-size:9pt; }}
.profile-compact h2 {{ font-size:14pt; }}

/* Presentation profile */
.profile-presentation {{ font-size:12pt; }}
.profile-presentation p, .profile-presentation li {{ font-size:12pt; }}
.profile-presentation h2 {{ font-size:20pt; }}

/* Print */
@media print {{
    html, body {{ width:{PAGE_W}in; }}
    .page {{ margin:0; box-shadow:none; border:none; }}
    * {{ -webkit-print-color-adjust:exact !important; color-adjust:exact !important; }}
}}
"""

LABELS = {
    "en": {
        "lang": "en",
        "summary": "Executive Summary",
        "toc": "Table of Contents",
        "disclaimer": "Important Notice",
        "takeaways": "Strategic Implications",
        "reference_note": "This report draws on public research and data from:",
        "formal_note": "Source materials are archived in the backup folder.",
        "disclaimer_text": "This document is a management research and strategy analysis deliverable for internal discussion purposes only. It does not constitute professional investment, legal, or regulatory advice.",
        "confidential": "Confidential",
        "prepared": "Prepared by",
    },
    "zh": {
        "lang": "zh-CN",
        "summary": "Executive Summary",
        "toc": "Table of Contents",
        "disclaimer": "Important Notice",
        "takeaways": "Strategic Implications",
        "reference_note": "Reference institutions:",
        "formal_note": "Source backup is archived in the backup folder.",
        "disclaimer_text": "This document is for management research and strategy discussion only.",
        "confidential": "Confidential",
        "prepared": "Prepared by",
    },
}


def render_report_html(report: Dict[str, Any], assets: Dict[str, str], output_file: Path, topic: str, language: str = "en") -> Path:
    labels = _labels(language)
    sections = _safe_sections(report.get("sections", []))
    institutions = report.get("reference_institutions", []) or []
    logo_path = assets.get("brand-logo", "")
    cover_path = assets.get("cover-background", "")
    title = str(report.get("report_title") or topic)
    page_no = 1
    report_date = datetime.utcnow().strftime("%B %Y")

    profile = os.getenv("REPORT_PROFILE", "executive").lower().strip()
    profile_class = f"profile-{profile}" if profile not in ("executive",) else ""

    parts: List[str] = [
        "<!DOCTYPE html>",
        f"<html lang='{labels['lang']}'>",
        "<head>",
        "<meta charset='utf-8' />",
        f"<title>{html.escape(title)}</title>",
        f"<style>{CSS}</style>",
        "</head>",
        f"<body{(' class=' + repr(profile_class)) if profile_class else ''}>",
    ]

    # ── Cover ──
    bg = f"background-image:url('{html.escape(cover_path)}');" if cover_path else "background:#061428;"
    parts += [
        f"<section class='page cover' style=\"{bg}\">",
        "<div class='cover-overlay'></div>",
        "<div class='cover-panel'>",
        f"<span class='cover-brand'>{html.escape(BRAND_NAME)}</span>",
        "<div class='cover-rule'></div>",
        f"<div class='cover-title'>{html.escape(title)}</div>",
        f"<div class='cover-sub'>{html.escape(REPORT_LABEL)}</div>",
        "<div class='cover-divider'></div>",
        "<div class='cover-meta'>",
        f"<div class='cover-meta-item'><span class='cover-meta-label'>Prepared by</span><span class='cover-meta-value'>{html.escape(BRAND_NAME)}</span></div>",
        f"<div class='cover-meta-item'><span class='cover-meta-label'>Date</span><span class='cover-meta-value'>{report_date}</span></div>",
        "<div class='cover-meta-item'><span class='cover-meta-label'>Classification</span><span class='cover-meta-value'>Confidential</span></div>",
        "</div>",
        "</div>",
        "</section>",
    ]
    page_no += 1

    # ── Executive Summary ──
    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='highlights-label'>{labels['summary']}</div>")
    parts.append(f"<h2>Decision-Relevant Conclusions</h2>")
    summary = [_clean_summary_item(x) for x in (report.get("executive_summary", []) or [])[:8]] or ["Evidence should be translated into a focused management agenda."]
    parts.append("<div class='highlight-grid'>")
    for idx, item in enumerate(summary[:8], start=1):
        parts.append(f"<div class='highlight-card'><div class='num'>{idx:02d}</div><div class='text'>{html.escape(_shorten(item, 200))}</div></div>")
    parts.append("</div></div></section>")
    page_no += 1

    # ── Table of Contents ──
    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='toc-head'>{labels['toc']}</div>")
    parts.append("<ol class='toc-list'>")
    for s_idx, section in enumerate(sections, start=1):
        parts.append(f"<li><span class='toc-num'>Chapter {s_idx:02d}</span>{html.escape(_strip_number_prefix(section.get('title', 'Section')))}</li>")
    parts.append("</ol></div></section>")
    page_no += 1

    # ── Disclaimer ──
    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='toc-head'>{labels['disclaimer']}</div>")
    parts.append(f"<p class='disclaimer-text'>{html.escape(labels['disclaimer_text'])}</p>")
    if institutions:
        parts.append(f"<p class='small-note'>{html.escape(labels['reference_note'])} {html.escape(', '.join(str(x) for x in institutions))}.</p>")
    parts.append(f"<p class='small-note'>{html.escape(labels['formal_note'])}</p>")
    parts.append("</div></section>")
    page_no += 1

    # ── Content Sections ──
    for idx, section in enumerate(sections, start=1):
        parts.append("<section class='page'>")
        _page_header(parts, logo_path, page_no, labels)

        title_text = _strip_number_prefix(section.get("title", f"Section {idx}"))
        lead = str(section.get("lead", ""))
        paragraphs = [str(p) for p in (section.get("paragraphs", []) or [])]
        while len(paragraphs) < 3:
            paragraphs.append("The evidence should be translated into management-grade implications and tested against strategic constraints.")
        takeaways = [str(x) for x in (section.get("key_takeaways", []) or [])[:3]]

        visual = _resolve_visual(section, idx, assets)
        if visual:
            v_path = Path(assets[visual])
            if not v_path.exists() or v_path.stat().st_size == 0:
                visual = ""

        # Build text column
        text_col = []
        for p in paragraphs[:2]:
            text_col.append(f"<p>{html.escape(_shorten(p, 620))}</p>")
        if takeaways:
            text_col.append("<div class='insight-panel'>")
            text_col.append(f"<div class='insight-head'>{html.escape(labels['takeaways'])}</div>")
            text_col.append("<ul>")
            for item in takeaways:
                text_col.append(f"<li>{html.escape(_shorten(item, 150))}</li>")
            text_col.append("</ul></div>")
        for p in paragraphs[2:4]:
            text_col.append(f"<p>{html.escape(_shorten(p, 500))}</p>")

        # Build visual column
        if visual:
            cls = "chart-inline" if visual.startswith("chart-") else "section-visual"
            vis_col = [f"<img class='{cls}' src='{html.escape(assets[visual])}' alt='' />"]
        else:
            vis_col = ["<div class='visual-empty'></div>"]

        parts.append("<div class='content-area'>")
        parts.append(f"<span class='chapter-label'>Chapter {idx:02d}</span>")
        parts.append(f"<div class='section-title'>{html.escape(title_text)}</div>")
        if lead:
            parts.append(f"<div class='lead'>{html.escape(_shorten(lead, 250))}</div>")

        grid_class = "section-grid-flip" if idx % 2 == 0 else "section-grid"
        parts.append(f"<div class='{grid_class}'>")
        if idx % 2 == 0:
            parts.append("<div>")
            parts.extend(vis_col)
            parts.append("</div><div>")
            parts.extend(text_col)
            parts.append("</div>")
        else:
            parts.append("<div>")
            parts.extend(text_col)
            parts.append("</div><div>")
            parts.extend(vis_col)
            parts.append("</div>")
        parts.append("</div></div></section>")
        page_no += 1

    # ── References ──
    if institutions:
        parts.append("<section class='page'>")
        _page_header(parts, logo_path, page_no, labels)
        parts.append("<div class='content-area'>")
        parts.append(f"<div class='toc-head'>Sources & References</div>")
        parts.append(f"<p class='disclaimer-text'>{html.escape(labels['reference_note'])} {html.escape(', '.join(str(x) for x in institutions))}.</p>")
        parts.append(f"<p class='small-note'>{html.escape(labels['formal_note'])}</p>")
        parts.append("</div></section>")

    parts.append("</body></html>")
    output_file.write_text("\n".join(parts), encoding="utf-8")
    return output_file


def render_report_markdown(report: Dict[str, Any], assets: Dict[str, str], output_file: Path, topic: str, language: str = "en") -> Path:
    labels = _labels(language)
    sections = _safe_sections(report.get("sections", []))
    lines: List[str] = [f"# {report.get('report_title', topic)}", "", f"**Prepared by**: {BRAND_NAME}", "", f"**Topic**: {topic}", "", f"## {labels['summary']}", ""]
    for item in report.get("executive_summary", []) or []:
        lines.append(f"- {_clean_summary_item(item)}")
    lines.extend(["", f"## {labels['toc']}", ""])
    for section in sections:
        lines.append(f"- {_strip_number_prefix(section.get('title', 'Section'))}")
    lines.extend(["", f"## {labels['disclaimer']}", "", labels['disclaimer_text'], ""])
    for section in sections:
        lines.extend([f"## {_strip_number_prefix(section.get('title', 'Section'))}", ""])
        if section.get("lead"):
            lines.extend([f"> {section.get('lead')}", ""])
        for paragraph in section.get("paragraphs", []):
            lines.extend([str(paragraph), ""])
    output_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return output_file


def _page_header(parts: List[str], logo_path: str, page_no: int, labels: Dict[str, str]) -> None:
    brand_display = html.escape(BRAND_NAME)
    report_display = html.escape(REPORT_LABEL)
    conf_display = labels['confidential']

    # Header row — table layout is stable in wkhtmltopdf; flex can cause collision
    parts.append("<div class='run-head'>")
    parts.append("<div class='run-head-inner'>")
    if logo_path and not logo_path.lower().endswith(".svg"):
        parts.append(f"<span class='run-head-brand'><img class='logo-fixed' src='{html.escape(logo_path)}' alt='' /></span>")
    else:
        parts.append(f"<span class='run-head-brand'>{brand_display}</span>")
    parts.append(f"<span class='run-head-label'>{report_display} &nbsp;&nbsp; {conf_display}</span>")
    parts.append("</div></div>")

    # Footer row — same stable table pattern
    parts.append("<div class='run-foot'>")
    parts.append(f"<span class='run-foot-left'>{brand_display} &nbsp;&mdash;&nbsp; {conf_display}</span>")
    parts.append(f"<span class='run-foot-pg'>{page_no}</span>")
    parts.append("</div>")


def _labels(language: str) -> Dict[str, str]:
    return LABELS["en"] if str(language).lower().startswith("en") else LABELS["zh"]


def _resolve_visual(section: Dict[str, Any], idx: int, assets: Dict[str, str]) -> str:
    for key in [f"image-{idx}", str(section.get("visual_hint", "")), f"chart-{idx}", "cover-background"]:
        if key and key in assets:
            return key
    return ""


def _safe_sections(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list) and value:
        return [x if isinstance(x, dict) else {"title": str(x), "paragraphs": [str(x)]} for x in value]
    return [{"title": "Executive Priorities and Implications", "lead": "The analysis should be translated into a concise management agenda.", "paragraphs": ["The available evidence should be organized around decision quality, execution risk, and near-term management implications.", "The most useful output is a short list of actions that can be tested against public evidence and client constraints.", "Follow-up work should validate the assumptions against the source backup."], "key_takeaways": ["Focus on actionability and near-term decision quality."], "visual_hint": "image-1"}]


def _strip_number_prefix(text: str) -> str:
    return re.sub(r"^\s*\d+[\.)、]\s*", "", str(text or "")).strip()


def _clean_summary_item(item: str) -> str:
    return " ".join(str(item or "").split())


def _shorten(value: Any, max_chars: int) -> str:
    text = " ".join(str(value or "").replace("\n", " ").split())
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "."
