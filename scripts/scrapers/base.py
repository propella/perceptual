from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class Exhibition:
    """Exhibition data structure."""

    title: str
    venue: str
    start_date: date
    end_date: date
    source_url: str
    source: str
    description: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None


class BaseScraper(ABC):
    """Base class for exhibition scrapers."""

    source_name: str = "unknown"
    base_url: str = ""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-Agent": "perceptual-exhibition-collector/0.1.0"}
        )

    def fetch(self, url: str) -> BeautifulSoup:
        """Fetch URL and return parsed HTML."""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        # Force UTF-8 encoding for Japanese sites
        response.encoding = "utf-8"
        return BeautifulSoup(response.text, "lxml")

    @abstractmethod
    def scrape(self) -> list[Exhibition]:
        """Scrape exhibitions from the source. Must be implemented by subclasses."""
        pass
