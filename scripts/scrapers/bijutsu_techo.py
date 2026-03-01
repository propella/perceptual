import json
import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class BijutsuTechoScraper(BaseScraper):
    """Scraper for Bijutsu Techo (美術手帖)."""

    source_name = "bijutsu_techo"
    base_url = "https://bijutsutecho.com"
    events_url = "https://bijutsutecho.com/exhibitions"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from Bijutsu Techo."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        # Try to extract from __NUXT__ data
        nuxt_data = self._extract_nuxt_data(soup)
        if nuxt_data:
            for exhibition in self._parse_nuxt_data(nuxt_data):
                if exhibition.source_url not in seen_urls:
                    seen_urls.add(exhibition.source_url)
                    exhibitions.append(exhibition)
        else:
            # Fallback to HTML parsing
            for exhibition in self._parse_html(soup):
                if exhibition.source_url not in seen_urls:
                    seen_urls.add(exhibition.source_url)
                    exhibitions.append(exhibition)

        return exhibitions

    def _extract_nuxt_data(self, soup) -> dict | None:
        """Extract exhibition data from __NUXT__ JavaScript object."""
        for script in soup.find_all("script"):
            text = script.string or ""
            if "window.__NUXT__" in text:
                match = re.search(r"window\.__NUXT__\s*=\s*(\{.+\})", text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
        return None

    def _parse_nuxt_data(self, data: dict) -> list[Exhibition]:
        """Parse exhibitions from NUXT data structure."""
        exhibitions = []

        def find_exhibitions(obj, results):
            if isinstance(obj, dict):
                if "title" in obj and "museumName" in obj:
                    results.append(obj)
                for value in obj.values():
                    find_exhibitions(value, results)
            elif isinstance(obj, list):
                for item in obj:
                    find_exhibitions(item, results)

        items = []
        find_exhibitions(data, items)

        for item in items:
            try:
                exhibition = self._parse_nuxt_item(item)
                if exhibition:
                    exhibitions.append(exhibition)
            except Exception:
                continue

        return exhibitions

    def _parse_nuxt_item(self, item: dict) -> Exhibition | None:
        """Parse a single exhibition from NUXT data."""
        title = item.get("title")
        venue = item.get("museumName")
        if not title or not venue:
            return None

        # Parse periods - try both startDate/endDate and startAt/endAt
        periods = item.get("periods", [])
        if not periods:
            return None

        first_period = periods[0]
        last_period = periods[-1]

        start_ts = first_period.get("startDate") or first_period.get("startAt")
        end_ts = last_period.get("endDate") or last_period.get("endAt")
        if not start_ts or not end_ts:
            return None

        start_date = datetime.fromtimestamp(start_ts).date()
        end_date = datetime.fromtimestamp(end_ts).date()

        return Exhibition(
            title=title,
            venue=venue,
            start_date=start_date,
            end_date=end_date,
            source_url=f"{self.base_url}/exhibitions/{item.get('id', '')}",
            source=self.source_name,
            image_url=item.get("imageUrl"),
            description=item.get("description"),
        )

    def _parse_html(self, soup) -> list[Exhibition]:
        """Fallback HTML parsing."""
        exhibitions = []

        for card in soup.select("a[href*='/exhibitions/']"):
            try:
                title_elem = card.select_one("h3")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                text = card.get_text()

                # Extract date
                date_match = re.search(
                    r"(\d{4})\.(\d{1,2})\.(\d{1,2})\s*[-–]\s*(\d{1,2})\.(\d{1,2})",
                    text,
                )
                if not date_match:
                    continue

                year = int(date_match.group(1))
                start_date = datetime(
                    year, int(date_match.group(2)), int(date_match.group(3))
                ).date()
                end_month = int(date_match.group(4))
                end_day = int(date_match.group(5))
                end_year = year if end_month >= start_date.month else year + 1
                end_date = datetime(end_year, end_month, end_day).date()

                href = card.get("href", "")
                img = card.select_one("img")

                exhibitions.append(
                    Exhibition(
                        title=title,
                        venue="会場情報なし",
                        start_date=start_date,
                        end_date=end_date,
                        source_url=f"{self.base_url}{href}" if href.startswith("/") else href,
                        source=self.source_name,
                        image_url=img.get("src") if img else None,
                    )
                )
            except Exception:
                continue

        return exhibitions
