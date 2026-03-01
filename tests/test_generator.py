import json
from datetime import date
from pathlib import Path

from ics import Calendar

from scripts.generator import (
    exhibition_to_dict,
    generate_ics,
    generate_id,
    generate_json,
)
from scripts.scrapers.base import Exhibition


def make_exhibition():
    return Exhibition(
        title="テスト展",
        venue="テスト美術館",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 5, 31),
        source_url="https://example.com/exhibition",
        source="test",
        description="テスト説明",
        address="東京都渋谷区",
        tags=["キネティックアート"],
    )


class TestGenerateId:
    def test_generates_consistent_id(self):
        exhibition = make_exhibition()
        id1 = generate_id(exhibition)
        id2 = generate_id(exhibition)
        assert id1 == id2

    def test_different_exhibitions_have_different_ids(self):
        e1 = make_exhibition()
        e2 = Exhibition(
            title="別の展覧会",
            venue="別の美術館",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 5, 31),
            source_url="https://example.com",
            source="test",
        )
        assert generate_id(e1) != generate_id(e2)

    def test_id_is_16_chars(self):
        exhibition = make_exhibition()
        assert len(generate_id(exhibition)) == 16


class TestExhibitionToDict:
    def test_converts_to_dict(self):
        exhibition = make_exhibition()
        result = exhibition_to_dict(exhibition)
        assert result["title"] == "テスト展"
        assert result["venue"] == "テスト美術館"
        assert result["startDate"] == "2026-03-01"
        assert result["endDate"] == "2026-05-31"
        assert result["tags"] == ["キネティックアート"]
        assert "id" in result


class TestGenerateJson:
    def test_creates_json_file(self, tmp_path: Path):
        exhibitions = [make_exhibition()]
        output = tmp_path / "data" / "exhibitions.json"
        generate_json(exhibitions, output)

        assert output.exists()
        data = json.loads(output.read_text())
        assert "lastUpdated" in data
        assert len(data["exhibitions"]) == 1
        assert data["exhibitions"][0]["title"] == "テスト展"

    def test_creates_parent_directories(self, tmp_path: Path):
        output = tmp_path / "deep" / "nested" / "path" / "exhibitions.json"
        generate_json([], output)
        assert output.exists()


class TestGenerateIcs:
    def test_creates_ics_file(self, tmp_path: Path):
        exhibitions = [make_exhibition()]
        output = tmp_path / "data" / "exhibitions.ics"
        generate_ics(exhibitions, output)

        assert output.exists()
        calendar = Calendar(output.read_text())
        events = list(calendar.events)
        assert len(events) == 1
        assert events[0].name == "テスト展"

    def test_event_has_location(self, tmp_path: Path):
        exhibitions = [make_exhibition()]
        output = tmp_path / "exhibitions.ics"
        generate_ics(exhibitions, output)

        calendar = Calendar(output.read_text())
        event = list(calendar.events)[0]
        assert event.location == "東京都渋谷区"

    def test_event_description_includes_url(self, tmp_path: Path):
        exhibitions = [make_exhibition()]
        output = tmp_path / "exhibitions.ics"
        generate_ics(exhibitions, output)

        calendar = Calendar(output.read_text())
        event = list(calendar.events)[0]
        assert "https://example.com/exhibition" in event.description

    def test_empty_exhibitions(self, tmp_path: Path):
        output = tmp_path / "exhibitions.ics"
        generate_ics([], output)

        calendar = Calendar(output.read_text())
        assert len(list(calendar.events)) == 0
