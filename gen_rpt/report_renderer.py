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
PAD_X, PAD_TOP, PAD_BOTTOM = (0.50, 0.34, 0.28) if PAGE_FORMAT == "A4" else (0.36, 0.30, 0.24)
CW = round(PAGE_W - PAD_X * 2, 2)

CSS = f"""
@page {{ size:{PAGE_W}in {PAGE_H}in; margin:0; }}
:root {{
  --accent:{PALETTE['accent']};
  --accent2:{PALETTE.get('bright_blue',PALETTE['accent'])};
  --ink:{PALETTE['ink']};
  --muted:{PALETTE['subtle']};
  --line:{PALETTE['line']};
  --paper:{PALETTE['paper']};
  --panel:{PALETTE['panel']};
  --navy:#051C2C;
  --mid:#4A5568;
  --gray-bg:#F4F5F7;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{width:{PAGE_W}in;background:#fff;}}
body{{
  font-family:Georgia,"Times New Roman","Noto Serif",serif;
  font-size:9.5pt;line-height:1.68;color:var(--ink);
  word-spacing:0.01em;letter-spacing:0.003em;
  text-rendering:optimizeLegibility;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  font-kerning:normal;
  font-feature-settings:"kern" 1,"liga" 1,"onum" 1;
  orphans:2;widows:2;
  text-wrap:pretty;
}}

/* ── Page ── */
.page{{
  width:{PAGE_W}in;height:{PAGE_H}in;position:relative;
  background:var(--paper);
  padding:{PAD_TOP}in {PAD_X}in {PAD_BOTTOM}in {PAD_X}in;
  page-break-after:always;overflow:hidden;
}}
.content-area{{margin-top:0.20in;}}

/* ── Running Header ── */
.run-head{{
  position:absolute;top:0.12in;left:{PAD_X}in;right:{PAD_X}in;
  border-bottom:0.4pt solid var(--line);padding-bottom:0.03in;
  display:table;width:{CW}in;
}}
.run-head-inner{{display:table;width:100%;}}
.run-head-brand{{
  display:table-cell;font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:5.5pt;font-weight:600;letter-spacing:0.07em;
  text-transform:uppercase;color:var(--accent);vertical-align:bottom;white-space:nowrap;
}}
.run-head-label{{
  display:table-cell;text-align:right;
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:5pt;color:var(--muted);letter-spacing:0.03em;
  font-weight:400;white-space:nowrap;vertical-align:bottom;
}}

/* ── Running Footer ── */
.run-foot{{
  position:absolute;bottom:0.10in;left:{PAD_X}in;right:{PAD_X}in;
  border-top:0.4pt solid var(--line);padding-top:0.03in;
  display:table;width:{CW}in;
}}
.run-foot-left{{
  display:table-cell;font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:5pt;color:var(--muted);letter-spacing:0.02em;font-weight:400;white-space:nowrap;
}}
.run-foot-pg{{
  display:table-cell;text-align:right;
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:5pt;color:var(--muted);font-weight:400;letter-spacing:0.04em;white-space:nowrap;
}}

/* ── Type Hierarchy ── */
h1{{font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;font-size:24pt;line-height:1.08;font-weight:800;color:var(--navy);letter-spacing:-0.025em;margin-bottom:0.12in;}}
h2{{font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;font-size:14pt;line-height:1.22;font-weight:600;color:var(--navy);letter-spacing:-0.008em;margin-bottom:0.08in;}}
h3{{font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;font-size:11.5pt;line-height:1.26;font-weight:600;color:var(--ink);letter-spacing:0;margin-bottom:0.06in;}}
p{{margin:0 0 0.11in;font-size:9.5pt;line-height:1.68;color:var(--ink);letter-spacing:0.003em;orphans:2;widows:2;}}
ul,ol{{margin:0 0 0.10in 0.16in;padding:0;}}
li{{font-size:9.5pt;line-height:1.62;margin-bottom:0.04in;color:var(--ink);letter-spacing:0.003em;}}

/* ── Chapter Label ── */
.chapter-label{{
  display:block;font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;letter-spacing:0.10em;
  text-transform:uppercase;color:var(--accent);margin-bottom:0.05in;
}}
.section-title{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:17pt;font-weight:600;line-height:1.14;
  color:var(--navy);letter-spacing:-0.012em;margin-bottom:0.06in;
}}
.lead{{
  font-size:9.5pt;line-height:1.58;color:var(--accent);
  font-weight:500;margin-bottom:0.10in;font-style:normal;
  letter-spacing:0.005em;
}}

/* ── Section Grid ── */
.section-grid{{
  display:grid;grid-template-columns:1.25fr 0.75fr;gap:0.20in;
  align-items:start;margin-top:0.06in;
}}

/* ── Visuals ── */
.section-visual{{width:100%;height:4.20in;object-fit:cover;display:block;page-break-inside:avoid;}}
.chart-inline{{width:100%;max-height:4.20in;object-fit:contain;display:block;page-break-inside:avoid;}}
.visual-empty{{height:4.20in;background:var(--panel);border:0.4pt dashed var(--line);}}

/* ── Executive Summary ── */
.exec-label{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;letter-spacing:0.10em;
  text-transform:uppercase;color:var(--accent);
  margin-bottom:0.12in;padding-bottom:0.06in;
  border-bottom:0.4pt solid var(--line);
}}
.exec-findings{{margin-top:0.08in;}}
.exec-item{{
  display:table;width:100%;padding:0.08in 0;
  border-bottom:0.4pt solid #ECEDF0;
}}
.exec-num{{
  display:table-cell;width:0.34in;vertical-align:top;padding-top:0.01in;
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:8pt;font-weight:600;color:var(--accent);letter-spacing:0.02em;
}}
.exec-text{{
  display:table-cell;vertical-align:top;
  font-size:9.5pt;line-height:1.62;color:var(--ink);letter-spacing:0.003em;
}}

/* ── Implication Panel ── */
.impl-panel{{
  background:var(--gray-bg);padding:0.10in 0.13in;
  margin:0.10in 0 0.08in;page-break-inside:avoid;
  border-top:0.4pt solid var(--line);
}}
.impl-head{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6pt;font-weight:600;letter-spacing:0.08em;
  text-transform:uppercase;color:var(--mid);margin-bottom:0.05in;
}}
.impl-panel ul{{margin:0;padding:0 0 0 0.14in;}}
.impl-panel li{{font-size:8.5pt;line-height:1.56;margin-bottom:0.03in;color:var(--ink);letter-spacing:0.003em;}}

/* ── TOC ── */
.toc-label{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;letter-spacing:0.10em;
  text-transform:uppercase;color:var(--accent);
  margin-bottom:0.14in;padding-bottom:0.06in;
  border-bottom:0.4pt solid var(--line);
}}
.toc-list{{list-style:none;margin:0;padding:0;}}
.toc-list li{{
  font-size:9.5pt;line-height:1.48;margin-bottom:0.04in;
  padding:0.05in 0;border-bottom:0.4pt solid #F0F1F3;
  color:var(--ink);display:table;width:100%;letter-spacing:0.003em;
}}
.toc-num{{
  display:table-cell;width:0.80in;padding-right:0.12in;
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;color:var(--accent);
  letter-spacing:0.05em;vertical-align:top;padding-top:0.03in;
}}
.toc-title-text{{display:table-cell;vertical-align:top;}}

/* ── Disclaimer / refs ── */
.disc-label{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;letter-spacing:0.10em;
  text-transform:uppercase;color:var(--accent);
  margin-bottom:0.12in;padding-bottom:0.06in;
  border-bottom:0.4pt solid var(--line);
}}
.disc-text{{font-size:9pt;line-height:1.62;color:var(--muted);margin-bottom:0.10in;letter-spacing:0.005em;}}
.disc-note{{font-size:8pt;line-height:1.56;color:var(--muted);margin-top:0.08in;letter-spacing:0.005em;}}
.ref-block{{
  margin-top:0.22in;padding-top:0.12in;
  border-top:0.4pt solid var(--line);
}}

/* ── Cover ── */
.cover{{padding:0;background-size:cover;background-position:center top;}}
.cover-img-zone{{
  position:absolute;top:0;left:0;right:0;height:55%;
  background-size:cover;background-position:center;
}}
.cover-img-overlay{{
  position:absolute;top:0;left:0;right:0;height:55%;
  background:linear-gradient(180deg,rgba(5,28,44,0.60) 0%,rgba(5,28,44,0.35) 100%);
  z-index:1;
}}
.cover-white{{
  position:absolute;bottom:0;left:0;right:0;height:48%;
  background:#ffffff;z-index:2;
  padding:0.40in 0.55in 0.50in;
}}
.cover-brand-line{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:6.5pt;font-weight:600;letter-spacing:0.10em;
  text-transform:uppercase;color:var(--accent);margin-bottom:0.14in;
}}
.cover-rule{{width:0.36in;height:1.5pt;background:var(--accent);margin-bottom:0.18in;}}
.cover-title{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:28pt;line-height:1.06;font-weight:800;
  color:var(--navy);letter-spacing:-0.025em;margin-bottom:0.10in;
}}
.cover-sub{{
  font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:8.5pt;color:var(--muted);font-weight:400;
  letter-spacing:0.04em;text-transform:uppercase;margin-bottom:0.28in;
}}
.cover-divider{{width:100%;height:0.4pt;background:var(--line);margin-bottom:0.14in;}}
.cover-meta{{display:table;border-collapse:separate;border-spacing:0;}}
.cover-meta-item{{display:table-cell;vertical-align:top;padding-right:0.48in;}}
.cover-meta-item:last-child{{padding-right:0;}}
.cover-meta-label{{
  display:block;font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:5.5pt;font-weight:500;letter-spacing:0.08em;
  text-transform:uppercase;color:var(--muted);margin-bottom:0.04in;white-space:nowrap;
}}
.cover-meta-value{{
  display:block;font-family:-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:8.5pt;color:var(--navy);font-weight:600;white-space:nowrap;letter-spacing:0.005em;
}}

/* ── Profiles ── */
.profile-compact{{font-size:8.5pt;}}
.profile-compact p,.profile-compact li{{font-size:8.5pt;}}
.profile-compact h2{{font-size:13pt;}}
.profile-presentation{{font-size:12pt;}}
.profile-presentation p,.profile-presentation li{{font-size:12pt;}}
.profile-presentation h2{{font-size:20pt;}}

/* ── Print ── */
@media print{{
  html,body{{width:{PAGE_W}in;}}
  .page{{margin:0;box-shadow:none;border:none;}}
  *{{-webkit-print-color-adjust:exact !important;color-adjust:exact !important;print-color-adjust:exact !important;}}
  p{{orphans:2;widows:2;}}
}}
"""

