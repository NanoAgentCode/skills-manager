from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_investment_bank_html.py"
SPEC = importlib.util.spec_from_file_location("report_renderer", SCRIPT)
assert SPEC and SPEC.loader
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class ReportValidationTests(unittest.TestCase):
    def test_checked_in_fixture_is_renderable(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "sample-report.json"
        renderer.validate_report_data(json.loads(fixture.read_text(encoding="utf-8")))

    def test_empty_report_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required data"):
            renderer.validate_report_data({})


if __name__ == "__main__":
    unittest.main()
