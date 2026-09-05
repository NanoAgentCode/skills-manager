from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "subtitle_to_markdown.py"
SPEC = importlib.util.spec_from_file_location("subtitle_to_markdown", SCRIPT)
assert SPEC and SPEC.loader
subtitle_to_markdown = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subtitle_to_markdown)


class SubtitleConverterTests(unittest.TestCase):
    def test_reads_short_vtt_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.vtt"
            source.write_text("WEBVTT\n\n00:01.250 --> 00:03.000\n短时间戳字幕\n", encoding="utf-8")
            self.assertEqual([(1, "短时间戳字幕")], subtitle_to_markdown.read_cues(source))

    def test_reads_ass_ttml_and_youtube_json3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ass = root / "source.ass"
            ass.write_text("Dialogue: 0,0:00:02.00,0:00:03.00,Default,,0,0,0,,{\\i1}ASS 字幕\\N第二行", encoding="utf-8")
            ttml = root / "source.ttml"
            ttml.write_text('<tt><body><p begin="00:00:04.000">TTML 字幕</p></body></tt>', encoding="utf-8")
            json3 = root / "source.json3"
            json3.write_text(json.dumps({"events": [{"tStartMs": 5500, "segs": [{"utf8": "JSON3 字幕"}]}]}), encoding="utf-8")
            self.assertEqual([(2, "ASS 字幕 第二行")], subtitle_to_markdown.read_cues(ass))
            self.assertEqual([(4, "TTML 字幕")], subtitle_to_markdown.read_cues(ttml))
            self.assertEqual([(5, "JSON3 字幕")], subtitle_to_markdown.read_cues(json3))

    def test_empty_cues_are_not_rendered_as_a_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "empty.vtt"
            output = Path(tmp) / "transcript.md"
            source.write_text("WEBVTT\n", encoding="utf-8")
            self.assertEqual([], subtitle_to_markdown.read_cues(source))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("No usable subtitle cues", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
