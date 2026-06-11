# Database Config Reference

Use JSON for connection config. Keep real config files local and ignored by git.

## SQLite

```json
{
  "type": "sqlite",
  "path": "C:/path/to/database.sqlite3",
  "read_only": true,
  "timeout_seconds": 30
}
```

## PostgreSQL

```json
{
  "type": "postgres",
  "host": "127.0.0.1",
  "port": 5432,
  "database": "app",
  "user": "readonly_user",
  "password": "replace-me",
  "schema": "public",
  "sslmode": "prefer",
  "timeout_seconds": 30
}
```

## MySQL

```json
{
  "type": "mysql",
  "host": "127.0.0.1",
  "port": 3306,
  "database": "app",
  "user": "readonly_user",
  "password": "replace-me",
  "charset": "utf8mb4",
  "timeout_seconds": 30
}
```

## SQL Server

```json
{
  "type": "sqlserver",
  "driver": "ODBC Driver 18 for SQL Server",
  "host": "127.0.0.1",
  "port": 1433,
  "database": "app",
  "user": "readonly_user",
  "password": "replace-me",
  "trust_server_certificate": true,
  "timeout_seconds": 30
}
```

## Oracle 11g

Oracle 11g normally requires Thick mode. Install the `oracledb` Python package and Oracle Instant Client on the machine running the query, then set `client_lib_dir` if the client libraries are not already on `PATH`.

This skill provides an ignored local dependency folder at `dependencies/`. You can put Oracle Instant Client there, for example `dependencies/instantclient_11_2/`, and point `client_lib_dir` to its absolute path.

Use `service_name` when the database is configured with a service:

```json
{
  "type": "oracle11g",
  "host": "127.0.0.1",
  "port": 1521,
  "service_name": "ORCL",
  "user": "readonly_user",
  "password": "replace-me",
  "thick_mode": true,
  "client_lib_dir": "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2",
  "timeout_seconds": 30
}
```

Use `sid` for older SID-based connections:

```json
{
  "type": "oracle11g",
  "host": "127.0.0.1",
  "port": 1521,
  "sid": "ORCL",
  "user": "readonly_user",
  "password": "replace-me",
  "thick_mode": true,
  "client_lib_dir": "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2",
  "timeout_seconds": 30
}
```

If the Oracle client libraries are already discoverable through `PATH`, omit `client_lib_dir`.

Use `password_env` to avoid storing the password in config:

```json
{
  "type": "oracle11g",
  "host": "127.0.0.1",
  "port": 1521,
  "service_name": "ORCL",
  "user": "readonly_user",
  "password_env": "DB_PASSWORD",
  "thick_mode": true,
  "client_lib_dir": "D:/lark-projects/skills-manager/database/python-db-query/dependencies/instantclient_11_2"
}
```

## Required Conversation Fields

If no config exists, collect only the fields needed for the selected database type.

- SQLite: database file path.
- PostgreSQL/MySQL/SQL Server: host, port, database, user, password, and SSL/trust options if needed.
- Oracle 11g: host, port, user, password, `service_name` or `sid`, and Oracle Instant Client path if it is not on `PATH`.
- MongoDB: URI, or host, port, database, optional user/password, and `auth_source`.
- Redis: URI, or host, port, db, and optional user/password.

Ask whether the user wants the config saved locally before writing it.

## MongoDB

```json
{
  "type": "mongo",
  "uri": "mongodb://mongo.local:27017/appmaster?authSource=admin",
  "database": "appmaster",
  "timeout_seconds": 30
}
```

Or split fields:

```json
{
  "type": "mongo",
  "host": "mongo.local",
  "port": 27017,
  "database": "appmaster",
  "auth_source": "admin",
  "user": "readonly_user",
  "password_env": "MONGO_PASSWORD",
  "timeout_seconds": 30
}
```

## Redis

```json
{
  "type": "redis",
  "host": "127.0.0.1",
  "port": 6379,
  "db": 0,
  "password_env": "REDIS_PASSWORD",
  "timeout_seconds": 30
}
```

URI form:

```json
{
  "type": "redis",
  "uri": "redis://:password@127.0.0.1:6379/0",
  "timeout_seconds": 30
}
```
