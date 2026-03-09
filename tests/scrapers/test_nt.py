import responses

from scripts.scrapers.nt import NTScraper

SAMPLE_HTML = """
<html>
<body>
<h3 id="content_1_2">直近の開催<a class="anchor_super" href="./#o2346d18">&dagger;</a></h3>
<ul class="list1 list-indent1">
  <li>2026-03-07 <a href="./?NT%E6%9D%BE%E6%88%B82026" class="link_page_passage">NT松戸2026</a></li>
  <li>2026-06-27,28 <a href="./?NT%E9%87%91%E6%B2%A22026"
    class="link_page_passage">NT金沢2026</a></li>
</ul>
</body>
</html>
"""


class TestNTScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2

    @responses.activate
    def test_scrape_sets_source(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].source == "nt"

    @responses.activate
    def test_scrape_extracts_title(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].title == "NT松戸2026"

    @responses.activate
    def test_scrape_extracts_single_date(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].start_date.day == 7
        assert exhibitions[0].end_date.day == 7

    @responses.activate
    def test_scrape_extracts_date_range(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[1].start_date.day == 27
        assert exhibitions[1].end_date.day == 28

    @responses.activate
    def test_scrape_sets_tags(self):
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert "メイカー" in exhibitions[0].tags

    @responses.activate
    def test_scrape_fetches_detail_image(self):
        """詳細ページから plugin=ref 画像 URL を取得する。"""
        detail_html = """
        <html><body>
        <img src="?plugin=ref&page=NT松戸2026&src=banner.jpg">
        </body></html>
        """
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/",
            body=SAMPLE_HTML,
            status=200,
        )
        # Detail pages for both list items
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/?NT%E6%9D%BE%E6%88%B82026",
            body=detail_html,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://wiki.nicotech.jp/nico_tech/?NT%E9%87%91%E6%B2%A22026",
            body="<html><body></body></html>",
            status=200,
        )

        scraper = NTScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].image_url is not None
        assert "plugin=ref" in exhibitions[0].image_url
        assert exhibitions[1].image_url is None

    def test_parse_date_single(self):
        scraper = NTScraper()
        start, end = scraper._parse_date("2026-03-07")

        assert start.year == 2026
        assert start.month == 3
        assert start.day == 7
        assert start == end

    def test_parse_date_range(self):
        scraper = NTScraper()
        start, end = scraper._parse_date("2026-06-27,28")

        assert start.day == 27
        assert end.day == 28
        assert start.month == end.month
