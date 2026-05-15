from __future__ import annotations

import html
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from .theme import load_theme

THEME = load_theme()
PALETTE = THEME["palette"]
BRAND_NAME = THEME["brand_name"]
REPORT_LABEL = THEME.get("report_label", "Deep Research Report")
FONT_FAMILY = THEME.get("font_family", "Trebuchet MS, Aptos, Arial, sans-serif")
PAGE_FORMAT = os.getenv("REPORT_PAGE_FORMAT", "A4").upper()
PAGE_W, PAGE_H = (8.27, 11.69) if PAGE_FORMAT == "A4" else (6.93, 9.84)
PAD_X, PAD_TOP, PAD_BOTTOM = (0.42, 0.38, 0.30) if PAGE_FORMAT == "A4" else (0.30, 0.30, 0.24)

CSS = f"""
@page {{ size:{PAGE_W}in {PAGE_H}in; margin:0; }}

/* Base Theme Variables */
:root {{
    --accent: {PALETTE['accent']};
    --accent2: {PALETTE.get('bright_blue', PALETTE['accent'])};
    --ink: {PALETTE['ink']};
    --muted: {PALETTE['subtle']};
    --line: {PALETTE['line']};
    --paper: {PALETTE['paper']};
    --panel: {PALETTE['panel']};
    
    /* Executive Profile Defaults */
    --base-font-size: 10.5pt;
    --line-height: 1.65;
    --h1-size: 24pt;
    --h2-size: 18pt;
    --h3-size: 14pt;
    --paragraph-spacing: 0.15in;
    --bullet-spacing: 0.08in;
    --takeaway-padding: 0.12in 0.14in;
    --font-family: "Inter", "Helvetica Neue", "Segoe UI", Arial, sans-serif;
}}

/* Compact Profile */
.profile-compact {{
    --base-font-size: 9.5pt;
    --line-height: 1.5;
    --h1-size: 20pt;
    --h2-size: 15pt;
    --paragraph-spacing: 0.1in;
    --bullet-spacing: 0.05in;
    --takeaway-padding: 0.08in 0.1in;
}}

/* Presentation Profile */
.profile-presentation {{
    --base-font-size: 13pt;
    --line-height: 1.5;
    --h1-size: 28pt;
    --h2-size: 22pt;
    --paragraph-spacing: 0.2in;
    --bullet-spacing: 0.1in;
    --takeaway-padding: 0.15in 0.2in;
}}

* {{ box-sizing: border-box; text-rendering: auto; -webkit-font-smoothing: antialiased; letter-spacing: 0px !important; word-spacing: 0px !important; }}
html, body {{ width: {PAGE_W}in; margin: 0; padding: 0; background: #fff; }}

body {{ 
    font-family: var(--font-family); 
    color: var(--ink); 
    font-size: var(--base-font-size); 
    line-height: var(--line-height); 
}}

.page {{ 
    width: {PAGE_W}in; 
    height: {PAGE_H}in; 
    margin: 0; 
    background: var(--paper); 
    position: relative; 
    padding: {PAD_TOP}in {PAD_X}in {PAD_BOTTOM}in {PAD_X}in; 
    page-break-after: always; 
    overflow: hidden; 
}}

/* Typography Hierarchy */
h1, h2, h3 {{ margin: 0; color: var(--ink); font-weight: 600; letter-spacing: -0.01em; }}
h1 {{ font-size: var(--h1-size); line-height: 1.1; margin-bottom: 0.15in; }}
h2 {{ font-size: var(--h2-size); line-height: 1.25; margin-bottom: 0.12in; }}
h3 {{ font-size: var(--h3-size); line-height: 1.3; margin-bottom: 0.08in; }}

p {{ 
    margin: 0 0 var(--paragraph-spacing); 
    text-align: left; 
    color: var(--ink);
}}

ul, ol {{ 
    margin: 0.05in 0 var(--paragraph-spacing) 0.2in; 
    padding: 0; 
}}
li {{ margin-bottom: var(--bullet-spacing); }}

.lead {{ 
    font-size: calc(var(--base-font-size) * 1.15); 
    line-height: 1.45; 
    color: var(--accent); 
    font-weight: 500; 
    margin-bottom: 0.18in; 
}}

.kicker {{ 
    color: var(--accent); 
    font-size: calc(var(--base-font-size) * 0.7); 
    font-weight: 700; 
    letter-spacing: 0.08em; 
    text-transform: uppercase; 
    margin-bottom: 0.06in; 
}}

/* Structural Layouts */
.section-grid {{ 
    display: grid; 
    grid-template-columns: 1.1fr 0.9fr; 
    gap: 0.25in; 
    align-items: start; 
}}

.highlight-grid {{ 
    display: grid; 
    grid-template-columns: repeat(2, 1fr); 
    gap: 0.12in 0.16in; 
    margin-top: 0.15in; 
}}

/* Components */
.highlight-card {{ 
    border-left: 4px solid var(--accent); 
    background: #fff; 
    padding: 0.12in 0.14in; 
    min-height: 0.65in; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 0 0 1px var(--line); 
    border-radius: 2px;
    page-break-inside: avoid;
}}
.highlight-card .num {{ color: var(--accent); font-size: calc(var(--base-font-size) * 0.85); font-weight: 700; margin-bottom: 0.04in; }}
.highlight-card .text {{ color: var(--ink); font-size: calc(var(--base-font-size) * 0.9); line-height: 1.45; }}

.takeaway {{ 
    border-left: 4px solid var(--accent); 
    background: var(--panel); 
    padding: var(--takeaway-padding); 
    margin: 0.15in 0 var(--paragraph-spacing); 
    page-break-inside: avoid; 
    border-radius: 0 4px 4px 0;
}}
.takeaway strong {{ display: block; margin-bottom: 0.04in; font-weight: 600; color: var(--ink); }}
.takeaway ul {{ margin-bottom: 0; }}

/* Visuals & Images */
.section-visual {{ 
    width: 100%; 
    height: 3.95in; 
    object-fit: cover; 
    display: block; 
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    page-break-inside: avoid;
}}
.chart-inline {{ 
    width: 100%; 
    max-height: 3.85in; 
    object-fit: contain; 
    border: none; 
    margin: 0.1in 0; 
    page-break-inside: avoid;
}}

.placeholder {{ 
    height: 3.95in; 
    background: linear-gradient(135deg, var(--paper), var(--panel)); 
    border: 1px dashed var(--line); 
    position: relative; 
    border-radius: 4px;
}}
.placeholder::before {{ content: ""; position: absolute; left: 0.25in; right: 0.25in; top: 1.6in; height: 0.035in; background: var(--accent2); transform: rotate(-14deg); opacity: 0.2; }}
.placeholder::after {{ content: "Strategic visual"; position: absolute; left: 0.25in; bottom: 0.25in; color: var(--muted); font-size: calc(var(--base-font-size) * 0.8); }}

/* Headers and Footers */
.page-header {{ position: absolute; top: 0.12in; left: {PAD_X}in; right: 0.92in; color: var(--muted); font-size: calc(var(--base-font-size) * 0.55); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }}
.page-footer {{ position: absolute; bottom: 0.09in; left: {PAD_X}in; right: {PAD_X}in; display: flex; justify-content: space-between; color: var(--muted); font-size: calc(var(--base-font-size) * 0.55); font-weight: 500; }}
.logo-fixed {{ position: absolute; top: 0.12in; right: 0.28in; width: 0.50in; z-index: 10; object-fit: contain; }}

/* Cover Page */
.cover {{ padding: 0; background-size: cover; background-position: center; }}
.cover::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(5,28,44,.92), rgba(5,28,44,.65), rgba(5,28,44,.1)); }}
.cover-panel {{ 
    position: absolute; 
    left: 0.48in; 
    top: 0.8in; 
    width: 5.4in; 
    background: rgba(255,255,255,.98); 
    color: var(--ink); 
    padding: 0.35in 0.4in; 
    z-index: 2; 
    border-top: 4px solid var(--accent2); 
    border-radius: 0 0 2px 2px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}}
.cover-panel .eyebrow {{ font-size: calc(var(--base-font-size) * 0.75); color: var(--accent); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.04in; }}
.cover-panel h1 {{ font-size: 26pt; line-height: 1.15; font-weight: 300; margin: 0.15in 0 0.2in; letter-spacing: -0.02em; }}
.cover-date {{ font-size: calc(var(--base-font-size) * 0.8); color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}

/* Utilities */
.contents-list {{ margin-top: 0.2in; font-size: calc(var(--base-font-size) * 0.95); line-height: 1.6; }}
.contents-list li {{ margin-bottom: 0.08in; }}

.reference-note, .disclaimer-text, .small-note {{ color: var(--muted); font-size: calc(var(--base-font-size) * 0.8); line-height: 1.5; }}
.reference-note {{ border-top: 1px solid var(--line); padding-top: 0.1in; margin-top: 0.2in; }}

@media print {{ 
    html, body {{ width: {PAGE_W}in; }} 
    .page {{ margin: 0; box-shadow: none; border: none; }} 
    * {{ -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }}
}}
"""

