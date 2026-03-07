import re
from datetime import date

from scripts.scrapers.base import BaseScraper, Exhibition


class ArtscapeScraper(BaseScraper):
    """Scraper for artscape (https://artscape.jp) - national art exhibition aggregator."""

    source_name = "artscape"
    base_url = "https://artscape.jp"
    events_url = "https://artscape.jp/exhibitions/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from artscape."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        for a in soup.select("a[href*='/exhibitions/']"):
            try:
                exhibition = self._parse_item(a)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, a) -> Exhibition | None:
        """Parse a single exhibition link element."""
        href = a.get("href", "")
        if not re.search(r"/exhibitions/\d+/", href):
            return None

        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        title_elem = a.select_one("h3")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        if not title:
            return None

        text = a.get_text(separator=" ", strip=True)
        start_date, end_date = self._parse_dates(text)
        if not start_date or not end_date:
            return None

        # First <p> is typically the venue name
        venue = "artscape"
        paragraphs = a.select("p")
        if paragraphs:
            venue = paragraphs[0].get_text(strip=True) or venue

        img = a.select_one("img")
        image_url = None
        if img:
            src = img.get("src") or img.get("data-src", "")
            if src.startswith("http"):
                image_url = src
            elif src.startswith("/"):
                image_url = f"{self.base_url}{src}"

        return Exhibition(
            title=title,
            venue=venue,
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _parse_dates(self, text: str) -> tuple[date | None, date | None]:
        """Parse date format: '会期：2026年03月07日～2026年03月14日'."""
        pattern = (
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
            r".+?"
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        )
        match = re.search(pattern, text, re.DOTALL)
        if match:
            start = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            end = date(int(match.group(4)), int(match.group(5)), int(match.group(6)))
            return start, end
        return None, None
