from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "query_db.py"

spec = importlib.util.spec_from_file_location("query_db", SCRIPT)
query_db = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(query_db)


def metadata_args(**overrides):
    values = {
        "test_connection": False,
        "list_tables": False,
        "list_schemas": False,
        "list_views": False,
        "describe": None,
        "list_indexes": None,
        "primary_key": None,
        "count": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class MetadataSqlTests(unittest.TestCase):
    def test_schema_queries_cover_relational_dialects(self):
        args = metadata_args(list_schemas=True)
        for dialect in ("sqlite", "postgres", "mysql", "sqlserver", "oracle"):
            with self.subTest(dialect=dialect):
                sql = query_db.metadata_sql({"type": dialect}, args)
                self.assertIsInstance(sql, str)
                self.assertTrue(sql)

    def test_qualified_table_filters_schema(self):
        args = metadata_args(list_indexes="audit.events")
        for dialect in ("postgres", "mysql", "sqlserver", "oracle"):
            with self.subTest(dialect=dialect):
                sql = query_db.metadata_sql({"type": dialect}, args).lower()
                self.assertIn("audit", sql)
                self.assertIn("events", sql)

    def test_primary_key_queries_cover_relational_dialects(self):
        args = metadata_args(primary_key="users")
        for dialect in ("sqlite", "postgres", "mysql", "sqlserver", "oracle"):
            with self.subTest(dialect=dialect):
                sql = query_db.metadata_sql({"type": dialect}, args)
                self.assertIn("key_ordinal", sql.lower())

    def test_information_schema_primary_key_join_is_table_scoped(self):
        args = metadata_args(primary_key="users")
        for dialect in ("postgres", "mysql", "sqlserver"):
            with self.subTest(dialect=dialect):
                sql = query_db.metadata_sql({"type": dialect}, args).lower()
                self.assertIn("kcu.table_name = tc.table_name", sql)


class ReadOnlyGuardTests(unittest.TestCase):
    def test_blocks_side_effects_that_start_with_select_or_pragma(self):
        for sql in (
            "select * into copied_users from users",
            "select 1; commit",
            "pragma user_version = 123",
        ):
            with self.subTest(sql=sql), self.assertRaises(SystemExit):
                query_db.assert_query_allowed(sql, allow_write=False)

    def test_allows_one_select_with_a_terminal_semicolon(self):
        query_db.assert_query_allowed("select 1;", allow_write=False)


class SqliteEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.db_path = root / "sample.sqlite3"
        self.config_path = root / "config.json"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(
                """
                create table users (id integer primary key, email text not null);
                create unique index idx_users_email on users(email);
                create view active_users as select id, email from users;
                """
            )
            conn.commit()
        finally:
            conn.close()
        self.config_path.write_text(
            json.dumps({"type": "sqlite", "path": str(self.db_path), "read_only": True}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_query(self, *args: str):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.config_path), *args, "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_metadata_and_explain_commands(self):
        schemas = self.run_query("--list-schemas")
        self.assertEqual("main", schemas[0]["name"])

        views = self.run_query("--list-views")
        self.assertEqual("active_users", views[0]["view_name"])

        indexes = self.run_query("--list-indexes", "users")
        self.assertEqual("idx_users_email", indexes[0]["name"])

        primary_key = self.run_query("--primary-key", "users")
        self.assertEqual({"column_name": "id", "key_ordinal": 1}, primary_key[0])

        plan = self.run_query("--explain", "--sql", "select * from users where email = 'a@example.com'")
        self.assertIn("idx_users_email", plan[0]["detail"])


if __name__ == "__main__":
    unittest.main()
