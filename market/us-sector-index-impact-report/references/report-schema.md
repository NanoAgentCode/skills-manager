# Report JSON Schema

Build a JSON object with these top-level fields before calling the renderer.

```json
{
  "title": "2026-07-02 U.S. sector moves and China market impact",
  "subtitle": "Investment-bank style morning report",
  "session_date": "2026-07-02",
  "generated_at": "2026-07-03 09:30 CST",
  "analyst": "Codex",
  "house_view": "Risk appetite improved, but China read-through is concentrated in AI hardware and platform beta.",
  "executive_summary": [
    "Nasdaq Composite rose 0.0%, while Nasdaq 100 rose 0.0%; technology leadership remained narrow.",
    "Semiconductors led U.S. industries; energy lagged on weaker crude."
  ],
  "indices": [
    {
      "name": "Nasdaq Composite",
      "ticker": "IXIC",
      "close": "0.00",
      "change_points": "+0.00",
      "change_pct": "+0.00%",
      "note": "Official close"
    }
  ],
  "sectors": [
    {
      "rank": 1,
      "name": "Semiconductors",
      "ticker": "SOX",
      "close": "0.00",
      "change_points": "+0.00",
      "change_pct": "+0.00%",
      "interpretation": "AI compute demand and earnings revisions supported the group."
    }
  ],
  "core_factors": [
    {
      "factor": "AI capital expenditure",
      "direction": "Positive",
      "evidence": "Hyperscaler capex guidance and AI infrastructure orders supported semiconductor and networking names.",
      "market_impact": "Supports AI hardware, optical networking and power/cooling supply chains; raises valuation and FCF scrutiny."
    }
  ],
  "ai_capex_analysis": [
    {
      "heading": "Capex visibility",
      "body": "Assess whether U.S. hyperscaler capex is accelerating, stable, or showing digestion risk, and connect it to semiconductors, AI servers, networking, power, cooling and cloud margins."
    }
  ],
  "geopolitics_dollar_gold": [
    {
      "heading": "Dollar policy and gold",
      "body": "Explain DXY, Treasury yields, Fed expectations, official dollar-policy signals if relevant, and global gold's session move."
    }
  ],
  "us_interpretation": [
    {
      "heading": "Technology leadership",
      "body": "Describe the price action and why it matters."
    }
  ],
  "hong_kong_impact": [
    {
      "sector": "Internet platforms",
      "direction": "Positive",
      "rationale": "U.S. megacap tech strength can lift platform sentiment, but earnings read-through is indirect.",
      "watchlist": "Hang Seng Tech, Tencent, Alibaba, Meituan"
    }
  ],
  "a_share_impact": [
    {
      "sector": "AI hardware",
      "direction": "Positive",
      "rationale": "Semiconductor and AI-server strength can support CPO, PCB, optical module and server supply-chain sentiment.",
      "watchlist": "CPO, PCB, AI servers, domestic semiconductor equipment"
    }
  ],
  "scenarios": [
    {
      "case": "Base",
      "probability": "50%",
      "view": "Asia tech beta improves, but market waits for local earnings and policy confirmation."
    }
  ],
  "sources": [
    {
      "label": "Nasdaq market activity",
      "url": "https://www.nasdaq.com/market-activity/index/comp",
      "used_for": "Nasdaq Composite close and change",
      "retrieved_at": "2026-07-03"
    }
  ]
}
```

Rules:

- Keep numeric display fields as strings when the source has signs, commas, percent symbols, or formatting that should appear unchanged.
- Use arrays even when a section has one item; this keeps the renderer deterministic.
- Omit optional fields only when the data is unavailable. Prefer `null` over invented values.
- Use Chinese prose in narrative fields unless the user asks for English.
- Always include `core_factors`, `ai_capex_analysis`, and `geopolitics_dollar_gold` for this skill. If the session was not AI-, geopolitics-, dollar-, or gold-driven, explain why the factor was not dominant.
