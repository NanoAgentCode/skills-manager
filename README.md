# skills-manager

本仓库用于管理可复用的 Codex/Claude Skills。目前包含 Dify 相关的两个 skill，覆盖 Dify Console Admin API 自动化与 Dify DSL 应用构建。


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
```

使用 DSL App Builder 处理涉及远程 Dify 创建或更新应用的任务时，应同时安装 `dify-console-admin-api`，因为前者会引用后者的 Admin API 流程。

## 安全注意事项

- 不要把 `ADMIN_API_KEY` 写入仓库文件、README、PR 描述或长期脚本。
- 导出 DSL 默认使用 `include_secret=false`。
- 覆盖更新应用前先导出旧 DSL 作为备份。
- Admin API 调用失败时先排查配置和服务状态；不要绕过 API 直接写数据库，除非用户明确授权。

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
