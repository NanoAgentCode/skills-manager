# Skills Manager Agent Guide

This repository is a reusable skills library. Treat each `SKILL.md` as the source of truth for one skill, regardless of model provider.

## How To Use A Skill

1. Identify the user request and choose the closest skill by reading the index below.
2. Open that skill's `SKILL.md` completely before acting.
3. Follow the workflow in `SKILL.md`.
4. Load linked files under `scripts/`, `references/`, `assets/`, or templates only when the skill says they are needed.
5. Prefer bundled scripts for repeatable or fragile operations.
6. Do not expose secrets from local config files. Use `config.example.json` for examples and keep real `config.json` values private.
7. If a platform cannot auto-discover skills, the user can invoke a skill by saying: `Read <skill-path>/SKILL.md and follow it for this task.`

## Output Directory

- Put generated skill artifacts under the repository root `output/` directory by default.
- Use a skill-specific subdirectory such as `output/wechat-format/`, `output/wechat-history-article-archive/`, `output/mindmap-builder/`, or `output/us-sector-index-impact-report/`.
- Respect a user-specified output path, but do not create new default output folders inside individual skill directories.

## Skill Index

### Content Production

- `media/video-transcriber/SKILL.md`: prefer existing subtitle/caption files, support YouTube captions and Bilibili AI subtitle JSON before audio extraction, then extract audio from local media, approved online video URLs, or user-authorized WeChat Channels/视频号 material; treat 视频号 share links as restricted when they hand off to phone WeChat, and request user credentials or exported artifacts when access requires them.
- `wechat/wechat-format/SKILL.md`: package Markdown, plain text, or rough notes into WeChat official-account compatible HTML; defaults to the repo-local `scripts/article_workflow.py` for repeated article runs, with terminology polishing, structured/enhanced Markdown, a 26-theme gallery, optional covers, and draft publishing.
- `wechat/wechat-history-article-archive/SKILL.md`: archive self-owned WeChat historical mass-send article URLs from lawful link sources; normalizes URL lists, batch-fetches public article pages, and saves Markdown, metadata, indexes, and local images by default. Use `wechat-format` afterward for migration, reformatting, or republishing.
- `wechat/wechat-format/wechat-cover/SKILL.md`: generate a WeChat article cover from an article path or topic.
- `writing/technical-article-polisher/SKILL.md`: polish technical Chinese articles or machine-translated drafts by checking terminology accuracy in context and reporting terminology changes.

### Knowledge And Visual Artifacts

- `diagram/drawio-skill/SKILL.md`: generate polished `.drawio` diagrams for architecture, flowcharts, UML/sequence/class diagrams, ERDs, C4, ML/DL figures, codebase/IaC/API/schema visualizations, and exportable PNG/SVG/PDF/JPG outputs through the draw.io desktop CLI when available.
- `diagram/excalidraw/SKILL.md`: generate clean `.excalidraw` diagrams and hand-drawn-style visualizations for flowcharts, architecture sketches, system explanations, data flows, and relationship maps; exports SVG through Kroki or PNG/SVG through the local Excalidraw CLI.
- `mindmap/mindmap-builder/SKILL.md`: convert PDFs, notes, outlines, papers, reports, or books into offline markmap HTML; supports overview-first long document mode.
- `mindmap/mindmap-publisher/SKILL.md`: publish an already generated offline mindmap HTML folder to a static hosting path and return a URL.

### Platform And Data Automation

- `dify/dify-console-admin-api/SKILL.md`: automate Dify Console Admin API app creation, DSL export/import, overwrite import, and import confirmation.
- `dify/dify-dsl-app-builder/SKILL.md`: design, generate, update, import, and verify Dify workflow or advanced-chat DSL.
- `database/python-db-query/SKILL.md`: run safe Python database queries using local ignored config files.

### Engineering Quality

- `debugging/backend-log-contract-trace/SKILL.md`: trace backend logs through API parameters, DTO/VOs, services, MyBatis XML, SQL columns, cross-service parameters, and database constraints; includes a concrete example in the recommended output shape.
- `quality/skill-linter/SKILL.md`: lint skill structure, trigger descriptions, references, metadata, README sync, and secret hygiene.

### Research And Markets

- `market/stock-analysis-system/SKILL.md`: run or adapt the imported Python FastAPI stock analysis service for A-share, Hong Kong, U.S. stock, ETF, and LOF technical analysis, using AKShare data retrieval, technical indicators, scoring, and smoke tests.
- `market/us-sector-index-impact-report/SKILL.md`: analyze last night's U.S. sector and Nasdaq/Nasdaq 100 moves, core gain/loss factors, U.S. AI capex fundamentals, and likely Hong Kong/A-share sector impact; renders an investment-bank style HTML report.

## Platform Notes

- Codex: use `SKILL.md` plus optional `agents/openai.yaml` UI metadata.
- Claude: use the same `SKILL.md` workflow; `CLAUDE.md` is a compatibility entrypoint.
- Gemini: use `GEMINI.md` as the entrypoint, then read the selected `SKILL.md`.
- GLM: use `GLM.md` as the entrypoint, then read the selected `SKILL.md`.
- DeepSeek: use `DEEPSEEK.md` as the entrypoint, then read the selected `SKILL.md`.

## Portability Rules

- Keep skill names lowercase hyphen-case and match the skill folder name where possible.
- Keep platform-specific metadata outside `SKILL.md`; prefer `agents/openai.yaml`, `CLAUDE.md`, `GEMINI.md`, `GLM.md`, or `DEEPSEEK.md`.
- Include both PowerShell and portable command examples when adding new scripts.
- When a command is Windows-only, say so in the skill body.
- Do not assume a platform has Codex-specific tools, MCP servers, or browser automation unless the current environment exposes them.
