"""A built-in sample HTML document used by the offline demo and tests.

Part of Web Scraper Python by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

SAMPLE_URL = "https://example.com/blog/post"

SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Viprasol Sample Page &amp; Demo</title>
  <meta charset="utf-8">
  <meta name="description" content="A demo page for the web scraper.">
  <meta name="author" content="Viprasol Tech">
  <meta property="og:title" content="Sample Page">
  <style>.hidden { display: none; }</style>
  <script>console.log("ignored");</script>
</head>
<body>
  <header><h1>Welcome to the Demo</h1></header>
  <p>This page demonstrates <strong>offline</strong> scraping.</p>
  <nav>
    <a href="/about">About</a>
    <a href="../contact">Contact</a>
    <a href="https://viprasol.com">Viprasol</a>
    <a href="#top">Back to top</a>
  </nav>
  <table>
    <tr><th>Symbol</th><th>Price</th></tr>
    <tr><td>BTC</td><td>65000</td></tr>
    <tr><td>ETH</td><td>3200</td></tr>
  </table>
  <footer><p>Built by Viprasol Tech.</p></footer>
</body>
</html>
"""
