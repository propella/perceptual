import responses

from scripts.scrapers.tokyo_art_beat import TokyoArtBeatScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/events/abc123">
    <h3>キネティックアート展</h3>
    <p>東京都美術館</p>
    <p>上野</p>
    <p>2026/3/1-5/31</p>
    <img src="//images.ctfassets.net/example/image.jpg">
</a>
<a href="/events/def456">
    <h3>サウンドインスタレーション</h3>
    <p>ICC</p>
    <p>2026/4/1-6/30</p>
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

        assert exhibitions[0].image_url == "https://images.ctfassets.net/example/image.jpg"

    @responses.activate
    def test_scrape_extracts_venue(self):
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].venue == "東京都美術館"
        assert exhibitions[1].venue == "ICC"

    @responses.activate
    def test_scrape_handles_protocol_relative_image(self):
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].image_url == "https://images.ctfassets.net/example/image.jpg"
        assert exhibitions[1].image_url is None

    @responses.activate
    def test_scrape_extracts_image_from_next_data(self):
        """Test image extraction from __NEXT_DATA__ when no img tag exists."""
        html_with_next_data = """
        <html>
        <body>
        <script id="__NEXT_DATA__" type="application/json">
        {"props":{"pageProps":{"fallback":{"events":{"data":[
            {"slug":"abc123","eventName":"Test",
             "imageposter":{"fields":{"file":{"url":"//images.ctfassets.net/poster.jpg"}}}}
        ]}}}}}
        </script>
        <a href="/events/-/Test/abc123/2026-03-01">
            <h3>テスト展</h3>
            <p>美術館</p>
            <p>2026/3/1-5/31</p>
        </a>
        </body>
        </html>
        """
        responses.add(
            responses.GET,
            "https://www.tokyoartbeat.com/events",
            body=html_with_next_data,
            status=200,
        )

        scraper = TokyoArtBeatScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 1
        assert exhibitions[0].image_url == "https://images.ctfassets.net/poster.jpg"

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
