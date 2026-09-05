#!/usr/bin/env python3
"""Run database queries from a local config file.

Defaults to read-only query execution. Real credentials should live in a local
config file ignored by git.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import uuid
from pathlib import Path
from typing import Any, Iterable


READ_ONLY_PREFIXES = (
    "select",
    "with",
    "show",
    "describe",
    "desc",
    "explain",
    "pragma",
)

BLOCKED_WORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|merge|grant|revoke|vacuum|replace|attach|detach|load_extension|commit)\b",
    re.IGNORECASE,
)

IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.$]*$")


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        print_missing_config(path)
        raise SystemExit(2)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_missing_config(path: Path) -> None:
    print(f"Config file not found: {path}", file=sys.stderr)
    print("Create a local config.json from config.example.json, or ask the user for connection details.", file=sys.stderr)
    print("Required fields depend on database type:", file=sys.stderr)
    print("- sqlite: type, path", file=sys.stderr)
    print("- postgres/mysql/sqlserver: type, host, port, database, user, password", file=sys.stderr)
    print("- oracle11g: type, host, port, service_name or sid, user, password, client_lib_dir if needed", file=sys.stderr)


def read_sql(args: argparse.Namespace) -> str:
    if args.sql:
        return args.sql
    if args.sql_file:
        return Path(args.sql_file).read_text(encoding="utf-8")
    raise SystemExit(
        "Provide --sql/--sql-file, a metadata command, --count, or --test-connection."
    )


def normalized_db_type(config: dict[str, Any]) -> str:
    raw = str(config.get("type", "")).lower()
    aliases = {
        "postgresql": "postgres",
        "mssql": "sqlserver",
        "oracle11g": "oracle",
        "mongodb": "mongo",
    }
    return aliases.get(raw, raw)


def resolve_password(config: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(config)
    if not resolved.get("password") and resolved.get("password_env"):
        env_name = str(resolved["password_env"])
        value = os.environ.get(env_name)
        if not value:
            raise SystemExit(f"Password environment variable is not set: {env_name}")
        resolved["password"] = value
    return resolved


def validate_identifier(name: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise SystemExit(f"Unsafe table identifier: {name}")
    return name


def identifier_parts(name: str) -> list[str]:
    validate_identifier(name)
    parts = name.split(".")
    if len(parts) > 3:
        raise SystemExit(f"Unsupported qualified table identifier: {name}")
    return parts


def table_schema_parts(name: str, default_schema: str | None = None) -> tuple[str | None, str]:
    parts = identifier_parts(name)
    if len(parts) == 1:
        return default_schema, parts[0]
    return parts[-2], parts[-1]


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def metadata_sql(config: dict[str, Any], args: argparse.Namespace) -> str | None:
    dialect = normalized_db_type(config)
    if args.test_connection:
        return "select 1 as ok from dual" if dialect == "oracle" else "select 1 as ok"

    if args.list_tables:
        if dialect == "sqlite":
            return "select name as table_name from sqlite_master where type = 'table' order by name"
        if dialect == "oracle":
            return "select table_name from user_tables order by table_name"
        if dialect == "postgres":
            return (
                "select table_schema, table_name from information_schema.tables "
                "where table_type = 'BASE TABLE' and table_schema not in ('pg_catalog', 'information_schema') "
                "order by table_schema, table_name"
            )
        if dialect == "mysql":
            return "show tables"
        if dialect == "sqlserver":
            return (
                "select table_schema, table_name from information_schema.tables "
                "where table_type = 'BASE TABLE' order by table_schema, table_name"
            )

    if args.list_schemas:
        if dialect == "sqlite":
            return "pragma database_list"
        if dialect == "oracle":
            return "select username as schema_name from all_users order by username"
        return "select schema_name from information_schema.schemata order by schema_name"

    if args.list_views:
        if dialect == "sqlite":
            return "select name as view_name, sql from sqlite_master where type = 'view' order by name"
        if dialect == "oracle":
            return "select view_name, text_length from user_views order by view_name"
        if dialect in {"postgres", "mysql", "sqlserver"}:
            return (
                "select table_schema, table_name as view_name from information_schema.views "
                "order by table_schema, table_name"
            )

    if args.describe:
        table = validate_identifier(args.describe)
        schema, bare_table = table_schema_parts(table, config.get("schema"))
        if dialect == "sqlite":
            pragma_schema = f"{schema}." if schema else ""
            return f"pragma {pragma_schema}table_info({sql_literal(bare_table)})"
        if dialect == "oracle":
            if schema:
                return (
                    "select owner as table_schema, column_name, data_type, data_length, nullable "
                    "from all_tab_columns "
                    f"where owner = {sql_literal(schema.upper())} and table_name = {sql_literal(bare_table.upper())} "
                    "order by column_id"
                )
            return (
                "select column_name, data_type, data_length, nullable from user_tab_columns "
                f"where table_name = {sql_literal(bare_table.upper())} order by column_id"
            )
        if dialect in {"postgres", "mysql", "sqlserver"}:
            schema_filter = f" and table_schema = {sql_literal(schema)}" if schema else ""
            return (
                "select column_name, data_type, is_nullable from information_schema.columns "
                f"where table_name = {sql_literal(bare_table)}{schema_filter} order by ordinal_position"
            )

    if args.list_indexes:
        table = validate_identifier(args.list_indexes)
        schema, bare_table = table_schema_parts(table, config.get("schema"))
        if dialect == "sqlite":
            pragma_schema = f"{schema}." if schema else ""
            return f"pragma {pragma_schema}index_list({sql_literal(bare_table)})"
        if dialect == "oracle":
            if schema:
                return (
                    "select i.owner as table_schema, i.index_name, i.uniqueness, c.column_name, c.column_position "
                    "from all_indexes i join all_ind_columns c on c.index_owner = i.owner and c.index_name = i.index_name "
                    f"where i.table_owner = {sql_literal(schema.upper())} and i.table_name = {sql_literal(bare_table.upper())} "
                    "order by i.index_name, c.column_position"
                )
            return (
                "select i.index_name, i.uniqueness, c.column_name, c.column_position "
                "from user_indexes i join user_ind_columns c on c.index_name = i.index_name "
                f"where i.table_name = {sql_literal(bare_table.upper())} order by i.index_name, c.column_position"
            )
        if dialect == "postgres":
            schema_filter = f" and schemaname = {sql_literal(schema)}" if schema else ""
            return (
                "select schemaname as table_schema, indexname as index_name, indexdef "
                f"from pg_indexes where tablename = {sql_literal(bare_table)}{schema_filter} "
                "order by schemaname, indexname"
            )
        if dialect == "mysql":
            selected_schema = schema or config.get("database")
            schema_filter = f" and table_schema = {sql_literal(str(selected_schema))}" if selected_schema else ""
            return (
                "select table_schema, index_name, non_unique, column_name, seq_in_index "
                "from information_schema.statistics "
                f"where table_name = {sql_literal(bare_table)}{schema_filter} order by index_name, seq_in_index"
            )
        if dialect == "sqlserver":
            schema_filter = f" and s.name = {sql_literal(schema)}" if schema else ""
            return (
                "select s.name as table_schema, i.name as index_name, i.is_unique, i.type_desc, "
                "c.name as column_name, ic.key_ordinal "
                "from sys.indexes i join sys.tables t on t.object_id = i.object_id "
                "join sys.schemas s on s.schema_id = t.schema_id "
                "left join sys.index_columns ic on ic.object_id = i.object_id and ic.index_id = i.index_id "
                "left join sys.columns c on c.object_id = ic.object_id and c.column_id = ic.column_id "
                f"where t.name = {sql_literal(bare_table)}{schema_filter} and i.name is not null "
                "order by s.name, i.name, ic.key_ordinal"
            )

    if args.primary_key:
        table = validate_identifier(args.primary_key)
        schema, bare_table = table_schema_parts(table, config.get("schema"))
        if dialect == "sqlite":
            schema_arg = f", {sql_literal(schema)}" if schema else ""
            return (
                "select name as column_name, pk as key_ordinal from pragma_table_info"
                f"({sql_literal(bare_table)}{schema_arg}) where pk > 0 order by pk"
            )
        if dialect == "oracle":
            owner_filter = f" and c.owner = {sql_literal(schema.upper())}" if schema else ""
            if schema:
                join_condition = "cc.constraint_name = c.constraint_name and cc.owner = c.owner"
                scope = "all_constraints"
                columns = "all_cons_columns"
            else:
                join_condition = "cc.constraint_name = c.constraint_name"
                scope = "user_constraints"
                columns = "user_cons_columns"
            return (
                "select cc.column_name, cc.position as key_ordinal "
                f"from {scope} c join {columns} cc on {join_condition} "
                f"where c.constraint_type = 'P' and c.table_name = {sql_literal(bare_table.upper())}{owner_filter} "
                "order by cc.position"
            )
        schema_filter = f" and tc.table_schema = {sql_literal(schema)}" if schema else ""
        return (
            "select kcu.column_name, kcu.ordinal_position as key_ordinal "
            "from information_schema.table_constraints tc join information_schema.key_column_usage kcu "
            "on kcu.constraint_name = tc.constraint_name and kcu.table_schema = tc.table_schema "
            "and kcu.table_name = tc.table_name "
            f"where tc.constraint_type = 'PRIMARY KEY' and tc.table_name = {sql_literal(bare_table)}{schema_filter} "
            "order by kcu.ordinal_position"
        )

    if args.count:
        table = validate_identifier(args.count)
        return f"select count(*) as row_count from {table}"

    return None


def is_document_or_kv(config: dict[str, Any]) -> bool:
    return normalized_db_type(config) in {"mongo", "redis"}


def assert_query_allowed(sql: str, allow_write: bool) -> None:
    if allow_write:
        return
    stripped = strip_sql_comments(sql).strip().lower()
    if not stripped:
        raise SystemExit("SQL is empty.")
    # A terminal semicolon is harmless, but accepting multiple statements turns a
    # read-only prefix check into a write primitive. Drivers differ in whether
    # they accept multiple statements, so reject them before connecting.
    statement = stripped[:-1].rstrip() if stripped.endswith(";") else stripped
    if ";" in statement:
        raise SystemExit("Blocked multiple SQL statements. Submit one read-only statement at a time.")
    if not statement.startswith(READ_ONLY_PREFIXES):
        raise SystemExit("Blocked non-read-only SQL. Pass --allow-write only after explicit user approval.")
    if BLOCKED_WORDS.search(statement) or re.search(r"\bselect\b[\s\S]*\binto\b", statement):
        raise SystemExit("Blocked SQL containing write or DDL keyword. Pass --allow-write only after explicit user approval.")
    if statement.startswith("pragma") and ("=" in statement or re.search(r"\b(writable_schema|journal_mode|foreign_keys)\b", statement)):
        raise SystemExit("Blocked state-changing PRAGMA. Pass --allow-write only after explicit user approval.")


def strip_sql_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    lines = []
    for line in sql.splitlines():
        lines.append(re.sub(r"--.*$", "", line))
    return "\n".join(lines)


def connect(config: dict[str, Any]):
    db_type = str(config.get("type", "")).lower()
    timeout = int(config.get("timeout_seconds", 30))
    if db_type in {"mongo", "mongodb"}:
        return connect_mongo(config, timeout)
    if db_type == "redis":
        return connect_redis(config, timeout)
    if db_type == "sqlite":
        return connect_sqlite(config, timeout)
    if db_type in {"postgres", "postgresql"}:
        return connect_postgres(config, timeout)
    if db_type == "mysql":
        return connect_mysql(config, timeout)
    if db_type in {"sqlserver", "mssql"}:
        return connect_sqlserver(config, timeout)
    if db_type in {"oracle", "oracle11g"}:
        return connect_oracle(config, timeout)
    raise SystemExit(f"Unsupported database type: {db_type}")


def connect_mongo(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        from pymongo import MongoClient  # type: ignore
    except ModuleNotFoundError:
        raise SystemExit("MongoDB driver missing. Install pymongo after user approval.")

    if config.get("uri"):
        uri = str(config["uri"])
    else:
        host = config.get("host", "127.0.0.1")
        port = int(config.get("port", 27017))
        database = config.get("database", "admin")
        auth_source = config.get("auth_source") or config.get("authSource")
        user = config.get("user")
        password = config.get("password")
        auth_part = f"{user}:{password}@" if user and password else ""
        uri = f"mongodb://{auth_part}{host}:{port}/{database}"
        if auth_source:
            uri += f"?authSource={auth_source}"
    return MongoClient(uri, serverSelectionTimeoutMS=timeout * 1000)


def connect_redis(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        import redis  # type: ignore
    except ModuleNotFoundError:
        raise SystemExit("Redis driver missing. Install redis after user approval.")

    if config.get("uri"):
        return redis.Redis.from_url(
            str(config["uri"]),
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            decode_responses=True,
            protocol=int(config.get("protocol", 2)),
        )
    return redis.Redis(
        host=config.get("host", "127.0.0.1"),
        port=int(config.get("port", 6379)),
        db=int(config.get("db", 0)),
        username=config.get("user") or config.get("username"),
        password=config.get("password"),
        socket_connect_timeout=timeout,
        socket_timeout=timeout,
        decode_responses=True,
        protocol=int(config.get("protocol", 2)),
    )


def connect_sqlite(config: dict[str, Any], timeout: int):
    db_path = config.get("path") or config.get("database")
    if not db_path:
        raise SystemExit("SQLite config requires 'path'.")
    uri = False
    target = str(db_path)
    if config.get("read_only", True):
        resolved = Path(target).expanduser().resolve()
        target = f"file:{resolved.as_posix()}?mode=ro"
        uri = True
    conn = sqlite3.connect(target, timeout=timeout, uri=uri)
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        import psycopg  # type: ignore

        return psycopg.connect(
            host=config.get("host"),
            port=config.get("port", 5432),
            dbname=config.get("database") or config.get("dbname"),
            user=config.get("user"),
            password=config.get("password"),
            sslmode=config.get("sslmode", "prefer"),
            connect_timeout=timeout,
        )
    except ModuleNotFoundError:
        try:
            import psycopg2  # type: ignore

            return psycopg2.connect(
                host=config.get("host"),
                port=config.get("port", 5432),
                dbname=config.get("database") or config.get("dbname"),
                user=config.get("user"),
                password=config.get("password"),
                sslmode=config.get("sslmode", "prefer"),
                connect_timeout=timeout,
            )
        except ModuleNotFoundError:
            raise SystemExit("PostgreSQL driver missing. Install psycopg or psycopg2 after user approval.")


def connect_mysql(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        import pymysql  # type: ignore

        return pymysql.connect(
            host=config.get("host"),
            port=int(config.get("port", 3306)),
            database=config.get("database"),
            user=config.get("user"),
            password=config.get("password"),
            charset=config.get("charset", "utf8mb4"),
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except ModuleNotFoundError:
        try:
            import mysql.connector  # type: ignore

            return mysql.connector.connect(
                host=config.get("host"),
                port=int(config.get("port", 3306)),
                database=config.get("database"),
                user=config.get("user"),
                password=config.get("password"),
                charset=config.get("charset", "utf8mb4"),
                connection_timeout=timeout,
            )
        except ModuleNotFoundError:
            raise SystemExit("MySQL driver missing. Install pymysql or mysql-connector-python after user approval.")


def connect_sqlserver(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        import pyodbc  # type: ignore
    except ModuleNotFoundError:
        raise SystemExit("SQL Server driver missing. Install pyodbc after user approval.")

    driver = config.get("driver", "ODBC Driver 18 for SQL Server")
    server = config.get("host", "127.0.0.1")
    port = config.get("port", 1433)
    trust = "yes" if config.get("trust_server_certificate", False) else "no"
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server},{port};DATABASE={config.get('database')};"
        f"UID={config.get('user')};PWD={config.get('password')};"
        f"TrustServerCertificate={trust};Connection Timeout={timeout};"
    )
    return pyodbc.connect(conn_str)


def connect_oracle(config: dict[str, Any], timeout: int):
    config = resolve_password(config)
    try:
        import oracledb  # type: ignore

        if config.get("thick_mode", str(config.get("type", "")).lower() == "oracle11g"):
            client_lib_dir = config.get("client_lib_dir")
            try:
                if client_lib_dir:
                    oracledb.init_oracle_client(lib_dir=client_lib_dir)
                else:
                    oracledb.init_oracle_client()
            except Exception as exc:
                # Oracle client can only be initialized once per process; ignore
                # the common "already initialized" case, but surface real setup errors.
                if "already been initialized" not in str(exc).lower():
                    raise SystemExit(f"Oracle Thick mode initialization failed: {exc}")

        dsn = build_oracle_dsn(oracledb, config)
        conn = oracledb.connect(
            user=config.get("user"),
            password=config.get("password"),
            dsn=dsn,
        )
        try:
            conn.call_timeout = timeout * 1000
        except Exception:
            pass
        return conn
    except ModuleNotFoundError:
        try:
            import cx_Oracle  # type: ignore

            dsn = build_oracle_dsn(cx_Oracle, config)
            return cx_Oracle.connect(
                user=config.get("user"),
                password=config.get("password"),
                dsn=dsn,
                encoding=config.get("encoding", "UTF-8"),
                nencoding=config.get("nencoding", "UTF-8"),
            )
        except ModuleNotFoundError:
            raise SystemExit(
                "Oracle driver missing. Install the oracledb Python package and Oracle Instant Client for Oracle 11g, "
                "or install cx_Oracle after user approval."
            )


def build_oracle_dsn(driver_module, config: dict[str, Any]) -> str:
    if config.get("dsn"):
        return str(config["dsn"])

    host = config.get("host")
    port = int(config.get("port", 1521))
    service_name = config.get("service_name")
    sid = config.get("sid")
    if not host:
        raise SystemExit("Oracle config requires 'host' or 'dsn'.")
    if service_name:
        return driver_module.makedsn(host, port, service_name=service_name)
    if sid:
        return driver_module.makedsn(host, port, sid=sid)
    raise SystemExit("Oracle config requires 'service_name', 'sid', or 'dsn'.")


def execute_query(conn, sql: str, params: dict[str, Any] | list[Any] | None, limit: int | None, allow_write: bool = False):
    cur = conn.cursor()
    cur.execute(sql, params or {})
    if cur.description is None:
        if allow_write:
            conn.commit()
        else:
            conn.rollback()
        return [], []
    columns = [col[0] for col in cur.description]
    rows = cur.fetchmany(limit) if limit else cur.fetchall()
    if not allow_write:
        try:
            conn.rollback()
        except Exception:
            pass
    return columns, normalize_rows(rows, columns)


def begin_read_only_session(conn, dialect: str, enabled: bool) -> None:
    """Ask engines that support it to enforce a read-only transaction server-side."""
    if not enabled or dialect in {"sqlite", "sqlserver"}:
        return
    statements = {
        "postgres": "SET TRANSACTION READ ONLY",
        "mysql": "SET SESSION TRANSACTION READ ONLY",
        "oracle": "SET TRANSACTION READ ONLY",
    }
    statement = statements.get(dialect)
    if not statement:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(statement)
    finally:
        try:
            cursor.close()
        except Exception:
            pass


def execute_explain(
    conn,
    dialect: str,
    sql: str,
    params: dict[str, Any] | list[Any] | None,
    limit: int | None,
):
    if dialect == "sqlite":
        return execute_query(conn, f"explain query plan {sql}", params, limit)
    if dialect == "postgres":
        return execute_query(conn, f"explain (format json) {sql}", params, limit)
    if dialect == "mysql":
        return execute_query(conn, f"explain format=json {sql}", params, limit)
    if dialect == "sqlserver":
        cur = conn.cursor()
        try:
            cur.execute("set showplan_text on")
            cur.execute(sql, params or {})
            columns = [col[0] for col in cur.description]
            rows = cur.fetchall()
            if limit:
                rows = rows[:limit]
            return columns, normalize_rows(rows, columns)
        finally:
            try:
                cur.execute("set showplan_text off")
            except Exception:
                pass
    if dialect == "oracle":
        statement_id = f"PYDB_{uuid.uuid4().hex[:20].upper()}"
        cur = conn.cursor()
        try:
            cur.execute(f"explain plan set statement_id = {sql_literal(statement_id)} for {sql}", params or {})
            cur.execute(
                "select plan_table_output from table(dbms_xplan.display('PLAN_TABLE', :statement_id, 'BASIC +PREDICATE'))",
                {"statement_id": statement_id},
            )
            columns = [col[0] for col in cur.description]
            rows = cur.fetchmany(limit) if limit else cur.fetchall()
            return columns, normalize_rows(rows, columns)
        finally:
            try:
                cur.execute("delete from plan_table where statement_id = :statement_id", {"statement_id": statement_id})
                conn.rollback()
            except Exception:
                pass
    raise SystemExit(f"Execution plans are not supported for database type: {dialect}")


def normalize_rows(rows: Iterable[Any], columns: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            out.append(row)
        elif hasattr(row, "keys"):
            out.append({key: row[key] for key in row.keys()})
        else:
            out.append({columns[i]: row[i] for i in range(len(columns))})
    return out


def write_output(rows: list[dict[str, Any]], columns: list[str], args: argparse.Namespace) -> None:
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "csv":
            with out_path.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
        else:
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2, default=str)
        print(f"Wrote {len(rows)} row(s) to {out_path}")
        return

    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    elif args.format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    else:
        print_table(rows, columns)


def print_table(rows: list[dict[str, Any]], columns: list[str]) -> None:
    if not columns:
        print("Query executed. No result set.")
        return
    if not rows:
        print(" | ".join(columns))
        print("-+-".join("-" * len(col) for col in columns))
        print("\n0 row(s)")
        return
    widths = {col: min(max(len(col), *(len(str(row.get(col, ""))) for row in rows)), 48) for col in columns}
    print(" | ".join(col.ljust(widths[col]) for col in columns))
    print("-+-".join("-" * widths[col] for col in columns))
    for row in rows:
        cells = []
        for col in columns:
            value = str(row.get(col, ""))
            if len(value) > widths[col]:
                value = value[: widths[col] - 1] + "…"
            cells.append(value.ljust(widths[col]))
        print(" | ".join(cells))
    print(f"\n{len(rows)} row(s)")


def parse_params(raw: str | None):
    if not raw:
        return None
    return json.loads(raw)


def parse_json_arg(raw: str | None, default):
    if raw is None:
        return default
    return json.loads(raw)


def run_mongo(client, config: dict[str, Any], args: argparse.Namespace) -> tuple[list[str], list[dict[str, Any]]]:
    database_name = config.get("database") or config.get("db") or "admin"
    db = client.get_database(str(database_name))

    if args.test_connection:
        result = client.admin.command("ping")
        return ["ok"], [{"ok": result.get("ok")}]
    if args.mongo_list_collections or args.list_tables:
        names = db.list_collection_names()
        return ["collection_name"], [{"collection_name": name} for name in names[: args.limit or len(names)]]
    if args.mongo_count:
        collection = validate_identifier(args.mongo_count)
        query = parse_json_arg(args.filter, {})
        return ["collection", "count"], [{"collection": collection, "count": db[collection].count_documents(query)}]
    if args.mongo_find:
        collection = validate_identifier(args.mongo_find)
        query = parse_json_arg(args.filter, {})
        projection = parse_json_arg(args.projection, None)
        cursor = db[collection].find(query, projection).limit(args.limit or 100)
        rows = [dict(row) for row in cursor]
        columns = sorted({key for row in rows for key in row.keys()})
        return columns, rows
    if args.mongo_insert_one:
        require_write(args.allow_write, "MongoDB insert_one")
        collection = validate_identifier(args.mongo_insert_one)
        document = parse_json_arg(args.document, None)
        if not isinstance(document, dict):
            raise SystemExit("--document must be a JSON object for --mongo-insert-one")
        result = db[collection].insert_one(document)
        return ["inserted_id"], [{"inserted_id": str(result.inserted_id)}]
    if args.mongo_update_many:
        require_write(args.allow_write, "MongoDB update_many")
        collection = validate_identifier(args.mongo_update_many)
        query = parse_json_arg(args.filter, {})
        update = parse_json_arg(args.update, None)
        if not isinstance(update, dict):
            raise SystemExit("--update must be a JSON object for --mongo-update-many")
        result = db[collection].update_many(query, update)
        return ["matched_count", "modified_count"], [{"matched_count": result.matched_count, "modified_count": result.modified_count}]
    if args.mongo_delete_many:
        require_write(args.allow_write, "MongoDB delete_many")
        collection = validate_identifier(args.mongo_delete_many)
        query = parse_json_arg(args.filter, {})
        result = db[collection].delete_many(query)
        return ["deleted_count"], [{"deleted_count": result.deleted_count}]
    raise SystemExit("Provide a MongoDB command such as --test-connection, --mongo-list-collections, --mongo-find, or --mongo-count.")


def run_redis(client, args: argparse.Namespace) -> tuple[list[str], list[dict[str, Any]]]:
    if args.test_connection or args.redis_ping:
        return ["ping"], [{"ping": client.ping()}]
    if args.redis_dbsize:
        return ["dbsize"], [{"dbsize": client.dbsize()}]
    if args.redis_scan:
        keys = []
        for key in client.scan_iter(match=args.redis_scan, count=args.limit or 100):
            keys.append(key)
            if args.limit and len(keys) >= args.limit:
                break
        return ["key"], [{"key": key} for key in keys]
    if args.redis_get:
        value = client.get(args.redis_get)
        return ["key", "value"], [{"key": args.redis_get, "value": value}]
    if args.redis_ttl:
        return ["key", "ttl"], [{"key": args.redis_ttl, "ttl": client.ttl(args.redis_ttl)}]
    if args.redis_set:
        require_write(args.allow_write, "Redis set")
        if args.value is None:
            raise SystemExit("--value is required for --redis-set")
        return ["ok"], [{"ok": client.set(args.redis_set, args.value)}]
    if args.redis_del:
        require_write(args.allow_write, "Redis del")
        return ["deleted"], [{"deleted": client.delete(args.redis_del)}]
    raise SystemExit("Provide a Redis command such as --test-connection, --redis-dbsize, --redis-scan, or --redis-get.")


def require_write(allow_write: bool, operation: str) -> None:
    if not allow_write:
        raise SystemExit(f"Blocked write operation: {operation}. Pass --allow-write only after explicit user approval.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a database query using a local JSON config file.")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.json"))
    parser.add_argument("--sql")
    parser.add_argument("--sql-file")
    parser.add_argument("--list-tables", action="store_true", help="List tables visible to the configured user.")
    parser.add_argument("--list-schemas", action="store_true", help="List schemas or SQLite attached databases.")
    parser.add_argument("--list-views", action="store_true", help="List views visible to the configured user.")
    parser.add_argument("--describe", metavar="TABLE", help="Describe columns for a table.")
    parser.add_argument("--list-indexes", metavar="TABLE", help="List indexes and indexed columns for a table.")
    parser.add_argument("--primary-key", metavar="TABLE", help="Show primary-key columns for a table.")
    parser.add_argument("--explain", action="store_true", help="Show the execution plan for --sql or --sql-file without running it.")
    parser.add_argument("--count", metavar="TABLE", help="Count rows in a table.")
    parser.add_argument("--test-connection", action="store_true", help="Run a minimal connection test query.")
    parser.add_argument("--params", help="JSON object or array of query parameters.")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--out")
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument("--mongo-list-collections", action="store_true")
    parser.add_argument("--mongo-find", metavar="COLLECTION")
    parser.add_argument("--mongo-count", metavar="COLLECTION")
    parser.add_argument("--mongo-insert-one", metavar="COLLECTION")
    parser.add_argument("--mongo-update-many", metavar="COLLECTION")
    parser.add_argument("--mongo-delete-many", metavar="COLLECTION")
    parser.add_argument("--filter", help="MongoDB JSON filter object.")
    parser.add_argument("--projection", help="MongoDB JSON projection object.")
    parser.add_argument("--document", help="MongoDB JSON document for insert.")
    parser.add_argument("--update", help="MongoDB JSON update document.")
    parser.add_argument("--redis-ping", action="store_true")
    parser.add_argument("--redis-dbsize", action="store_true")
    parser.add_argument("--redis-scan", metavar="PATTERN")
    parser.add_argument("--redis-get", metavar="KEY")
    parser.add_argument("--redis-ttl", metavar="KEY")
    parser.add_argument("--redis-set", metavar="KEY")
    parser.add_argument("--redis-del", metavar="KEY")
    parser.add_argument("--value", help="Value for Redis set.")
    args = parser.parse_args()

    metadata_commands = [
        args.list_tables,
        args.list_schemas,
        args.list_views,
        bool(args.describe),
        bool(args.list_indexes),
        bool(args.primary_key),
        bool(args.count),
        args.test_connection,
    ]
    if sum(bool(command) for command in metadata_commands) > 1:
        parser.error("Choose only one metadata, count, or connection-test command at a time.")
    if (args.sql or args.sql_file) and any(metadata_commands):
        parser.error("Do not combine --sql/--sql-file with a metadata, count, or connection-test command.")
    if args.sql and args.sql_file:
        parser.error("Choose either --sql or --sql-file, not both.")
    if args.explain and args.allow_write:
        parser.error("--explain cannot be combined with --allow-write.")

    config = load_config(Path(args.config))
    if is_document_or_kv(config):
        relational_only = [args.list_schemas, args.list_views, args.describe, args.list_indexes, args.primary_key, args.explain]
        if any(relational_only):
            raise SystemExit("Schemas, views, indexes, primary keys, and SQL execution plans require a relational database config.")
        conn = connect(config)
        try:
            if normalized_db_type(config) == "mongo":
                columns, rows = run_mongo(conn, config, args)
            else:
                columns, rows = run_redis(conn, args)
            write_output(rows, columns, args)
        finally:
            conn.close()
        return 0

    if args.explain:
        sql = read_sql(args)
        assert_query_allowed(sql, False)
        params = parse_params(args.params)
        conn = connect(config)
        try:
            dialect = normalized_db_type(config)
            # Oracle EXPLAIN PLAN writes a session-local PLAN_TABLE entry and
            # rolls it back in execute_explain, so a read-only transaction would
            # make that supported inspection path fail.
            begin_read_only_session(conn, dialect, dialect != "oracle")
            columns, rows = execute_explain(conn, dialect, sql, params, args.limit)
            write_output(rows, columns, args)
        finally:
            conn.close()
        return 0

    sql = metadata_sql(config, args) or read_sql(args)
    assert_query_allowed(sql, args.allow_write)
    params = parse_params(args.params)
    conn = connect(config)
    try:
        begin_read_only_session(conn, normalized_db_type(config), not args.allow_write)
        columns, rows = execute_query(conn, sql, params, args.limit, allow_write=args.allow_write)
        write_output(rows, columns, args)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
