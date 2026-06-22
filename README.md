# skills-manager

## Recently Added Skills

### `debugging/backend-log-contract-trace`

Trace backend logs to the exact code path and contract boundary.

- Follow failures from route/controller to service, mapper interface/XML, SQL, and database constraints.
- Check API parameters, DTO/VO fields, entity fields, SQL column names, and cross-service payload names.
- Re-open current files before and after edits to avoid stale-memory conclusions.

### `wechat/wechat-history-article-archive`

Archive historical mass-send articles for a WeChat official account the user owns or is explicitly authorized to operate.

- Collect or normalize `mp.weixin.qq.com/s?...` article URLs from lawful sources.
- Save local HTML and metadata backups in batch.
- Use this before migration, reformatting, or long-term archival of historical article content.

本仓库用于管理可复用的 AI agent skills。目前包含 Dify、Mindmap、WeChat、Writing、Database、Debugging、Quality 和 Superpowers 八类 skill，并提供 Codex、Claude、Gemini、GLM、DeepSeek 的兼容入口。

- Dify：覆盖 Dify Console Admin API 自动化与 Dify DSL 应用构建。
- Mindmap：把 PDF、文本、大纲或文档内容转换为离线可双击打开的思维导图 HTML；支持长文档默认总览、章节按需展开和对话式展开；仅在用户明确要求发布时，将静态产物发布到配置好的 Web 静态目录。
- WeChat：把 Markdown、纯文本或粗糙笔记排版成微信公众号兼容 HTML，可选生成封面并推送到公众号草稿箱。
- Writing：润色中文技术文章或机器翻译稿，结合上下文检查专业术语准确性，并输出术语修改记录。
- Database：通过 Python 脚本执行数据库查询，连接配置单独存放到本地配置文件；缺少配置时通过对话收集必要字段。
- Debugging：从后端日志一路追到接口参数、DTO/VO、实体字段、MyBatis XML、SQL 列名、跨服务参数和数据库约束。
- Quality：检查 skill 结构、触发描述、资源引用、UI 元数据、多模型入口、敏感信息和 README 同步状态。
- Superpowers：从 `obra/superpowers` 同步的软件开发方法论技能集，覆盖 brainstorm、计划编写、TDD、代码审查、并行子代理和工作树流程。

## 多模型兼容

本仓库的能力本体是每个目录中的 `SKILL.md`。不同模型或客户端的差异主要在于是否能自动发现和触发 skill；只要模型能读取 `SKILL.md` 和相关资源，就可以按同一套流程执行。

| 模型/客户端 | 兼容入口 | 说明 |
|---|---|---|
| Codex | `SKILL.md` + `agents/openai.yaml` + `AGENTS.md` | `agents/openai.yaml` 用于 Codex/OpenAI UI 元数据。 |
| Claude / Claude Code | `CLAUDE.md` + `SKILL.md` | Claude 可直接读取 `SKILL.md`；`CLAUDE.md` 提供仓库级入口。 |
| Gemini | `GEMINI.md` + `SKILL.md` | `GEMINI.md` 引导 Gemini 先读技能索引，再读目标 skill。 |
| GLM | `GLM.md` + `SKILL.md` | GLM 未必自动发现 skill，建议显式要求读取入口文件和目标 `SKILL.md`。 |
| DeepSeek | `DEEPSEEK.md` + `SKILL.md` | DeepSeek 未必自动发现 skill，建议显式要求读取入口文件和目标 `SKILL.md`。 |

通用调用方式：

```text
请先阅读 AGENTS.md，再阅读 <skill-path>/SKILL.md，并严格按该 skill 的流程完成任务。
```

示例：

```text
请先阅读 AGENTS.md，再阅读 wechat/wechat-format/SKILL.md，把这篇文章排版成公众号 HTML。
```

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
- 提供专门的 [DSL 导入规则参考](dify/dify-dsl-app-builder/dsl-import-rules.md)，说明 edge 连接、迭代内部连接和通用 DSL builder 模式。

### `mindmap/mindmap-builder`

