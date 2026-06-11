#!/usr/bin/env python3
"""Create a local database config JSON file without echoing passwords."""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a local database config.json.")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "config.json"))
    parser.add_argument("--type", required=True, choices=["sqlite", "postgres", "mysql", "sqlserver", "oracle", "oracle11g", "mongo", "mongodb", "redis"])
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--database")
    parser.add_argument("--uri")
    parser.add_argument("--auth-source")
    parser.add_argument("--db", type=int, help="Redis database number.")
    parser.add_argument("--path", help="SQLite database path.")
    parser.add_argument("--user")
    parser.add_argument("--password-env", help="Read password from this environment variable instead of storing it.")
    parser.add_argument("--service-name")
    parser.add_argument("--sid")
    parser.add_argument("--client-lib-dir")
    parser.add_argument("--no-password", action="store_true", help="Do not prompt for or write a password.")
    args = parser.parse_args()

    config: dict[str, object] = {"type": args.type, "timeout_seconds": 30}
    if args.type == "sqlite":
        if not args.path:
            raise SystemExit("--path is required for sqlite")
        config["path"] = args.path
        config["read_only"] = True
    elif args.type in {"mongo", "mongodb"}:
        if args.uri:
            config["uri"] = args.uri
        else:
            config["host"] = args.host or "127.0.0.1"
            config["port"] = args.port or 27017
            config["database"] = args.database or "admin"
            if args.user:
                config["user"] = args.user
            if args.auth_source:
                config["auth_source"] = args.auth_source
            if args.password_env:
                config["password_env"] = args.password_env
            elif not args.no_password and args.user:
                config["password"] = getpass.getpass("Database password: ")
    elif args.type == "redis":
        if args.uri:
            config["uri"] = args.uri
        else:
            config["host"] = args.host or "127.0.0.1"
            config["port"] = args.port or 6379
            config["db"] = args.db or 0
            if args.user:
                config["user"] = args.user
            if args.password_env:
                config["password_env"] = args.password_env
            elif not args.no_password:
                config["password"] = getpass.getpass("Redis password: ")
    else:
        for key in ["host", "port", "database", "user"]:
            value = getattr(args, key)
            if value is not None:
                config[key] = value
        if args.password_env:
            config["password_env"] = args.password_env
        elif not args.no_password:
            config["password"] = getpass.getpass("Database password: ")

    if args.type in {"oracle", "oracle11g"}:
        config["thick_mode"] = args.type == "oracle11g"
        if args.service_name:
            config["service_name"] = args.service_name
        if args.sid:
            config["sid"] = args.sid
        if args.client_lib_dir:
            config["client_lib_dir"] = args.client_lib_dir

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote local config: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
