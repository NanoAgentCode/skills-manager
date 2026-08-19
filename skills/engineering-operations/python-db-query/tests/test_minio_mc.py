from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "minio_mc.py"
INIT_CONFIG = SCRIPT.parent / "init_config.py"
spec = importlib.util.spec_from_file_location("minio_mc", SCRIPT)
minio_mc = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(minio_mc)
sys.modules["minio_mc"] = minio_mc

check_spec = importlib.util.spec_from_file_location("check_dependencies", SCRIPT.parent / "check_dependencies.py")
check_dependencies = importlib.util.module_from_spec(check_spec)
assert check_spec.loader is not None
check_spec.loader.exec_module(check_dependencies)


class MinioConfigTests(unittest.TestCase):
    def test_windows_and_linux_binary_names(self):
        self.assertEqual(["mc.exe", "mc"], minio_mc.local_binary_names("nt"))
        self.assertEqual(["mc", "mc.exe"], minio_mc.local_binary_names("posix"))

    def test_credentials_use_environment_not_command_arguments(self):
        config = {
            "type": "minio",
            "endpoint": "https://minio.example.com",
            "access_key_env": "TEST_MINIO_ACCESS",
            "secret_key_env": "TEST_MINIO_SECRET",
        }
        with patch.dict(os.environ, {"TEST_MINIO_ACCESS": "access+key", "TEST_MINIO_SECRET": "secret/@key"}):
            env = minio_mc.build_mc_environment(config)
        self.assertEqual(
            "https://access%2Bkey:secret%2F%40key@minio.example.com",
            env["MC_HOST_skillsmanager"],
        )
        self.assertEqual("true", env["MC_JSON"])
        self.assertEqual("true", env["MC_QUIET"])

    def test_endpoint_rejects_embedded_credentials_and_paths(self):
        for endpoint in ("https://user:secret@minio.example.com", "https://minio.example.com/path"):
            with self.subTest(endpoint=endpoint), self.assertRaises(SystemExit):
                minio_mc.normalize_endpoint(endpoint)

    def test_configured_relative_mc_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            binary = root / "tools" / "mc.exe"
            binary.parent.mkdir()
            binary.touch()
            binary.chmod(0o755)
            resolved = minio_mc.find_mc({"mc_path": "tools/mc.exe"}, root / "config.json")
            self.assertEqual(binary.resolve(), resolved)

    def test_dependency_check_executes_configured_mc_version(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            binary = root / ("mc.exe" if os.name == "nt" else "mc")
            binary.touch()
            binary.chmod(0o755)
            completed = subprocess.CompletedProcess([], 0, stdout="mc version RELEASE.TEST\n", stderr="")
            with patch.object(check_dependencies.subprocess, "run", return_value=completed) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    ok = check_dependencies.check_minio({"mc_path": str(binary)}, root / "config.json")
        self.assertTrue(ok)
        self.assertEqual([str(binary.resolve()), "--version"], run.call_args.args[0])

    def test_init_config_uses_environment_variable_references(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "config.json"
            result = subprocess.run(
                [
                    sys.executable,
                    os.fspath(INIT_CONFIG),
                    "--out",
                    os.fspath(output),
                    "--type",
                    "minio",
                    "--endpoint",
                    "http://127.0.0.1:9000",
                    "--access-key-env",
                    "MINIO_ACCESS_KEY",
                    "--secret-key-env",
                    "MINIO_SECRET_KEY",
                    "--mc-path",
                    "dependencies/mc.exe",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            config = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("minio", config["type"])
        self.assertEqual("MINIO_ACCESS_KEY", config["access_key_env"])
        self.assertEqual("MINIO_SECRET_KEY", config["secret_key_env"])
        self.assertNotIn("secret_key", config)


class MinioOperationTests(unittest.TestCase):
    def test_read_operations_map_to_mc(self):
        cases = [
            (argparse.Namespace(command="test-connection"), ["ls", "skillsmanager"]),
            (argparse.Namespace(command="list-buckets"), ["ls", "skillsmanager"]),
            (
                argparse.Namespace(command="list-objects", bucket="assets", prefix="images/", recursive=True),
                ["ls", "--recursive", "skillsmanager/assets/images/"],
            ),
            (
                argparse.Namespace(command="stat", bucket="assets", object="images/logo.png"),
                ["stat", "skillsmanager/assets/images/logo.png"],
            ),
        ]
        for args, expected in cases:
            with self.subTest(command=args.command):
                self.assertEqual(expected, minio_mc.build_operation(args))

    def test_download_refuses_implicit_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "existing.txt"
            destination.write_text("keep", encoding="utf-8")
            args = argparse.Namespace(
                command="download",
                bucket="assets",
                object="existing.txt",
                destination=str(destination),
                overwrite=False,
            )
            with self.assertRaises(SystemExit):
                minio_mc.build_operation(args)
            self.assertEqual("keep", destination.read_text(encoding="utf-8"))

    def test_runner_does_not_put_credentials_in_arguments(self):
        completed = subprocess.CompletedProcess([], 0, stdout='{"status":"success"}\n', stderr="")
        env = {"MC_HOST_skillsmanager": "https://access:secret@minio.example.com"}
        with patch.object(minio_mc.subprocess, "run", return_value=completed) as run:
            with contextlib.redirect_stdout(io.StringIO()):
                minio_mc.run_mc(Path("mc.exe"), ["ls", "skillsmanager"], env)
        command = run.call_args.args[0]
        self.assertNotIn("access", " ".join(command))
        self.assertNotIn("secret", " ".join(command))
        self.assertEqual(env, run.call_args.kwargs["env"])


if __name__ == "__main__":
    unittest.main()
