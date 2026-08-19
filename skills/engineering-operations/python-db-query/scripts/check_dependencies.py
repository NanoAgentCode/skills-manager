#!/usr/bin/env python3
"""Check Python DB Query skill dependencies and optional database config."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def status(ok: bool, message: str) -> None:
    prefix = "[OK]" if ok else "[FAIL]"
    print(f"{prefix} {message}")


def module_version(name: str) -> str | None:
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError:
        return None
    if spec is None:
        return None
    module = importlib.import_module(name)
    return getattr(module, "__version__", "installed")


def check_oracle(config: dict | None) -> bool:
    version = module_version("oracledb")
    if not version:
        status(False, "oracledb is not installed")
        return False
    status(True, f"oracledb {version} is installed")

    ok = True
    if str(version).startswith("4."):
        status(False, "oracledb 4.x requires newer Oracle Client libraries; Oracle 11g support here expects oracledb==2.5.1")
        ok = False

    if config:
        client_lib_dir = config.get("client_lib_dir")
        if client_lib_dir:
            client_path = Path(client_lib_dir)
            has_dir = client_path.exists()
            has_oci = (client_path / "oci.dll").exists()
            status(has_dir, f"client_lib_dir exists: {client_path}")
            status(has_oci, "oci.dll exists under client_lib_dir")
            ok = ok and has_dir and has_oci
    return ok


def check_minio(config: dict, config_path: Path) -> bool:
    from minio_mc import find_mc

    try:
        mc_path = find_mc(config, config_path)
    except SystemExit as exc:
        status(False, str(exc))
        return False
    result = subprocess.run(
        [str(mc_path), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    version = (result.stdout or result.stderr).strip().splitlines()
    status(result.returncode == 0, f"MinIO Client: {version[0] if version else mc_path}")
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check database query skill dependencies.")
    parser.add_argument("--config", help="Optional config.json path for client-specific checks.")
    args = parser.parse_args()

    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")

    config = None
    config_path = None
    if args.config:
        config_path = Path(args.config).expanduser().resolve()
        if not config_path.exists():
            status(False, f"config file not found: {config_path}")
            return 2
        config = json.loads(config_path.read_text(encoding="utf-8"))

    status(True, "sqlite3 is built in")
    if config and str(config.get("type", "")).lower() in {"oracle", "oracle11g"}:
        return 0 if check_oracle(config) else 1
    if config and str(config.get("type", "")).lower() == "minio":
        assert config_path is not None
        return 0 if check_minio(config, config_path) else 1

    ok = True
    for module_name, label in [
        ("oracledb", "Oracle"),
        ("psycopg", "PostgreSQL psycopg"),
        ("psycopg2", "PostgreSQL psycopg2"),
        ("pymysql", "MySQL PyMySQL"),
        ("mysql.connector", "MySQL Connector"),
        ("pyodbc", "SQL Server pyodbc"),
        ("pymongo", "MongoDB PyMongo"),
        ("redis", "Redis client"),
    ]:
        version = module_version(module_name)
        status(bool(version), f"{label}: {version or 'not installed'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
