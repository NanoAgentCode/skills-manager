---
name: obsidian-memory
description: 将本地 Obsidian Vault 作为 Codex 可检索、可审核、可视化的中文外部长期记忆系统。Use when 用户要求接入或使用 Obsidian 外部记忆、任务开始前检索项目背景、历史决策、稳定知识和用户偏好，任务结束后提取候选记忆，处理记忆冲突、过期和替代关系，或维护 Vault 记忆索引；适用于 Markdown 笔记、Obsidian 双向链接和本地文件型知识库，不用于保存密码、令牌等敏感信息。
---

# Obsidian 外部记忆

将 Obsidian Vault 视为用户可检查的长期记忆源。默认 Vault 为 `D:\WorkSpace\AgentVault`；用户指定其他路径时，以用户路径为准。

## 工作流程

1. 确认 Vault 路径存在。
2. 读取 Vault 根目录的 `AGENTS.md`、`90-System/Memory-Rules.md` 和 `90-System/Codex-Memory-Index.md`。
3. 从当前任务提取 2 到 5 个关键词，运行 `scripts/search-memory.ps1`。只读取命中的少量相关笔记，不遍历整个 Vault。
4. 仅采用与当前任务相关、状态有效且来源清楚的记忆。用户当前指令始终优先于历史记忆。
5. 完成用户任务。
6. 判断是否出现值得长期保存的信息。只有稳定偏好、重要决策、可复用知识、项目长期背景或已验证方案才进入候选记忆。
7. 按 `references/memory-schema.md` 和 Vault 中的模板写入 `00-Inbox/Codex/`。除非用户明确要求，不要直接写入正式记忆目录。
8. 用户确认并将候选记忆归档后，运行 `scripts/rebuild-index.ps1` 更新索引。

## 检索记忆

从仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\knowledge-visualization\obsidian-memory\scripts\search-memory.ps1 `
  -Query "检索词" -VaultPath "D:\WorkSpace\AgentVault"
```

需要限制范围时，传入 `-Scope "30-Decisions"`。检索结果只用于定位文件；读取后还要检查 `scope`、`status`、`source` 和适用场景。

## 写入候选记忆

- 文件名使用 `YYYY-MM-DD-简短主题.md`，同日重名时增加两位序号。
- 使用 `Templates/长期记忆模板.md`，内容使用中文。
- 写明摘要、适用场景、不适用场景、证据来源和关联笔记。
- 不保存密码、令牌、身份证号、银行卡号、私钥、Cookie 或未脱敏的个人敏感信息。
- 不把一次性任务步骤、临时错误、未经验证的推测保存为长期记忆。

## 处理冲突和过期

- 当前事实与旧记忆冲突时，不静默覆盖。
- 新建或更新正确记忆，将旧记忆的 `status` 改为 `superseded`，并填写 `superseded_by`。
- 暂时无法确认的内容使用 `uncertain`，已过时但没有替代项的内容使用 `stale`。
- 只有 `status: active` 且来源可信的记忆可以直接作为当前任务依据。

## 重建索引

候选记忆被人工归档后运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\knowledge-visualization\obsidian-memory\scripts\rebuild-index.ps1 `
  -VaultPath "D:\WorkSpace\AgentVault"
```

脚本只索引正式目录，不索引 `00-Inbox/Codex/`。

## 资源

- `scripts/search-memory.ps1`：按关键词搜索中文 Markdown 记忆。
- `scripts/rebuild-index.ps1`：根据正式记忆目录重建 Obsidian 双向链接索引。
- `references/memory-schema.md`：记忆分类、字段和生命周期规范。
