import re
from datetime import date

from scripts.scrapers.base import BaseScraper, Exhibition


class NMAOScraper(BaseScraper):
    """Scraper for 国立国際美術館 / National Museum of Art, Osaka (https://www.nmao.go.jp)."""

    source_name = "nmao"
    base_url = "https://www.nmao.go.jp"
    events_url = "https://www.nmao.go.jp/exhibition/current_exhibition/"
    venue = "国立国際美術館"
    address = "大阪府大阪市北区中之島4-2-55"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from 国立国際美術館."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        for a in soup.select("a[href*='/events/event/']"):
            try:
                exhibition = self._parse_item(a)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, a) -> Exhibition | None:
        """Parse a single exhibition item from its link element."""
        href = a.get("href", "")
        if not href:
            return None

        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        # Image is inside the <a> tag
        img = a.select_one("img")
        image_url = None
        if img:
            src = img.get("src") or img.get("data-src", "")
            if src.startswith("http"):
                image_url = src
            elif src.startswith("/"):
                image_url = f"{self.base_url}{src}"

        # Title and date appear as sibling elements after the <a> tag
        parent = a.parent
        if parent is None:
            return None

        # Find title: h2 or h3 following this link within the parent
        title = self._find_next_text(a, ["h2", "h3", "h4"])
        if not title:
            return None

        # Find date: p element following this link
        date_text = self._find_next_text(a, ["p"])
        if not date_text:
            return None

        start_date, end_date = self._parse_dates(date_text)
        if not start_date or not end_date:
            return None

        return Exhibition(
            title=title,
            venue=self.venue,
            address=self.address,
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _find_next_text(self, element, tags: list[str]) -> str | None:
        """Find the next sibling element matching one of the given tags."""
        sibling = element.find_next_sibling()
        while sibling:
            if sibling.name in tags:
                text = sibling.get_text(strip=True)
                if text:
                    return text
            sibling = sibling.find_next_sibling()
        return None

    def _parse_dates(self, text: str) -> tuple[date | None, date | None]:
        """Parse date format: '2026年3月14日（土）– 2026年6月14日（日）'."""
        pattern = (
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
            r"[^(\d{4}年)]*"
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        )
        match = re.search(pattern, text)
        if match:
            start = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            end = date(int(match.group(4)), int(match.group(5)), int(match.group(6)))
            return start, end
        return None, None
