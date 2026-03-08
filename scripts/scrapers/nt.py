import re
from datetime import date
from urllib.parse import urljoin

from bs4 import NavigableString

from scripts.scrapers.base import BaseScraper, Exhibition


class NTScraper(BaseScraper):
    """Scraper for NT (ニコ技) maker events (wiki.nicotech.jp)."""

    source_name = "nt"
    base_url = "https://wiki.nicotech.jp/nico_tech/"
    events_url = "https://wiki.nicotech.jp/nico_tech/"

    def scrape(self) -> list[Exhibition]:
        """Scrape upcoming NT events from the wiki."""
        soup = self.fetch(self.events_url)
        exhibitions = []

        # Find "直近の開催" section
        upcoming_h3 = soup.find("h3", id="content_1_2")
        if not upcoming_h3:
            upcoming_h3 = soup.find(
                "h3", string=re.compile("直近の開催")
            )
        if not upcoming_h3:
            return exhibitions

        # Get the <ul> immediately after the heading
        ul = upcoming_h3.find_next_sibling("ul")
        if not ul:
            return exhibitions

        for li in ul.find_all("li"):
            try:
                ex = self._parse_li(li)
                if ex:
                    exhibitions.append(ex)
            except Exception:
                continue

        return exhibitions

    def _parse_li(self, li) -> Exhibition | None:
        """Parse a single list item into an Exhibition."""
        a = li.find("a")
        if not a:
            return None

        title = a.get_text(strip=True)
        href = a.get("href", "")
        url = urljoin(self.base_url, href)

        # Extract date text from NavigableString before the <a>
        date_text = ""
        for content in li.contents:
            if isinstance(content, NavigableString):
                date_text = str(content).strip()
                if date_text:
                    break

        start_date, end_date = self._parse_date(date_text)
        if not start_date:
            return None

        # Venue: event name without year (e.g., "NT松戸2026" → "NT松戸")
        venue = re.sub(r"\d{4}$", "", title).strip() or title

        return Exhibition(
            title=title,
            venue=venue,
            start_date=start_date,
            end_date=end_date,
            source_url=url,
            source=self.source_name,
            tags=["メイカー", "ものづくり"],
        )

    def _parse_date(self, text: str) -> tuple:
        """Parse date strings like '2026-03-07' or '2026-06-27,28'."""
        text = text.strip()

        # Range within same month: YYYY-MM-DD,DD
        m = re.match(r"(\d{4})-(\d{2})-(\d{2}),(\d{1,2})", text)
        if m:
            start = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            end = date(int(m.group(1)), int(m.group(2)), int(m.group(4)))
            return start, end

        # Single date: YYYY-MM-DD
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
        if m:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d, d

        return None, None
