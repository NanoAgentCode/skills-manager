#!/usr/bin/env python3
"""Convert subtitle files into a readable Markdown transcript."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


TIMESTAMP_LINE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})"
)
INLINE_TIMESTAMP = re.compile(r"<\d{2}:\d{2}:\d{2}[.]\d{3}>")
HTML_TAG = re.compile(r"<[^>]+>")
SRT_INDEX = re.compile(r"^\d+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert .srt, .vtt, or Bilibili .json subtitles to Markdown.")
    parser.add_argument("input", help="Input subtitle file (.srt/.vtt/.json).")
    parser.add_argument("--output", help="Output Markdown file. Defaults beside the input.")
    parser.add_argument(
        "--merge-window",
        type=int,
        default=20,
        help="Seconds per paragraph bucket for timestamped transcript output.",
    )
    parser.add_argument(
        "--title",
        default="Transcript",
        help="Markdown title.",
    )
    return parser.parse_args()


def timestamp_to_seconds(value: str) -> int:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))


def seconds_to_timestamp(value: int) -> str:
    hours = value // 3600
    minutes = (value % 3600) // 60
    seconds = value % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def clean_text(line: str) -> str:
    line = INLINE_TIMESTAMP.sub("", line)
    line = HTML_TAG.sub("", line)
    line = html.unescape(line)
    return " ".join(line.split())


def read_text_cues(path: Path) -> list[tuple[int, str]]:
    cues: list[tuple[int, str]] = []
    current_start: int | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_start, current_lines
        if current_start is None:
            current_lines = []
            return
        text = clean_text(" ".join(current_lines))
        if text:
            cues.append((current_start, text))
        current_start = None
        current_lines = []

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        match = TIMESTAMP_LINE.search(line)
        if match:
            flush()
            current_start = timestamp_to_seconds(match.group("start"))
            continue
        if SRT_INDEX.match(line):
            continue
        current_lines.append(line)

    flush()
    return cues


def read_bilibili_json_cues(path: Path) -> list[tuple[int, str]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    body = data.get("body")
    if not isinstance(body, list):
        raise SystemExit(f"Unsupported JSON subtitle shape: {path}")

    cues: list[tuple[int, str]] = []
    for item in body:
        if not isinstance(item, dict):
            continue
        text = clean_text(str(item.get("content", "")))
        if not text:
            continue
        try:
            timestamp = int(float(item.get("from", 0)))
        except (TypeError, ValueError):
            timestamp = 0
        cues.append((timestamp, text))
    return cues


def read_cues(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() == ".json":
        return read_bilibili_json_cues(path)
    return read_text_cues(path)


def dedupe_cues(cues: list[tuple[int, str]]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    last_text = ""
    for timestamp, text in cues:
        if not text:
            continue
        if text == last_text:
            continue
        if last_text and text.startswith(last_text + " "):
            if result:
                result[-1] = (timestamp, text)
            last_text = text
            continue
        result.append((timestamp, text))
        last_text = text
    return result


def render_markdown(title: str, cues: list[tuple[int, str]], merge_window: int) -> str:
    lines = [f"# {title}", ""]
    if not cues:
        lines.append("_No subtitle text found._")
        return "\n".join(lines) + "\n"

    bucket_start: int | None = None
    bucket_text: list[str] = []

    def flush_bucket() -> None:
        nonlocal bucket_start, bucket_text
        if bucket_start is None or not bucket_text:
            return
        paragraph = " ".join(bucket_text)
        lines.append(f"[{seconds_to_timestamp(bucket_start)}] {paragraph}")
        lines.append("")
        bucket_start = None
        bucket_text = []

    for timestamp, text in cues:
        if bucket_start is None:
            bucket_start = timestamp
        if timestamp - bucket_start >= merge_window:
            flush_bucket()
            bucket_start = timestamp
        bucket_text.append(text)

    flush_bucket()
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input subtitle does not exist: {input_path}")
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_suffix(".md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cues = dedupe_cues(read_cues(input_path))
    output_path.write_text(
        render_markdown(args.title, cues, args.merge_window),
        encoding="utf-8",
    )
    print(f"Wrote: {output_path}")
    print(f"Cues: {len(cues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
