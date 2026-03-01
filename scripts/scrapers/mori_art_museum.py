import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class MoriArtMuseumScraper(BaseScraper):
    """Scraper for Mori Art Museum (森美術館)."""

    source_name = "mori_art_museum"
    base_url = "https://www.mori.art.museum"
    events_url = "https://www.mori.art.museum/jp/exhibitions/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from Mori Art Museum."""
        soup = self.fetch(self.events_url)
        exhibitions = []

        for item in soup.select("a[href*='/exhibitions/']"):
            try:
                exhibition = self._parse_item(item)
                if exhibition:
                    exhibitions.append(exhibition)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, item) -> Exhibition | None:
        """Parse a single exhibition item."""
        href = item.get("href", "")
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
            venue="森美術館",
            address="東京都港区六本木6-10-1 六本木ヒルズ森タワー53F",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _extract_title(self, item) -> str | None:
        """Extract exhibition title."""
        # Try heading elements first
        for tag in ["h1", "h2", "h3", "h4"]:
            elem = item.select_one(tag)
            if elem:
                return elem.get_text(strip=True)

        # Try to get text directly
        text = item.get_text(strip=True)
        # Remove date patterns
        text = re.sub(r"\d{4}\.\d{1,2}\.\d{1,2}.*$", "", text)
        text = text.strip()
        return text if len(text) > 2 else None

    def _parse_dates(self, text: str) -> tuple:
        """Parse date format like '2025.12.3（水）～ 2026.3.29（日）'."""
        pattern = (
            r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
            r".*?[～〜\-–].*?"
            r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
        )
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
