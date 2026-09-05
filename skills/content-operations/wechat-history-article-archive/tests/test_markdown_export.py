from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "markdown_export.py"
SPEC = importlib.util.spec_from_file_location("markdown_export", SCRIPT)
assert SPEC and SPEC.loader
markdown_export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(markdown_export)


class WeChatMarkdownParserTests(unittest.TestCase):
    def test_void_image_tag_does_not_extend_content_beyond_container(self) -> None:
        parser = markdown_export.WeChatMarkdownParser()
        parser.feed('<div id="js_content"><p>正文</p><img src="https://example.test/a.jpg"></div><p>页脚</p>')
        markdown, images = parser.render()
        self.assertIn("正文", markdown)
        self.assertNotIn("页脚", markdown)
        self.assertEqual(1, len(images))

    def test_missing_content_container_is_not_an_article(self) -> None:
        parser = markdown_export.WeChatMarkdownParser()
        parser.feed("<html><body>验证页面</body></html>")
        self.assertFalse(parser.content_found)

    def test_export_rejects_a_verification_page_before_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            article_dir = Path(tmp) / "article"
            article_dir.mkdir()
            with self.assertRaisesRegex(ValueError, "#js_content"):
                markdown_export.export_article_markdown(
                    article_dir, "<html><body>验证页面</body></html>", {}, "test-agent", 1
                )
            self.assertFalse((article_dir / "article.md").exists())


if __name__ == "__main__":
    unittest.main()
