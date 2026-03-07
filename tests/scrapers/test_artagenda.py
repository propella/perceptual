import responses

from scripts.scrapers.artagenda import ArtagendaScraper

SAMPLE_HTML = """
<html>
<body>
<div class="exhibition-item">
  <a href="https://www.artagenda.jp/exhibition/detail/11076">
    <img src="https://www.artagenda.jp/img/event/11076/thumbnail.jpg">
    <h3>インスタレーション展2026</h3>
  </a>
  <p>[金沢21世紀美術館｜石川県]開催中</p>
  <p>会期：2026年3月7日(土)〜2026年5月24日(日)</p>
</div>
<div class="exhibition-item">
  <a href="https://www.artagenda.jp/exhibition/detail/11077">
    <img src="https://www.artagenda.jp/img/event/11077/thumbnail.jpg">
    <h3>メディアアート展</h3>
  </a>
  <p>[森美術館｜東京都]開催予定</p>
  <p>会期：2026年6月1日(月)〜2026年8月31日(月)</p>
</div>
<a href="https://www.artagenda.jp/about/">
  <p>無関係なリンク</p>
</a>
</body>
</html>
"""


class TestArtagendaScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert len(exhibitions) == 2

    @responses.activate
    def test_scrape_extracts_title(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].title == "インスタレーション展2026"

    @responses.activate
    def test_scrape_extracts_venue(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].venue == "金沢21世紀美術館"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 5

    @responses.activate
    def test_scrape_extracts_image_url(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert "11076" in exhibitions[0].image_url

    @responses.activate
    def test_scrape_sets_source(self):
        responses.add(
            responses.GET,
            "https://www.artagenda.jp/exhibition/index",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtagendaScraper()
        exhibitions = scraper.scrape()
        assert all(e.source == "artagenda" for e in exhibitions)

    def test_parse_dates(self):
        scraper = ArtagendaScraper()
        start, end = scraper._parse_dates("会期：2026年3月7日(土)〜2026年5月24日(日)")
        assert start.year == 2026
        assert start.month == 3
        assert start.day == 7
        assert end.month == 5
        assert end.day == 24
