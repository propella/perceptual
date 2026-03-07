import re
from datetime import date

from scripts.scrapers.base import BaseScraper, Exhibition


class Kanazawa21Scraper(BaseScraper):
    """Scraper for 金沢21世紀美術館 (https://www.kanazawa21.jp)."""

    source_name = "kanazawa21"
    base_url = "https://www.kanazawa21.jp"
    events_url = "https://www.kanazawa21.jp/exhibition/"
    venue = "金沢21世紀美術館"
    address = "石川県金沢市広坂1-2-1"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from 金沢21世紀美術館."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        # Links to detail pages use data_list.php?g=17&d=[ID]
        for a in soup.select("a[href*='data_list.php']"):
            try:
                exhibition = self._parse_item(a)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, a) -> Exhibition | None:
        """Parse a single exhibition item."""
        href = a.get("href", "")
        if not href or "g=17" not in href and "g=76" not in href:
            return None

        if href.startswith("http"):
            source_url = href
        elif href.startswith("/"):
            source_url = f"{self.base_url}{href}"
        else:
            source_url = f"{self.base_url}/{href.lstrip('../')}"

        text = a.get_text(separator=" ", strip=True)

        title_elem = a.select_one("h4") or a.select_one("h3") or a.select_one("h2")
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            # Fall back to first non-date text
            title = re.sub(r"\d{4}年.*$", "", text).strip()
        if not title:
            return None

        start_date, end_date = self._parse_dates(text)
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
            venue=self.venue,
            address=self.address,
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

    def _parse_dates(self, text: str) -> tuple[date | None, date | None]:
        """Parse date format: '2025年10月18日(土) - 2026年3月15日(日)'."""
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
