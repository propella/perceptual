from bs4 import BeautifulSoup

from scripts.scrapers.base import BaseScraper


class PlaywrightBaseScraper(BaseScraper):
    """Base scraper that uses Playwright for JavaScript-rendered pages."""

    def fetch_js(self, url: str) -> BeautifulSoup:
        """Fetch URL using Playwright and return parsed HTML."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_extra_http_headers(
                    {"User-Agent": "perceptual-exhibition-collector/0.1.0"}
                )
                page.goto(url, timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                html = page.content()
            finally:
                browser.close()

        return BeautifulSoup(html, "lxml")
