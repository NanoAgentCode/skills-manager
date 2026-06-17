# Claude Compatibility Entry

Use this repository as a skills library.

Before acting on a task that matches a skill, read `AGENTS.md`, choose the matching `SKILL.md`, then read that `SKILL.md` completely and follow it.

The canonical skill format is:

```text
skill-folder/
  SKILL.md
  scripts/
  references/
  assets/
  agents/openai.yaml
```

`agents/openai.yaml` is Codex/OpenAI UI metadata. Claude can ignore it unless the user asks about cross-platform compatibility.

For direct invocation, support prompts like:

```text
Use the skill at wechat/wechat-format/SKILL.md for this article.
Read quality/skill-linter/SKILL.md and lint this skill.
```

Preserve the behavior in each selected `SKILL.md`; do not replace it with generic advice.
