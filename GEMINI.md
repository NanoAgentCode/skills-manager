# Gemini Compatibility Entry

Use this repository as a skills library.

Start by reading `AGENTS.md` for the skill index and shared rules. When the user request matches a skill, read the selected `SKILL.md` completely before acting.

Recommended direct prompt:

```text
Read AGENTS.md, then read <skill-path>/SKILL.md, and follow that skill for this task.
```

Notes for Gemini:

- `SKILL.md` is the source of truth.
- `agents/openai.yaml` is Codex UI metadata and can usually be ignored.
- If a skill references scripts, inspect the script arguments before running them.
- If a skill uses PowerShell examples and the current environment is not Windows, translate commands to the local shell while preserving behavior.

@./AGENTS.md
