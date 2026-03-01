import responses

from scripts.scrapers.icc import ICCScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/ja/exhibitions/2025/test-exhibition">
    <span>展示</span>
    <h3>メディアアートの未来</h3>
    <span>2025年12月13日（土）—2026年3月8日（日）</span>
    <img src="/images/exhibition.jpg">
</a>
<a href="/ja/exhibitions/2026/another-show">
    <h3>インタラクティブ展</h3>
    <span>2026年4月1日（水）—2026年6月30日（火）</span>
</a>
</body>
</html>
"""

DETAIL_HTML = """
<html><body>
<img src="/uploads/assets/007/detail.7768.small.jpg">
</body></html>
"""


class TestICCScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2026/another-show",
            body=DETAIL_HTML,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "メディアアートの未来"
        assert exhibitions[0].source == "icc"

    @responses.activate
    def test_scrape_sets_venue(self):
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2026/another-show",
            body=DETAIL_HTML,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert "ICC" in exhibitions[0].venue

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2026/another-show",
            body=DETAIL_HTML,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2025
        assert exhibitions[0].start_date.month == 12
        assert exhibitions[0].end_date.year == 2026
        assert exhibitions[0].end_date.month == 3

    @responses.activate
    def test_scrape_builds_full_image_url(self):
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2026/another-show",
            body=DETAIL_HTML,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].image_url == "https://www.ntticc.or.jp/images/exhibition.jpg"

    @responses.activate
    def test_scrape_adds_media_art_tag(self):
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2026/another-show",
            body=DETAIL_HTML,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert "メディアアート" in exhibitions[0].tags

    @responses.activate
    def test_scrape_fetches_detail_image(self):
        """Test that detail page is fetched for exhibitions without images."""
        html_no_img = """
        <html><body>
        <a href="/ja/exhibitions/2025/test-show">
            <h3>展覧会X</h3>
            <span>2025年12月13日（土）—2026年3月8日（日）</span>
        </a>
        </body></html>
        """
        detail_html = """
        <html><body>
        <img src="/uploads/assets/007/abc123.7768.small.jpg">
        </body></html>
        """
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/",
            body=html_no_img,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.ntticc.or.jp/ja/exhibitions/2025/test-show",
            body=detail_html,
            status=200,
        )

        scraper = ICCScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 1
        assert exhibitions[0].image_url == "https://www.ntticc.or.jp/uploads/assets/007/abc123.7768.small.jpg"

    def test_parse_dates(self):
        scraper = ICCScraper()
        start, end = scraper._parse_dates(
            "2025年12月13日（土）—2026年3月8日（日）"
        )
        assert start.year == 2025
        assert start.month == 12
        assert start.day == 13
        assert end.year == 2026
        assert end.month == 3
        assert end.day == 8
