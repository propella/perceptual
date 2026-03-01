import re
from datetime import datetime

from scripts.scrapers.base import BaseScraper, Exhibition


class ICCScraper(BaseScraper):
    """Scraper for NTT ICC (InterCommunication Center)."""

    source_name = "icc"
    base_url = "https://www.ntticc.or.jp"
    events_url = "https://www.ntticc.or.jp/ja/exhibitions/"

    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from ICC."""
        soup = self.fetch(self.events_url)
        exhibitions = []
        seen_urls = set()

        # Look for links with year in path (e.g., /ja/exhibitions/2025/...)
        for item in soup.select("a[href*='/exhibitions/202']"):
            try:
                exhibition = self._parse_item(item)
                if exhibition and exhibition.source_url not in seen_urls:
                    exhibitions.append(exhibition)
                    seen_urls.add(exhibition.source_url)
            except Exception:
                continue

        # Fetch images from individual exhibition pages
        for exhibition in exhibitions:
            if not exhibition.image_url:
                try:
                    exhibition.image_url = self._fetch_detail_image(
                        exhibition.source_url
                    )
                except Exception:
                    pass

        return exhibitions

    def _parse_item(self, item) -> Exhibition | None:
        """Parse a single exhibition item."""
        href = item.get("href", "")
        if not href or "/exhibitions/" not in href:
            return None

        # Get text from item and parent
        text = item.get_text(separator=" ", strip=True)
        parent = item.find_parent("li") or item.find_parent("div") or item.find_parent()
        parent_text = parent.get_text(separator=" ", strip=True) if parent else text

        if not text and not parent_text:
            return None

        # Extract title (usually the main text)
        title = self._extract_title(item, text or parent_text)
        if not title:
            return None

        # Extract date range - try parent text first
        start_date, end_date = self._parse_dates(parent_text)
        if not start_date or not end_date:
            start_date, end_date = self._parse_dates(text)
        if not start_date or not end_date:
            return None

        # Build full URL
        if href.startswith("/"):
            source_url = f"{self.base_url}{href}"
        else:
            source_url = href

        # Extract image
        img = item.select_one("img")
        image_url = img.get("src") if img else None
        if image_url and image_url.startswith("/"):
            image_url = f"{self.base_url}{image_url}"

        return Exhibition(
            title=title,
            venue="NTTインターコミュニケーション・センター [ICC]",
            address="東京都新宿区西新宿3-20-2 東京オペラシティタワー4F",
            start_date=start_date,
            end_date=end_date,
            source_url=source_url,
            source=self.source_name,
            image_url=image_url,
            tags=["メディアアート"],
        )

    def _extract_title(self, item, text: str) -> str | None:
        """Extract exhibition title."""
        # Try to find title in heading elements
        for tag in ["h1", "h2", "h3", "h4"]:
            elem = item.select_one(tag)
            if elem:
                return elem.get_text(strip=True)

        # Remove date patterns and category labels from text
        title = re.sub(
            r"\d{4}年\d{1,2}月\d{1,2}日.*$",
            "",
            text,
            flags=re.DOTALL,
        )
        title = re.sub(r"^(展示|企画展|イベント)\s*", "", title)
        title = title.strip()

        return title if len(title) > 2 else None

    def _parse_dates(self, text: str) -> tuple:
        """Parse Japanese date format like '2025年12月13日（土）—2026年3月8日（日）'."""
        pattern = (
            r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?"
            r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        )
        match = re.search(pattern, text)
        if match:
            start_date = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            ).date()
            end_date = datetime(
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6)),
            ).date()
            return start_date, end_date

        return None, None

    def _fetch_detail_image(self, url: str) -> str | None:
        """Fetch exhibition detail page and extract first exhibition image."""
        soup = self.fetch(url)
        for img in soup.select("img[src*='/uploads/assets/']"):
            src = img.get("src", "").strip()
            if src.startswith("/"):
                return f"{self.base_url}{src}"
            if src.startswith("http"):
                return src
        return None
