import re
from datetime import date

from scripts.scrapers.base import BaseScraper, Exhibition


class ArtagendaScraper(BaseScraper):
    """Scraper for アートアジェンダ (https://www.artagenda.jp) - national art aggregator."""

    source_name = "artagenda"
    base_url = "https://www.artagenda.jp"
    events_url = "https://www.artagenda.jp/exhibition/index"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from artagenda.

        The actual HTML structure:
          <a href="/exhibition/detail/ID"><img></a>   <- image link
          <h3><a href="/exhibition/detail/ID">Title</a></h3>  <- title in h3
          <p>[Venue|Prefecture]status</p>
          <p>会期：dates</p>
        """
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls: set[str] = set()

        # Select title links: <a> inside <h3> pointing to exhibition detail
        for h3_link in soup.select("h3 a[href*='/exhibition/detail/']"):
            try:
                exhibition = self._parse_item(h3_link)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_item(self, a) -> Exhibition | None:
        """Parse a single exhibition from the title link (inside h3)."""
        href = a.get("href", "")
        if not href:
            return None

        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        title = a.get_text(strip=True)
        if not title:
            return None

        # h3 is the parent of this title link
        h3 = a.parent

        # Image is in a preceding sibling <a> with the same href
        image_url = None
        prev_a = h3.find_previous_sibling("a")
        if prev_a and prev_a.get("href") == href:
            img = prev_a.select_one("img")
            if img:
                src = img.get("src") or img.get("data-src", "")
                if src.startswith("http"):
                    image_url = src
                elif src.startswith("/"):
                    image_url = f"{self.base_url}{src}"

        # Venue and dates are in <p> siblings following the h3
        venue = None
        start_date = None
        end_date = None
        for sibling in h3.find_next_siblings():
            if sibling.name in ("h3", "h2"):
                break  # Next exhibition item
            if sibling.name != "p":
                continue
            text = sibling.get_text(strip=True)
            if not text:
                continue
            if venue is None:
                venue_match = re.search(r"\[([^｜\]]+)(?:｜[^\]]+)?\]", text)
                if venue_match:
                    venue = venue_match.group(1).strip()
            if start_date is None:
                s, e = self._parse_dates(text)
                if s and e:
                    start_date, end_date = s, e

        if not start_date or not end_date:
            return None

        return Exhibition(
            title=title,
            venue=venue or "アートアジェンダ",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
        )

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
