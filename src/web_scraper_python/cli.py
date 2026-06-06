"""Command-line interface for Web Scraper Python.

``web-scraper-python demo`` scrapes a built-in sample HTML document fully
offline and prints the extracted links, metadata, tables and text.

Part of Web Scraper Python by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from web_scraper_python import __version__
from web_scraper_python.sample import SAMPLE_HTML, SAMPLE_URL
from web_scraper_python.scraper import FixtureFetcher, Scraper

app = typer.Typer(add_completion=False, help="Web Scraper Python — by Viprasol Tech.")
console = Console()


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"web-scraper-python [bold cyan]{__version__}[/] — by Viprasol Tech")


@app.command()
def demo() -> None:
    """Scrape the built-in sample page offline and print the results."""
    fetcher = FixtureFetcher({SAMPLE_URL: SAMPLE_HTML})
    scraper = Scraper(fetcher)
    page = scraper.scrape(SAMPLE_URL)

    console.print(f"URL:   [bold]{page.url}[/]")
    console.print(f"Title: [bold green]{page.title}[/]")

    meta_table = Table(title="Metadata", show_header=True, header_style="bold cyan")
    meta_table.add_column("key")
    meta_table.add_column("value")
    for key, value in page.meta.items():
        meta_table.add_row(key, value)
    console.print(meta_table)

    console.print("\n[bold]Links[/] (resolved absolutely):")
    for link in page.links:
        console.print(f"  - {link}")

    for index, rows in enumerate(page.tables):
        data_table = Table(title=f"Table {index + 1}", header_style="bold cyan")
        if rows:
            for header in rows[0]:
                data_table.add_column(header)
            for row in rows[1:]:
                data_table.add_row(*row)
        console.print(data_table)

    console.print("\n[bold]Text[/]:")
    console.print(page.text)


if __name__ == "__main__":
    app()
