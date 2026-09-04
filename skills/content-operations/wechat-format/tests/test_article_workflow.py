from __future__ import annotations

import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("wechat_article_workflow", SCRIPT_DIR / "article_workflow.py")
assert SPEC and SPEC.loader
WORKFLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORKFLOW)

FORMAT_SPEC = importlib.util.spec_from_file_location("wechat_format", SCRIPT_DIR / "format.py")
assert FORMAT_SPEC and FORMAT_SPEC.loader
FORMAT = importlib.util.module_from_spec(FORMAT_SPEC)
FORMAT_SPEC.loader.exec_module(FORMAT)


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class PolishStyleTests(unittest.TestCase):
    def test_non_interactive_polishing_requires_explicit_style(self) -> None:
        args = SimpleNamespace(
            skip_ai=False,
            preserve_content=False,
            skip_terminology=False,
            polish_style=None,
            non_interactive=True,
        )

        with self.assertRaisesRegex(SystemExit, "No default is used"):
            WORKFLOW.resolve_polish_style(args)

    def test_interactive_prompt_rejects_blank_until_user_selects(self) -> None:
        args = SimpleNamespace(
            skip_ai=False,
            preserve_content=False,
            skip_terminology=False,
            polish_style=None,
            non_interactive=False,
        )

        with mock.patch("builtins.input", side_effect=["", "invalid", "2"]) as mocked_input:
            selected = WORKFLOW.resolve_polish_style(args)

        self.assertEqual(selected, "popular-science")
        self.assertEqual(mocked_input.call_count, 3)

    def test_skipped_polishing_does_not_require_style(self) -> None:
        for skipped in ("skip_ai", "preserve_content", "skip_terminology"):
            values = {
                "skip_ai": False,
                "preserve_content": False,
                "skip_terminology": False,
                "polish_style": None,
                "non_interactive": True,
            }
            values[skipped] = True
            self.assertIsNone(WORKFLOW.resolve_polish_style(SimpleNamespace(**values)))

    def test_polish_styles_produce_distinct_audience_guidance(self) -> None:
        professional = WORKFLOW.build_terminology_prompts("Title", "Body", "professional")
        popular_science = WORKFLOW.build_terminology_prompts("Title", "Body", "popular-science")

        self.assertIn("domain knowledge", professional[0])
        self.assertIn("non-specialists", popular_science[0])
        self.assertNotEqual(professional, popular_science)


class WechatCompatibilityTests(unittest.TestCase):
    def render_bytedance_sample(self) -> str:
        markdown = "# Title\n\nBody.\n\n![Diagram](https://example.com/diagram.png)\n\n*Caption.*\n"
        html = FORMAT.md_to_html(markdown)
        html = FORMAT.inject_inline_styles(html, FORMAT.load_theme("bytedance"))
        return FORMAT.convert_image_captions(html)

    def test_bytedance_render_has_no_gradient_backgrounds(self) -> None:
        self.assertNotIn("gradient(", self.render_bytedance_sample())

    def test_bytedance_body_accents_meet_normal_text_contrast(self) -> None:
        theme = FORMAT.load_theme("bytedance")
        for style_name in ("strong", "em", "a"):
            with self.subTest(style=style_name):
                color = theme["styles"][style_name]["color"]
                self.assertGreaterEqual(contrast_ratio(color, "#ffffff"), 4.5)

    def test_styled_image_caption_is_centered_without_body_indent(self) -> None:
        rendered = self.render_bytedance_sample()
        caption = re.search(r'<p style="([^"]+)"[^>]*>Caption\.</p>', rendered)

        self.assertIsNotNone(caption)
        self.assertIn("text-align:center", caption.group(1))
        self.assertNotIn("text-indent", caption.group(1))
        self.assertIn('data-darkmode-color="#a0a0a0"', caption.group(0))


