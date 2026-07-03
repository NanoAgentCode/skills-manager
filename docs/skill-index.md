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
- `wechat/`: WeChat article formatting, cover generation, and authorized archive workflows.
- `writing/`: Chinese technical article polishing.
- `database/`: safe Python database querying with local ignored configs.
- `debugging/`: backend log-to-contract tracing.
- `quality/`: skill linting and release checks.
- `superpowers/`: upstream software-development process skills.
