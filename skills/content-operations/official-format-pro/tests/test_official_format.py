import ast
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "official_format.py"


def find_officecli():
    executable = shutil.which("officecli")
    if executable:
        return executable
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate = Path(local_app_data) / "OfficeCLI" / "officecli.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def load_pure_helpers():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    wanted = {"format_date", "_parse_attachment_content"}
    nodes = [node for node in tree.body if isinstance(node, ast.Import) and any(alias.name == "re" for alias in node.names)]
    nodes.extend(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted)
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SCRIPT), "exec"), namespace)
    return namespace


class PureHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_pure_helpers()

    def test_format_date_normalizes_supported_numeric_forms(self):
        format_date = self.helpers["format_date"]
        self.assertEqual("2026年4月16日", format_date("2026-04-16"))
        self.assertEqual("2026年4月16日", format_date("2026/04/16"))

    def test_attachment_parser_splits_numbered_items_and_strips_punctuation(self):
        parse = self.helpers["_parse_attachment_content"]
        self.assertEqual(["附件：1. 方案一", "2. 方案二"], parse("1. 方案一  2. 方案二。"))


@unittest.skipUnless(importlib.util.find_spec("docx"), "python-docx is not installed")
class DocumentGenerationTests(unittest.TestCase):
    def test_generates_docx_with_title_and_body(self):
        from docx import Document

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "content.txt"
            output = Path(tmp) / "output.docx"
            source.write_text("一、工作安排\n这是正文。", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(SCRIPT), "--title", "测试通知", "--input", str(source), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            text = "\n".join(paragraph.text for paragraph in Document(output).paragraphs)
            self.assertIn("测试通知", text)
            self.assertIn("这是正文。", text)
            officecli = find_officecli()
            if officecli:
                try:
                    validation = subprocess.run(
                        [officecli, "validate", str(output)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
                    issues = subprocess.run(
                        [officecli, "view", str(output), "issues"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(0, issues.returncode, issues.stdout + issues.stderr)
                    self.assertNotIn("Empty paragraph", issues.stdout)
                finally:
                    subprocess.run(
                        [officecli, "close", str(output)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )


if __name__ == "__main__":
    unittest.main()
