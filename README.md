# Run

python main.py --topic "AI Agent Market Research" --language en --provider groq
Specialized agents designed for specific industries

# gen_rpt

A **Deep Research Research Report Generator** that can be directly run in a GitHub repo.

You can input a "topic description" in GitHub Actions, and it will automatically complete this chain:

1. Use DeepSeek to generate a research plan
2. Automatically perform public web search and information scraping
3. Organize content according to Deep Research + Management Consulting problem decomposition methods
4. Automatically generate branded insight cards and unified visual style charts
5. Automatically generate cover page, table of contents, and disclaimers
6. Automatically execute PDF QA; if layout risks are found, it will compress content and re-render
7. Synchronously output `HTML + Markdown + PDF + PPTX + HTML Presentation`
8. Write the results directly back to the `reports/` directory of the current repo

## What is supported now

- **Action input a one-sentence topic**, automatically generate a complete research report
- **BlueOcean branded presentation**: Theme colors, fonts, and chart styles are centralized in `branding/theme.json`
- **Cover Page**: Automatically generate a formal cover; if you put a custom cover image, the custom image is prioritized
- **Every page PDF Logo**: Currently uses a dummy `BlueOcean` logo, which can be directly replaced
- **Table of Contents**: Automatically generate a chapter table of contents
- **Disclaimer**: Automatically generate formal disclaimers such as "does not constitute investment advice"
- **Pyramid Principle**: Titles and introductions require conclusions first, crisp & sharp
- **Seven-step method and issue tree**: First decompose the problem, then collect evidence, locate key points, and form recommendations
- **Strategy Ten Questions Thinking**: Integrates dimensions such as market competitiveness, source of advantage, trends, uncertainty, execution determination, etc.
- **Reference weakening**: Formal documents do not directly list reference links, only keep institutional source descriptions
- **Reference backup**: Complete source drafts automatically enter the `backup/` folder
- **PDF QA**: Automatically check for PDF text overlap, small fonts, abnormally large fonts, meta-tag leakage, and page density risks
- **Automatic repair**: When QA fails, it will automatically shorten titles/body text/chart labels, switch to a compact profile, and re-render
- **Multi-format output**: Automatically generate `report.html`, `report.md`, `report.pdf`, `report.pptx`, `presentation.html`
- **Write back to repo**: Not an artifact, but directly committed to the repository
- **Chinese chart font fix**: The workflow will install CJK fonts and automatically fallback in Matplotlib

## Project Structure

```text
gen_rpt/
├── .github/workflows/generate_deep_research.yml
├── branding/
│   ├── theme.json
│   └── logo.svg
├── gen_rpt/
│   ├── brand_assets.py
│   ├── deepseek_client.py
│   ├── graphics.py
│   ├── pdf_qa.py
│   ├── pdf_renderer.py
│   ├── ppt_renderer.py
│   ├── presentation_renderer.py
│   ├── report_renderer.py
│   ├── research_pipeline.py
│   ├── theme.py
│   └── web_fetch.py
├── reports/
├── requirements.txt
├── .env.example
└── README.md
```

## Workflow Instructions

There is already a manually triggered GitHub Action in the repository:

- Workflow Name: `Generate Deep Research Report`
- Trigger Method: `Actions -> Generate Deep Research Report -> Run workflow`
- Input Parameters:
  - `topic`: Your research topic, you can directly input a sentence
  - `slug`: Optional, custom output directory name
  - `language`: `zh` or `en`
  - `target_length`: Optional, target length; when empty, Chinese defaults to 3000, English defaults to 1500
  - `model`: Default `deepseek-chat`

When running is complete, the generated results will be written to:

```text
reports/YYYY-MM-DD-your-topic-slug/
  report.html
  report.md
  report.pdf
  report.pptx
  presentation.html
  qa_result.json
  report_payload.json
  research_plan.json
  sources.json
  assets/
    brand-logo.svg
    cover-background.png
    card-1.png
    chart-1.png
  backup/
    reference_notes.md
    source_01.txt
    source_02.txt
    qa/
      pdf_qa.json
      page_001.png
      page_002.png
```

## PDF QA and Automatic Repair

The generation process is now:

```text
render HTML/MD/PDF
→ run_pdf_qa(report.pdf)
→ If passed: continue to generate PPTX and HTML presentation
→ If not passed: apply_pdf_qa_fixes()
→ Re-render HTML/MD/PDF
→ Run QA again
→ Generate PPTX and HTML presentation
```

QA will check:
- Whether PDF can be opened
- Whether page count is abnormal
- Whether text is extractable
- Whether text blocks overlap
- Whether there are too small fonts
- Whether there are abnormally large fonts
- Whether internal meta-tags like `BCG-style`, `McKinsey-style`, `sample card` are leaked
- Whether HTML pages have overflow risks due to dense text + images on the same page

QA screenshots will be saved in:

```text
reports/.../backup/qa/
```

If automatic repair is triggered, the original model output will be retained as:

```text
report_payload_prefixed.json
```

The final formally used one is:

```text
report_payload.json
```

## PPTX and HTML Presentation

In addition to the formal research report, the system will also generate:

```text
report.pptx
presentation.html
```

- `report.pptx`: Suitable for continuing manual editing and sending to teams for modification
- `presentation.html`: Suitable for direct browser presentation, supports keyboard page flipping
  - Right arrow / Space: Next page
  - Left arrow: Previous page
  - F: Full screen

## DeepSeek API Secret Configuration

The variable name is already reserved:

```bash
DEEPSEEK_API_KEY
```

Please configure it in the repository like this:

1. Open the repository
2. Enter `Settings`
3. Enter `Secrets and variables`
4. Click `Actions`
5. New secret
6. Name fill in: `DEEPSEEK_API_KEY`
7. Value fill in your DeepSeek API Key

## Brand and Cover Replacement Location

### 1. Replace PDF / PPT Logo

The current dummy logo is here:

```text
branding/logo.svg
```

You just need to replace this file with your formal logo later.

### 2. Replace Cover Background Image

If the following files exist, the system will prioritize using them:

```text
branding/cover_background.png
branding/cover_background.jpg
```

If they do not exist, the code will automatically generate an abstract cover background.

### 3. Replace Theme Color

The theme configuration file is in:

```text
branding/theme.json
```

This controls:
- HTML / PDF theme color
- Card / Chart color scheme
- PPTX color scheme
- Presentation HTML color scheme
- Brand name
- Font chain

## Difference between Formal Documents and Backup

Formal documents include:
- `report.html`
- `report.md`
- `report.pdf`
- `report.pptx`
- `presentation.html`

Formal documents will not directly list a complete list of Reference links, but will only explain which institutions' or platforms' public research was referenced at the end of the text in small gray text.

The complete source draft will enter:

```text
reports/.../backup/
```

Suitable for internal archiving, tracing, and secondary verification.

## Local Running

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install PDF Dependencies (Local)

If you also want to generate PDFs locally, please install additionally:

```bash
wkhtmltopdf
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Then change the following in `.env`:

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

To your own key.

### 4. Execute Generation

```bash
export DEEPSEEK_API_KEY=your_key
python -m gen_rpt.main \
  --topic "Generate a deep research report on AI Agent market evolution, competitive landscape, and commercialization path" \
  --language en \
  --target-length 1500 \
  --model deepseek-chat \
  --out-root reports
```

## Report Generation Logic

- **Plan**: Research goals, decision questions, issue tree, search terms
- **Search**: Public web search and scraping
- **Read**: Extract web body text, organize information pool
- **Synthesize**: Structured report JSON
- **Visualize**: Generate BlueOcean memo style cards and charts
- **Render**: HTML, Markdown, PDF, PPTX, HTML Presentation
- **QA**: PDF automatic detection and automatic repair
- **Archive**: Source drafts and QA screenshots enter backup

## Boundaries of Current Version

- PDF QA is heuristic detection, can find obvious overlap/font abnormalities/density risks, but is not a complete visual understanding model
- Automatic repair is mainly achieved by compressing text, shortening labels, and reducing page density
- The current default cover background is programmatically generated, not truly connected to an image model generation
- Public web search depends on general search page structure, which can continue to be enhanced for stability in the future
- Chart data mainly comes from the model's structured organization of public information, complex quantitative research can continue to superimpose specialized data sources

## Author

- [@yt-feng](https://github.com/yt-feng)