该 skill 适合把资料整理成 markmap 思维导图，并生成离线 HTML：

- 从 PDF、文本、笔记、大纲或工作流输出中提炼层级结构。
- 生成 markmap 友好的 Markdown。
- 对书籍、长报告、长论文、手册或研究资料包，支持“先生成总览图，再按用户选择展开章节/小节”的长文档模式。
- 用户明确要求“总览图”“默认只展示总览”“用户可选章节”“章节展开”“对话式展开”“按需展开”时，直接进入长文档模式。
- 论文默认规则：25 页以内优先生成单张论文总览图；25 页以上默认生成 `overview + section-index + sections/` 的长文档结构。
- 文本量默认规则：英文约 20,000 words 以内、中文约 30,000 characters 以内优先单张总览；超过该范围且具有文档结构时，默认使用长文档模式。
- 长文档模式要求 `overview.md`、`section-index.md` 和章节展开图使用同一套章节/小节标签，避免总览节点和展开节点对不上。
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

长文档默认流程：

```text
PDF / 论文 / 书籍 / 长报告
        ↓
抽取目录、章节、小节和关键主题
        ↓
生成 section-index.md
        ↓
生成 overview.md / overview.html
        ↓
用户选择章节或小节
        ↓
生成 sections/{section-slug}.md / .html
```

示例输出结构：

```text
overview.md
overview.html
section-index.md
sections/
  section-05-cow-bench.md
  section-05-cow-bench.html
markmap-assets/
```

### `mindmap/mindmap-publisher`

该 skill 只在用户明确要求“发布、部署、托管、暴露、生成服务器预览 URL”时使用。它不会参与普通本地思维导图生成。

发布输入必须包含：

- `SourceHtml`：已生成的离线思维导图 HTML。
- `StaticRoot`：服务器静态资源目录。
- `PublicBaseUrl`：公网域名或访问源。
- `PathPrefix`：强制要求的 URL 路径前缀，例如 `/mindmaps`。
- `Slug`：发布目录名。

发布结果：

```text
{StaticRoot}/{Slug}/index.html
{StaticRoot}/{Slug}/markmap-assets/...
{PublicBaseUrl}{PathPrefix}/{Slug}/index.html
```

注意：`PathPrefix` 不能省略，不能是 `/`，也不能由 skill 猜测。

### `wechat/wechat-format`

该 skill 适合完成微信公众号内容生产流程：

- 将 Markdown、纯文本或格式粗糙的笔记转换为微信公众号兼容的内联样式 HTML。
- 提供 30 个排版主题，并支持浏览器画廊预览主题效果。
- 自动识别访谈对话、重点引用、图片序列等内容结构，并增强排版。
- 技术文章会先按 `writing/technical-article-polisher` 做术语和语境质量检查，并保留术语修改记录。
- 可选生成公众号封面图。
- 可选上传图片到微信 CDN，并把文章推送到公众号草稿箱。

纯排版只需要本地 Python 依赖；没有 `config.json` 时会使用内置默认配置，并把产物写入 `wechat/wechat-format/.tmp/`。推送草稿箱时需要在 `config.json` 中配置公众号 `app_id`、`app_secret` 和作者信息。`config.json` 已由该 skill 自带的 `.gitignore` 忽略，不应提交到仓库。

### `writing/technical-article-polisher`

该 skill 适合对中文技术文章、机器翻译稿、AI/工程/架构类文章做专业润色，可用于技术博客、公众号文章、产品技术稿、文档、报告或发布前审校：

- 结合文章上下文判断关键专业术语是否准确。
- 检查机器翻译导致的误译、直译、术语不一致和概念混淆。
- 保留作者原意，不把技术判断改写成泛泛的产品话术。
- 输出润色后的 Markdown 文章。
- 最后列出术语修改记录和不确定术语。

### `database/python-db-query`

该 skill 适合通过 Python 执行数据库查询：

