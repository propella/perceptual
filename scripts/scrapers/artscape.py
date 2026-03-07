import re
from datetime import date

from scripts.scrapers.base import Exhibition
from scripts.scrapers.base_playwright import PlaywrightBaseScraper


class ArtscapeScraper(PlaywrightBaseScraper):
    """Scraper for artscape (https://artscape.jp) - national art exhibition aggregator."""

    source_name = "artscape"
    base_url = "https://artscape.jp"
    events_url = "https://artscape.jp/exhibitions/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from artscape."""
        soup = self.fetch_js(self.events_url)
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
        """Parse a single exhibition link element.

        The actual HTML structure has the h3, venue, and date OUTSIDE the <a> tag,
        in the parent container div:
          <div>
            <a href="/exhibitions/ID/"><img></a>
            <div><h3>Title</h3></div>
            <div>Venue</div>
            <div>会期：dates</div>
          </div>
        """
        href = a.get("href", "")
        if not re.search(r"/exhibitions/\d+/", href):
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

        # Title, venue, dates are in the parent container (sibling divs of the <a>)
        parent = a.parent
        if parent is None:
            return None

        title_elem = parent.select_one("h3")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        if not title:
            return None

        parent_text = parent.get_text(separator=" ", strip=True)
        start_date, end_date = self._parse_dates(parent_text)
        if not start_date or not end_date:
            return None

        # Venue: first div/p in parent that has no h3 (not the title/badge div) and no dates
        venue = "artscape"
        for elem in parent.select("p, div"):
            if elem.find("h3"):  # Skip the title+status badge div
                continue
            text = elem.get_text(strip=True)
            if text and not re.search(r"\d{4}年", text):
                venue = text
                break

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
