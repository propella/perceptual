import responses

from scripts.scrapers.mot import MOTScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/exhibitions/test-exhibition/">
    <article class="l-exhibitions-article">
        <img src="/images/exhibition1.jpg">
        <h2>現代美術の新展開</h2>
        <span>2025.12.3 - 2026.3.29</span>
        <p class="p-exhibitions-label">開催中</p>
    </article>
</a>
<a href="/exhibitions/another-show/">
    <article class="l-exhibitions-article">
        <h2>インスタレーション展</h2>
        <span>2026年4月1日 - 2026年6月30日</span>
    </article>
</a>
<a href="/exhibitions/">
    <span>All Exhibitions</span>
</a>
</body>
</html>
"""


class TestMOTScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.mot-art-museum.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MOTScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "現代美術の新展開"
        assert exhibitions[0].source == "mot"

    @responses.activate
    def test_scrape_sets_venue(self):
        responses.add(
            responses.GET,
            "https://www.mot-art-museum.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MOTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].venue == "東京都現代美術館"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.mot-art-museum.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MOTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2025
        assert exhibitions[0].start_date.month == 12
        assert exhibitions[0].end_date.year == 2026
        assert exhibitions[0].end_date.month == 3

    @responses.activate
    def test_scrape_builds_full_urls(self):
        responses.add(
            responses.GET,
            "https://www.mot-art-museum.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MOTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].source_url == "https://www.mot-art-museum.jp/exhibitions/test-exhibition/"
        assert exhibitions[0].image_url == "https://www.mot-art-museum.jp/images/exhibition1.jpg"

    def test_parse_dates_dot_format(self):
        scraper = MOTScraper()
        start, end = scraper._parse_dates("2025.12.3 - 2026.3.29")
        assert start.year == 2025
        assert start.month == 12
        assert start.day == 3
        assert end.year == 2026
        assert end.month == 3
        assert end.day == 29

    def test_parse_dates_japanese_format(self):
        scraper = MOTScraper()
        start, end = scraper._parse_dates("2025年12月3日 - 2026年3月29日")
        assert start.year == 2025
        assert start.month == 12
        assert end.year == 2026
        assert end.month == 3
