"""Unit tests for the stdlib HTML extractors."""

from __future__ import annotations

from web_scraper_python.extract import (
    extract_links,
    extract_meta,
    extract_tables,
    extract_text,
)

HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Hello &amp; World</title>
  <meta name="description" content="A test page.">
  <meta property="og:title" content="OG Hello">
</head>
<body>
  <a href="/about">About</a>
  <a href="../contact">Contact</a>
  <a href="https://other.example/x">External</a>
  <a href="#frag">Fragment</a>
  <p>First paragraph.</p>
  <script>var ignored = 1;</script>
  <p>Second   paragraph.</p>
  <table>
    <tr><th>Name</th><th>Age</th></tr>
    <tr><td>Ada</td><td>36</td></tr>
  </table>
</body>
</html>
"""

BASE = "https://example.com/blog/post"


def test_extract_links_resolves_relative_and_skips_fragments() -> None:
    links = extract_links(HTML, BASE)
    assert links == [
        "https://example.com/about",
        "https://example.com/contact",
        "https://other.example/x",
    ]


def test_extract_links_without_base_returns_raw() -> None:
    assert extract_links('<a href="/x">x</a>') == ["/x"]


def test_extract_meta_parses_title_and_meta() -> None:
    meta = extract_meta(HTML)
    assert meta["title"] == "Hello & World"
    assert meta["description"] == "A test page."
    assert meta["og:title"] == "OG Hello"


def test_extract_meta_always_has_title_key() -> None:
    assert extract_meta("<html></html>")["title"] == ""


def test_extract_tables_parses_rows() -> None:
    tables = extract_tables(HTML)
    assert len(tables) == 1
    assert tables[0] == [["Name", "Age"], ["Ada", "36"]]


def test_extract_text_strips_tags_and_scripts() -> None:
    text = extract_text(HTML)
    assert "First paragraph." in text
    assert "Second paragraph." in text  # whitespace collapsed
    assert "ignored" not in text
    assert "<p>" not in text
    assert "Hello & World" not in text  # title is not body text
