import re
from datetime import date
from urllib.parse import urljoin

from scripts.scrapers.base import BaseScraper, Exhibition


class MakerFaireScraper(BaseScraper):
    """Scraper for Maker Faire / Make Japan (makezine.jp)."""

    source_name = "maker_faire"
    base_url = "https://makezine.jp"
    events_url = "https://makezine.jp/event/"

    def scrape(self) -> list[Exhibition]:
        """Scrape Maker Faire events from makezine.jp."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls = set()

        # Find links to annual event pages (e.g., /event/mft2026/)
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if re.search(r"/event/mft\d{4}", href):
                url = urljoin(self.base_url, href)
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                try:
                    detail = self.fetch(url)
                    ex = self._parse_event_page(detail, url)
                    if ex:
                        exhibitions.append(ex)
                except Exception:
                    continue

        # Fallback: parse the /event/ page itself
        if not exhibitions:
            ex = self._parse_event_page(soup, self.events_url)
            if ex:
                exhibitions.append(ex)

        return exhibitions

    def _parse_event_page(self, soup, url: str) -> Exhibition | None:
        """Parse a single Maker Faire event page."""
        # Title: find heading containing "Maker Faire"
        title = None
        for tag in ["h1", "h2", "h3"]:
            for el in soup.select(tag):
                t = el.get_text(strip=True)
                if "Maker Faire" in t or "メイカーフェア" in t:
                    title = t
                    break
            if title:
                break

        if not title:
            return None

        # Dates: look for 日時 section with YYYY/M/D format
        start_date, end_date = self._extract_dates(soup)
        if not start_date:
            return None

        # Venue: look for 会場 section
        venue = self._extract_text_after_heading(soup, "会場") or "Maker Faire Tokyo"

        # Image
        image_url = None
        for img in soup.select("img[src]"):
            src = img.get("src", "")
            if any(kw in src for kw in ["mft", "maker", "event", "top"]):
                image_url = urljoin(self.base_url, src)
                break

        return Exhibition(
            title=title,
            venue=venue,
            start_date=start_date,
            end_date=end_date,
            source_url=url,
            source=self.source_name,
            image_url=image_url,
            tags=["メイカー", "ものづくり"],
        )

    def _extract_dates(self, soup) -> tuple:
        """Extract start and end dates from 日時 section."""
        # Look for 日時 heading and extract dates from surrounding text
        for h in soup.select("h2, h3, h4, h5, dt, th"):
            if "日時" in h.get_text():
                parent = h.find_parent(["div", "section", "article", "dl", "table", "tr"])
                text = parent.get_text() if parent else ""
                result = self._parse_slash_dates(text)
                if result[0]:
                    return result

        # Fallback: search entire page for slash-format dates
        return self._parse_slash_dates(soup.get_text())

    def _parse_slash_dates(self, text: str) -> tuple:
        """Parse YYYY/M/D dates from text. Returns (start_date, end_date)."""
        matches = re.findall(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
        if matches:
            start = date(int(matches[0][0]), int(matches[0][1]), int(matches[0][2]))
            end = date(int(matches[-1][0]), int(matches[-1][1]), int(matches[-1][2]))
            return start, end
        return None, None

    def _extract_text_after_heading(self, soup, heading_text: str) -> str | None:
        """Return the text content immediately after a heading element."""
        for h in soup.select("h2, h3, h4, h5, dt, th"):
            if heading_text in h.get_text():
                next_el = h.find_next_sibling()
                if next_el:
                    text = next_el.get_text(strip=True)
                    return text[:80] if text else None
        return None
