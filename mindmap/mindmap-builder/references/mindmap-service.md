# Mindmap Local and Service Reference

This reference is based on `D:\lark-projects\DifyApp\mindmap`.

## Default Local Client Flow

Use this path for desktop/client usage. It does not require FastAPI, `/preview`, `/html`, or a running server.

```text
PDF/text/outline
  -> compact markmap Markdown
  -> markmap-cli generates HTML
  -> user double-clicks the HTML file
```

Command:

```bash
markmap input.md --output output.html --no-open
```

## Dependency Check and Install

Before rendering local HTML, check dependencies:

```powershell
node --version
npm --version
markmap --version
```

Expected:

- `node` exists.
- `npm` exists.
- `markmap` exists.

If `markmap` is missing and Node/npm are available, ask the user for approval before installing because npm may access the network:

```powershell
npm install -g markmap-cli
```

After installation, verify again:

```powershell
markmap --version
```

If Node/npm are missing, do not try to install `markmap-cli` first. Tell the user Node.js is required, then install `markmap-cli` after Node/npm are available.

Validation:

- The output `.html` file exists.
- The file has non-trivial size.
- The root title appears in the generated HTML.
- Opening via `file:///.../output.html` works in a browser.

## Optional Service

- Framework: FastAPI.
- Default config path: `D:\lark-projects\DifyApp\mindmap\config.ini`.
- Current configured host/port: `0.0.0.0:16066`.
- Common local base URL: `http://127.0.0.1:16066`.
- Renderer dependency: `markmap-cli` executable named `markmap`.
- Markdown warning length: 30,000 characters.
- Markdown max length: 50,000 characters.
- Markmap timeout: 30 seconds.

Use the service only when a Dify/Web workflow needs an HTTP URL, multiple users need browser access, or generated files must be hosted by a server.

## Optional Mindmap Endpoints

### POST /upload

Generate a mindmap HTML preview from Markdown.

- Content-Type: `text/plain; charset=utf-8`.
- Body: Markdown text.
- CDN links remain in the generated HTML.
- Response: plain string preview URL, for example `http://127.0.0.1:16066/html/<file>.html`.

### POST /upload-local

Generate a mindmap HTML preview from Markdown and replace selected CDN links with local static paths.

- Content-Type: `text/plain; charset=utf-8`.
- Body: Markdown text.
- Prefer this route for local/offline Dify workflows.
- Response: plain string preview URL.

### GET /html/{filename}

Fetch the generated mindmap HTML file.

- `filename` must be a direct `.html` filename.
- Directory traversal is rejected.

## Optional Dify Workflow Mapping

Use this shape when generating a Dify DSL or a platform-neutral workflow IR:

```text
start
  -> llm/template/code: convert user input to markmap Markdown
  -> http-request: POST http://127.0.0.1:16066/upload-local
  -> answer/end: display the returned preview URL
```

HTTP request configuration:

- Method: `POST`.
- URL: `${MINDMAP_BASE_URL}/upload-local`.
- Headers:
  - `Content-Type: text/plain; charset=utf-8`
- Body: raw Markdown string.
- Expected response: plain text URL.

Use `${MINDMAP_BASE_URL}/upload` only when CDN resources are acceptable.

## Markdown Generation Rules

- Use a single root `#` heading.
- Use `##` for top-level branches.
- Use `###` for secondary clusters.
- Use bullets for leaves.
- Keep node labels compact, ideally under 20 Chinese characters or 8 English words.
- Convert paragraphs into parent-child relationships instead of preserving prose blocks.
- Remove repeated section titles, navigation text, boilerplate, and irrelevant metadata.
- For long source material, summarize first, then render the summary as Markdown.

Example:

```markdown
# 产品方案

## 用户目标
- 快速理解项目结构
- 生成可分享的预览链接

## 核心流程
- 收集输入
- 整理层级
- 调用 mindmap 服务
- 返回 HTML 预览

## 集成方式
- Dify HTTP 节点
- 自研 workflow adapter
- 手动 curl 调用
```

## curl Examples

Generate local-resource mindmap:

```bash
curl -X POST "http://127.0.0.1:16066/upload-local" \
  -H "Content-Type: text/plain; charset=utf-8" \
  --data-binary @mindmap.md
```

## Common Failures

- `markmap command not found`: install Node.js and `markmap-cli`, then verify `markmap --version`.
- Local HTML is blank or too dense: reduce content length or simplify deeply nested Markdown.
- `504 markmap生成超时`: reduce content length before calling the optional service.
- Empty body: send raw UTF-8 Markdown, not JSON, to `/upload` or `/upload-local`.
- Need offline local use: generate HTML with `markmap-cli` instead of calling the service.
- Wrong URL: verify `config.ini` or the active server logs before assuming the port.
