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
        seen_urls = set()

        # Find date elements (h5) and look for associated links
        for h5 in soup.select("h5"):
            date_text = h5.get_text(strip=True)
            start_date, end_date = self._parse_dates(date_text)
            if not start_date or not end_date:
                continue

            # Find parent container
            parent = h5.find_parent()
            while parent and parent.name not in ["section", "div", "article", "body"]:
                parent = parent.find_parent()

            if not parent:
                continue

            # Find associated program links
            for link in parent.select("a[href*='/program/']"):
                href = link.get("href", "")
                if href == "/program/" or href in seen_urls:
                    continue

                title = self._extract_title(link, link.get_text(strip=True))
                if not title:
                    continue

                source_url = f"{self.base_url}{href}" if href.startswith("/") else href
                seen_urls.add(href)

                img = link.select_one("img")
                image_url = None
                if img:
                    src = img.get("src", "")
                    if src.startswith("http"):
                        image_url = src
                    elif src.startswith("/"):
                        image_url = f"{self.base_url}{src}"

                exhibitions.append(
                    Exhibition(
                        title=title,
                        venue="21_21 DESIGN SIGHT",
                        address="東京都港区赤坂9-7-6 東京ミッドタウン ミッドタウン・ガーデン",
                        start_date=start_date,
                        end_date=end_date,
                        source_url=source_url,
                        source=self.source_name,
                        image_url=image_url,
                    )
                )
                break  # Only one exhibition per date

        return exhibitions

    def _parse_item(self, item) -> Exhibition | None:
        """Parse a single exhibition item."""
        href = item.get("href", "")
        if not href or href.endswith("/program/"):
            return None

        # Only process /program/ links
        if "/program/" not in href:
            return None

        text = item.get_text(separator=" ", strip=True)
        if not text:
            return None

        # Extract title
        title = self._extract_title(item, text)
        if not title:
            return None

        # Extract dates - also check parent element for dates
        start_date, end_date = self._parse_dates(text)
        if not start_date or not end_date:
            # Try to find date in parent
            parent = item.find_parent()
            if parent:
                parent_text = parent.get_text(separator=" ", strip=True)
                start_date, end_date = self._parse_dates(parent_text)

        if not start_date or not end_date:
            return None

        # Build URL
        if href.startswith("http"):
            source_url = href
        elif href.startswith("/"):
            source_url = f"{self.base_url}{href}"
        else:
            source_url = f"{self.base_url}/program/{href}"

        # Extract image
        img = item.select_one("img")
        image_url = None
        if img:
            src = img.get("src", "")
            if src.startswith("http"):
                image_url = src
            elif src.startswith("/"):
                image_url = f"{self.base_url}{src}"
            else:
                image_url = f"{self.base_url}/{src}"

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

        # Try to extract from text with 「...」format
        if text:
            match = re.search(r"「(.+?)」", text)
            if match:
                return match.group(1)
            # Clean up prefix
            text = re.sub(r"^(企画展|展覧会)\s*", "", text)
            if len(text) > 2:
                return text

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
