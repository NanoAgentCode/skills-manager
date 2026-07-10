# Skill Index

This document summarizes the reusable skills in this repository. Treat each `SKILL.md` as the source of truth.

## Content Production

Use this group when the request is about turning media, notes, drafts, or archived material into publishable content.

- `media/video-transcriber/SKILL.md`: transcript, subtitle, summary, meeting-note, and article-draft workflows from local media, approved online videos, existing captions, YouTube captions, Bilibili subtitle JSON, or user-authorized WeChat Channels material.
- `writing/technical-article-polisher/SKILL.md`: Chinese technical article polishing, machine-translation cleanup, terminology checks, and publication-ready Markdown.
- `wechat/wechat-format/SKILL.md`: WeChat official-account article packaging through the repo-local `scripts/article_workflow.py`, including terminology polishing, structured/enhanced Markdown, a 26-theme gallery, themed outputs, optional covers, and draft publishing.
- `wechat/wechat-history-article-archive/SKILL.md`: authorized historical WeChat article backup from lawful `mp.weixin.qq.com/s?...` URL sources, with Markdown, metadata, indexes, and local images by default.
- `wechat/wechat-format/wechat-cover/SKILL.md`: cover-image generation for WeChat articles.

## Knowledge And Visual Artifacts

Use this group when the request is about systematic technical understanding, diagrams, mindmaps, visual explanation, or offline knowledge views.

- `knowledge/technical-cognition-framework/SKILL.md`: evidence-based frameworks for systematically understanding a technology through its definition, concept relationships, motivation, construction methods, scenarios, boundaries, common confusions, and relationship with LLMs and agents; includes Ontology as a worked reference.
- `diagram/drawio-skill/SKILL.md`: polished `.drawio` architecture, flowchart, UML, ERD, C4, ML/DL, codebase, IaC, OpenAPI, SQL schema, and system diagrams with local draw.io CLI export when available.
- `diagram/excalidraw/SKILL.md`: clean `.excalidraw` flowcharts, architecture sketches, process diagrams, relationship maps, and whiteboard-style visual explanations with Kroki SVG or local PNG/SVG export.
- `mindmap/mindmap-builder/SKILL.md`: offline markmap HTML generation from PDFs, notes, outlines, reports, papers, books, or other documents; supports overview-first long document mode.
- `mindmap/mindmap-publisher/SKILL.md`: static publishing for already generated offline mindmap HTML folders when the user explicitly asks to publish or host.

## Platform And Data Automation

Use this group when the request is about Dify apps, DSL import/export, platform configuration, or database-backed lookup.

- `dify/dify-console-admin-api/SKILL.md`: Dify Console Admin API automation for app creation, DSL export/import, overwrite import, and pending import confirmation.
- `dify/dify-dsl-app-builder/SKILL.md`: Dify workflow or advanced-chat DSL design, generation, update, import, and verification.
- `database/python-db-query/SKILL.md`: safe Python database querying with ignored local configs, read-only defaults, tabular/JSON/CSV output, and explicit authorization for writes.

## Engineering Quality

Use this group when the request is about diagnosing code paths or validating skills.

- `debugging/backend-log-contract-trace/SKILL.md`: backend log-to-contract tracing across routes/controllers, DTO/VOs, services, mapper XML, SQL columns, cross-service parameters, and database constraints.
- `quality/skill-linter/SKILL.md`: skill structure, trigger metadata, resource links, UI metadata, README sync, platform compatibility entrypoints, and secret hygiene checks.

## Research And Markets

Use this group when the request is about market research, public-market impact analysis, or investment-bank style output.

- `market/stock-analysis-system/SKILL.md`: local Python FastAPI stock-analysis service for A-share, Hong Kong, U.S. stock, ETF, and LOF technical analysis, including AKShare data retrieval, technical indicators, scoring, and API smoke tests.
- `market/us-sector-index-impact-report/SKILL.md`: most recent completed U.S. trading session analysis, Nasdaq/Nasdaq 100 and sector moves, core drivers, U.S. AI capex fundamentals, and Hong Kong/A-share sector implications rendered as standalone HTML. Includes a stable checked-in renderer fixture at `fixtures/sample-report.json`.

Primary command:

```powershell
.\scripts\run-python.ps1 .\market\us-sector-index-impact-report\scripts\render_investment_bank_html.py `
  --input .\output\us-sector-index-impact-report\report-data.json `
  --output .\output\us-sector-index-impact-report\us-sector-impact-report.html
```

On Windows, use the repository launcher for Python-based skills so commands do not depend on `python` or `py` being on `PATH`. If Python is unavailable, the launcher reports the missing interpreter prerequisite and the locations it checked.

Preview the stable fixture:

```powershell
.\market\us-sector-index-impact-report\scripts\preview_sample_report.ps1
```

## Other Categories

- `knowledge/`: systematic technical cognition frameworks and worked concept references.
- `dify/`: Dify Console Admin API automation and DSL app building.
- `mindmap/`: offline markmap HTML generation and optional static publishing.
- `wechat/`: WeChat article formatting, cover generation, and authorized archive workflows.
- `writing/`: Chinese technical article polishing.
- `database/`: safe Python database querying with local ignored configs.
- `debugging/`: backend log-to-contract tracing.
- `quality/`: skill linting and release checks.
