import re
from datetime import datetime

from bs4 import BeautifulSoup

from scripts.scrapers.base import Exhibition
from scripts.scrapers.base_playwright import PlaywrightBaseScraper

DATE_RE = re.compile(r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日")
# Continuation of a date range: "(土) 6日", "〜2026年8月2日", "〜8月2日" etc.
DATE_CONT_RE = re.compile(
    r"\s*(?:\([^)]*\))?\s*[〜~～\-–・、]?\s*"
    r"(?:(\d{4})年\s*)?(?:(\d{1,2})月\s*)?(\d{1,2})日"
)
VENUE_RE = re.compile(r"^\s*(?:\([^)]*\))?\s*(.+?)(?:にて|で)開催")


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
        start_date, end_date, date_end_pos = self._parse_dates(page_text)
        if not start_date:
            return None

        # Venue: the sentence following the dates ("...にて開催されます")
        venue = None
        m = VENUE_RE.match(page_text[date_end_pos : date_end_pos + 100])
        if m:
            venue = re.sub(r"^東京[、,][^の]*の", "", m.group(1).strip())
        if not venue:
            venue = self._find_venue(soup)

        # Address: find text containing 東京都 with ward/district info
        address = None
        for el in soup.select("td"):
            text = el.get_text(strip=True)
            if "東京都" in text and ("丁目" in text or "区" in text):
                address = text[:100]
                break

        # Image: og:image first, then domain-matching img fallback
        image_url = None
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img:
            content = og_img.get("content", "").strip()
            if content:
                image_url = content
        if not image_url:
            for img in soup.select("img"):
                src = img.get("src", "")
                if src.startswith(self.base_url):
                    image_url = src
                    break
                if src.startswith("/"):
                    image_url = f"{self.base_url}{src}"
                    break

        return Exhibition(
            title=title,
            venue=venue,
            address=address,
            start_date=start_date,
            end_date=end_date,
            source_url=self.events_url,
            source=self.source_name,
            image_url=image_url,
            tags=["メイカー", "ものづくり", "博物"],
        )

    def _find_venue(self, soup) -> str:
        """Fallback: find text containing ビッグサイト or venue keywords."""
        for el in soup.select("td, p, strong"):
            text = el.get_text(strip=True)
            m = re.search(r"(東京ビッグサイト[^\s、。\n]*|[^\s、。\n]*ホール)", text)
            if m:
                return m.group(1)
        return "博物ふぇすてぃばる"

    def _parse_dates(self, text: str) -> tuple:
        """Parse the first event's date range from text.

        The page may list several events (upcoming and past), so only the
        first YYYY年M月D日 and the days directly following it are used.
        Returns (start, end, position just after the date range).
        """
        m = DATE_RE.search(text)
        if not m:
            return None, None, 0
        year, month, day = (int(g) for g in m.groups())
        start = datetime(year, month, day).date()
        end = start
        pos = m.end()
        while cont := DATE_CONT_RE.match(text, pos):
            explicit_year = cont.group(1)
            if explicit_year:
                year = int(explicit_year)
            if cont.group(2):
                month = int(cont.group(2))
            day = int(cont.group(3))
            try:
                candidate = datetime(year, month, day).date()
            except ValueError:
                break
            if candidate < end and not explicit_year:
                # Range crossing new year, e.g. 12月30日〜1月3日
                candidate = candidate.replace(year=candidate.year + 1)
            if candidate < end:
                break
            end = candidate
            pos = cont.end()
        return start, end, pos
