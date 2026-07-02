# Skills Manager Agent Guide

This repository is a reusable skills library. Treat each `SKILL.md` as the source of truth for one skill, regardless of model provider.

## How To Use A Skill

1. Identify the user request and choose the closest skill by reading the index below.
2. Open that skill's `SKILL.md` completely before acting.
3. Follow the workflow in `SKILL.md`.
4. Load linked files under `scripts/`, `references/`, `assets/`, or templates only when the skill says they are needed.
5. Prefer bundled scripts for repeatable or fragile operations.
6. Do not expose secrets from local config files. Use `config.example.json` for examples and keep real `config.json` values private.
7. If a platform cannot auto-discover skills, the user can invoke a skill by saying: `Read <skill-path>/SKILL.md and follow it for this task.`

## Skill Index

- `dify/dify-console-admin-api/SKILL.md`: automate Dify Console Admin API app creation, DSL export/import, overwrite import, and import confirmation.
- `dify/dify-dsl-app-builder/SKILL.md`: design, generate, update, import, and verify Dify workflow or advanced-chat DSL.
- `mindmap/mindmap-builder/SKILL.md`: convert PDFs, notes, outlines, papers, reports, or books into offline markmap HTML; supports overview-first long document mode.
- `mindmap/mindmap-publisher/SKILL.md`: publish an already generated offline mindmap HTML folder to a static hosting path and return a URL.
- `wechat/wechat-format/SKILL.md`: format Markdown, plain text, or rough notes into WeChat official-account compatible HTML; optionally generate covers and publish drafts.
- `wechat/wechat-history-article-archive/SKILL.md`: archive self-owned WeChat historical mass-send article URLs and save local HTML/metadata backups from lawful link sources.
- `wechat/wechat-format/wechat-cover/SKILL.md`: generate a WeChat article cover from an article path or topic.
- `writing/technical-article-polisher/SKILL.md`: polish technical Chinese articles or machine-translated drafts by checking terminology accuracy in context and reporting terminology changes.
- `database/python-db-query/SKILL.md`: run safe Python database queries using local ignored config files.
- `debugging/backend-log-contract-trace/SKILL.md`: trace backend logs through API parameters, DTO/VOs, services, MyBatis XML, SQL columns, cross-service parameters, and database constraints; includes a concrete example in the recommended output shape.
- `quality/skill-linter/SKILL.md`: lint skill structure, trigger descriptions, references, metadata, README sync, and secret hygiene.
- `superpowers/superpowers/skills/*/SKILL.md`: upstream software-development process skills for brainstorming, planning, TDD, reviews, debugging, and worktrees.

## Platform Notes

- Codex: use `SKILL.md` plus optional `agents/openai.yaml` UI metadata.
- Claude: use the same `SKILL.md` workflow; `CLAUDE.md` is a compatibility entrypoint.
- Gemini: use `GEMINI.md` as the entrypoint, then read the selected `SKILL.md`.
- GLM: use `GLM.md` as the entrypoint, then read the selected `SKILL.md`.
- DeepSeek: use `DEEPSEEK.md` as the entrypoint, then read the selected `SKILL.md`.

## Portability Rules

- Keep skill names lowercase hyphen-case and match the skill folder name where possible.
- Keep platform-specific metadata outside `SKILL.md`; prefer `agents/openai.yaml`, `CLAUDE.md`, `GEMINI.md`, `GLM.md`, or `DEEPSEEK.md`.
- Include both PowerShell and portable command examples when adding new scripts.
- When a command is Windows-only, say so in the skill body.
- Do not assume a platform has Codex-specific tools, MCP servers, or browser automation unless the current environment exposes them.
