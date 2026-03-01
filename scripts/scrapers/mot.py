import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class MOTScraper(BaseScraper):
    """Scraper for Museum of Contemporary Art Tokyo (東京都現代美術館)."""

    source_name = "mot"
    base_url = "https://www.mot-art-museum.jp"
    events_url = "https://www.mot-art-museum.jp/exhibitions/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from MOT."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls = set()

        for item in soup.select("a[href*='/exhibitions/']"):
            try:
                exhibition = self._parse_item(item)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, item) -> Exhibition | None:
        """Parse a single exhibition item."""
        # Get link element
        if item.name == "a":
            link = item
        else:
            link = item.find_parent("a") or item.select_one("a")

        if not link:
            return None

        href = link.get("href", "")
        if not href or "/exhibitions/" not in href or href.endswith("/exhibitions/"):
            return None

        text = item.get_text(separator=" ", strip=True)
        if not text:
            return None

        # Extract title
        title = self._extract_title(item)
        if not title:
            return None

        # Extract dates
        start_date, end_date = self._parse_dates(text)
        if not start_date or not end_date:
            return None

        # Build URL
        if href.startswith("/"):
            source_url = f"{self.base_url}{href}"
        else:
            source_url = href

        # Extract image
        img = item.select_one("img")
        image_url = None
        if img:
            src = img.get("src", "")
            if src.startswith("/"):
                image_url = f"{self.base_url}{src}"
            else:
                image_url = src

        return Exhibition(
            title=title,
            venue="東京都現代美術館",
            address="東京都江東区三好4-1-1",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _extract_title(self, item) -> str | None:
        """Extract exhibition title."""
        # Try h2 first (main title element)
        h2 = item.select_one("h2")
        if h2:
            return h2.get_text(strip=True)

        # Try other headings
        for tag in ["h1", "h3", "h4"]:
            elem = item.select_one(tag)
            if elem:
                return elem.get_text(strip=True)

        return None

    def _parse_dates(self, text: str) -> tuple:
        """Parse date formats from MOT."""
        # Pattern: 2025.12.3 - 2026.3.29 or 2025年12月3日 - 2026年3月29日
        patterns = [
            # Dot format: 2025.12.3 - 2026.3.29
            (
                r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
                r".*?[-–—〜～].*?"
                r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
            ),
            # Japanese format: 2025年12月3日 - 2026年3月29日
            (
                r"(\d{4})年(\d{1,2})月(\d{1,2})日"
                r".*?[-–—〜～].*?"
                r"(\d{4})年(\d{1,2})月(\d{1,2})日"
            ),
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start_date = datetime(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                ).date()
                end_date = datetime(
                    int(match.group(4)),
                    int(match.group(5)),
                    int(match.group(6)),
                ).date()
                return start_date, end_date

        return None, None
