#!/usr/bin/env python3
"""Render a standalone investment-bank style HTML report from JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def pct_class(value: Any) -> str:
    text = str(value or "").strip()
    if text.startswith("-"):
        return "neg"
    if text.startswith("+") or (text and text[0].isdigit() and text not in {"0", "0.0", "0.00", "0%"}):
        return "pos"
    return "flat"


def render_summary(items: list[Any]) -> str:
    cards = []
    for index, item in enumerate(items, start=1):
        cards.append(
            f"""
            <article class="summary-card">
              <span>{index:02d}</span>
              <p>{esc(item)}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_indices(indices: list[dict[str, Any]]) -> str:
    cards = []
    for item in indices:
        cls = pct_class(item.get("change_pct"))
        cards.append(
            f"""
            <article class="metric">
              <div class="metric-label">{esc(item.get("name"))}</div>
              <div class="metric-ticker">{esc(item.get("ticker"))}</div>
              <div class="metric-close">{esc(item.get("close"))}</div>
              <div class="metric-change {cls}">{esc(item.get("change_points"))} / {esc(item.get("change_pct"))}</div>
              <p>{esc(item.get("note"))}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_sector_rows(sectors: list[dict[str, Any]]) -> str:
    rows = []
    for item in sectors:
        cls = pct_class(item.get("change_pct"))
        rows.append(
            f"""
            <tr>
              <td>{esc(item.get("rank"))}</td>
              <td><strong>{esc(item.get("name"))}</strong><span>{esc(item.get("ticker"))}</span></td>
              <td>{esc(item.get("close"))}</td>
              <td>{esc(item.get("change_points"))}</td>
              <td class="{cls}">{esc(item.get("change_pct"))}</td>
              <td>{esc(item.get("interpretation"))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_sector_cards(sectors: list[dict[str, Any]]) -> str:
    cards = []
    for item in sectors:
        cls = pct_class(item.get("change_pct"))
        cards.append(
            f"""
            <article class="sector-card {cls}">
              <div class="rank-pill">#{esc(item.get("rank"))}</div>
              <h3>{esc(item.get("name"))}</h3>
              <div class="ticker-line">{esc(item.get("ticker"))}</div>
              <div class="sector-change {cls}">{esc(item.get("change_pct"))}</div>
              <p>{esc(item.get("interpretation"))}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_text_blocks(items: list[dict[str, Any]]) -> str:
    blocks = []
    for item in items:
        blocks.append(
            f"""
            <article class="note">
              <div class="card-kicker">Analyst Note</div>
              <h3>{esc(item.get("heading"))}</h3>
              <p>{esc(item.get("body"))}</p>
            </article>
            """
        )
    return "\n".join(blocks)


def render_factor_rows(factors: list[dict[str, Any]]) -> str:
    rows = []
    for item in factors:
        direction = str(item.get("direction") or "Neutral").lower()
        rows.append(
            f"""
            <tr>
              <td><strong>{esc(item.get("factor"))}</strong></td>
              <td><span class="badge {esc(direction)}">{esc(item.get("direction"))}</span></td>
              <td>{esc(item.get("evidence"))}</td>
              <td>{esc(item.get("market_impact"))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_factor_cards(factors: list[dict[str, Any]]) -> str:
    cards = []
    for item in factors:
        direction = str(item.get("direction") or "Neutral").lower()
        cards.append(
            f"""
            <article class="factor-card">
              <div class="factor-head">
                <h3>{esc(item.get("factor"))}</h3>
                <span class="badge {esc(direction)}">{esc(item.get("direction"))}</span>
              </div>
              <div class="mini-label">Evidence</div>
              <p class="factor-evidence">{esc(item.get("evidence"))}</p>
              <div class="mini-label impact-label">Implication</div>
              <p class="factor-impact">{esc(item.get("market_impact"))}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_impact_cards(items: list[dict[str, Any]]) -> str:
    cards = []
    for item in items:
        direction = str(item.get("direction") or "Neutral").lower()
        cards.append(
            f"""
            <article class="impact {esc(direction)}">
              <div class="impact-top">
                <h3>{esc(item.get("sector"))}</h3>
                <span class="badge {esc(direction)}">{esc(item.get("direction"))}</span>
              </div>
              <p>{esc(item.get("rationale"))}</p>
              <footer><span>Watchlist</span>{esc(item.get("watchlist"))}</footer>
            </article>
            """
        )
    return "\n".join(cards)


def render_scenarios(items: list[dict[str, Any]]) -> str:
    cards = []
    for item in items:
        cards.append(
            f"""
            <article class="scenario">
              <div><strong>{esc(item.get("case"))}</strong><span>{esc(item.get("probability"))}</span></div>
              <p>{esc(item.get("view"))}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_sources(items: list[dict[str, Any]]) -> str:
    rows = []
    for item in items:
        url = esc(item.get("url"))
        rows.append(
            f"""
            <tr>
              <td>{esc(item.get("label"))}</td>
              <td><a href="{url}">{url}</a></td>
              <td>{esc(item.get("used_for"))}</td>
              <td>{esc(item.get("retrieved_at"))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_report(data: dict[str, Any]) -> str:
    summary = render_summary(data.get("executive_summary", []))
    indices = render_indices(data.get("indices", []))
    sectors = render_sector_cards(data.get("sectors", []))
    factors = render_factor_cards(data.get("core_factors", []))
    ai_blocks = render_text_blocks(data.get("ai_capex_analysis", []))
    geo_blocks = render_text_blocks(data.get("geopolitics_dollar_gold", []))
    us_blocks = render_text_blocks(data.get("us_interpretation", []))
    hk_cards = render_impact_cards(data.get("hong_kong_impact", []))
    cn_cards = render_impact_cards(data.get("a_share_impact", []))
    scenarios = render_scenarios(data.get("scenarios", []))
    sources = render_sources(data.get("sources", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(data.get("title"))}</title>
  <style>
    :root {{
      --ink: #17202b;
      --muted: #697586;
      --paper: #f5f1e9;
      --paper-2: #eadfcf;
      --card: #fffdf7;
      --red: #c93a35;
      --red-dark: #9f2724;
      --green: #08745f;
      --blue: #174e7c;
      --navy: #102235;
      --gold: #c79238;
      --yellow: #f6d45c;
      --mint: #dff3ec;
      --line: #223044;
      --shadow: 0 24px 70px rgba(16, 34, 53, .18);
      --soft-shadow: 0 14px 36px rgba(16, 34, 53, .10);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Segoe UI", sans-serif;
      line-height: 1.55;
      background:
        linear-gradient(90deg, rgba(16,34,53,.045) 1px, transparent 1px),
        linear-gradient(0deg, rgba(16,34,53,.035) 1px, transparent 1px),
        radial-gradient(circle at 12% 8%, rgba(201,58,53,.13), transparent 24%),
        radial-gradient(circle at 88% 2%, rgba(8,116,95,.10), transparent 22%),
        var(--paper);
      background-size: 34px 34px, 34px 34px, auto, auto, auto;
    }}
    .page {{ width: min(1180px, calc(100% - 28px)); margin: 0 auto 70px; }}
    header.cover {{
      position: relative;
      overflow: hidden;
      min-height: 500px;
      margin: 24px auto 22px;
      padding: clamp(22px, 5vw, 52px);
      border: 1px solid rgba(34,48,68,.18);
      border-radius: 28px;
      background:
        linear-gradient(135deg, rgba(255,253,247,.96), rgba(246,238,224,.94)),
        var(--card);
      box-shadow: var(--shadow);
    }}
    .cover::before {{
      content: "";
      position: absolute;
      width: 560px;
      height: 560px;
      right: -210px;
      top: -230px;
      border-radius: 50%;
      background: linear-gradient(145deg, var(--red), #e66f4f);
      opacity: .92;
    }}
    .cover::after {{
      content: "";
      position: absolute;
      width: 180px;
      height: 180px;
      right: 78px;
      top: 80px;
      border: 18px solid rgba(255,255,255,.36);
      border-radius: 50%;
      transform: rotate(-12deg);
    }}
    .brand-row {{ position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: center; gap: 16px; }}
    .cover-label {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 9px 14px;
      border: 1px solid rgba(34,48,68,.22);
      border-radius: 12px;
      background: #fff7df;
      color: var(--navy);
      box-shadow: 0 8px 24px rgba(16,34,53,.10);
      font-weight: 950;
    }}
    .cover-label::before {{
      content: "";
      width: 13px;
      height: 13px;
      border: 1px solid var(--line);
      border-radius: 50%;
      background: var(--red);
    }}
    .date-chip {{ position: relative; z-index: 2; border: 1px solid rgba(34,48,68,.20); border-radius: 999px; padding: 8px 14px; background: white; font-weight: 900; color: var(--navy); box-shadow: 0 8px 22px rgba(16,34,53,.08); }}
    h1 {{ position: relative; z-index: 2; max-width: 880px; margin: 52px 0 18px; font-size: clamp(36px, 5.4vw, 70px); line-height: 1.02; letter-spacing: 0; color: var(--navy); }}
    .subtitle {{ position: relative; z-index: 2; max-width: 760px; font-size: clamp(18px, 2.2vw, 24px); font-weight: 760; color: #3d4858; }}
    .host-card {{
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 14px;
      align-items: center;
      max-width: 720px;
      margin-top: 32px;
      padding: 16px;
      border: 1px solid rgba(34,48,68,.18);
      border-radius: 18px;
      background: white;
      box-shadow: 0 18px 42px rgba(16,34,53,.13);
    }}
    .avatar {{ display: grid; place-items: center; width: 70px; height: 70px; border: 1px solid rgba(34,48,68,.18); border-radius: 18px; background: var(--navy); color: white; font-size: 30px; font-weight: 950; }}
    .host-card strong {{ display: block; font-size: 18px; }}
    .host-card p {{ margin: 4px 0 0; color: var(--muted); text-indent: 2em; }}
    .meta {{ position: relative; z-index: 2; display: flex; flex-wrap: wrap; gap: 10px; margin-top: 28px; }}
    .meta span {{ padding: 7px 12px; border: 1px solid rgba(34,48,68,.16); border-radius: 999px; background: rgba(255,253,247,.88); font-size: 13px; font-weight: 850; box-shadow: 0 8px 20px rgba(16,34,53,.06); }}
    .nav-strip {{
      position: sticky;
      top: 0;
      z-index: 5;
      display: flex;
      gap: 10px;
      overflow-x: auto;
      margin: 18px 0 26px;
      padding: 10px;
      border: 1px solid rgba(34,48,68,.14);
      border-radius: 999px;
      background: rgba(255,253,247,.92);
      box-shadow: 0 12px 28px rgba(16,34,53,.10);
      backdrop-filter: blur(12px);
    }}
    .nav-strip a {{ flex: 0 0 auto; padding: 7px 12px; border-radius: 999px; color: var(--navy); text-decoration: none; font-size: 13px; font-weight: 900; }}
    .nav-strip a:hover {{ background: var(--navy); color: white; }}
    .chapter {{ margin: 28px 0; }}
    .section-title {{ display: flex; align-items: center; gap: 12px; margin: 0 0 16px; }}
    .section-title span {{ display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid rgba(34,48,68,.18); border-radius: 13px; background: var(--navy); color: white; font-weight: 950; box-shadow: 0 10px 24px rgba(16,34,53,.18); }}
    h2 {{ margin: 0; font-size: clamp(24px, 3vw, 36px); letter-spacing: 0; }}
    .big-card, .summary-card, .metric, .note, .impact, .scenario, .sector-card, .factor-card {{
      position: relative;
      overflow: hidden;
      background: var(--card);
      border: 1px solid rgba(34,48,68,.16);
      border-radius: 20px;
      box-shadow: var(--soft-shadow);
      transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }}
    .summary-card:hover, .metric:hover, .note:hover, .impact:hover, .scenario:hover, .sector-card:hover, .factor-card:hover {{
      transform: translateY(-3px);
      border-color: rgba(34,48,68,.30);
      box-shadow: 0 22px 52px rgba(16,34,53,.16);
    }}
    .big-card {{ padding: clamp(20px, 3vw, 32px); box-shadow: var(--shadow); }}
    .house-view {{ font-size: clamp(19px, 2.2vw, 26px); font-weight: 850; }}
    .house-view em {{ font-style: normal; background: linear-gradient(transparent 58%, rgba(255,216,77,.75) 58%); }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(245px, 1fr)); gap: 16px; }}
    .summary-card {{ min-height: 155px; padding: 18px; border-top: 5px solid var(--red); }}
    .summary-card::after {{ content: ""; position: absolute; right: -28px; bottom: -28px; width: 90px; height: 90px; border-radius: 50%; background: rgba(201,58,53,.10); }}
    .summary-card span {{ display: inline-grid; place-items: center; width: 40px; height: 40px; margin-bottom: 12px; border-radius: 12px; background: var(--red); color: white; font-weight: 950; }}
    .summary-card p {{ margin: 0; font-weight: 800; text-indent: 2em; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(235px, 1fr)); gap: 16px; }}
    .metric {{ padding: 18px; }}
    .metric::before {{ content: ""; position: absolute; inset: 0 0 auto; height: 7px; background: linear-gradient(90deg, var(--red), var(--gold)); }}
    .metric-label {{ margin-top: 8px; color: var(--muted); font-size: 14px; font-weight: 800; }}
    .metric-ticker {{ margin-top: 3px; font-size: 14px; font-weight: 950; }}
    .metric-close {{ margin-top: 10px; font-size: clamp(28px, 4vw, 44px); line-height: 1; font-weight: 950; }}
    .metric-change {{ display: inline-flex; margin-top: 12px; padding: 6px 11px; border: 1px solid currentColor; border-radius: 999px; background: white; font-weight: 950; }}
    .metric p {{ color: var(--muted); margin: 12px 0 0; font-size: 14px; text-indent: 2em; }}
    .pos {{ color: var(--green); }} .neg {{ color: var(--red-dark); }} .flat {{ color: var(--muted); }}
    .sector-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(215px, 1fr)); gap: 16px; }}
    .sector-card {{ min-height: 225px; padding: 18px; border-left: 5px solid #ccd6e0; }}
    .sector-card.pos {{ border-left-color: var(--green); }}
    .sector-card.neg {{ border-left-color: var(--red); }}
    .rank-pill {{ position: absolute; top: 14px; right: 14px; padding: 5px 10px; border-radius: 999px; background: #eef2f6; color: var(--navy); font-weight: 950; }}
    .sector-card h3 {{ width: calc(100% - 58px); margin: 0 0 4px; font-size: 18px; line-height: 1.22; }}
    .ticker-line {{ color: var(--muted); font-weight: 850; }}
    .sector-change {{ margin: 14px 0 10px; font-size: 36px; line-height: 1; font-weight: 950; }}
    .sector-card p {{ margin: 0; color: #473b33; text-indent: 2em; }}
    .factor-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .factor-card {{ padding: 18px; background: #fffdfa; border-top: 5px solid var(--gold); }}
    .factor-head {{ display: flex; justify-content: space-between; align-items: start; gap: 12px; margin-bottom: 12px; }}
    .factor-head h3 {{ margin: 0; font-size: 20px; line-height: 1.24; }}
    .badge {{ flex: 0 0 auto; border-radius: 999px; padding: 5px 11px; background: #eef2f6; font-size: 12px; font-weight: 950; color: var(--navy); }}
    .badge.positive {{ background: var(--mint); }} .badge.negative {{ background: #ffd1cd; }} .badge.neutral {{ background: #e8e0d4; }}
    .factor-evidence {{ margin: 0; padding: 12px; border-radius: 14px; background: #fff3d8; font-weight: 750; text-indent: 2em; }}
    .factor-impact {{ margin: 12px 0 0; color: var(--muted); text-indent: 2em; }}
    .mini-label {{ margin: 4px 0 7px; color: var(--red-dark); font-size: 11px; font-weight: 950; letter-spacing: .08em; text-transform: uppercase; }}
    .impact-label {{ margin-top: 12px; color: var(--green); }}
    .notes, .impact-grid, .scenario-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .note {{ padding: 20px; border-left: 5px solid var(--blue); }}
    .card-kicker {{ margin-bottom: 8px; color: var(--gold); font-size: 11px; font-weight: 950; letter-spacing: .10em; text-transform: uppercase; }}
    .note h3 {{ margin: 0 0 10px; font-size: 21px; line-height: 1.25; }}
    .note p {{ margin: 0; color: #473b33; text-indent: 2em; }}
    .impact {{ padding: 18px; background: #fffdfa; border-top: 5px solid #ccd6e0; }}
    .impact.positive {{ border-top-color: var(--green); }}
    .impact.negative {{ border-top-color: var(--red); }}
    .impact.neutral {{ border-top-color: var(--gold); }}
    .impact-top {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 10px; }}
    .impact h3 {{ margin: 0; font-size: 21px; }}
    .impact p {{ margin: 0; text-indent: 2em; }}
    .impact footer {{ margin-top: 14px; padding: 12px; border-radius: 14px; background: #f3f6f8; color: var(--muted); font-weight: 800; }}
    .impact footer span {{ display: block; margin-bottom: 4px; color: var(--navy); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }}
    .scenario {{ padding: 18px; background: #f3fff9; border-left: 5px solid var(--green); }}
    .scenario div {{ display: flex; justify-content: space-between; gap: 12px; color: var(--green); font-size: 20px; font-weight: 950; }}
    .scenario p {{ margin: 10px 0 0; text-indent: 2em; }}
    .question-strip {{ display: inline-block; margin-bottom: 12px; padding: 7px 13px; border-radius: 999px; background: var(--navy); color: white; font-weight: 950; box-shadow: 0 10px 24px rgba(16,34,53,.14); }}
    .table-wrap {{ overflow-x: auto; background: var(--card); border: 1px solid rgba(34,48,68,.16); border-radius: 18px; box-shadow: var(--soft-shadow); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid rgba(33,26,22,.18); text-align: left; vertical-align: top; }}
    th {{ background: #efe4d3; font-size: 13px; }}
    td span {{ display: block; color: var(--muted); font-size: 12px; margin-top: 2px; }}
    a {{ color: var(--blue); overflow-wrap: anywhere; }}
    .mini-note {{ color: var(--muted); font-weight: 800; margin: 0 0 12px; }}
    @media (max-width: 720px) {{
      .page {{ width: min(100% - 18px, 1180px); }}
      header.cover {{ min-height: 0; margin-top: 10px; border-radius: 22px; }}
      .cover::before {{ width: 280px; height: 280px; right: -150px; top: -120px; }}
      h1 {{ margin-top: 34px; }}
      .brand-row {{ align-items: flex-start; flex-direction: column; }}
      .host-card {{ grid-template-columns: 1fr; }}
      .avatar {{ width: 58px; height: 58px; }}
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ width: 100%; margin: 0; }}
      header.cover, .big-card, .summary-card, .metric, .note, .impact, .scenario, .sector-card, .factor-card, .table-wrap {{ box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="cover">
      <div class="brand-row">
        <div class="cover-label">投研图解报告</div>
        <div class="date-chip">美股交易日 {esc(data.get("session_date"))}</div>
      </div>
      <h1>{esc(data.get("title"))}</h1>
      <div class="subtitle">{esc(data.get("subtitle"))}</div>
      <div class="host-card">
        <div class="avatar">讲</div>
        <div>
          <strong>核心观点</strong>
          <p>{esc(data.get("house_view"))}</p>
        </div>
      </div>
      <div class="meta">
        <span>Generated: {esc(data.get("generated_at"))}</span>
        <span>Analyst: {esc(data.get("analyst"))}</span>
        <span>AI capex / 美元 / 黄金 / 港股A股</span>
      </div>
    </header>

    <nav class="nav-strip">
      <a href="#summary">结论</a>
      <a href="#indices">大数字</a>
      <a href="#drivers">驱动</a>
      <a href="#ai-capex">AI capex</a>
      <a href="#macro">美元/黄金/地缘</a>
      <a href="#hk">港股</a>
      <a href="#ashare">A股</a>
      <a href="#risk">风险</a>
    </nav>

    <section class="chapter" id="summary">
      <div class="section-title"><span>01</span><h2>先看结论</h2></div>
      <div class="summary">{summary}</div>
    </section>

    <section class="chapter" id="indices">
      <div class="section-title"><span>02</span><h2>昨晚几个大数字</h2></div>
      <div class="metrics">{indices}</div>
    </section>

    <section class="chapter" id="sectors">
      <div class="section-title"><span>03</span><h2>哪些行业在涨，哪些在跌？</h2></div>
      <div class="sector-grid">{sectors}</div>
    </section>

    <section class="chapter" id="drivers">
      <div class="section-title"><span>04</span><h2>为什么会这样？</h2></div>
      <div class="question-strip">观点 - 证据 - 影响：先看驱动，再看传导</div>
      <div class="factor-grid">{factors}</div>
    </section>

    <section class="chapter" id="ai-capex">
      <div class="section-title"><span>05</span><h2>AI资本开支：到底变了吗？</h2></div>
      <div class="question-strip">重点不是有没有AI，而是钱花得值不值</div>
      <div class="notes">{ai_blocks}</div>
    </section>

    <section class="chapter" id="macro">
      <div class="section-title"><span>06</span><h2>美元、黄金、地缘政治怎么看？</h2></div>
      <div class="question-strip">美元弱一点，黄金强一点，风险偏好不一定更差</div>
      <div class="notes">{geo_blocks}</div>
    </section>

    <section class="chapter" id="us">
      <div class="section-title"><span>07</span><h2>这对美股本身说明什么？</h2></div>
      <div class="notes">{us_blocks}</div>
    </section>

    <section class="chapter" id="hk">
      <div class="section-title"><span>08</span><h2>传到港股，谁更敏感？</h2></div>
      <div class="impact-grid">{hk_cards}</div>
    </section>

    <section class="chapter" id="ashare">
      <div class="section-title"><span>09</span><h2>传到A股，重点看三条线</h2></div>
      <div class="impact-grid">{cn_cards}</div>
    </section>

    <section class="chapter" id="risk">
      <div class="section-title"><span>10</span><h2>接下来怎么验证？</h2></div>
      <div class="scenario-grid">{scenarios}</div>
    </section>

    <section class="chapter" id="sources">
      <div class="section-title"><span>源</span><h2>数据来源</h2></div>
      <p class="mini-note">来源仅用于交叉验证指数、行业代理、宏观变量和AI资本开支相关叙事；不构成投资建议。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Source</th><th>URL</th><th>Used For</th><th>Retrieved</th></tr></thead>
          <tbody>{sources}</tbody>
        </table>
      </div>
    </section>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an investment-bank style HTML report from JSON.")
    parser.add_argument("--input", required=True, help="Path to report JSON.")
    parser.add_argument("--output", required=True, help="Path to output HTML.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(data), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
