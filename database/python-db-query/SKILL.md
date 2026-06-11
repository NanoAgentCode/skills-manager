---
name: python-db-query
description: Use when Codex needs to run database queries with Python, inspect query results, export query output, or help configure a database connection. Supports config-file based connection management; if no config exists, collect database type, host/path, credentials, and database name from the user through conversation before running queries.
---

# Python DB Query

## Overview

Use this skill to run SQL queries through `scripts/query_db.py` while keeping database connection settings in a local config file.

Do not commit real credentials. The skill includes `config.example.json`; create a local `config.json` or another ignored config file for actual connections.

## Workflow

1. Confirm the query goal and target database.
2. Look for a config file in this order:
   - User-provided `--config` path.
   - `database/python-db-query/config.json`.
   - A project-local config path the user names.
3. If no config exists, ask the user for the required connection fields:
   - `type`: `sqlite`, `postgres`, `mysql`, `sqlserver`, `oracle`, `oracle11g`, `mongo`, or `redis`.
   - Host/port/database/user/password for server databases, or `path` for SQLite.
   - Optional schema and SSL/options if needed.
4. Save real settings only to an ignored local config file after the user provides them.
5. Optionally run `scripts/check_dependencies.py --config .\config.json` before the first connection.
6. Run the query with `scripts/query_db.py`.
7. Summarize results without exposing credentials.

## Safety Rules

- Default to read-only SQL. The script blocks write statements unless `--allow-write` is explicitly passed.
- Do not print passwords, tokens, DSNs with credentials, or full config contents in final answers.
- Prefer `password_env` over plain `password` when users can set an environment variable.
- Ask before running potentially expensive queries, broad table scans, or write operations.
- Prefer `--limit` for exploratory queries.
- For unknown schemas, first query metadata tables or run small sample queries.

## Config

Start from:

```powershell
Copy-Item .\config.example.json .\config.json
```

Then edit `config.json` locally. See `references/config.md` for config examples and field descriptions.

The skill `.gitignore` ignores:

- `config.json`
- `config.*.json`
- `.env`
- `outputs/`

Native client binaries can be placed under `dependencies/`. That directory ignores everything except its README and `.gitignore`, so Oracle Instant Client or other local database clients do not get committed.

Initialize a config without echoing the password:

```powershell
python .\scripts\init_config.py --type oracle11g --host oracle-dev.lark.com --port 1521 --service-name ORCL --user LARK_MASTER --client-lib-dir "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2"
```

Or use an environment variable instead of writing a password:

```powershell
$env:DB_PASSWORD="..."
python .\scripts\init_config.py --type oracle11g --host oracle-dev.lark.com --port 1521 --service-name ORCL --user LARK_MASTER --password-env DB_PASSWORD --client-lib-dir "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2"
```

Install bundled Python wheels offline:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_offline_dependencies.ps1 -Python python
```

Check dependencies:

```powershell
python .\scripts\check_dependencies.py --config .\config.json
```

## Query Examples

Run inline SQL:

```powershell
python .\scripts\query_db.py --config .\config.json --sql "select * from users limit 10"
```

Run SQL from a file:

```powershell
python .\scripts\query_db.py --config .\config.json --sql-file .\queries\active_users.sql --format table
```

Export JSON:

```powershell
python .\scripts\query_db.py --config .\config.json --sql "select id, name from users" --format json --out .\outputs\users.json
```

Export CSV:

```powershell
python .\scripts\query_db.py --config .\config.json --sql "select * from orders limit 100" --format csv --out .\outputs\orders.csv
```

List tables:

```powershell
python .\scripts\query_db.py --config .\config.json --list-tables
```

Describe a table:

```powershell
python .\scripts\query_db.py --config .\config.json --describe FLOW_TOOL_NODE
```

Count a table:

```powershell
python .\scripts\query_db.py --config .\config.json --count FLOW_TOOL_NODE
```

Test a connection:

```powershell
python .\scripts\query_db.py --config .\config.json --test-connection
```

MongoDB examples:

```powershell
python .\scripts\query_db.py --config .\config.json --test-connection
python .\scripts\query_db.py --config .\config.json --mongo-list-collections
python .\scripts\query_db.py --config .\config.json --mongo-count TOPO
python .\scripts\query_db.py --config .\config.json --mongo-find TOPO --filter "{}" --limit 5 --format json
```

MongoDB writes require `--allow-write`:

```powershell
python .\scripts\query_db.py --config .\config.json --mongo-insert-one TOPO --document "{""name"":""demo""}" --allow-write
```

Redis examples:

```powershell
python .\scripts\query_db.py --config .\config.json --test-connection
python .\scripts\query_db.py --config .\config.json --redis-dbsize
python .\scripts\query_db.py --config .\config.json --redis-scan "*" --limit 20
python .\scripts\query_db.py --config .\config.json --redis-get my-key
```

Redis writes require `--allow-write`:

```powershell
python .\scripts\query_db.py --config .\config.json --redis-set my-key my-value --allow-write
```

If the current machine does not expose `python`, use the active Python executable available in the environment.

## Driver Notes

- SQLite uses Python's built-in `sqlite3`.
- PostgreSQL requires either `psycopg` or `psycopg2`.
- MySQL requires either `pymysql` or `mysql-connector-python`.
- SQL Server requires `pyodbc`.
- Oracle 11g requires `oracledb==2.5.1` in Thick mode with Oracle Instant Client 11.2 or another compatible client, or the legacy `cx_Oracle` driver.
- MongoDB requires `pymongo`.
- Redis requires `redis`.

If a driver is missing, do not install automatically. Tell the user which package is required and ask before installing dependencies.
