#!/usr/bin/env python3
"""Extract transcription-friendly audio from a media file or approved URL.

The script intentionally stays small and dependency-free. It wraps ffmpeg,
creates a stable output folder, optionally downloads an online media source,
and can run a user-supplied transcription command with placeholders.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract mono 16 kHz audio from video/audio or an approved URL."
    )
    parser.add_argument("input", help="Path to a local media file, or a URL with --allow-url-download.")
    parser.add_argument(
        "--output-dir",
        default=str(Path("output") / "video-transcriber"),
        help="Base output directory. A media-stem subfolder is created inside it.",
    )
    parser.add_argument(
        "--audio-name",
        default="audio.wav",
        help="Output audio filename inside the media output folder.",
    )
    parser.add_argument("--sample-rate", default="16000", help="Audio sample rate.")
    parser.add_argument("--channels", default="1", help="Audio channel count.")
    parser.add_argument(
        "--ffmpeg",
        default="ffmpeg",
        help="ffmpeg executable path or command name.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the extracted audio if it already exists.",
    )
    parser.add_argument(
        "--allow-url-download",
        action="store_true",
        help="Allow downloading when input is an http(s) URL.",
    )
    parser.add_argument(
        "--downloader",
        default="yt-dlp",
        help="Downloader executable for URL inputs. Default: yt-dlp.",
    )
    parser.add_argument(
        "--download-command",
        help=(
            "Optional URL download command. Placeholders: {url}, {output_template}, "
            "{output_dir}, {stem}."
        ),
    )
    parser.add_argument(
        "--transcribe-command",
        help=(
            "Optional transcription command. Placeholders: {audio}, {output_dir}, "
            "{stem}, {transcript}."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running ffmpeg or transcription.",
    )
    return parser.parse_args()


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def safe_stem(value: str) -> str:
    keep = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            keep.append(char)
        elif char in {".", " ", "/"}:
            keep.append("-")
    stem = "".join(keep).strip("-_")
    while "--" in stem:
        stem = stem.replace("--", "-")
    return stem[:80] or "online-video"


def quote_command(parts: list[str]) -> str:
    if sys.platform.startswith("win"):
        return subprocess.list2cmdline(parts)
    return " ".join(shlex.quote(part) for part in parts)


def ensure_tool(command: str) -> None:
    if Path(command).exists():
        return
    if shutil.which(command):
        return
    raise SystemExit(f"Required executable not found: {command}")


def run_command(parts: list[str], dry_run: bool) -> None:
    print(quote_command(parts))
    if dry_run:
        return
    subprocess.run(parts, check=True)


def format_transcribe_command(template: str, values: dict[str, str]) -> list[str]:
    formatted = template.format(**values)
    return shlex.split(formatted, posix=not sys.platform.startswith("win"))


def format_download_command(template: str, values: dict[str, str]) -> list[str]:
    formatted = template.format(**values)
    return shlex.split(formatted, posix=not sys.platform.startswith("win"))


def find_downloaded_media(media_dir: Path) -> Path:
    candidates = [
        path
        for path in media_dir.glob("source.*")
        if path.is_file() and path.name != "source.part"
    ]
    if not candidates:
        raise SystemExit(f"Downloaded media file not found in: {media_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def main() -> int:
    args = parse_args()
    input_value = args.input
    input_is_url = is_url(input_value)

    output_base = Path(args.output_dir).expanduser().resolve()
    if input_is_url:
        if not args.allow_url_download:
            raise SystemExit("URL input requires --allow-url-download.")
        parsed = urlparse(input_value)
        url_hint = f"{parsed.netloc}{parsed.path}" if parsed.path else parsed.netloc
        media_stem = safe_stem(url_hint)
    else:
        input_path = Path(input_value).expanduser().resolve()
        if not input_path.exists():
            raise SystemExit(f"Input file does not exist: {input_path}")
        if not input_path.is_file():
            raise SystemExit(f"Input path is not a file: {input_path}")
        media_stem = input_path.stem

    media_dir = output_base / media_stem
    if not args.dry_run:
        media_dir.mkdir(parents=True, exist_ok=True)

    if input_is_url:
        output_template = media_dir / "source.%(ext)s"
        download_values = {
            "url": input_value,
            "output_template": str(output_template),
            "output_dir": str(media_dir),
            "stem": media_stem,
        }
        if args.download_command:
            download_parts = format_download_command(args.download_command, download_values)
        else:
            if not args.dry_run:
                ensure_tool(args.downloader)
            download_parts = [args.downloader, "-o", str(output_template), input_value]
        run_command(download_parts, args.dry_run)
        input_path = media_dir / "source.media" if args.dry_run else find_downloaded_media(media_dir)

    audio_path = media_dir / args.audio_name
    transcript_path = media_dir / "transcript.txt"

    if audio_path.exists() and not args.overwrite:
        print(f"Audio already exists, reusing: {audio_path}")
    else:
        if not args.dry_run:
            ensure_tool(args.ffmpeg)
        command = [
            args.ffmpeg,
            "-hide_banner",
            "-y" if args.overwrite else "-n",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            str(args.channels),
            "-ar",
            str(args.sample_rate),
            str(audio_path),
        ]
        run_command(command, args.dry_run)

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": input_value,
        "input_type": "url" if input_is_url else "file",
        "source_media": str(input_path),
        "output_dir": str(media_dir),
        "audio": str(audio_path),
        "sample_rate": str(args.sample_rate),
        "channels": str(args.channels),
    }

    if args.transcribe_command:
        values = {
            "audio": str(audio_path),
            "output_dir": str(media_dir),
            "stem": media_stem,
            "transcript": str(transcript_path),
        }
        transcribe_parts = format_transcribe_command(args.transcribe_command, values)
        manifest["transcribe_command"] = quote_command(transcribe_parts)
        run_command(transcribe_parts, args.dry_run)

    manifest_path = media_dir / "media-manifest.json"
    if not args.dry_run:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(f"Manifest: {manifest_path}")
    print(f"Audio: {audio_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
