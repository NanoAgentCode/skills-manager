#!/usr/bin/env python3
"""Run read-only MinIO operations through the official mc client."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit


MC_ALIAS = "skillsmanager"


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Config file not found: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    if str(config.get("type", "")).lower() != "minio":
        raise SystemExit("MinIO config requires type=minio.")
    return config


def resolve_env_value(config: dict[str, Any], value_key: str, env_key: str) -> str | None:
    value = config.get(value_key)
    if value:
        return str(value)
    env_name = config.get(env_key)
    if not env_name:
        return None
    resolved = os.environ.get(str(env_name))
    if not resolved:
        raise SystemExit(f"Required environment variable is not set: {env_name}")
    return resolved


def normalize_endpoint(raw_endpoint: str) -> tuple[str, str, str]:
    endpoint = raw_endpoint.strip()
    if not endpoint:
        raise SystemExit("MinIO config requires 'endpoint'.")
    if "://" not in endpoint:
        endpoint = f"https://{endpoint}"
    parsed = urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SystemExit("MinIO endpoint must be an http:// or https:// URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise SystemExit("MinIO endpoint must not contain credentials, a path, query, or fragment.")
    return parsed.scheme, parsed.netloc, urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def build_mc_environment(config: dict[str, Any]) -> dict[str, str]:
    scheme, host, endpoint = normalize_endpoint(str(config.get("endpoint", "")))
    access_key = resolve_env_value(config, "access_key", "access_key_env")
    secret_key = resolve_env_value(config, "secret_key", "secret_key_env")
    session_token = resolve_env_value(config, "session_token", "session_token_env")

    if config.get("anonymous", False):
        if access_key or secret_key or session_token:
            raise SystemExit("Anonymous MinIO config cannot include credentials.")
        host_value = endpoint
    else:
        if not access_key or not secret_key:
            raise SystemExit(
                "MinIO config requires access_key/access_key_env and secret_key/secret_key_env, "
                "or anonymous=true."
            )
        user_info = f"{quote(access_key, safe='')}:{quote(secret_key, safe='')}"
        if session_token:
            user_info += f":{quote(session_token, safe='')}"
        host_value = f"{scheme}://{user_info}@{host}"

    env = os.environ.copy()
    env[f"MC_HOST_{MC_ALIAS}"] = host_value
    env["MC_JSON"] = "true"
    env["MC_NO_COLOR"] = "true"
    env["MC_DISABLE_PAGER"] = "true"
    env["MC_QUIET"] = "true"
    if config.get("insecure", False):
        env["MC_INSECURE"] = "true"
    return env


def local_binary_names(platform_name: str) -> list[str]:
    return ["mc.exe", "mc"] if platform_name == "nt" else ["mc", "mc.exe"]


def find_mc(config: dict[str, Any], config_path: Path) -> Path:
    configured = config.get("mc_path")
    if configured:
        candidate = Path(str(configured)).expanduser()
        if not candidate.is_absolute():
            candidate = config_path.parent / candidate
        if candidate.is_file():
            if os.name != "nt" and not os.access(candidate, os.X_OK):
                raise SystemExit(f"Configured mc binary is not executable: {candidate}")
            return candidate.resolve()
        raise SystemExit(f"Configured mc binary not found: {candidate}")

    skill_root = Path(__file__).resolve().parents[1]
    for name in local_binary_names(os.name):
        candidate = skill_root / "dependencies" / name
        if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
            return candidate

    discovered = shutil.which("mc.exe" if os.name == "nt" else "mc") or shutil.which("mc")
    if discovered:
        return Path(discovered)
    raise SystemExit(
        "MinIO Client (mc) was not found. Set mc_path, place mc/mc.exe under dependencies/, "
        "or install mc on PATH after user approval."
    )


def validate_bucket(bucket: str) -> str:
    if not bucket or "/" in bucket or "\\" in bucket or any(ord(char) < 32 for char in bucket):
        raise SystemExit(f"Invalid bucket name: {bucket!r}")
    return bucket


def validate_object_name(object_name: str) -> str:
    cleaned = object_name.lstrip("/")
    if not cleaned or any(ord(char) < 32 for char in cleaned):
        raise SystemExit("Object name must be non-empty and cannot contain control characters.")
    return cleaned


def remote_target(bucket: str | None = None, object_name: str | None = None) -> str:
    target = MC_ALIAS
    if bucket:
        target += f"/{validate_bucket(bucket)}"
    if object_name:
        target += f"/{validate_object_name(object_name)}"
    return target


def build_operation(args: argparse.Namespace) -> list[str]:
    if args.command in {"test-connection", "list-buckets"}:
        return ["ls", remote_target()]
    if args.command == "list-objects":
        target = remote_target(args.bucket, args.prefix) if args.prefix else remote_target(args.bucket)
        return ["ls", *(["--recursive"] if args.recursive else []), target]
    if args.command == "stat":
        return ["stat", remote_target(args.bucket, args.object)]
    if args.command == "download":
        destination = Path(args.destination).expanduser()
        if destination.exists() and not args.overwrite:
            raise SystemExit(f"Destination already exists: {destination}. Pass --overwrite to replace it.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        return ["cp", remote_target(args.bucket, args.object), str(destination)]
    raise SystemExit(f"Unsupported MinIO command: {args.command}")


def run_mc(mc_path: Path, operation: list[str], env: dict[str, str]) -> int:
    command = [str(mc_path), "--json", "--no-color", "--quiet", "--disable-pager", *operation]
    result = subprocess.run(command, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.stdout:
        sys.stdout.write(result.stdout)
        if not result.stdout.endswith("\n"):
            sys.stdout.write("\n")
    if result.returncode != 0:
        message = result.stderr.strip() or "mc returned an error without diagnostic output"
        raise SystemExit(f"MinIO mc command failed ({result.returncode}): {message}")
    return 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run read-only MinIO operations through the official mc client.")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.json"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("test-connection", help="Validate credentials by listing visible buckets.")
    subparsers.add_parser("list-buckets", help="List visible buckets.")

    list_objects = subparsers.add_parser("list-objects", help="List objects in a bucket.")
    list_objects.add_argument("bucket")
    list_objects.add_argument("--prefix")
    list_objects.add_argument("--recursive", action="store_true")

    stat = subparsers.add_parser("stat", help="Show object metadata.")
    stat.add_argument("bucket")
    stat.add_argument("object")

    download = subparsers.add_parser("download", help="Download one object to a local path.")
    download.add_argument("bucket")
    download.add_argument("object")
    download.add_argument("destination")
    download.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    config_path = Path(args.config).expanduser().resolve()
    config = load_config(config_path)
    mc_path = find_mc(config, config_path)
    env = build_mc_environment(config)
    operation = build_operation(args)
    return run_mc(mc_path, operation, env)


if __name__ == "__main__":
    raise SystemExit(main())
