from datetime import date

from scripts.filters import filter_exhibitions, matches_filter
from scripts.scrapers.base import Exhibition


def make_exhibition(title: str, description: str = "", tags: list[str] | None = None):
    """Helper to create exhibition for testing."""
    return Exhibition(
        title=title,
        venue="テスト美術館",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 5, 31),
        source_url="https://example.com",
        source="test",
        description=description,
        tags=tags,
    )


class TestMatchesFilter:
    def test_matches_genre_keyword(self):
        exhibition = make_exhibition("キネティックアート展")
        assert matches_filter(exhibition) is True

    def test_matches_artist_name(self):
        exhibition = make_exhibition("テオ・ヤンセン展")
        assert matches_filter(exhibition) is True

    def test_matches_english_keyword(self):
        exhibition = make_exhibition("Sound Art Festival")
        assert matches_filter(exhibition) is True

    def test_matches_in_description(self):
        exhibition = make_exhibition("現代美術展", description="メディアアートの最前線")
        assert matches_filter(exhibition) is True

    def test_matches_in_tags(self):
        exhibition = make_exhibition("展覧会", tags=["インスタレーション"])
        assert matches_filter(exhibition) is True

    def test_no_match(self):
        exhibition = make_exhibition("日本画展", description="伝統的な日本画")
        assert matches_filter(exhibition) is False

    def test_case_insensitive(self):
        exhibition = make_exhibition("KINETIC ART")
        assert matches_filter(exhibition) is True


class TestFilterExhibitions:
    def test_filters_list(self):
        exhibitions = [
            make_exhibition("キネティックアート展"),
            make_exhibition("日本画展"),
            make_exhibition("サウンドアート展"),
        ]
        result = filter_exhibitions(exhibitions)
        assert len(result) == 2
        assert result[0].title == "キネティックアート展"
        assert result[1].title == "サウンドアート展"

    def test_empty_list(self):
        assert filter_exhibitions([]) == []

    def test_no_matches(self):
        exhibitions = [
            make_exhibition("日本画展"),
            make_exhibition("油絵展"),
        ]
        assert filter_exhibitions(exhibitions) == []
