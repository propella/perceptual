from datetime import date

import pytest
import responses

from scripts.scrapers.base import BaseScraper, Exhibition


class DummyScraper(BaseScraper):
    """Dummy scraper for testing."""

    source_name = "dummy"
    base_url = "https://example.com"

    def scrape(self) -> list[Exhibition]:
        return []


class TestExhibition:
    def test_exhibition_creation(self):
        exhibition = Exhibition(
            title="テスト展",
            venue="テスト美術館",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 5, 31),
            source_url="https://example.com/exhibition",
            source="test",
        )
        assert exhibition.title == "テスト展"
        assert exhibition.venue == "テスト美術館"
        assert exhibition.description is None

    def test_exhibition_with_optional_fields(self):
        exhibition = Exhibition(
            title="テスト展",
            venue="テスト美術館",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 5, 31),
            source_url="https://example.com/exhibition",
            source="test",
            description="説明文",
            tags=["キネティックアート"],
        )
        assert exhibition.description == "説明文"
        assert exhibition.tags == ["キネティックアート"]


class TestBaseScraper:
    def test_scraper_has_user_agent(self):
        scraper = DummyScraper()
        assert "perceptual" in scraper.session.headers["User-Agent"]

    def test_scraper_with_custom_session(self):
        import requests

        custom_session = requests.Session()
        custom_session.headers["X-Custom"] = "test"
        scraper = DummyScraper(session=custom_session)
        assert scraper.session.headers["X-Custom"] == "test"

    @responses.activate
    def test_fetch_returns_soup(self):
        responses.add(
            responses.GET,
            "https://example.com/page",
            body="<html><body><h1>Test</h1></body></html>",
            status=200,
        )
        scraper = DummyScraper()
        soup = scraper.fetch("https://example.com/page")
        assert soup.h1.text == "Test"

    @responses.activate
    def test_fetch_raises_on_error(self):
        responses.add(
            responses.GET,
            "https://example.com/error",
            status=404,
        )
        scraper = DummyScraper()
        with pytest.raises(Exception):
            scraper.fetch("https://example.com/error")
