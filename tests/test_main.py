import json
import tempfile
from datetime import date
from pathlib import Path

from scripts.main import deduplicate_exhibitions, load_existing_exhibitions, merge_exhibitions
from scripts.scrapers.base import Exhibition

TODAY = date(2026, 3, 7)


def make_exhibition(source_url: str, title: str = "Test", end_date: date = date(2026, 5, 31)):
    """Helper to create exhibition for testing."""
    return Exhibition(
        title=title,
        venue="テスト美術館",
        start_date=date(2026, 3, 1),
        end_date=end_date,
        source_url=source_url,
        source="test",
    )


class TestMergeExhibitions:
    def test_new_exhibitions_are_added(self):
        existing = []
        new = [make_exhibition("https://example.com/1", "新展覧会")]
        result = merge_exhibitions(existing, new, TODAY)
        assert len(result) == 1
        assert result[0].title == "新展覧会"

    def test_existing_active_exhibitions_are_preserved(self):
        existing = [make_exhibition("https://example.com/1", "既存展覧会")]
        new = [make_exhibition("https://example.com/2", "新展覧会")]
        result = merge_exhibitions(existing, new, TODAY)
        urls = {ex.source_url for ex in result}
        assert "https://example.com/1" in urls
        assert "https://example.com/2" in urls

    def test_expired_existing_exhibitions_are_dropped(self):
        expired = make_exhibition("https://example.com/old", end_date=date(2026, 3, 6))
        active = make_exhibition("https://example.com/active")
        result = merge_exhibitions([expired, active], [], TODAY)
        urls = {ex.source_url for ex in result}
        assert "https://example.com/old" not in urls
        assert "https://example.com/active" in urls

    def test_new_overwrites_existing_same_url(self):
        existing = [make_exhibition("https://example.com/1", "旧タイトル")]
        new = [make_exhibition("https://example.com/1", "新タイトル")]
        result = merge_exhibitions(existing, new, TODAY)
        assert len(result) == 1
        assert result[0].title == "新タイトル"

    def test_existing_not_in_new_scrape_is_preserved(self):
        existing = [make_exhibition("https://example.com/1", "既存のみ")]
        new = [make_exhibition("https://example.com/2", "新規のみ")]
        result = merge_exhibitions(existing, new, TODAY)
        assert len(result) == 2


class TestLoadExistingExhibitions:
    def test_returns_empty_list_if_file_not_exists(self):
        result = load_existing_exhibitions(Path("/nonexistent/path.json"))
        assert result == []

    def test_loads_exhibitions_from_json(self):
        data = {
            "lastUpdated": "2026-03-01T00:00:00+00:00",
            "exhibitions": [
                {
                    "id": "abc123",
                    "title": "テスト展",
                    "venue": "テスト美術館",
                    "startDate": "2026-03-01",
                    "endDate": "2026-05-31",
                    "sourceUrl": "https://example.com/1",
                    "source": "test",
                    "description": None,
                    "address": None,
                    "imageUrl": None,
                    "tags": [],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmp_path = Path(f.name)
        result = load_existing_exhibitions(tmp_path)
        tmp_path.unlink()
        assert len(result) == 1
        assert result[0].title == "テスト展"
        assert result[0].start_date == date(2026, 3, 1)
        assert result[0].end_date == date(2026, 5, 31)

    def test_skips_invalid_items(self):
        data = {
            "exhibitions": [
                {"id": "bad"},  # missing required fields
                {
                    "id": "ok",
                    "title": "正常展",
                    "venue": "館",
                    "startDate": "2026-03-01",
                    "endDate": "2026-05-31",
                    "sourceUrl": "https://example.com/ok",
                    "source": "test",
                },
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmp_path = Path(f.name)
        result = load_existing_exhibitions(tmp_path)
        tmp_path.unlink()
        assert len(result) == 1
        assert result[0].title == "正常展"


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
