---
name: stock-analysis-system
description: Run or adapt a Python FastAPI stock analysis service for A-share, Hong Kong, U.S. stock, ETF, and LOF technical analysis using AKShare, pandas, and technical indicators. Use when the user asks to analyze an individual security by market and date range, start a local stock analysis API, inspect or extend the imported stock service, test market data retrieval, or produce technical-score based investment-analysis output.
---

# Stock Analysis System

## Overview

This skill wraps the imported `NanoAgentCode/stock` Python project as a reusable local stock-analysis service. It provides a FastAPI API that fetches market data, calculates technical indicators, scores the latest trend, and returns a structured analysis report.

The service is for research and learning workflows only. Do not present its output as personalized investment advice.

## Capabilities

- Analyze A-share, Hong Kong, U.S. stock, ETF, and LOF symbols.
- Fetch data through AKShare-based data sources.
- Calculate MA5/MA20/MA60, RSI, MACD, Bollinger bands, volume ratios, ATR, volatility, and ROC.
- Generate a 0-100 technical score and rule-based recommendation.
- Expose local FastAPI endpoints for health checks, market metadata, and stock analysis.

## Required Workflow

1. Clarify the target market and symbol.
   - Supported market values are `A`, `HK`, `US`, `ETF`, and `LOF`.
   - Ask for a date range only when the user needs a specific period; otherwise use the service defaults.

2. Read the implementation files before modifying behavior.
   - Use `scripts/app_modular.py` as the preferred service entrypoint.
   - Use `scripts/modules/stock_service.py` for data retrieval, indicator calculation, scoring, and report assembly.
   - Use `scripts/modules/config.py` for supported markets, scoring weights, API settings, and example tokens.
   - Treat `scripts/main_back.py` as the older monolithic implementation kept for reference.

3. Set up dependencies when running locally.
   - Prefer a virtual environment outside committed files.
   - Install dependencies from `scripts/requirements.txt` or `scripts/pyproject.toml`.
   - Some data-source libraries are network-dependent and may fail when providers change or block requests.

4. Start the local API from the skill script directory.

```powershell
cd .\market\stock-analysis-system\scripts
python -m uvicorn app_modular:app --host 0.0.0.0 --port 8000
```

Portable shell:

```bash
cd market/stock-analysis-system/scripts
python3 -m uvicorn app_modular:app --host 0.0.0.0 --port 8000
```

5. Call the API with an explicit market and symbol.

```http
POST /analyze-stock/
Authorization: Bearer xue123
Content-Type: application/json

{
  "stock_code": "AAPL",
  "market_type": "US"
}
```

Omit `start_date` and `end_date` for the default rolling recent-year window ending today. Pass explicit `YYYYMMDD` values only when the user needs a historical backtest period.

6. Validate results.
   - Check `/health` first when diagnosing service startup.
   - Check `/markets` to confirm supported market metadata.
   - Use `scripts/test_us_markets.py` for U.S. market smoke tests and `scripts/test_markets.py` for multi-market checks.
   - If live data retrieval fails, report the exact provider error and whether the failure is code, dependency, network, symbol, or provider related.

## Configuration And Security

- The imported project includes example tokens in `scripts/modules/config.py` for local testing. Replace them before using the API in any shared environment.
- Do not commit real API keys or private credentials. If a future data source needs credentials, store them in a local ignored config file and document a `config.example` file instead.
- The service enables broad CORS in the imported app for local development. Restrict allowed origins before deployment.

## Output

For one-off analysis, summarize the score, recommendation, latest price indicators, data source, and any data-quality limitation in the final response.

For generated files, write outputs under `output/stock-analysis-system/` unless the user specifies another path.

## Reference

The upstream README from `NanoAgentCode/stock.git` is preserved at [references/upstream-README.md](references/upstream-README.md).
