# Local Dependencies

Put local database client dependencies here when a driver needs native files.

This directory ignores machine-specific database clients by default. The official Windows AMD64 `mc.exe` and Linux AMD64 `mc` binaries are intentional tracked exceptions so MinIO queries work without a separate client download on those platforms.

## Bundled MinIO Client

The MinIO wrapper discovers the bundled official client here before checking `PATH`:

- Windows AMD64: `dependencies/mc.exe`
- Linux AMD64: `dependencies/mc` (tracked as executable)

Both binaries are MinIO Client `RELEASE.2025-08-13T08-35-41Z` and were verified against the SHA-256 files from the official download server before being added. See `references/minio.md` for config fields and update guidance.

## Python wheels

Python driver wheels can be stored in:

```text
dependencies/
  python-wheels/
    *.whl
```

Install them offline with:

```powershell
..\..\..\scripts\run-python.ps1 -m pip install --no-index --find-links .\dependencies\python-wheels -r .\dependencies\requirements-offline.txt
```

Or use the helper from the skill root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_offline_dependencies.ps1
```

The repository launcher resolves Python without relying on `python` or `py` being on `PATH`. If it cannot find Python, it reports the missing Python interpreter prerequisite and the checked locations.

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
  "client_lib_dir": "D:/lark-projects/skills-manager/skills/engineering-operations/python-db-query/dependencies/instantclient_11_2"
}
```

Do not commit real database credentials or additional machine-specific client binaries. The two documented MinIO Client files are the only intentional binary exceptions.
