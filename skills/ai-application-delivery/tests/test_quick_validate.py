from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "quick_validate.py"
SPEC = importlib.util.spec_from_file_location("quick_validate", SCRIPT)
assert SPEC and SPEC.loader
quick_validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quick_validate)


def workflow() -> dict:
    return {
        "workflow": {
            "graph": {
                "nodes": [
                    {"id": "start", "data": {"type": "start"}},
                    {"id": "end", "data": {"type": "end"}},
                ],
                "edges": [
                    {
                        "id": "start-source-end-target",
                        "source": "start",
                        "sourceHandle": "source",
                        "target": "end",
                        "targetHandle": "target",
                        "type": "custom",
                        "data": {"sourceType": "start", "targetType": "end"},
                    }
                ],
            }
        }
    }


class GeneratedDslValidationTests(unittest.TestCase):
    def test_json_input_checks_edges_against_node_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workflow.json"
            path.write_text(json.dumps(workflow()), encoding="utf-8")
            validator = quick_validate.Validator()
            quick_validate.validate_workflow_input(validator, path)
            self.assertEqual([], validator.errors)

    def test_mismatched_edge_type_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workflow.json"
            payload = workflow()
            payload["workflow"]["graph"]["edges"][0]["data"]["targetType"] = "code"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validator = quick_validate.Validator()
            quick_validate.validate_workflow_input(validator, path)
            self.assertTrue(any("type metadata matches nodes" in error for error in validator.errors))


if __name__ == "__main__":
    unittest.main()
