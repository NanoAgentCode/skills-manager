# skills-manager

本仓库用于管理可复用的 Codex/Claude Skills。目前包含 Dify 和 Mindmap 两类 skill：

- Dify：覆盖 Dify Console Admin API 自动化与 Dify DSL 应用构建。
- Mindmap：把 PDF、文本、大纲或文档内容转换为离线可双击打开的思维导图 HTML。

## 功能覆盖

### `dify/dify-console-admin-api`

该 skill 适合在不使用浏览器登录 cookie 的情况下，通过 `ADMIN_API_KEY` 调用 Dify Console API：

- 创建 workflow 应用。
- 导出应用或指定 workflow 的 DSL。
- 通过 YAML 内容或 YAML URL 导入 DSL。
- 覆盖导入已有 workflow 或 advanced-chat 应用。
- 处理 `202 pending` 导入确认。
- 排查 `401 Invalid token`、连接失败、依赖损坏等常见问题。

### `dify/dify-dsl-app-builder`

该 skill 适合根据自然语言需求生成或更新 Dify DSL：

- 收集 `DIFY_BASE_URL`、`ADMIN_API_KEY`、`WORKSPACE_ID`、`APP_ID` 等必要参数。
- 先设计 DSL 方案，再生成或修改 DSL。
- 创建新应用并导入 DSL。
- 更新已有应用前导出备份。
- 导入后重新导出远端 DSL，验证变量、节点和输出。
- 提供常见节点参考：`start`、`end`、`answer`、`if-else`、`iteration`、`code`、`template-transform`、`parameter-extractor`、`llm`、`agent`、`http-request`、`tool`、`knowledge-retrieval`。

### `mindmap/mindmap-builder`

该 skill 适合把资料整理成 markmap 思维导图，并生成离线 HTML：

- 从 PDF、文本、笔记、大纲或工作流输出中提炼层级结构。
- 生成 markmap 友好的 Markdown。
- 使用 `markmap-cli` 生成可双击打开的 `.html` 文件。
- 携带 `d3`、`markmap-view`、`markmap-toolbar` 的本地 JS/CSS 资源。
- 通过 `scripts/render_offline_mindmap.ps1` 把 CDN 引用替换为本地 `markmap-assets/` 路径。
- 自动检查 `node`、`npm`、`markmap` 是否可用。
- 缺少 `markmap-cli` 时，在用户授权后使用 `npm install -g markmap-cli` 安装。
- 默认只生成离线 HTML，不依赖 FastAPI 服务、服务端预览接口或外部 CDN。

默认客户端流程不依赖服务端预览：

```text
PDF / 文本 / 大纲
        ↓
生成 markmap Markdown
        ↓
离线渲染脚本生成 HTML + markmap-assets/
        ↓
双击 HTML 或用浏览器打开
```

## 使用方式

把需要使用的 skill 目录安装或复制到 Codex/Claude 可发现的 skills 目录中，保持目录名与 `SKILL.md` frontmatter 的 `name` 一致：

```text
dify-dsl-app-builder/
  SKILL.md
  nodes-basic.md
  nodes-logic.md
  nodes-processing.md
  nodes-ai.md
  nodes-external.md

dify-console-admin-api/
  SKILL.md

mindmap-builder/
  SKILL.md
  agents/
    openai.yaml
  assets/
    markmap/
      d3.min.js
      markmap-view.js
      markmap-toolbar.js
      markmap-toolbar.css
  scripts/
    render_offline_mindmap.ps1
  references/
    mindmap-service.md
```

使用 DSL App Builder 处理涉及远程 Dify 创建或更新应用的任务时，应同时安装 `dify-console-admin-api`，因为前者会引用后者的 Admin API 流程。

使用 Mindmap Builder 生成本地 HTML 时，需要本机具备 Node.js、npm 和 markmap-cli。Skill 会按以下命令检查依赖：

```powershell
node --version
npm --version
markmap --version
```

如果缺少 `markmap-cli`，在用户授权后安装：

```powershell
npm install -g markmap-cli
```

生成离线 HTML：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\render_offline_mindmap.ps1 `
  -InputMarkdown .\input.md `
  -OutputHtml .\output.html
```

输出目录中会同时生成：

```text
output.html
markmap-assets/
  d3.min.js
  markmap-view.js
  markmap-toolbar.js
  markmap-toolbar.css
```

移动或分享 HTML 时，需要保留同级 `markmap-assets/` 目录。

## 安全注意事项

- 不要把 `ADMIN_API_KEY` 写入仓库文件、README、PR 描述或长期脚本。
- 导出 DSL 默认使用 `include_secret=false`。
- 覆盖更新应用前先导出旧 DSL 作为备份。
- Admin API 调用失败时先排查配置和服务状态；不要绕过 API 直接写数据库，除非用户明确授权。
- 通过 npm 安装依赖前应征得用户授权，避免未经确认的网络下载或全局环境修改。
- Mindmap Builder 当前按单机客户端方式生成离线 HTML 文件，不提供服务端托管或预览 URL。

## 扩展思路

Dify DSL App Builder 的组织方式可以扩展到任何“由自然语言需求生成 DSL 描述”的场景，例如 CI/CD pipeline、Kubernetes manifest、Terraform、API 网关路由、低代码平台配置、工作流编排、监控告警规则等。

通用模式可以拆成两类 skill：

- **DSL Builder skill**：负责把用户需求转换成结构化方案，再生成或更新 DSL 文件。
- **Platform API skill**：负责把 DSL 导入目标平台、覆盖更新已有资源、导出远端配置并做验证。

设计这类 skill 时建议保留同一条闭环：

- **参数收集**：明确目标平台地址、鉴权方式、资源 ID、操作类型和输出路径。
- **方案确认**：先描述 DSL 的资源类型、输入、步骤、依赖、输出和错误处理，再生成文件。
- **模板拆分**：把常用节点、资源块、字段 schema、边关系或连接规则拆到独立参考文件，按需读取。
- **安全边界**：避免把 token、secret、私钥、数据库密码写入仓库或最终回复。
- **变更保护**：覆盖更新前导出现有配置作为备份。
- **回读验证**：导入或部署后再从目标平台导出配置，检查关键变量、节点、资源和输出是否符合预期。
- **版本适配**：当平台 DSL schema 变化时，优先更新参考文件和验证规则，保持主 `SKILL.md` 精简稳定。

这套结构的关键不是绑定 Dify，而是把“需求理解 -> DSL 生成 -> 平台应用 -> 远端验证”做成可复用流程。只要目标系统支持声明式配置或可导入的 DSL，就可以按这个模式沉淀专用 skill。
