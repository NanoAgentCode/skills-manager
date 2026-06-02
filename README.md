# skills-manager

本仓库用于管理可复用的 Codex/Claude Skills。目前包含 Dify 相关的两个 skill，覆盖 Dify Console Admin API 自动化与 Dify DSL 应用构建。

## Dify Skills 检查结果

检查日期：2026-06-02

| Skill | 路径 | 功能完整性 | 校验结果 |
|---|---|---|---|
| Dify DSL App Builder | `dify/dify-dsl-app-builder` | 基本完整。支持从需求设计 DSL、生成 workflow/advanced-chat DSL、创建应用、覆盖更新、导入后导出验证，并提供常用节点模板。 | 已通过 `quick_validate.py` |
| Dify Console Admin API | `dify/dify-console-admin-api` | 基本完整。支持 admin key 鉴权说明、创建 workflow 应用、导出 DSL、从 YAML 内容或 URL 导入 DSL、覆盖导入、pending 导入确认和常见错误排查。 | 已通过 `quick_validate.py` |

已修复的问题：

- 移除 `dify-console-admin-api/SKILL.md` 中当前 skill 校验器不支持的 `disable-model-invocation` frontmatter 字段。
- 修正 `dify-dsl-app-builder/SKILL.md` 中指向 Admin API skill 的路径，从 `skills/dify-console-admin-api/SKILL.md` 改为当前仓库实际路径 `dify/dify-console-admin-api/SKILL.md`。

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

## 后续可增强项

- 为两个 skill 增加 `agents/openai.yaml`，改善在 UI 列表中的展示名称、短描述和默认提示。
- 增加示例 DSL 或测试 fixture，用于真实导入/导出回归验证。
- 若 Dify 版本升级导致 DSL schema 变化，优先补充节点参考文件，而不是把大量模板堆进 `SKILL.md`。
