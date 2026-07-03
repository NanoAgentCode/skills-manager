# Skill Index

This document summarizes the reusable skills in this repository. Treat each `SKILL.md` as the source of truth.

## Market

### `market/us-sector-index-impact-report/SKILL.md`

Use this skill to analyze the most recent completed U.S. trading session and produce an investment-bank style HTML report for Hong Kong and A-share sector implications.

Core coverage:

- Nasdaq Composite and Nasdaq 100 performance.
- U.S. sector or industry-index gain/loss ranking.
- Core drivers behind the session: macro factors, earnings/fundamentals, valuation/positioning, policy and geopolitics.
- U.S. AI capital expenditure focus: hyperscaler capex, data-center buildout, GPU/ASIC, HBM, AI servers, optical networking/CPO, PCB, power and cooling.
- Hong Kong and A-share impact split into direct read-through, supply-chain/order read-through, and sentiment beta.
- Standalone HTML rendering through `scripts/render_investment_bank_html.py`.

Primary command:

```powershell
py .\market\us-sector-index-impact-report\scripts\render_investment_bank_html.py `
  --input .\report-data.json `
  --output .\us-sector-impact-report.html
```

## Other Categories

- `dify/`: Dify Console Admin API automation and DSL app building.
- `mindmap/`: offline markmap HTML generation and optional static publishing.
- `wechat/`: WeChat article production and authorized archive workflows.
  - `wechat/wechat-format/SKILL.md`: Markdown/plain-text/rough-note packaging into WeChat-compatible inline HTML through the repo-local `scripts/article_workflow.py` by default, including terminology polishing, structured/enhanced Markdown, a 26-theme gallery, final themed outputs, optional covers, and draft publishing.
  - `wechat/wechat-history-article-archive/SKILL.md`: self-owned or explicitly authorized historical mass-send article backup from lawful `mp.weixin.qq.com/s?...` URL sources, with URL normalization, batch archiving, Markdown/metadata/index/image outputs by default, and optional follow-up into `wechat-format` for reformatting or migration.
  - `wechat/wechat-format/wechat-cover/SKILL.md`: cover-image generation for WeChat articles.
- `writing/`: Chinese technical article polishing.
- `database/`: safe Python database querying with local ignored configs.
- `debugging/`: backend log-to-contract tracing.
- `quality/`: skill linting and release checks.
- `superpowers/`: upstream software-development process skills.
