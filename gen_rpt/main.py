from __future__ import annotations

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path

from .deepseek_client import DeepSeekClient
from .latex_renderer import render_latex_pdf
from .research_pipeline import ResearchPipeline
from .logger import log_stage, log_success, log_info, log_error, log_warning


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60] or "deep-research-topic"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a rich deep research report.")
    parser.add_argument("--topic", required=True, help="Research topic or the sentence you typed into GitHub Action.")
    parser.add_argument("--slug", default="", help="Optional custom output slug.")
    parser.add_argument("--language", default="en", help="Report language. Default: en")
    parser.add_argument("--model", default="deepseek-chat", help="DeepSeek model name.")
    parser.add_argument("--target-length", type=int, default=0, help="Optional legacy target length. Leave empty for natural report length.")
    parser.add_argument("--out-root", default="reports", help="Output root directory.")
    return parser.parse_args()


def print_summary(start_time: float, output_dir: Path, result: dict | None = None, latex_result: dict | None = None, error: str | None = None) -> None:
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print(" EXECUTION SUMMARY")
    print("="*60)
    print(f"Total execution time : {total_time:.2f} seconds")
    print(f"Output directory     : {output_dir}")
    
    if error:
        print(f"Status               : FAILED")
        print(f"Error                : {error}")
    else:
        qa_result = result.get("qa_result", {}) if result else {}
        qa_passed = qa_result.get("passed", False)
        print(f"QA Status            : {'PASSED' if qa_passed else 'FAILED'}")
        
        print("\nGenerated Files:")
        print(f"  - HTML             : {output_dir / 'report.html'}")
        print(f"  - Markdown         : {output_dir / 'report.md'}")
        print(f"  - PDF              : {output_dir / 'report.pdf'}")
        print(f"  - PPTX             : {output_dir / 'report.pptx'}")
        print(f"  - Presentation     : {output_dir / 'presentation.html'}")
        print(f"  - QA Result        : {output_dir / 'qa_result.json'}")
        
        if latex_result:
            print(f"  - LaTeX Source     : {latex_result.get('tex_path')}")
            if latex_result.get("pdf_path"):
                print(f"  - LaTeX PDF        : {latex_result.get('pdf_path')}")
                
        # Check for warnings/errors written to files
        warnings = []
        if (output_dir / "plan_error.txt").exists():
            warnings.append("Plan generation failed and used fallback.")
        if (output_dir / "synthesis_error.txt").exists():
            warnings.append("Synthesis failed and used fallback.")
            
        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  - {w}")
                
    print("="*60 + "\n")


def main() -> None:
    start_time = time.time()
    
    log_stage("INIT", "Loading configuration")
    args = parse_args()
    
    normalized_language = "zh" if str(args.language).lower().startswith("zh") else "en"
    target_length = args.target_length or 0

    log_stage("INIT", f"Initializing client with model {args.model}")
    client = DeepSeekClient(model=args.model)
    pipeline = ResearchPipeline(client=client, language=normalized_language, target_length=target_length)

    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    slug = args.slug.strip() or slugify(args.topic)
    output_dir = Path(args.out_root) / f"{date_prefix}-{slug}"

    log_stage("INIT", f"Output directory target: {output_dir}")
    
    result = None
    latex_result = None
    error_msg = None
    
    try:
        result = pipeline.build_report(topic=args.topic, output_dir=output_dir)
        
        log_stage("RENDER", "Rendering LaTeX PDF")
        latex_result = render_latex_pdf(
            report=result.get("report", {}),
            assets=result.get("asset_map", {}),
            output_dir=output_dir,
            topic=result.get("report", {}).get("_display_topic") or args.topic,
            language=normalized_language,
        )
        
        log_success("Report generation completed")
        
    except Exception as exc:
        log_error(f"Execution failed: {exc}")
        error_msg = str(exc)

    # Maintain GitHub Actions compatibility
    step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if step_summary and result:
        qa_result = result.get("qa_result", {})
        report_path = output_dir / "report.html"
        markdown_path = output_dir / "report.md"
        pdf_path = output_dir / "report.pdf"
        pptx_path = output_dir / "report.pptx"
        presentation_path = output_dir / "presentation.html"
        qa_path = output_dir / "qa_result.json"
        
        latex_tex_path = Path(latex_result.get("tex_path", output_dir / "report_latex.tex")) if latex_result else output_dir / "report_latex.tex"
        latex_pdf_path = Path(latex_result.get("pdf_path")) if latex_result and latex_result.get("pdf_path") else output_dir / "report_latex.pdf"
        
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write("## Deep Research report generated\n")
            f.write(f"- Topic: {args.topic}\n")
            f.write(f"- Language: {normalized_language}\n")
            f.write(f"- HTML: `{report_path}`\n")
            f.write(f"- Markdown: `{markdown_path}`\n")
            f.write(f"- PDF: `{pdf_path}`\n")
            f.write(f"- LaTeX source: `{latex_tex_path}`\n")
            f.write(f"- LaTeX PDF: `{latex_pdf_path}`\n")
            f.write(f"- PPTX: `{pptx_path}`\n")
            f.write(f"- HTML Presentation: `{presentation_path}`\n")
            f.write(f"- QA passed: `{qa_result.get('passed')}`\n")
            f.write(f"- QA issues: `{len(qa_result.get('issues', []))}`\n")
            f.write(f"- Assets: {len(result['asset_map'])}\n")

    # Print summary to terminal
    print_summary(start_time, output_dir, result, latex_result, error_msg)


if __name__ == "__main__":
    main()