LABELS = {
    "en": {"lang": "en", "summary": "Key highlights", "toc": "Contents", "disclaimer": "Disclaimer", "takeaways": "Takeaways", "reference_note": "This report was informed by public research and data from:", "formal_note": "The full source backup is archived in the backup folder.", "disclaimer_text": "This document is a management consulting and research analysis deliverable for strategy discussion only. It is not professional advisory guidance."},
    "zh": {"lang": "zh-CN", "summary": "Key highlights", "toc": "Contents", "disclaimer": "Disclaimer", "takeaways": "Takeaways", "reference_note": "Reference institutions:", "formal_note": "Source backup is archived in the backup folder.", "disclaimer_text": "This document is for management research and strategy discussion only."},
}


def render_report_html(report: Dict[str, Any], assets: Dict[str, str], output_file: Path, topic: str, language: str = "en") -> Path:
    labels = _labels(language)
    sections = _safe_sections(report.get("sections", []))
    institutions = report.get("reference_institutions", []) or []
    logo_path = assets.get("brand-logo", "")
    cover_path = assets.get("cover-background", "")
    title = str(report.get("report_title") or topic)
    page_no = 1
    
    profile = os.getenv("REPORT_PROFILE", "executive").lower().strip()
    profile_class = f"profile-{profile}"
    
    parts: List[str] = ["<!DOCTYPE html>", f"<html lang='{labels['lang']}'>", "<head>", "<meta charset='utf-8' />", f"<title>{html.escape(title)}</title>", f"<style>{CSS}</style>", "</head>", f"<body class='{profile_class}'>"]

    bg = f"background-image:url('{html.escape(cover_path)}');" if cover_path else "background:#051C2C;"
    parts.append(f"<section class='page cover' style=\"{bg}\">")
    parts.append(f"<div class='cover-panel'>")
    parts.append(f"<div class='eyebrow'>{html.escape(BRAND_NAME)} | {html.escape(REPORT_LABEL)}</div>")
    parts.append(f"<h1>{html.escape(title)}</h1>")
    parts.append(f"<div class='cover-date'>Strategic Intelligence Brief &nbsp;&mdash;&nbsp; {html.escape(topic)}</div>")
    parts.append(f"</div></section>")
    page_no += 1

    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no)
    parts.append(f"<div class='kicker'>{labels['summary']}</div><h2>The report opens with decision-relevant conclusions</h2><div class='highlight-grid'>")
    summary = [_clean_summary_item(x) for x in (report.get("executive_summary", []) or [])[:8]] or ["Evidence should be translated into a focused management agenda."]
    for idx, item in enumerate(summary[:8], start=1):
        parts.append(f"<div class='highlight-card'><div class='num'>{idx:02d}</div><div class='text'>{html.escape(_shorten(item, 210))}</div></div>")
    parts.append("</div></section>")
    page_no += 1

    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no)
    parts.append(f"<div class='kicker'>{labels['toc']}</div><h2>{labels['toc']}</h2><ol class='contents-list'>")
    for section in sections:
        parts.append(f"<li>{html.escape(_strip_number_prefix(section.get('title', 'Section')))}</li>")
    parts.append("</ol></section>")
    page_no += 1

    parts.append("<section class='page'>")
    _page_header(parts, logo_path, page_no)
    parts.append(f"<div class='kicker'>{labels['disclaimer']}</div><h2>{labels['disclaimer']}</h2><p class='disclaimer-text'>{html.escape(labels['disclaimer_text'])}</p>")
    if institutions:
        parts.append(f"<p class='small-note'>{html.escape(labels['reference_note'])} {html.escape(', '.join(str(x) for x in institutions))}.</p>")
    parts.append(f"<p class='small-note'>{html.escape(labels['formal_note'])}</p></section>")
    page_no += 1

    for idx, section in enumerate(sections, start=1):
        parts.append("<section class='page'>")
        _page_header(parts, logo_path, page_no)
        title_text = _strip_number_prefix(section.get("title", f"Section {idx}"))
        lead = str(section.get("lead", ""))
        paragraphs = [str(p) for p in (section.get("paragraphs", []) or [])]
        while len(paragraphs) < 3:
            paragraphs.append("Evidence should be validated against the source backup and translated into management implications.")
        takeaways = [str(x) for x in (section.get("key_takeaways", []) or [])[:3]]
        
        visual = _resolve_visual(section, idx, assets)
        if visual:
            v_path = Path(assets[visual])
            if not v_path.exists() or v_path.stat().st_size == 0:
                visual = ""

        text_column = []
        for p in paragraphs[:2]:
            text_column.append(f"<p>{html.escape(_shorten(p, 650))}</p>")
        if takeaways:
            text_column.append(f"<div class='takeaway'><strong>{html.escape(labels['takeaways'])}</strong><ul>")
            for item in takeaways:
                text_column.append(f"<li>{html.escape(_shorten(item, 150))}</li>")
            text_column.append("</ul></div>")
        for p in paragraphs[2:4]:
            text_column.append(f"<p>{html.escape(_shorten(p, 520))}</p>")

        visual_column = []
        if visual:
            cls = "chart-inline" if visual.startswith("chart-") else "section-visual"
            visual_column.append(f"<img class='{cls}' src='{html.escape(assets[visual])}' alt='{html.escape(visual)}' />")
        else:
            visual_column.append("<div class='placeholder'></div>")

        parts.append(f"<div class='kicker'>Chapter {idx}</div><h2>{html.escape(title_text)}</h2>")
        if lead:
            parts.append(f"<div class='lead'>{html.escape(_shorten(lead, 260))}</div>")
            
        parts.append("<div class='section-grid'>")
        if idx % 2 == 0:
            parts.append("<div>")
            parts.extend(visual_column)
            parts.append("</div><div>")
            parts.extend(text_column)
            parts.append("</div>")
        else:
            parts.append("<div>")
            parts.extend(text_column)
            parts.append("</div><div>")
            parts.extend(visual_column)
            parts.append("</div>")
        parts.append("</div></section>")
        page_no += 1

    if institutions:
        parts.append("<section class='page'>")
        _page_header(parts, logo_path, page_no)
        parts.append(f"<div class='reference-note'>{html.escape(labels['reference_note'])} {html.escape(', '.join(str(x) for x in institutions))}. {html.escape(labels['formal_note'])}</div>")
        parts.append("</section>")
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


