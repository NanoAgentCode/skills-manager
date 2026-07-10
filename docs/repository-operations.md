# Repository Operations

This guide contains shared installation, invocation, validation, output, and security conventions. Skill-specific workflows remain in each `SKILL.md`.

## Use A Skill

1. Choose the closest business scenario in `docs/skill-index.md`.
2. Read the selected `SKILL.md` completely.
3. Use bundled scripts for repeatable operations.
4. Keep generated artifacts under `output/<skill-name>/` unless the user supplies another path.

Example:

```text
Read AGENTS.md, then read skills/content-operations/wechat-format/SKILL.md, and format this article for WeChat.
```

## Windows Python Launcher

Do not assume `python` or `py` is available on `PATH`. From the repository root, use:

```powershell
.\scripts\run-python.ps1 <script-path> [arguments]
```

The launcher checks configured runtimes, repository environments, the Windows registry, and common installation paths. It reports a clear prerequisite error when no interpreter is available.

## Repository Validation

Lint every skill and the compatibility entrypoints:

```powershell
.\scripts\run-python.ps1 .\skills\skill-governance\skill-linter\scripts\lint_skill.py . --repo-root .
```

Run the skill-linter unit tests:

```powershell
.\scripts\run-python.ps1 -m unittest discover -s .\skills\skill-governance\skill-linter\tests -v
```

Run the dependency-free Dify structure checks:

```powershell
.\scripts\run-python.ps1 .\skills\ai-application-delivery\quick_validate.py
```

## Outputs

- Default generated artifacts belong under the repository-level `output/` directory.
- Use a skill-specific subdirectory such as `output/wechat-format/` or `output/mindmap-builder/`.
- Keep temporary files, local configs, downloaded dependencies, and generated previews ignored.
- Do not create default output directories inside a skill folder.

## Security

- Never commit real API keys, tokens, passwords, cookies, private endpoints, or account credentials.
- Use `config.example.json` for documentation and ignored `config.json` files for local values.
- Database operations are read-only by default; writes and DDL require explicit authorization.
- Export Dify DSL with `include_secret=false` unless the user explicitly requires otherwise.
- Request approval before installing packages, downloading models, or using browser session state.

## Maintenance Checklist

When adding or moving a skill:

1. Keep the folder name equal to the `SKILL.md` frontmatter `name`.
2. Update `docs/skill-index.md` and affected documentation.
3. Check repository-relative commands and hard-coded parent-directory depth.
4. Run the repository linter and relevant smoke tests.
5. Confirm generated or local files remain ignored.
