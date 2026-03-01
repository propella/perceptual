import pytest


@pytest.fixture
def sample_exhibition():
    """Sample exhibition data for testing."""
    return {
        "id": "test-id-123",
        "title": "テスト展覧会",
        "description": "テスト用の展覧会データ",
        "venue": "テスト美術館",
        "address": "東京都渋谷区",
        "startDate": "2026-03-01",
        "endDate": "2026-05-31",
        "imageUrl": "https://example.com/image.jpg",
        "sourceUrl": "https://example.com/exhibition",
        "source": "test_source",
        "tags": ["キネティックアート", "メディアアート"],
    }
