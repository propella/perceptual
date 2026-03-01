from datetime import date

from scripts.main import deduplicate_exhibitions
from scripts.scrapers.base import Exhibition


def make_exhibition(source_url: str, title: str = "Test"):
    """Helper to create exhibition for testing."""
    return Exhibition(
        title=title,
        venue="テスト美術館",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 5, 31),
        source_url=source_url,
        source="test",
    )


class TestDeduplicateExhibitions:
    def test_removes_duplicates(self):
        exhibitions = [
            make_exhibition("https://example.com/1", "展覧会A"),
            make_exhibition("https://example.com/1", "展覧会A"),
            make_exhibition("https://example.com/2", "展覧会B"),
        ]
        result = deduplicate_exhibitions(exhibitions)
        assert len(result) == 2

    def test_keeps_first_occurrence(self):
        exhibitions = [
            make_exhibition("https://example.com/1", "First"),
            make_exhibition("https://example.com/1", "Second"),
        ]
        result = deduplicate_exhibitions(exhibitions)
        assert result[0].title == "First"

    def test_empty_list(self):
        assert deduplicate_exhibitions([]) == []

    def test_no_duplicates(self):
        exhibitions = [
            make_exhibition("https://example.com/1"),
            make_exhibition("https://example.com/2"),
        ]
        result = deduplicate_exhibitions(exhibitions)
        assert len(result) == 2