- 使用本地 `config.json` 管理数据库连接信息，仓库只提交 `config.example.json`。
- 没有配置文件时，先通过对话收集数据库类型、地址、库名、账号和密码等必要字段。
- 默认只允许只读 SQL；写入、DDL 或删除类操作需要用户明确授权后才使用 `--allow-write`。
- 支持 SQLite 内置连接；PostgreSQL、MySQL、SQL Server、Oracle 11g、MongoDB 和 Redis 依赖相应 Python 驱动。
- 支持表格、JSON、CSV 输出，并可导出查询结果到文件。

### `debugging/backend-log-contract-trace`

该 skill 适合排查 ToolFlow/app-model 这类后端日志到代码路径的问题：

- 从日志里的接口路径、异常类、SQL 片段、堆栈类名或错误码定位 controller/service/mapper。
- 核对接口参数、DTO/VO、实体字段、枚举/编码、MyBatis XML、SQL 列名和数据库约束。
- 排查跨服务参数契约，例如字段名、文件名、模型编码、下载参数和响应字段不一致。
- 修改前后都重新打开当前文件确认，避免基于旧记忆判断修复是否存在或是否被回滚。

### `quality/skill-linter`

该 skill 适合在创建、修改、评审或发布 skill 前做结构和质量检查：

- 检查 `SKILL.md` frontmatter 是否存在、字段是否完整、`name` 是否符合 hyphen-case 并匹配目录名。
- 检查 `description` 是否还残留模板文本、是否足够具体、是否包含明确触发/使用场景。
- 检查正文是否仍有 TODO 模板、相对 Markdown 链接和 `scripts/`、`references/`、`assets/` 引用是否能解析。
- 检查 `agents/openai.yaml` 是否存在，且 `default_prompt` 是否包含 `$skill-name`。
- 传入 `--repo-root` 时，检查仓库级 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`GLM.md`、`DEEPSEEK.md` 是否存在，并确认入口文件仍覆盖多模型兼容面、引导用户读取目标 `SKILL.md`。
- 扫描可能误提交的 `config.json`、API key、token、password 等敏感信息。
- 传入 `--repo-root` 时，检查仓库 README 是否提到该 skill 名称或路径。
- 支持单个 skill 检查，也支持扫描仓库内所有 `SKILL.md`。

示例：

```powershell
python .\quality\skill-linter\scripts\lint_skill.py .\quality\skill-linter --repo-root .
python .\quality\skill-linter\scripts\lint_skill.py . --repo-root .
python .\quality\skill-linter\scripts\lint_skill.py . --repo-root . --json
```

### `superpowers/superpowers`

