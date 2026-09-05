# Skill Routing And Delivery Acceptance Scenarios

Use these scenarios after changes that affect a skill's trigger, handoff, or final artifact. For each, select the named skill from `docs/skill-index.md`, read its `SKILL.md`, and verify the listed observable result.

| User request | Expected skill | Observable result |
|---|---|---|
| “把这份技术报告写成有出处的中文公众号文章。” | `technical-source-to-public-article` | Markdown article plus source/claim notes. |
| “把一段会议录音转成带时间戳的纪要。” | `video-transcriber` | A non-empty transcript with source route recorded. |
| “把这个 Markdown 做成可双击打开的思维导图。” | `mindmap-builder` | HTML plus sibling `markmap-assets/`, without external CDN links. |
| “我只想生成一个 Dify DSL，暂时没有管理员权限。” | `dify-dsl-app-builder` | Local DSL and static validation, without collecting remote credentials. |
| “查一下库里有哪些表，不要改数据。” | `python-db-query` | Metadata output through a read-only path. |
| “把已有技术文章排成微信公众号 HTML。” | `wechat-format` | Final manifest and preview/article HTML. |

Record failures as one of: incorrect routing, missing input contract, missing output artifact, unsafe default, or unverifiable completion. Keep individual scenario fixtures small and free of credentials or user data.
