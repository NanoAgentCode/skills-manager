---
name: mindmap-builder
description: Create local mindmap HTML files from notes, documents, PDFs, outlines, or workflow outputs using markmap-ready Markdown. Use when the user asks to generate a mind map, convert content into a mindmap, produce a double-clickable HTML mindmap, or add optional Dify/Web workflow integration for mindmap generation.
---

# Mindmap Builder

## Overview

Use this skill to turn user intent, notes, documents, or workflow outputs into Markdown that renders well as a markmap mindmap, then generate a local `.html` file that the user can open directly.

Prefer local HTML generation for desktop/client use. Read `references/mindmap-service.md` only when the user needs Dify/Web integration or a hosted preview URL.

## Workflow

1. Identify the desired output:
   - Markdown only: produce clean markmap-oriented Markdown.
   - Local HTML: generate a `.html` file with `markmap-cli`; this is the default.
   - Workflow/DSL integration: design nodes and edges only when a server URL is required.
2. Normalize the content into a mindmap hierarchy:
   - Use one `#` root title.
   - Use `##` for primary branches and `###` / list items for details.
   - Keep labels short; move long explanations into child bullets.
   - Preserve user-provided terminology unless it is clearly noisy or duplicated.
3. Keep generated Markdown render-safe:
   - Prefer concise hierarchical outlines over long prose.
   - For large inputs, summarize before rendering.
   - Keep labels short enough to read after rendering.
   - Avoid huge flat lists; group details under meaningful branches.
4. Check local dependencies before rendering:
   - Check `node --version`, `npm --version`, and `markmap --version`.
   - If `markmap` is missing but Node/npm exist, ask the user to approve installing `markmap-cli`.
   - If approved, install with `npm install -g markmap-cli`, then re-check `markmap --version`.
   - If Node/npm are missing, tell the user Node.js must be installed first.
5. Generate local output:
   - Save the Markdown next to the desired output when useful for iteration.
   - Run `markmap input.md --output output.html --no-open`.
   - Give the user the local HTML path; they can double-click it or open it with a browser.
6. Verify outputs:
   - Confirm the `.html` file exists and has non-trivial size.
   - Check the generated HTML contains the root title.
   - If integrating with DSL, ensure downstream nodes receive either a URL or file path string.

## Markdown Shape

Prefer this structure:

```markdown
# Topic

## Branch A
- Key point
- Key point
  - Supporting detail

## Branch B
### Sub-branch
- Detail
```

Avoid flat bullet dumps, table-heavy Markdown, deeply nested prose, embedded HTML, and code blocks unless the user explicitly wants those details preserved.

## Workflow Node Pattern

For local desktop/client use, no service is required:

```text
source content
  -> mindmap Markdown
  -> markmap-cli
  -> local HTML file
  -> double-click/open in browser
```

When adding mindmap generation to a Web or Dify workflow DSL, model it as:

```text
start/user input
  -> content organizer or LLM summarizer
  -> HTTP request: POST {MINDMAP_BASE_URL}/upload-local
  -> answer/end: return preview_url
```

The HTTP request body should be `text/plain; charset=utf-8` containing Markdown. The response is a plain string URL.

If the upstream content is unstructured or long, insert an LLM/code/template node before the HTTP request to create compact Markdown.

## Troubleshooting

- Dependency checks fail: read `references/mindmap-service.md` for exact check/install commands.
- `markmap command not found`: install `markmap-cli` and ensure `markmap` is on PATH.
- Blank or unreadable HTML: reduce Markdown size or simplify nested content.
- Empty/400 response: ensure the request body is non-empty UTF-8 Markdown.
- Need a shareable URL: use the optional Mindmap FastAPI service and `/upload-local`.
- Wrong port: read the running service config; the referenced project currently uses port `16066` in `config.ini`.
