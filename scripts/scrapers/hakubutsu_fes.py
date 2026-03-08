import re
from datetime import datetime

from bs4 import BeautifulSoup

from scripts.scrapers.base import Exhibition
from scripts.scrapers.base_playwright import PlaywrightBaseScraper


class HakubutsuFesScraper(PlaywrightBaseScraper):
    """Scraper for 博物ふぇすてぃばる (hakubutufes.info)."""

    source_name = "hakubutsu_fes"
    base_url = "https://www.hakubutufes.info"
    events_url = "https://www.hakubutufes.info/"

    def scrape(self) -> list[Exhibition]:
        """Scrape 博物ふぇすてぃばる event from the site."""
        soup = self._fetch_with_browser(self.events_url)
        ex = self._parse_page(soup)
        return [ex] if ex else []

    def _fetch_with_browser(self, url: str) -> BeautifulSoup:
        """Fetch with realistic browser UA to bypass Cloudflare protection."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )
                page = context.new_page()
                page.goto(url, timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                html = page.content()
            finally:
                browser.close()

        return BeautifulSoup(html, "lxml")

    def _parse_page(self, soup) -> Exhibition | None:
        """Parse the event page and return an Exhibition."""
        # Title: find "博物ふぇすてぃばる" in headings or table cells
        title = None
        for el in soup.select("h1, h2, h3, td, th"):
            text = el.get_text(strip=True)
            if "博物ふぇすてぃばる" in text:
                title = text
                break
        if not title:
            return None

        # Dates: search entire page for YYYY年M月D日 pattern
        page_text = soup.get_text()
        start_date, end_date = self._parse_dates(page_text)
        if not start_date:
            return None

        # Venue: find text containing ビッグサイト or venue keywords
        venue = "博物ふぇすてぃばる"
        for el in soup.select("td, p, strong"):
            text = el.get_text(strip=True)
            m = re.search(r"(東京ビッグサイト[^\s、。\n]*|[^\s、。\n]*ホール)", text)
            if m:
                venue = m.group(1)
                break

        # Address: find text containing 東京都 with ward/district info
        address = None
        for el in soup.select("td"):
            text = el.get_text(strip=True)
            if "東京都" in text and ("丁目" in text or "区" in text):
                address = text[:100]
                break

        return Exhibition(
            title=title,
            venue=venue,
            address=address,
            start_date=start_date,
            end_date=end_date,
            source_url=self.events_url,
            source=self.source_name,
            tags=["メイカー", "ものづくり", "博物"],
        )

    def _parse_dates(self, text: str) -> tuple:
        """Parse dates in format YYYY年M月D日 from text."""
        pattern = r"(\d{4})年\s*(\d{1,2})月(\d{1,2})日"
        matches = re.findall(pattern, text)
        if matches:
            start = datetime(
                int(matches[0][0]), int(matches[0][1]), int(matches[0][2])
            ).date()
            end = datetime(
                int(matches[-1][0]), int(matches[-1][1]), int(matches[-1][2])
            ).date()
            return start, end
        return None, None
