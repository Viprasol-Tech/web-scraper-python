"""HTML extraction helpers built on the standard-library ``html.parser``.

This module is the genuine logic of the scraper: parsing links (with
relative-to-absolute URL resolution), visible text, tables, and page
metadata. It depends only on the Python standard library — no
``requests``, ``bs4`` or ``lxml``.

Part of Web Scraper Python by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin

# Tags whose text content is not part of the visible/extractable page text.
_SKIP_TEXT_TAGS = frozenset({"script", "style", "head", "title", "noscript"})

# Tags that should be treated as block-level for text spacing purposes.
_BLOCK_TAGS = frozenset(
    {
        "p",
        "div",
        "br",
        "li",
        "tr",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "section",
        "article",
        "header",
        "footer",
        "ul",
        "ol",
        "table",
    }
)

# HTML void elements never carry an end tag.
_VOID_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


def _attrs_to_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    """Collapse a parser attribute list into a ``{name: value}`` mapping."""
    return {name.lower(): (value or "") for name, value in attrs}


class _LinkParser(HTMLParser):
    """Collect ``href`` values from anchor tags in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = _attrs_to_dict(attrs).get("href")
        if href:
            self.hrefs.append(href.strip())


def extract_links(html: str, base_url: str = "") -> list[str]:
    """Return all anchor ``href`` targets, resolved against ``base_url``.

    Relative URLs (``/about``, ``../x``, ``page.html``) are resolved to
    absolute URLs using :func:`urllib.parse.urljoin`. Empty and
    fragment-only (``#section``) links are skipped. Order and duplicates
    from the source document are preserved.

    Args:
        html: The HTML source to scan.
        base_url: The absolute URL the document was fetched from. When
            empty, hrefs are returned as-is.

    Returns:
        A list of resolved URLs in document order.
    """
    parser = _LinkParser()
    parser.feed(html)
    parser.close()

    links: list[str] = []
    for href in parser.hrefs:
        if not href or href.startswith("#"):
            continue
        links.append(urljoin(base_url, href) if base_url else href)
    return links


class _TextParser(HTMLParser):
    """Accumulate visible text, skipping script/style and titling blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name in _SKIP_TEXT_TAGS:
            self._skip_depth += 1
        elif name in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name in _SKIP_TEXT_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif name in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def extract_text(html: str) -> str:
    """Return the visible text of ``html`` with tags stripped.

    Script, style and head content is dropped. Inline whitespace is
    collapsed and block-level elements produce line breaks, yielding a
    readable plain-text rendering.

    Args:
        html: The HTML source to render to text.

    Returns:
        The extracted plain text.
    """
    parser = _TextParser()
    parser.feed(html)
    parser.close()
    return parser.text()


class _TableParser(HTMLParser):
    """Parse ``<table>`` elements into lists of row cell-strings."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._in_table = 0
        self._in_cell = False
        self._row: list[str] | None = None
        self._cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "table":
            self._in_table += 1
            self.tables.append([])
        elif name == "tr" and self._in_table:
            self._row = []
        elif name in ("td", "th") and self._in_table:
            self._in_cell = True
            self._cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name in ("td", "th") and self._in_cell:
            text = " ".join("".join(self._cell_parts).split())
            if self._row is not None:
                self._row.append(text)
            self._in_cell = False
        elif name == "tr" and self._row is not None:
            self.tables[-1].append(self._row)
            self._row = None
        elif name == "table" and self._in_table:
            self._in_table -= 1

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)


def extract_tables(html: str) -> list[list[list[str]]]:
    """Parse every ``<table>`` into a list of rows of cell strings.

    Each table becomes ``list[row]`` where each row is ``list[str]`` of
    cell text. Both ``<th>`` and ``<td>`` cells are captured. Cell text is
    whitespace-collapsed.

    Args:
        html: The HTML source to scan.

    Returns:
        One entry per table, each a list of rows, each row a list of cells.
    """
    parser = _TableParser()
    parser.feed(html)
    parser.close()
    return parser.tables


class _MetaParser(HTMLParser):
    """Extract the document title and ``<meta>`` name/property values."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.title: str = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "title":
            self._in_title = True
        elif name == "meta":
            data = _attrs_to_dict(attrs)
            key = data.get("name") or data.get("property") or data.get("http-equiv")
            if key and "content" in data:
                self.meta[key.lower()] = data["content"]

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def extract_meta(html: str) -> dict[str, str]:
    """Return page metadata: the ``<title>`` plus ``<meta>`` values.

    The returned mapping always contains a ``"title"`` key (possibly an
    empty string). Each ``<meta>`` element keyed by its ``name``,
    ``property`` (e.g. ``og:title``) or ``http-equiv`` attribute maps to
    its ``content`` value.

    Args:
        html: The HTML source to scan.

    Returns:
        A ``{key: content}`` mapping including ``"title"``.
    """
    parser = _MetaParser()
    parser.feed(html)
    parser.close()
    result: dict[str, str] = {"title": " ".join(unescape(parser.title).split())}
    result.update(parser.meta)
    return result
