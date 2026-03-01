import responses

from scripts.scrapers.design_sight import DesignSightScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/program/design_maestros/">
    <img src="/program/design_maestros/topweb.jpg">
    <h5>企画展「デザインの先生」</h5>
    <p>2025年11月21日 (金) - 2026年3月 8日 (日)</p>
</a>
<a href="/program/another_exhibition/">
    <h5>「インタラクティブ展」</h5>
    <p>2026年4月1日 (水) - 2026年6月30日 (火)</p>
</a>
<a href="/program/">
    <span>All Programs</span>
</a>
</body>
</html>
"""


class TestDesignSightScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.2121designsight.jp/program/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = DesignSightScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "デザインの先生"
        assert exhibitions[0].source == "design_sight"

    @responses.activate
    def test_scrape_sets_venue(self):
        responses.add(
            responses.GET,
            "https://www.2121designsight.jp/program/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = DesignSightScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].venue == "21_21 DESIGN SIGHT"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.2121designsight.jp/program/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = DesignSightScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2025
        assert exhibitions[0].start_date.month == 11
        assert exhibitions[0].end_date.year == 2026
        assert exhibitions[0].end_date.month == 3

    @responses.activate
    def test_scrape_builds_full_urls(self):
        responses.add(
            responses.GET,
            "https://www.2121designsight.jp/program/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = DesignSightScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].source_url == "https://www.2121designsight.jp/program/design_maestros/"
        assert exhibitions[0].image_url == "https://www.2121designsight.jp/program/design_maestros/topweb.jpg"

    def test_parse_dates(self):
        scraper = DesignSightScraper()
        start, end = scraper._parse_dates(
            "2025年11月21日 (金) - 2026年3月 8日 (日)"
        )
        assert start.year == 2025
        assert start.month == 11
        assert start.day == 21
        assert end.year == 2026
        assert end.month == 3
        assert end.day == 8

    def test_extract_title_removes_prefix(self):
        scraper = DesignSightScraper()

        class MockItem:
            def select_one(self, tag):
                if tag == "h5":
                    class MockElem:
                        def get_text(self, strip=False):
                            return "企画展「テスト展」"
                    return MockElem()
                return None

        title = scraper._extract_title(MockItem(), "")
        assert title == "テスト展"
