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


def balanced_grid_class(base_class: str, items: list[Any]) -> str:
    count = len(items)
    if count >= 8:
        bucket = "many"
    else:
        bucket = str(max(count, 1))
    return f"{base_class} balanced-grid grid-count-{bucket}"


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
    summary_items = data.get("executive_summary", [])
    index_items = data.get("indices", [])
    sector_items = data.get("sectors", [])
    factor_items = data.get("core_factors", [])
    ai_items = data.get("ai_capex_analysis", [])
    geo_items = data.get("geopolitics_dollar_gold", [])
    us_items = data.get("us_interpretation", [])
    hk_items = data.get("hong_kong_impact", [])
    cn_items = data.get("a_share_impact", [])
    scenario_items = data.get("scenarios", [])

    summary = render_summary(summary_items)
    indices = render_indices(index_items)
    sectors = render_sector_cards(sector_items)
    factors = render_factor_cards(factor_items)
    ai_blocks = render_text_blocks(ai_items)
    geo_blocks = render_text_blocks(geo_items)
    us_blocks = render_text_blocks(us_items)
    hk_cards = render_impact_cards(hk_items)
    cn_cards = render_impact_cards(cn_items)
    scenarios = render_scenarios(scenario_items)
    sources = render_sources(data.get("sources", []))
    summary_grid = balanced_grid_class("summary", summary_items)
    metrics_grid = balanced_grid_class("metrics", index_items)
    sector_grid = balanced_grid_class("sector-grid", sector_items)
    factor_grid = balanced_grid_class("factor-grid", factor_items)
    ai_grid = balanced_grid_class("notes", ai_items)
    geo_grid = balanced_grid_class("notes", geo_items)
    us_grid = balanced_grid_class("notes", us_items)
    hk_grid = balanced_grid_class("impact-grid", hk_items)
    cn_grid = balanced_grid_class("impact-grid", cn_items)
    scenario_grid = balanced_grid_class("scenario-grid", scenario_items)
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
      --paper: #f6f4ef;
      --paper-2: #ece5da;
      --card: #fffefa;
      --red: #a9433f;
      --red-dark: #7f2f2c;
      --green: #0f6b57;
      --blue: #1f5578;
      --navy: #102235;
      --gold: #a98242;
      --yellow: #ead6a2;
      --mint: #e8f3ee;
      --line: #223044;
      --shadow: 0 20px 54px rgba(16, 34, 53, .13);
      --soft-shadow: 0 10px 28px rgba(16, 34, 53, .075);
      --slide-shadow: 0 18px 46px rgba(16, 34, 53, .11);
      --font-display: "Microsoft JhengHei UI", "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
      --font-body: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
      --font-number: "Bahnschrift", "DIN Alternate", "Segoe UI Variable Display", "Aptos Display", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: var(--font-body);
      line-height: 1.55;
      background:
        linear-gradient(90deg, rgba(16,34,53,.025) 1px, transparent 1px),
        linear-gradient(0deg, rgba(16,34,53,.022) 1px, transparent 1px),
        radial-gradient(circle at 12% 8%, rgba(169,67,63,.055), transparent 26%),
        radial-gradient(circle at 88% 2%, rgba(15,107,87,.05), transparent 24%),
        var(--paper);
      background-size: 42px 42px, 42px 42px, auto, auto, auto;
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
        linear-gradient(135deg, rgba(255,254,250,.98), rgba(246,241,232,.96)),
        var(--card);
      box-shadow: var(--shadow);
    }}
    .cover::before {{
      content: "";
      position: absolute;
      width: 520px;
      height: 520px;
      right: -240px;
      top: -260px;
      border-radius: 50%;
      background: linear-gradient(145deg, rgba(169,67,63,.86), rgba(169,130,66,.48));
      opacity: .68;
    }}
    .cover::after {{
      content: "";
      position: absolute;
      width: 160px;
      height: 160px;
      right: 76px;
      top: 78px;
      border: 16px solid rgba(255,255,255,.28);
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
      background: #fbf4e5;
      color: var(--navy);
      box-shadow: 0 8px 24px rgba(16,34,53,.10);
      font-weight: 950;
    }}
    .cover-grid {{
      position: absolute;
      inset: auto 42px 34px auto;
      z-index: 1;
      display: grid;
      grid-template-columns: repeat(2, 138px);
      gap: 14px;
      opacity: .96;
    }}
    .cover-tile {{
      position: relative;
      min-height: 94px;
      padding: 16px 14px;
      border: 1px solid rgba(255,255,255,.60);
      border-radius: 16px;
      color: #fff9c8;
      box-shadow: 0 16px 36px rgba(16,34,53,.20), inset 0 0 0 1px rgba(255,255,255,.26);
      backdrop-filter: blur(14px) saturate(128%);
      overflow: hidden;
    }}
    .cover-tile::before {{
      content: "";
      position: absolute;
      inset: 7px;
      border: 1px dashed rgba(255,255,255,.48);
      border-radius: 12px;
      pointer-events: none;
    }}
    .cover-tile::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(255,255,255,.22), transparent 45%, rgba(255,255,255,.14));
      pointer-events: none;
    }}
    .cover-tile span, .cover-tile strong, .cover-tile em {{ position: relative; z-index: 1; display: block; }}
    .cover-tile span {{ font-family: var(--font-display); font-size: 20px; font-weight: 950; line-height: 1.1; }}
    .cover-tile strong {{ margin-top: 7px; font-family: var(--font-number); font-size: 24px; color: #fff2a6; line-height: 1; }}
    .cover-tile em {{ margin-top: 7px; color: rgba(255,255,255,.82); font-style: normal; font-size: 12px; font-weight: 900; letter-spacing: .02em; }}
    .glass-blue {{ background: linear-gradient(135deg, rgba(27,122,149,.76), rgba(74,57,158,.76)); }}
    .glass-rose {{ background: linear-gradient(135deg, rgba(179,66,76,.78), rgba(132,57,116,.76)); }}
    .glass-violet {{ background: linear-gradient(135deg, rgba(176,67,153,.76), rgba(67,79,145,.76)); }}
    .glass-green {{ background: linear-gradient(135deg, rgba(45,128,95,.76), rgba(55,79,150,.76)); }}
    .cover-label::before {{
      content: "";
      width: 13px;
      height: 13px;
      border: 1px solid var(--line);
      border-radius: 50%;
      background: var(--gold);
    }}
    .date-chip {{ position: relative; z-index: 2; border: 1px solid rgba(34,48,68,.20); border-radius: 999px; padding: 8px 14px; background: white; font-weight: 900; color: var(--navy); box-shadow: 0 8px 22px rgba(16,34,53,.08); }}
    h1 {{ position: relative; z-index: 2; max-width: 880px; margin: 48px 0 18px; font-family: var(--font-display); font-size: clamp(34px, 5vw, 64px); line-height: 1.05; letter-spacing: 0; color: var(--navy); }}
    .subtitle {{ position: relative; z-index: 2; max-width: 760px; font-family: var(--font-display); font-size: clamp(18px, 2.2vw, 24px); font-weight: 760; color: #3d4858; }}
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
      box-shadow: 0 14px 34px rgba(16,34,53,.10);
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
    .chapter {{
      position: relative;
      margin: 30px 0;
      padding: 24px;
      border: 1px solid rgba(34,48,68,.10);
      border-radius: 26px;
      background: rgba(255,254,250,.62);
      box-shadow: 0 14px 38px rgba(16,34,53,.055);
    }}
    .section-title {{ display: flex; align-items: center; gap: 12px; margin: 0 0 18px; padding-bottom: 14px; border-bottom: 1px solid rgba(34,48,68,.10); }}
    .section-title span {{ display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid rgba(34,48,68,.18); border-radius: 13px; background: var(--navy); color: white; font-weight: 950; box-shadow: 0 10px 24px rgba(16,34,53,.18); }}
    h2 {{ margin: 0; font-family: var(--font-display); font-size: clamp(24px, 3vw, 34px); letter-spacing: 0; }}
    .big-card, .summary-card, .metric, .note, .impact, .scenario, .sector-card, .factor-card {{
      position: relative;
      overflow: hidden;
      background: var(--card);
      border: 1px solid rgba(34,48,68,.16);
      border-radius: 20px;
      box-shadow: var(--slide-shadow);
      transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }}
    .summary-card:hover, .metric:hover, .note:hover, .impact:hover, .scenario:hover, .sector-card:hover, .factor-card:hover {{
      transform: translateY(-3px);
      border-color: rgba(34,48,68,.30);
      box-shadow: 0 18px 42px rgba(16,34,53,.12);
    }}
    .big-card {{ padding: clamp(20px, 3vw, 32px); box-shadow: var(--shadow); }}
    .house-view {{ font-size: clamp(19px, 2.2vw, 26px); font-weight: 850; }}
    .house-view em {{ font-style: normal; background: linear-gradient(transparent 58%, rgba(255,216,77,.75) 58%); }}
    .balanced-grid {{ display: grid; grid-template-columns: repeat(1, minmax(0, 1fr)); gap: 16px; align-items: stretch; }}
    .grid-count-2, .grid-count-4 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .grid-count-3, .grid-count-5, .grid-count-6 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .grid-count-7, .grid-count-many {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .summary-card {{ min-height: 170px; padding: 18px; border-top: 4px solid var(--gold); display: flex; flex-direction: column; }}
    .summary-card::after {{ content: ""; position: absolute; right: -34px; bottom: -34px; width: 96px; height: 96px; border-radius: 50%; background: rgba(169,130,66,.085); }}
    .summary-card span {{ display: inline-grid; place-items: center; width: 40px; height: 40px; margin-bottom: 12px; border-radius: 12px; background: var(--navy); color: white; font-weight: 950; }}
    .summary-card p {{ margin: 0; font-weight: 800; text-indent: 2em; }}
    .metric {{ padding: 18px; min-height: 190px; display: flex; flex-direction: column; background: linear-gradient(145deg, rgba(255,254,250,.88), rgba(247,240,227,.70)); backdrop-filter: blur(10px); }}
    .metric::before {{ content: ""; position: absolute; inset: 0 0 auto; height: 6px; background: linear-gradient(90deg, var(--blue), var(--gold)); opacity: .92; }}
    .metric-label {{ margin-top: 8px; color: var(--muted); font-size: 14px; font-weight: 800; }}
    .metric-ticker {{ margin-top: 3px; font-size: 14px; font-weight: 950; }}
    .metric-close {{ margin-top: 10px; font-family: var(--font-number); font-size: clamp(28px, 4vw, 44px); line-height: 1; font-weight: 950; }}
    .metric-change {{ display: inline-flex; margin-top: 12px; padding: 6px 11px; border: 1px solid currentColor; border-radius: 999px; background: white; font-family: var(--font-number); font-weight: 950; }}
    .metric p {{ color: var(--muted); margin: auto 0 0; padding-top: 12px; font-size: 14px; text-indent: 2em; }}
    .pos {{ color: var(--green); }} .neg {{ color: var(--red-dark); }} .flat {{ color: var(--muted); }}
    .sector-card {{ min-height: 245px; padding: 18px; border-left: 5px solid #ccd6e0; display: flex; flex-direction: column; }}
    .sector-card.pos {{ border-left-color: var(--green); }}
    .sector-card.neg {{ border-left-color: var(--red); }}
    .rank-pill {{ position: absolute; top: 14px; right: 14px; padding: 5px 10px; border-radius: 999px; background: #eef2f6; color: var(--navy); font-weight: 950; }}
    .sector-card h3 {{ width: calc(100% - 58px); margin: 0 0 4px; font-size: 18px; line-height: 1.22; }}
    .ticker-line {{ color: var(--muted); font-weight: 850; }}
    .sector-change {{ margin: 14px 0 10px; font-family: var(--font-number); font-size: 36px; line-height: 1; font-weight: 950; }}
    .sector-card p {{ margin: auto 0 0; color: #473b33; text-indent: 2em; }}
    .factor-card {{ padding: 18px; background: #fffdfa; border-top: 4px solid var(--gold); min-height: 270px; display: flex; flex-direction: column; }}
    .factor-head {{ display: flex; justify-content: space-between; align-items: start; gap: 12px; margin-bottom: 12px; }}
    .factor-head h3 {{ margin: 0; font-size: 20px; line-height: 1.24; }}
    .badge {{ flex: 0 0 auto; border-radius: 999px; padding: 5px 11px; background: #eef2f6; font-size: 12px; font-weight: 950; color: var(--navy); }}
    .badge.positive {{ background: var(--mint); }} .badge.negative {{ background: #ffd1cd; }} .badge.neutral {{ background: #e8e0d4; }}
    .factor-evidence {{ margin: 0; padding: 12px; border-radius: 14px; background: #f7f0e3; font-weight: 750; text-indent: 2em; }}
    .factor-impact {{ margin: 12px 0 0; color: var(--muted); text-indent: 2em; }}
    .mini-label {{ margin: 4px 0 7px; color: var(--red-dark); font-size: 11px; font-weight: 950; letter-spacing: .08em; text-transform: uppercase; }}
    .impact-label {{ margin-top: 12px; color: var(--green); }}
    .note {{ padding: 20px; border-left: 4px solid var(--blue); min-height: 230px; background: linear-gradient(145deg, rgba(255,254,250,.94), rgba(247,240,227,.70)); }}
    .card-kicker {{ margin-bottom: 8px; color: var(--gold); font-size: 11px; font-weight: 950; letter-spacing: .10em; text-transform: uppercase; }}
    .note h3 {{ margin: 0 0 10px; font-size: 21px; line-height: 1.25; }}
    .note p {{ margin: 0; color: #473b33; text-indent: 2em; }}
    .impact {{ padding: 18px; background: linear-gradient(145deg, rgba(255,254,250,.94), rgba(247,240,227,.72)); border-top: 4px solid #ccd6e0; min-height: 245px; display: flex; flex-direction: column; }}
    .impact.positive {{ border-top-color: var(--green); }}
    .impact.negative {{ border-top-color: var(--red); }}
    .impact.neutral {{ border-top-color: var(--gold); }}
    .impact-top {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 10px; }}
    .impact h3 {{ margin: 0; font-size: 21px; }}
    .impact p {{ margin: 0; text-indent: 2em; }}
    .impact footer {{ margin-top: auto; padding: 12px; border-radius: 14px; background: #f3f6f8; color: var(--muted); font-weight: 800; }}
    .impact footer span {{ display: block; margin-bottom: 4px; color: var(--navy); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }}
    .scenario {{ padding: 18px; background: #f6fbf8; border-left: 4px solid var(--green); min-height: 180px; }}
    .scenario div {{ display: flex; justify-content: space-between; gap: 12px; color: var(--green); font-size: 20px; font-weight: 950; }}
    .scenario p {{ margin: 10px 0 0; text-indent: 2em; }}
    .question-strip {{ display: inline-block; margin-bottom: 12px; padding: 7px 13px; border-radius: 999px; background: #20364d; color: white; font-weight: 900; box-shadow: 0 8px 18px rgba(16,34,53,.10); }}
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
      .cover-grid {{ display: none; }}
      .chapter {{ padding: 16px; border-radius: 20px; }}
      .balanced-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (min-width: 721px) and (max-width: 980px) {{
      .grid-count-3, .grid-count-5, .grid-count-6, .grid-count-7, .grid-count-many {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
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
        <span>AI capex / 美元 / 黄金 / 港股A股</span>
      </div>
      <div class="cover-grid">
        <div class="cover-tile glass-blue"><span>纳指</span><strong>-0.80%</strong><em>Nasdaq Composite</em></div>
        <div class="cover-tile glass-violet"><span>纳百</span><strong>-1.61%</strong><em>Nasdaq 100</em></div>
        <div class="cover-tile glass-rose"><span>黄金</span><strong>+1.25%</strong><em>Global Gold</em></div>
        <div class="cover-tile glass-green"><span>主线</span><strong>AI Capex</strong><em>Capital Spending</em></div>
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
      <div class="{summary_grid}">{summary}</div>
    </section>

    <section class="chapter" id="indices">
      <div class="section-title"><span>02</span><h2>昨晚几个大数字</h2></div>
      <div class="{metrics_grid}">{indices}</div>
    </section>

    <section class="chapter" id="sectors">
      <div class="section-title"><span>03</span><h2>哪些行业在涨，哪些在跌？</h2></div>
      <div class="{sector_grid}">{sectors}</div>
    </section>

    <section class="chapter" id="drivers">
      <div class="section-title"><span>04</span><h2>为什么会这样？</h2></div>
      <div class="question-strip">观点 - 证据 - 影响：先看驱动，再看传导</div>
      <div class="{factor_grid}">{factors}</div>
    </section>

    <section class="chapter" id="ai-capex">
      <div class="section-title"><span>05</span><h2>AI资本开支：到底变了吗？</h2></div>
      <div class="question-strip">重点不是有没有AI，而是钱花得值不值</div>
      <div class="{ai_grid}">{ai_blocks}</div>
    </section>

    <section class="chapter" id="macro">
      <div class="section-title"><span>06</span><h2>美元、黄金、地缘政治怎么看？</h2></div>
      <div class="question-strip">美元弱一点，黄金强一点，风险偏好不一定更差</div>
      <div class="{geo_grid}">{geo_blocks}</div>
    </section>

    <section class="chapter" id="us">
      <div class="section-title"><span>07</span><h2>这对美股本身说明什么？</h2></div>
      <div class="{us_grid}">{us_blocks}</div>
    </section>

    <section class="chapter" id="hk">
      <div class="section-title"><span>08</span><h2>传到港股，谁更敏感？</h2></div>
      <div class="{hk_grid}">{hk_cards}</div>
    </section>

    <section class="chapter" id="ashare">
      <div class="section-title"><span>09</span><h2>传到A股，重点看三条线</h2></div>
      <div class="{cn_grid}">{cn_cards}</div>
    </section>

    <section class="chapter" id="risk">
      <div class="section-title"><span>10</span><h2>接下来怎么验证？</h2></div>
      <div class="{scenario_grid}">{scenarios}</div>
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
