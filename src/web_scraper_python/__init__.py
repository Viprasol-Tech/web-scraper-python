"""Web Scraper Python — offline-friendly HTML extraction with a pluggable fetcher.

Part of Web Scraper Python by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from web_scraper_python.extract import (
    extract_links,
    extract_meta,
    extract_tables,
    extract_text,
)
from web_scraper_python.scraper import PageData, Scraper

__version__ = "0.1.0"

__all__ = [
    "PageData",
    "Scraper",
    "__version__",
    "extract_links",
    "extract_meta",
    "extract_tables",
    "extract_text",
]
