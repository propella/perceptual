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

        for article in soup.select("article.item-article"):
            try:
                exhibition = self._parse_article(article)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        return exhibitions

    def _parse_article(self, article) -> Exhibition | None:
        """Parse a single article element.

        Actual HTML structure:
          <article class="item-article item-exhibitions">
            <figure class="item-img">
              <a href="/exhibitions/ID/"><img /></a>
            </figure>
            <div class="item-txt">
              <h3 class="article-title"><a href="..."><span>Title</span></a></h3>
              <p>Venue<br/>location</p>
              <p>会期：dates</p>
            </div>
          </article>
        """
        # URL and source_url from h3 link or figure link
        h3 = article.select_one("h3.article-title")
        if not h3:
            return None
        title = h3.get_text(strip=True)
        if not title:
            return None

        h3_link = h3.select_one("a")
        if not h3_link:
            return None
        href = h3_link.get("href", "")
        if not re.search(r"/exhibitions/\d+/", href):
            return None
        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        # Image from figure (skip base64 data URIs, fall back to data-src)
        image_url = None
        img = article.select_one("figure img")
        if img:
            src = img.get("src", "")
            if src.startswith("data:"):
                src = img.get("data-src", "")
            if src.startswith("http"):
                image_url = src
            elif src.startswith("/"):
                image_url = f"{self.base_url}{src}"

        # Text content from item-txt
        item_txt = article.select_one("div.item-txt")
        if not item_txt:
            return None

        article_text = item_txt.get_text(separator=" ", strip=True)
        start_date, end_date = self._parse_dates(article_text)
        if not start_date or not end_date:
            return None

        # Venue: first <p> that has no year pattern
        venue = "artscape"
        for p in item_txt.select("p"):
            text = p.get_text(strip=True)
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

    def _parse_item(self, a) -> Exhibition | None:
        """Legacy: parse from <a> element (kept for test compatibility)."""
        href = a.get("href", "")
        if not re.search(r"/exhibitions/\d+/", href):
            return None

        source_url = href if href.startswith("http") else f"{self.base_url}{href}"

        img = a.select_one("img")
        image_url = None
        if img:
            src = img.get("src", "")
            if src.startswith("data:"):
                src = img.get("data-src", "")
            if src.startswith("http"):
                image_url = src
            elif src.startswith("/"):
                image_url = f"{self.base_url}{src}"

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

        venue = "artscape"
        for elem in parent.select("p, div"):
            if elem.find("h3"):
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
