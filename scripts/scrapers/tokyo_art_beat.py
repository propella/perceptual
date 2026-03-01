import json
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

        # Extract image map from __NEXT_DATA__ JSON
        image_map = self._extract_next_data_images(soup)

        for item in soup.select("a[href^='/events/']"):
            try:
                exhibition = self._parse_item(item, image_map)
                if exhibition and exhibition.source_url not in seen_urls:
                    seen_urls.add(exhibition.source_url)
                    exhibitions.append(exhibition)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, item, image_map: dict | None = None) -> Exhibition | None:
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

        # Extract venue from first <p> after <h3>
        venue = self._extract_venue(item)

        # Extract image: try HTML first, then __NEXT_DATA__
        image_url = self._extract_image_url(item)
        if not image_url and image_map:
            image_url = self._lookup_image(href, image_map)

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
        """Extract venue name from item.

        Tokyo Art Beat cards have the venue in the first <p> after <h3>.
        Falls back to @ or 会場: patterns in text.
        """
        # Primary: first <p> sibling after <h3>
        h3 = item.select_one("h3")
        if h3:
            p = h3.find_next_sibling("p")
            if p:
                venue = p.get_text(strip=True)
                if venue and not re.match(r"^\d{4}/", venue) and venue != "開催中":
                    return venue

        # Fallback: text patterns
        text = item.get_text(separator=" ")
        for pattern in [r"@\s*(.+?)(?:\s|$)", r"会場[：:]\s*(.+?)(?:\s|$)"]:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_image_url(self, item) -> str | None:
        """Extract image URL, handling protocol-relative URLs."""
        img = item.select_one("img")
        if not img:
            return None

        src = img.get("src") or img.get("data-src") or ""
        if not src:
            return None

        if src.startswith("//"):
            return f"https:{src}"
        return src if src.startswith("http") else None

    def _extract_next_data_images(self, soup) -> dict[str, str]:
        """Extract slug->image_url map from __NEXT_DATA__ JSON."""
        image_map: dict[str, str] = {}
        script = soup.select_one("script#__NEXT_DATA__")
        if not script or not script.string:
            return image_map

        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            return image_map

        # Find event objects recursively in the JSON
        events = self._find_events(data)
        for event in events:
            slug = event.get("slug", "")
            image_url = self._get_image_url_from_event(event)
            if slug and image_url:
                image_map[slug] = image_url

        return image_map

    def _find_events(self, obj) -> list[dict]:
        """Recursively find event objects (dicts with slug + imageposter)."""
        results = []
        if isinstance(obj, dict):
            if "slug" in obj and ("imageposter" in obj or "eventName" in obj):
                results.append(obj)
            for value in obj.values():
                results.extend(self._find_events(value))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(self._find_events(item))
        return results

    def _get_image_url_from_event(self, event: dict) -> str | None:
        """Extract image URL from a __NEXT_DATA__ event object."""
        poster = event.get("imageposter")
        if not isinstance(poster, dict):
            return None
        fields = poster.get("fields")
        if not isinstance(fields, dict):
            return None
        file_info = fields.get("file")
        if not isinstance(file_info, dict):
            return None
        url = file_info.get("url", "")
        if url.startswith("//"):
            return f"https:{url}"
        return url if url.startswith("http") else None

    def _lookup_image(self, href: str, image_map: dict[str, str]) -> str | None:
        """Look up image URL by matching href against slug in image_map."""
        for slug, url in image_map.items():
            if slug in href:
                return url
        return None
