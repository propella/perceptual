import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class TokyoArtBeatScraper(BaseScraper):
    """Scraper for Tokyo Art Beat."""

    source_name = "tokyo_art_beat"
    base_url = "https://www.tokyoartbeat.com"
    events_url = "https://www.tokyoartbeat.com/events"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from Tokyo Art Beat."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        for item in soup.select("a[href^='/events/']"):
            try:
                exhibition = self._parse_item(item)
                if exhibition and exhibition.source_url not in seen_urls:
                    seen_urls.add(exhibition.source_url)
                    exhibitions.append(exhibition)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, item) -> Exhibition | None:
        """Parse a single exhibition item."""
        href = item.get("href", "")
        if not href or "/events/" not in href:
            return None

        title_elem = item.select_one("h3")
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        if not title:
            return None

        # Extract date range
        date_text = item.get_text()
        start_date, end_date = self._parse_dates(date_text)
        if not start_date or not end_date:
            return None

        # Extract venue from text
        venue = self._extract_venue(item)

        # Extract image
        img = item.select_one("img")
        image_url = img.get("src") if img else None

        return Exhibition(
            title=title,
            venue=venue or "会場情報なし",
            start_date=start_date,
            end_date=end_date,
            source_url=f"{self.base_url}{href}",
            source=self.source_name,
            image_url=image_url,
        )

    def _parse_dates(self, text: str) -> tuple:
        """Parse date range from text like '2026/2/20-5/31'."""
        pattern = r"(\d{4})/(\d{1,2})/(\d{1,2})\s*[-–]\s*(\d{1,2})/(\d{1,2})"
        match = re.search(pattern, text)
        if match:
            year = int(match.group(1))
            start_month = int(match.group(2))
            start_day = int(match.group(3))
            end_month = int(match.group(4))
            end_day = int(match.group(5))

            start_date = datetime(year, start_month, start_day).date()
            end_year = year if end_month >= start_month else year + 1
            end_date = datetime(end_year, end_month, end_day).date()

            return start_date, end_date

        return None, None

    def _extract_venue(self, item) -> str | None:
        """Extract venue name from item."""
        text = item.get_text(separator=" ")
        # Common venue patterns
        for pattern in [r"@\s*(.+?)(?:\s|$)", r"会場[：:]\s*(.+?)(?:\s|$)"]:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
