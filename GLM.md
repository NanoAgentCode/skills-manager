# GLM Compatibility Entry

Use this repository as a skills library.

GLM may not auto-discover `SKILL.md` files. If no automatic skill mechanism is available, manually follow this process:

1. Read `AGENTS.md`.
2. Pick the matching skill from the Skill Index.
3. Read the selected `SKILL.md` completely.
4. Use bundled scripts and referenced files as instructed by that skill.
5. Report which skill was used and what verification was run.

Recommended direct prompt:

```text
请先阅读 AGENTS.md，再阅读 <skill-path>/SKILL.md，并严格按该 skill 的流程完成任务。
```

Treat `agents/openai.yaml` as optional Codex metadata.
