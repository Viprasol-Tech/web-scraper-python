"""Unit tests for the Scraper and pluggable fetcher."""

from __future__ import annotations

import pytest

from web_scraper_python.sample import SAMPLE_HTML, SAMPLE_URL
from web_scraper_python.scraper import FixtureFetcher, PageData, Scraper


def test_fixture_fetcher_returns_registered_html() -> None:
    fetcher = FixtureFetcher({"https://x/": "<html></html>"})
    assert fetcher("https://x/") == "<html></html>"


def test_fixture_fetcher_unknown_url_raises() -> None:
    with pytest.raises(KeyError):
        FixtureFetcher({})("https://missing/")


def test_scraper_scrapes_sample_offline() -> None:
    scraper = Scraper(FixtureFetcher({SAMPLE_URL: SAMPLE_HTML}))
    page = scraper.scrape(SAMPLE_URL)

    assert isinstance(page, PageData)
    assert page.url == SAMPLE_URL
    assert page.title == "Viprasol Sample Page & Demo"
    assert page.meta["author"] == "Viprasol Tech"
    assert "https://example.com/about" in page.links
    assert "https://viprasol.com" in page.links
    assert page.tables[0] == [
        ["Symbol", "Price"],
        ["BTC", "65000"],
        ["ETH", "3200"],
    ]
    assert "Welcome to the Demo" in page.text


def test_scrape_html_uses_url_for_link_resolution() -> None:
    page = Scraper().scrape_html('<a href="/p">p</a>', "https://h.test/dir/")
    assert page.links == ["https://h.test/p"]


def test_default_scraper_has_empty_fixture_fetcher() -> None:
    with pytest.raises(KeyError):
        Scraper().scrape("https://anything/")
