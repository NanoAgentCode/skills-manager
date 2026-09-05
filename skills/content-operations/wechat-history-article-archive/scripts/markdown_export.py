#!/usr/bin/env python3
"""Convert archived WeChat article HTML into Markdown and local images."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

TITLE_RE = re.compile(r'<h1[^>]*id="activity-name"[^>]*>\s*(?:<span[^>]*>)?(.+?)(?:</span>)?\s*</h1>', re.IGNORECASE | re.DOTALL)
AUTHOR_RE = re.compile(r'<span[^>]*id="js_author_name"[^>]*>(.*?)</span>', re.IGNORECASE | re.DOTALL)
ACCOUNT_RE = re.compile(r'<a[^>]*id="js_name"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_TAG_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
BLANK_LINES_RE = re.compile(r"\n{3,}")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def clean_inline_text(text: str) -> str:
    value = unescape(text).replace("\xa0", " ").replace("\u200b", "")
    value = WHITESPACE_RE.sub(" ", value)
    return value.strip()


def extract_meta_text(pattern: re.Pattern[str], html_text: str) -> str:
    match = pattern.search(html_text)
    if not match:
        return ""
    return clean_inline_text(TAG_RE.sub("", match.group(1)))


def infer_image_extension(url: str, attrs: dict[str, str], response: urllib.response.addinfourl | None = None) -> str:
    data_type = attrs.get("data-type", "").strip(".").lower()
    if data_type:
        return "." + data_type
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "wx_fmt" in query and query["wx_fmt"]:
        return "." + query["wx_fmt"][0].lower()
    suffix = Path(parsed.path).suffix.lower()
    if suffix:
        return suffix
    if response is not None:
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
        mapping = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }
        if content_type in mapping:
            return mapping[content_type]
    return ".jpg"


class WeChatMarkdownParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_content = False
        self.content_found = False
        self.depth = 0
        self.parts: list[str] = []
        self.images: list[dict[str, str]] = []
        self.list_stack: list[dict[str, int | str]] = []
        self.link_stack: list[str] = []
        self.blockquote_depth = 0
        self.in_pre = False
        self.in_code = False
        self.skip_depth = 0
        self.image_counter = 0

    def _current_text(self) -> str:
        return "".join(self.parts)

    def _endswith(self, suffix: str | tuple[str, ...]) -> bool:
        return self._current_text().endswith(suffix)

    def _ensure_newlines(self, count: int = 1) -> None:
        if not self.parts:
            return
        current = self._current_text()
        trailing = len(current) - len(current.rstrip("\n"))
        needed = max(count - trailing, 0)
        if needed:
            self.parts.append("\n" * needed)

    def _write(self, text: str) -> None:
        if not text or self.skip_depth:
            return
        if self.in_pre:
            self.parts.append(text)
            return

        value = text.replace("\r", "").replace("\n", " ")
        value = WHITESPACE_RE.sub(" ", value)
        if not value.strip():
            if self.parts and not self._endswith((" ", "\n")):
                self.parts.append(" ")
            return

        for chunk in value.split("\n"):
            if not chunk:
                continue
            if self.parts and not self._endswith((" ", "\n", "(", "[", "/", "`", "*")) and not chunk.startswith((".", ",", ":", ";", "!", "?", ")", "]")):
                self.parts.append(" ")
            if self.blockquote_depth and (not self.parts or self._endswith("\n")):
                self.parts.append("> " * self.blockquote_depth)
            self.parts.append(chunk.strip())

    def _open_block(self, prefix: str = "", blank: bool = True) -> None:
        self._ensure_newlines(2 if blank else 1)
        if prefix:
            if self.blockquote_depth:
                prefix = ("> " * self.blockquote_depth) + prefix
            self.parts.append(prefix)

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: (value or "") for key, value in attrs_list}
        if not self.in_content:
            if attrs.get("id") == "js_content":
                self.in_content = True
                self.content_found = True
                self.depth = 1
            return

        if tag not in VOID_TAGS:
            self.depth += 1
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return

        if tag in {"p", "div", "section"}:
            self._open_block()
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._open_block("#" * int(tag[1]) + " ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "hr":
            self._open_block("---")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
            self.in_code = True
        elif tag == "pre":
            self._open_block("```")
            self.parts.append("\n")
            self.in_pre = True
        elif tag == "blockquote":
            self._open_block()
            self.blockquote_depth += 1
        elif tag == "a":
            self.parts.append("[")
            self.link_stack.append(attrs.get("href", "").strip())
        elif tag == "ul":
            self.list_stack.append({"type": "ul", "index": 0})
            self._open_block()
        elif tag == "ol":
            self.list_stack.append({"type": "ol", "index": 0})
            self._open_block()
        elif tag == "li" and self.list_stack:
            current = self.list_stack[-1]
            current["index"] = int(current["index"]) + 1
            indent = "  " * (len(self.list_stack) - 1)
            bullet = "- " if current["type"] == "ul" else f"{current['index']}. "
            self._open_block(indent + bullet, blank=False)
        elif tag == "img":
            image_url = attrs.get("data-src") or attrs.get("src") or ""
            image_url = unescape(image_url.strip())
            if image_url:
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                self.image_counter += 1
                alt = clean_inline_text(attrs.get("alt") or f"image-{self.image_counter}")
                self.images.append(
                    {
                        "url": image_url,
                        "alt": alt or f"image-{self.image_counter}",
                        "attrs": json.dumps(attrs, ensure_ascii=False),
                    }
                )
                self._open_block(f"![{alt or 'image'}](images/image-{self.image_counter:03d})")

    def handle_endtag(self, tag: str) -> None:
        if not self.in_content:
            return
        if tag in VOID_TAGS:
            return
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth:
            if tag in {"strong", "b"}:
                self.parts.append("**")
            elif tag in {"em", "i"}:
                self.parts.append("*")
            elif tag == "code":
                self.parts.append("`")
                self.in_code = False
            elif tag == "pre":
                if not self._endswith("\n"):
                    self.parts.append("\n")
                self.parts.append("```")
                self.in_pre = False
                self._ensure_newlines(2)
            elif tag == "blockquote" and self.blockquote_depth:
                self.blockquote_depth -= 1
                self._ensure_newlines(2)
            elif tag == "a":
                href = self.link_stack.pop() if self.link_stack else ""
                self.parts.append(f"]({href})" if href else "]")
            elif tag in {"ul", "ol"} and self.list_stack:
                self.list_stack.pop()
                self._ensure_newlines(2)
            elif tag in {"p", "div", "section", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
                self._ensure_newlines(2)

        self.depth -= 1
        if self.depth <= 0:
            self.in_content = False

    def handle_data(self, data: str) -> None:
        if self.in_content and not self.skip_depth:
            self._write(data)

    def handle_entityref(self, name: str) -> None:
        if self.in_content and not self.skip_depth:
            self._write(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self.in_content and not self.skip_depth:
            self._write(unescape(f"&#{name};"))

    def render(self) -> tuple[str, list[dict[str, str]]]:
        markdown = "".join(self.parts).replace("\r", "")
        markdown = re.sub(r"[ \t]+\n", "\n", markdown)
        markdown = BLANK_LINES_RE.sub("\n\n", markdown).strip() + "\n"
        return markdown, self.images


def download_binary(url: str, destination: Path, user_agent: str, referer: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Referer": referer})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        image_bytes = response.read()
        extension = infer_image_extension(url, {}, response=response)
    destination = destination.with_suffix(extension)
    destination.write_bytes(image_bytes)
    return destination.name


def export_article_markdown(article_dir: Path, html_text: str, metadata: dict, user_agent: str, timeout: int) -> dict:
    parser = WeChatMarkdownParser()
    parser.feed(SCRIPT_TAG_RE.sub("", STYLE_TAG_RE.sub("", html_text)))
    content_md, images = parser.render()
    if not parser.content_found:
        raise ValueError("Article body #js_content was not found; the response may be a verification, login, or error page.")
    text_only = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", content_md).strip()
    if not text_only and not images:
        raise ValueError("Article body #js_content contains no text or images; the response was not archived as an article.")

    images_dir = article_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rewritten_md = content_md
    downloaded_images: list[dict[str, str]] = []
    referer = metadata.get("canonical_url") or metadata.get("source_url", "")
    for index, image in enumerate(images, start=1):
        base_path = images_dir / f"image-{index:03d}"
        filename = download_binary(image["url"], base_path, user_agent=user_agent, referer=referer, timeout=timeout)
        rewritten_md = rewritten_md.replace(f"](images/image-{index:03d})", f"](images/{filename})", 1)
        downloaded_images.append({"url": image["url"], "filename": filename, "alt": image["alt"]})

    title = extract_meta_text(TITLE_RE, html_text) or metadata.get("title", "")
    author = extract_meta_text(AUTHOR_RE, html_text) or metadata.get("author", "")
    account = extract_meta_text(ACCOUNT_RE, html_text) or metadata.get("nickname", "")
    header_lines = [f"# {title}".rstrip(), ""]
    if account:
        header_lines.append(f"- 公众号: {account}")
    if author:
        header_lines.append(f"- 作者: {author}")
    if metadata.get("publish_ct"):
        header_lines.append(f"- 发布时间戳: {metadata['publish_ct']}")
    if metadata.get("canonical_url"):
        header_lines.append(f"- 原文链接: {metadata['canonical_url']}")
    header_lines.extend(["", rewritten_md.strip(), ""])

    markdown_path = article_dir / "article.md"
    markdown_path.write_text("\n".join(header_lines), encoding="utf-8")

    metadata["title"] = title or metadata.get("title", "")
    metadata["author"] = author
    metadata["nickname"] = account or metadata.get("nickname", "")
    metadata["markdown_path"] = str(markdown_path)
    metadata["images_dir"] = str(images_dir)
    metadata["image_count"] = len(downloaded_images)

    return metadata
