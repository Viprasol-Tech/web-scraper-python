"""The :class:`Scraper` that ties a pluggable fetcher to the extractors.

The *fetch* step is a ``Callable[[str], str]`` so the library tests and
demos run fully offline: the default :class:`FixtureFetcher` returns
canned HTML from an in-memory mapping. Real HTTP is intentionally left to
the caller (pass e.g. a ``urllib.request``-based callable in production).

Part of Web Scraper Python by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from pydantic import BaseModel, Field

from web_scraper_python.extract import (
    extract_links,
    extract_meta,
    extract_tables,
    extract_text,
)

Fetcher = Callable[[str], str]
"""Signature of a fetch function: ``url -> html``."""


class FixtureFetcher:
    """A deterministic, offline fetcher backed by an in-memory mapping.

    Construct it with ``{url: html}`` fixtures. Calling the instance with
    a known URL returns its HTML; an unknown URL raises ``KeyError``. This
    is the default transport so the scraper needs no network.
    """

    def __init__(self, fixtures: Mapping[str, str]) -> None:
        self._fixtures: dict[str, str] = dict(fixtures)

    def __call__(self, url: str) -> str:
        try:
            return self._fixtures[url]
        except KeyError as exc:  # pragma: no cover - trivial re-raise
            raise KeyError(f"no fixture registered for URL: {url!r}") from exc


class PageData(BaseModel):
    """The structured result of scraping a single page."""

    url: str = Field(description="The URL the page was fetched from.")
    title: str = Field(default="", description="The page <title>.")
    meta: dict[str, str] = Field(
        default_factory=dict, description="Title plus <meta> name/property values."
    )
    links: list[str] = Field(default_factory=list, description="Absolute links found on the page.")
    tables: list[list[list[str]]] = Field(
        default_factory=list, description="Parsed tables as rows of cell strings."
    )
    text: str = Field(default="", description="Visible text with tags stripped.")


class Scraper:
    """Fetch a URL and extract links, text, tables and metadata.

    Args:
        fetcher: A ``Callable[[str], str]`` mapping a URL to HTML. Defaults
            to an empty :class:`FixtureFetcher` (offline). Inject a real
            HTTP callable for production use.
    """

    def __init__(self, fetcher: Fetcher | None = None) -> None:
        self.fetcher: Fetcher = fetcher if fetcher is not None else FixtureFetcher({})

    def scrape_html(self, html: str, url: str = "") -> PageData:
        """Extract structured data from an HTML string already in hand.

        Args:
            html: The HTML source to parse.
            url: The URL the HTML came from, used to resolve relative links.

        Returns:
            The populated :class:`PageData`.
        """
        meta = extract_meta(html)
        return PageData(
            url=url,
            title=meta.get("title", ""),
            meta=meta,
            links=extract_links(html, url),
            tables=extract_tables(html),
            text=extract_text(html),
        )

    def scrape(self, url: str) -> PageData:
        """Fetch ``url`` via the configured fetcher, then extract data.

        Args:
            url: The URL to fetch and scrape.

        Returns:
            The populated :class:`PageData`.
        """
        html = self.fetcher(url)
        return self.scrape_html(html, url)