LABELS = {
    "en": {
        "lang": "en",
        "summary": "Executive Summary",
        "toc": "Table of Contents",
        "disclaimer": "Important Notice",
        "takeaways": "Implications",
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
        "takeaways": "Implications",
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
    bg_style = f"background-image:url('{html.escape(cover_path)}');" if cover_path else "background:#051C2C;"
    parts += [
        "<section class='page cover'>",
        f"<div class='cover-img-zone' style=\"{bg_style}\"></div>",
        "<div class='cover-img-overlay'></div>",
        "<div class='cover-white'>",
        f"<div class='cover-brand-line'>{html.escape(BRAND_NAME)}</div>",
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
    _page_chrome(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='exec-label'>{labels['summary']}</div>")
    parts.append(f"<h2>Key Findings</h2>")
    summary = [_clean(x) for x in (report.get("executive_summary", []) or [])[:8]] or ["Evidence should be translated into a focused management agenda."]
    parts.append("<div class='exec-findings'>")
    for idx, item in enumerate(summary[:8], start=1):
        parts.append(f"<div class='exec-item'><span class='exec-num'>{idx:02d}</span><span class='exec-text'>{html.escape(_shorten(item, 220))}</span></div>")
    parts.append("</div></div></section>")
    page_no += 1

    # ── Table of Contents ──
    parts.append("<section class='page'>")
    _page_chrome(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='toc-label'>{labels['toc']}</div>")
    parts.append("<ul class='toc-list'>")
    for s_idx, section in enumerate(sections, start=1):
        stitle = html.escape(_strip_num(section.get('title', 'Section')))
        parts.append(f"<li><span class='toc-num'>Chapter {s_idx:02d}</span><span class='toc-title-text'>{stitle}</span></li>")
    parts.append("</ul></div></section>")
    page_no += 1

    # ── Disclaimer + References (single page) ──
    parts.append("<section class='page'>")
    _page_chrome(parts, logo_path, page_no, labels)
    parts.append("<div class='content-area'>")
    parts.append(f"<div class='disc-label'>{labels['disclaimer']}</div>")
    parts.append(f"<p class='disc-text'>{html.escape(labels['disclaimer_text'])}</p>")
    parts.append(f"<p class='disc-note'>{html.escape(labels['formal_note'])}</p>")
    if institutions:
        parts.append("<div class='ref-block'>")
        parts.append(f"<div class='disc-label'>Sources &amp; References</div>")
        inst_fmt = '; '.join(str(x) for x in institutions)
        parts.append(f"<p class='disc-text'>{html.escape(labels['reference_note'])} {html.escape(inst_fmt)}.</p>")
        parts.append("</div>")
    parts.append("</div></section>")
    page_no += 1

    # ── Content Sections ──
    for idx, section in enumerate(sections, start=1):
        parts.append("<section class='page'>")
        _page_chrome(parts, logo_path, page_no, labels)

        title_text = _strip_num(section.get("title", f"Section {idx}"))
        lead = str(section.get("lead", ""))
        paragraphs = [str(p) for p in (section.get("paragraphs", []) or []) if str(p).strip()]
        takeaways = [str(x) for x in (section.get("key_takeaways", []) or [])[:3]]

        visual = _resolve_visual(section, idx, assets)
        if visual:
            v_path = Path(assets[visual])
            if not v_path.exists() or v_path.stat().st_size == 0:
                visual = ""

        # Text column
        text_col = []
        for p in paragraphs[:2]:
            text_col.append(f"<p>{html.escape(_shorten(p, 650))}</p>")
        if takeaways:
            text_col.append("<div class='impl-panel'>")
            text_col.append(f"<div class='impl-head'>{html.escape(labels['takeaways'])}</div>")
            text_col.append("<ul>")
            for item in takeaways:
                text_col.append(f"<li>{html.escape(_shorten(item, 160))}</li>")
            text_col.append("</ul></div>")
        for p in paragraphs[2:3]:
            text_col.append(f"<p>{html.escape(_shorten(p, 500))}</p>")

        # Visual column
        if visual:
            cls = "chart-inline" if visual.startswith("chart-") else "section-visual"
            vis_col = [f"<img class='{cls}' src='{html.escape(assets[visual])}' alt='' />"]
        else:
            vis_col = ["<div class='visual-empty'></div>"]

        parts.append("<div class='content-area'>")
        parts.append(f"<span class='chapter-label'>Chapter {idx:02d}</span>")
        parts.append(f"<div class='section-title'>{html.escape(title_text)}</div>")
        if lead:
            parts.append(f"<div class='lead'>{html.escape(_shorten(lead, 260))}</div>")
        parts.append("<div class='section-grid'>")
        parts.append("<div>")
        parts.extend(text_col)
        parts.append("</div><div>")
        parts.extend(vis_col)
        parts.append("</div>")
        parts.append("</div></div></section>")
        page_no += 1

    parts.append("</body></html>")
    output_file.write_text("\n".join(parts), encoding="utf-8")
    return output_file


def render_report_markdown(report: Dict[str, Any], assets: Dict[str, str], output_file: Path, topic: str, language: str = "en") -> Path:
    labels = _labels(language)
    sections = _safe_sections(report.get("sections", []))
    lines: List[str] = [f"# {report.get('report_title', topic)}", "", f"**Prepared by**: {BRAND_NAME}", "", f"**Topic**: {topic}", "", f"## {labels['summary']}", ""]
    for item in report.get("executive_summary", []) or []:
        lines.append(f"- {_clean(item)}")
    lines.extend(["", f"## {labels['toc']}", ""])
    for section in sections:
        lines.append(f"- {_strip_num(section.get('title', 'Section'))}")
    lines.extend(["", f"## {labels['disclaimer']}", "", labels['disclaimer_text'], ""])
    for section in sections:
        lines.extend([f"## {_strip_num(section.get('title', 'Section'))}", ""])
        if section.get("lead"):
            lines.extend([f"> {section.get('lead')}", ""])
        for paragraph in section.get("paragraphs", []):
            lines.extend([str(paragraph), ""])
    output_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return output_file


def _page_chrome(parts: List[str], logo_path: str, page_no: int, labels: Dict[str, str]) -> None:
    brand = html.escape(BRAND_NAME)
    report_lbl = html.escape(REPORT_LABEL)

    parts.append("<div class='run-head'><div class='run-head-inner'>")
    if logo_path and not logo_path.lower().endswith(".svg"):
        parts.append(f"<span class='run-head-brand'><img style='height:0.16in;width:auto;object-fit:contain;vertical-align:bottom;' src='{html.escape(logo_path)}' alt='' /></span>")
    else:
        parts.append(f"<span class='run-head-brand'>{brand}</span>")
    parts.append(f"<span class='run-head-label'>{report_lbl}</span>")
    parts.append("</div></div>")

    parts.append("<div class='run-foot'>")
    parts.append(f"<span class='run-foot-left'>&copy; {brand} &middot; {labels['confidential']}</span>")
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


def _strip_num(text: str) -> str:
    return re.sub(r"^\s*\d+[\.)、]\s*", "", str(text or "")).strip()


def _clean(item: str) -> str:
    return " ".join(str(item or "").split())


def _shorten(value: Any, max_chars: int) -> str:
    text = " ".join(str(value or "").replace("\n", " ").split())
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "."
