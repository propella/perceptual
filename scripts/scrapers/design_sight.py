import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class DesignSightScraper(BaseScraper):
    """Scraper for 21_21 DESIGN SIGHT."""

    source_name = "design_sight"
    base_url = "https://www.2121designsight.jp"
    events_url = "https://www.2121designsight.jp/program/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from 21_21 DESIGN SIGHT."""
        soup = self.fetch(self.events_url)
        exhibitions = []

        for item in soup.select("a[href*='/program/']"):
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
        if not href or "/program/" not in href or href.endswith("/program/"):
            return None

        text = item.get_text(separator=" ", strip=True)
        if not text:
            return None

        # Extract title
        title = self._extract_title(item, text)
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
            venue="21_21 DESIGN SIGHT",
            address="東京都港区赤坂9-7-6 東京ミッドタウン ミッドタウン・ガーデン",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _extract_title(self, item, text: str) -> str | None:
        """Extract exhibition title."""
        # Look for heading elements
        for tag in ["h1", "h2", "h3", "h4", "h5"]:
            elem = item.select_one(tag)
            if elem:
                title = elem.get_text(strip=True)
                # Clean up "企画展「...」" format
                match = re.search(r"「(.+?)」", title)
                if match:
                    return match.group(1)
                return title

        # Try to extract from text before date
        match = re.match(r"^(.+?)\d{4}年", text)
        if match:
            return match.group(1).strip()

        return None

    def _parse_dates(self, text: str) -> tuple:
        """Parse date format like '2025年11月21日 (金) - 2026年3月 8日 (日)'."""
        # Pattern for full year-month-day format
        pattern = (
            r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?"
            r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日"
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
