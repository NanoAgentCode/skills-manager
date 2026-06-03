---
name: mindmap-builder
description: Create offline local mindmap HTML files from notes, documents, PDFs, outlines, or workflow outputs using bundled markmap assets. Use when the user asks to generate a mind map, convert content into a mindmap, produce a double-clickable HTML mindmap, or render markmap output without relying on network/CDN access.
---

# Mindmap Builder

## Overview

Use this skill to turn user intent, notes, documents, or workflow outputs into Markdown that renders well as a markmap mindmap, then generate an offline local `.html` file that the user can open directly.

Prefer offline local HTML generation for desktop/client use. The skill bundles markmap browser assets in `assets/markmap/` so generated output does not need CDN access.

## Workflow

1. Identify the desired output:
   - Markdown only: produce clean markmap-oriented Markdown.
   - Offline local HTML: generate a `.html` file with bundled local JS/CSS assets; this is the default.
   - Markdown only: produce clean markmap-oriented Markdown when the user does not need HTML yet.
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
   - Prefer `scripts/render_offline_mindmap.ps1 -InputMarkdown input.md -OutputHtml output.html`.
   - This script runs `markmap`, copies bundled assets to `markmap-assets/`, and replaces CDN URLs with local paths.
   - Give the user the local HTML path and note that the sibling `markmap-assets/` folder must stay with it.
6. Verify outputs:
   - Confirm the `.html` file exists and has non-trivial size.
   - Check the generated HTML contains the root title.
   - Confirm the generated HTML no longer contains `cdn.jsdelivr.net`.
   - Confirm `markmap-assets/` contains `d3.min.js`, `markmap-view.js`, `markmap-toolbar.js`, and `markmap-toolbar.css`.

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
  -> render_offline_mindmap.ps1
  -> local HTML file + markmap-assets/
  -> double-click/open in browser
```

## Troubleshooting

- Dependency checks fail: read `references/mindmap-service.md` for exact check/install commands.
- `markmap command not found`: install `markmap-cli` and ensure `markmap` is on PATH.
- HTML still references CDN: render with `scripts/render_offline_mindmap.ps1`, not raw `markmap`.
- HTML moved without assets: keep the generated `markmap-assets/` folder next to the `.html` file.
- Blank or unreadable HTML: reduce Markdown size or simplify nested content.
