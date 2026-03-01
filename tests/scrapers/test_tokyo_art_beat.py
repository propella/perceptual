import responses

from scripts.scrapers.tokyo_art_beat import TokyoArtBeatScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/events/abc123">
    <h3>キネティックアート展</h3>
    <img src="https://example.com/image.jpg">
    <span>2026/3/1-5/31</span>
    <span>@ 東京都美術館</span>
</a>
<a href="/events/def456">
    <h3>サウンドインスタレーション</h3>
    <span>2026/4/1-6/30</span>
</a>
<a href="/other/page">
    <h3>Not an event</h3>
</a>
</body>
</html>
"""


class TestTokyoArtBeatScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "キネティックアート展"
        assert exhibitions[0].source == "tokyo_art_beat"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 5

    @responses.activate
    def test_scrape_extracts_image_url(self):
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].image_url == "https://example.com/image.jpg"

    def test_parse_dates(self):
        scraper = TokyoArtBeatScraper()
        start, end = scraper._parse_dates("展覧会 2026/3/1-5/31 開催")
        assert start.year == 2026
        assert start.month == 3
        assert start.day == 1
        assert end.month == 5
        assert end.day == 31

    def test_parse_dates_year_wrap(self):
        scraper = TokyoArtBeatScraper()
        start, end = scraper._parse_dates("2026/11/1-2/28")
        assert start.year == 2026
        assert end.year == 2027

    @responses.activate
    def test_scrape_deduplicates_by_url(self):
        """Test that duplicate URLs are filtered out."""
        html_with_duplicates = """
        <html>
        <body>
        <a href="/events/abc123">
            <h3>展覧会A</h3>
            <span>2026/3/1-5/31</span>
        </a>
        <a href="/events/abc123">
            <h3>展覧会A</h3>
            <span>2026/3/1-5/31</span>
        </a>
        <a href="/events/def456">
            <h3>展覧会B</h3>
            <span>2026/4/1-6/30</span>
        </a>
        </body>
        </html>
        """
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=html_with_duplicates,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        urls = [e.source_url for e in exhibitions]
        assert len(urls) == len(set(urls))