def _page_header(parts: List[str], logo_path: str, page_no: int) -> None:
    if logo_path and not logo_path.lower().endswith(".svg"):
        parts.append(f"<img class='logo-fixed' src='{html.escape(logo_path)}' alt='brand logo' />")
    parts.append(f"<div class='page-header'>{html.escape(BRAND_NAME)} | CONFIDENTIAL</div>")
    parts.append(f"<div class='page-footer'><span>{html.escape(BRAND_NAME)} | Confidential</span><span>{page_no}</span></div>")


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
    return [{"title": "Executive priorities and implications", "lead": "The analysis should be translated into a concise management agenda.", "paragraphs": ["The available evidence should be organized around decision quality, execution risk and near-term management implications.", "The most useful output is a short list of actions that can be tested against public evidence and client constraints.", "Follow-up work should validate the assumptions against the source backup."], "key_takeaways": ["Focus on actionability."], "visual_hint": "image-1"}]


def _strip_number_prefix(text: str) -> str:
    return re.sub(r"^\s*\d+[\.)、]\s*", "", str(text or "")).strip()


def _clean_summary_item(item: str) -> str:
    return " ".join(str(item or "").split())


def _shorten(value: Any, max_chars: int) -> str:
    text = " ".join(str(value or "").replace("\n", " ").split())
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "."
