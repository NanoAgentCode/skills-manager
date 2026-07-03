"""Configuration helpers for wechat-format scripts."""

from __future__ import annotations

import json
from pathlib import Path


def default_config(skill_dir: Path) -> dict:
    repo_root = skill_dir.parents[1]
    output_dir = repo_root / "output" / "wechat-format" / "tmp"
    return {
        "output_dir": str(output_dir),
        "vault_root": str(Path.home()),
        "image_search_paths": [],
        "settings": {
            "default_theme": "newspaper",
            "auto_open_browser": True,
        },
        "wechat": {
            "app_id": "",
            "app_secret": "",
            "author": "",
        },
        "cover": {
            "output_dir": str(repo_root / "output" / "wechat-cover"),
            "image_generation_script": "",
        },
        "ai": {
            "url": "",
            "api_key": "",
            "model": "",
        },
    }


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(skill_dir: Path) -> dict:
    config_path = skill_dir / "config.json"
    config = default_config(skill_dir)
    if not config_path.exists():
        return config

    with open(config_path, encoding="utf-8") as f:
        user_config = json.load(f)
    config = deep_merge(config, user_config)
    output_dir = Path(config["output_dir"]).expanduser()
    if not output_dir.is_absolute():
        output_dir = skill_dir / output_dir
    config["output_dir"] = str(output_dir)
    cover_config = config.get("cover")
    if isinstance(cover_config, dict):
        cover_output_dir = Path(str(cover_config.get("output_dir", ""))).expanduser()
        if not cover_output_dir.is_absolute():
            cover_output_dir = skill_dir / cover_output_dir
        cover_config["output_dir"] = str(cover_output_dir)
    return config
