# Local Dependencies

Put local database client dependencies here when a driver needs native files.

This directory is intentionally ignored by git because database clients can be large and may contain machine-specific binaries.

## Python wheels

Python driver wheels can be stored in:

```text
dependencies/
  python-wheels/
    *.whl
```

Install them offline with:

```powershell
$Python = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $Python -m pip install --no-index --find-links .\dependencies\python-wheels -r .\dependencies\requirements-offline.txt
```

Or use the helper from the skill root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_offline_dependencies.ps1 -Python $Python
```

The bundled `requirements-offline.txt` covers:

- Oracle 11g: `oracledb==2.5.1` plus Oracle Instant Client 11.2 or another compatible Thick mode client
- PostgreSQL: `psycopg[binary]`, `psycopg2-binary`
- MySQL: `pymysql`, `mysql-connector-python`
- SQL Server: `pyodbc`
- MongoDB: `pymongo`
- Redis: `redis`

## Oracle 11g

For Oracle 11g, place Oracle Instant Client in a subdirectory such as:

```text
dependencies/
  instantclient_11_2/
    oci.dll
    oraociicus11.dll
    ...
```

Then point `client_lib_dir` in `config.json` to the absolute path:

```json
{
  "type": "oracle11g",
  "host": "oracle-dev.lark.com",
  "port": 1521,
  "service_name": "ORCL",
  "user": "LARK_MASTER",
  "password": "replace-me",
  "thick_mode": true,
  "client_lib_dir": "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2"
}
```

Do not commit real database credentials or client binaries.
