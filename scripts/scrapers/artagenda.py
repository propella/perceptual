import re
from datetime import date

from scripts.scrapers.base import BaseScraper, Exhibition


class ArtagendaScraper(BaseScraper):
    """Scraper for アートアジェンダ (https://www.artagenda.jp) - national art aggregator."""

    source_name = "artagenda"
    base_url = "https://www.artagenda.jp"
    events_url = "https://www.artagenda.jp/exhibition/index"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from artagenda."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        for a in soup.select("a[href*='/exhibition/detail/']"):
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
        if not href:
            return None

        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        title_elem = a.select_one("h3")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        if not title:
            return None

        # Look for date and venue in the next sibling elements
        parent = a.parent
        venue, start_date, end_date = self._extract_meta(parent, a)

        if not start_date or not end_date:
            return None

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
            venue=venue or "アートアジェンダ",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _extract_meta(
        self, parent, a
    ) -> tuple[str | None, date | None, date | None]:
        """Extract venue and date from sibling elements after the link."""
        venue = None
        start_date = None
        end_date = None

        if parent is None:
            return venue, start_date, end_date

        # Search all text in parent container
        full_text = parent.get_text(separator="\n")

        # Venue: [会場名|都道府県] pattern
        venue_match = re.search(r"\[([^｜\]]+)(?:｜[^\]]+)?\]", full_text)
        if venue_match:
            venue = venue_match.group(1).strip()

        # Date: 会期：YYYY年M月D日(曜)〜YYYY年M月D日(曜)
        start_date, end_date = self._parse_dates(full_text)

        return venue, start_date, end_date

    def _parse_dates(self, text: str) -> tuple[date | None, date | None]:
        """Parse date format: '会期：2026年3月7日(土)〜2026年5月24日(日)'."""
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