class StageMarkdownAssetsTests(unittest.TestCase):
    def test_stages_relative_and_declared_assets_with_collision_safe_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            article_dir = root / "article"
            article_images = article_dir / "images"
            extra_assets = root / "visual-assets"
            render_dir = root / "render"
            article_images.mkdir(parents=True)
            extra_assets.mkdir()

            first_image = article_images / "diagram.png"
            second_image = extra_assets / "diagram.png"
            first_image.write_bytes(b"first-image")
            second_image.write_bytes(b"second-image")
            article_path = article_dir / "article-with-visuals.md"
            article_path.write_text("# Test\n", encoding="utf-8")

            content = "\n".join(
                [
                    "![First](images/diagram.png)",
                    "![Second](diagram.png)",
                    "![Remote](https://example.com/remote.png)",
                    "![Missing](missing.png)",
                ]
            )

            rewritten, staged, unresolved = WORKFLOW.stage_markdown_assets(
                content,
                article_path,
                render_dir,
                [extra_assets],
            )

            self.assertIn("![First](images/diagram.png)", rewritten)
            self.assertIn("![Second](images/diagram-2.png)", rewritten)
            self.assertIn("![Remote](https://example.com/remote.png)", rewritten)
            self.assertIn("![Missing](missing.png)", rewritten)
            self.assertEqual(unresolved, ["missing.png"])
            self.assertEqual(len(staged), 2)
            self.assertEqual((render_dir / "images" / "diagram.png").read_bytes(), b"first-image")
            self.assertEqual((render_dir / "images" / "diagram-2.png").read_bytes(), b"second-image")

    def test_reuses_one_staged_file_for_repeated_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            article_dir = root / "article"
            render_dir = root / "render"
            article_dir.mkdir()
            image = article_dir / "figure.svg"
            image.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
            article_path = article_dir / "article.md"
            article_path.write_text("# Test\n", encoding="utf-8")

            content = "![One](figure.svg)\n![Two](figure.svg)\n"
            rewritten, staged, unresolved = WORKFLOW.stage_markdown_assets(
                content,
                article_path,
                render_dir,
                [],
            )

            self.assertEqual(rewritten.count("images/figure.svg"), 2)
            self.assertEqual(len(staged), 1)
            self.assertEqual(unresolved, [])

    def test_rejects_missing_declared_handoff_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.md"
            with self.assertRaises(SystemExit):
                WORKFLOW.require_file(str(missing), "Source notes")
            with self.assertRaises(SystemExit):
                WORKFLOW.require_directories([str(missing)], "Asset root")

    def test_strict_asset_mode_rejects_unresolved_images(self) -> None:
        WORKFLOW.enforce_asset_resolution(["images/missing.png"], strict=False)
        with self.assertRaises(SystemExit):
            WORKFLOW.enforce_asset_resolution(["images/missing.png"], strict=True)


class ArticleWorkflowIntegrationTests(unittest.TestCase):
    def test_cli_archives_upstream_artifacts_and_renders_staged_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package_dir = root / "visual-package"
            images_dir = package_dir / "images"
            output_root = root / "wechat-output"
            images_dir.mkdir(parents=True)

            article = package_dir / "article-with-visuals.md"
            article.write_text(
                "# Integration Test\n\nBody.\n\n![Figure](images/figure.png)\n\n*Caption.*\n",
                encoding="utf-8",
            )
            (images_dir / "figure.png").write_bytes(
                base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
                )
            )
            source_notes = root / "source-notes.md"
            visual_plan = package_dir / "visual-plan.md"
            source_notes.write_text("# Source Notes\n", encoding="utf-8")
            visual_plan.write_text("# Visual Plan\n", encoding="utf-8")

            command = [
                sys.executable,
                str(SCRIPT_DIR / "article_workflow.py"),
                "--input",
                str(article),
                "--source-notes",
                str(source_notes),
                "--visual-plan",
                str(visual_plan),
                "--assets-dir",
                str(images_dir),
                "--preserve-content",
                "--strict-assets",
                "--theme",
                "apple-code",
                "--no-open",
                "--non-interactive",
                "--output-root",
                str(output_root),
            ]
            result = subprocess.run(
                command,
                cwd=SKILL_DIR.parents[2],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            self.assertEqual(result.returncode, 0, (result.stdout or "") + (result.stderr or ""))

            workflow_root = output_root / "article-with-visuals"
            manifest = json.loads((workflow_root / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["preserve_content"])
            self.assertTrue(manifest["strict_assets"])
            self.assertEqual(manifest["unresolved_assets"], [])
            self.assertEqual(len(manifest["staged_assets"]), 1)
            self.assertTrue(Path(manifest["source_notes"]).is_file())
            self.assertTrue(Path(manifest["visual_plan"]).is_file())
            self.assertTrue((workflow_root / "render" / "images" / "figure.png").is_file())

            final_dir = workflow_root / "final" / "apple-code" / "article-with-visuals"
            self.assertTrue((final_dir / "preview.html").is_file())
            self.assertTrue((final_dir / "article.html").is_file())
            self.assertTrue((final_dir / "images" / "figure.png").is_file())


if __name__ == "__main__":
    unittest.main()