该目录从 [obra/superpowers](https://github.com/obra/superpowers) 同步，包含一组面向 coding agent 的开发流程技能：

- `brainstorming`：写代码前进行苏格拉底式需求澄清和方案讨论。
- `writing-plans`：把已确认设计拆成可执行的小任务计划。
- `test-driven-development`：强调 red/green/refactor 的 TDD 流程。
- `subagent-driven-development`：用子代理逐任务实现并进行两阶段 review。
- `requesting-code-review` / `receiving-code-review`：代码审查与反馈处理。
- `using-git-worktrees`：为并行开发创建隔离工作树。
- `systematic-debugging`：系统化调试和根因分析。

该目录保留上游插件元数据（如 `.codex-plugin`、`.claude-plugin`），但不包含上游 `.git` 目录。

目录中几个关键层级的含义：

- `skills/`：真正的技能内容，每个子目录通常包含一个 `SKILL.md`，定义触发场景、执行流程和附加资源。
- `.codex-plugin/`：Codex 插件入口，描述插件名称、版本、展示信息，并指向 `skills/` 目录。
- `.claude-plugin/`：Claude Code 插件入口，描述 Claude 插件市场所需的名称、版本、作者和仓库信息。
- `hooks/`：生命周期钩子，用于在会话启动、清空或压缩等时机自动执行初始化或提醒逻辑。
- `docs/`、`tests/`、`assets/`：分别保存上游文档、测试和图标等辅助资源。

因此，`skills/` 是能力本体；`.codex-plugin/` 和 `.claude-plugin/` 是不同平台的安装包装；`hooks/` 是自动触发机制。

## 使用方式

把需要使用的 skill 目录安装或复制到目标 agent 可发现的 skills 目录中；如果目标 agent 没有自动发现机制，则在提示词中显式要求先读 `AGENTS.md` 和目标 `SKILL.md`。安装目录应保持目录名与 `SKILL.md` frontmatter 的 `name` 一致：

```text
dify-dsl-app-builder/
  SKILL.md
  agents/
    openai.yaml
  nodes-basic.md
  nodes-logic.md
  nodes-processing.md
  nodes-ai.md
  nodes-external.md
  dsl-import-rules.md

dify-console-admin-api/
  SKILL.md
  agents/
    openai.yaml

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

mindmap-publisher/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    publish_mindmap.ps1
  references/
    nginx-static-publish.md

wechat-format/
  SKILL.md
  README.md
  README_CN.md
  config.example.json
  scripts/
    check_dependencies.py
    format.py
    publish.py
    comment_reply.py
    generate.py
  themes/
  templates/
  wechat-cover/

python-db-query/
  SKILL.md
  config.example.json
  agents/
    openai.yaml
  scripts/
    check_dependencies.py
    init_config.py
    install_offline_dependencies.ps1
    query_db.py
  references/
    config.md

backend-log-contract-trace/
  SKILL.md
  agents/
    openai.yaml

skill-linter/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    lint_skill.py

superpowers/
  superpowers/
    README.md
    .codex-plugin/
    .claude-plugin/
    hooks/
    skills/
      brainstorming/
      writing-plans/
      test-driven-development/
      subagent-driven-development/
      ...
```

使用 DSL App Builder 处理涉及远程 Dify 创建或更新应用的任务时，应同时安装 `dify-console-admin-api`，因为前者会引用后者的 Admin API 流程。

### 快速校验

`quality/skill-linter` 可用于检查单个 skill 或整个仓库的 skill 质量：

```powershell
python .\quality\skill-linter\scripts\lint_skill.py .\quality\skill-linter --repo-root .
python .\quality\skill-linter\scripts\lint_skill.py . --repo-root .
```

`dify/` 目录下提供一个无外部服务依赖的快速校验脚本，用于确认当前两个 Dify skill 的基本结构和关键引用仍然可用：

```powershell
python .\dify\quick_validate.py
```

该脚本会检查：

- `dify-console-admin-api` 和 `dify-dsl-app-builder` 的 `SKILL.md` frontmatter。
- DSL App Builder 引用的节点模板、DSL 导入规则和 Console Admin API skill 是否存在。
- README 中列出的 Dify 路径是否能在仓库中解析。
- `dify/context-json-validator-workflow.yml` 是否具备 Dify app/workflow 的基本结构，且在安装了 PyYAML 时会进一步检查节点 ID 与 edge 引用。

脚本只做本地静态校验，不会调用 Dify 服务，也不会读取或输出 `ADMIN_API_KEY`。

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
- 不要把数据库密码、连接串或真实 `config.json` 提交到仓库；数据库查询 skill 已通过 `.gitignore` 忽略本地配置。
- 数据库查询默认只执行只读 SQL；任何写操作、DDL 或大范围扫描都应先获得用户明确确认。
- 导出 DSL 默认使用 `include_secret=false`。
- 覆盖更新应用前先导出旧 DSL 作为备份。
- Admin API 调用失败时先排查配置和服务状态；不要绕过 API 直接写数据库，除非用户明确授权。
- 通过 npm 安装依赖前应征得用户授权，避免未经确认的网络下载或全局环境修改。
- Mindmap Builder 当前按单机客户端方式生成离线 HTML 文件，不提供服务端托管或预览 URL。
- Mindmap Publisher 只负责把已生成的静态产物复制到用户指定的静态目录，并根据用户提供的 `PublicBaseUrl` 与 `PathPrefix` 计算访问 URL；它不会自动修改 Nginx 配置。

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
