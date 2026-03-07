import responses

from scripts.scrapers.nmao import NMAOScraper

SAMPLE_HTML = """
<html>
<body>
<div class="exhibition-card">
  <a href="https://www.nmao.go.jp/events/event/20260314_nakanishi/">
    <img src="https://www.nmao.go.jp/wp-content/uploads/2025/10/nakanishi-poster.jpg">
  </a>
  <h2>中西夏之 緩やかにみつめるためにいつまでも佇む、装置</h2>
  <p>2026年3月14日（土）– 2026年6月14日（日）</p>
</div>
<div class="exhibition-card">
  <a href="https://www.nmao.go.jp/events/event/collection20260314/">
    <img src="https://www.nmao.go.jp/wp-content/uploads/2025/12/collection-poster.jpg">
  </a>
  <h2>コレクション３</h2>
  <p>2026年3月14日（土）– 2026年6月14日（日）</p>
</div>
<a href="https://www.nmao.go.jp/about/">
  <p>無関係なリンク</p>
</a>
</body>
</html>
"""


class TestNMAOScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert len(exhibitions) == 2

    @responses.activate
    def test_scrape_extracts_title(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert "中西夏之" in exhibitions[0].title

    @responses.activate
    def test_scrape_sets_fixed_venue(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert all(e.venue == "国立国際美術館" for e in exhibitions)

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 6

    @responses.activate
    def test_scrape_extracts_image_url(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert "nakanishi-poster" in exhibitions[0].image_url

    @responses.activate
    def test_scrape_sets_source(self):
        responses.add(
            responses.GET,
            "https://www.nmao.go.jp/exhibition/current_exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = NMAOScraper()
        exhibitions = scraper.scrape()
        assert all(e.source == "nmao" for e in exhibitions)

    def test_parse_dates(self):
        scraper = NMAOScraper()
        start, end = scraper._parse_dates("2026年3月14日（土）– 2026年6月14日（日）")
        assert start.year == 2026
        assert start.month == 3
        assert start.day == 14
        assert end.month == 6
        assert end.day == 14
