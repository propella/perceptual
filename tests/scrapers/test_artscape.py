import responses

from scripts.scrapers.artscape import ArtscapeScraper

SAMPLE_HTML = """
<html>
<body>
<a href="https://artscape.jp/exhibitions/63464/">
  <img src="/wp-content/uploads/2026/01/exhibition1.jpg" alt="展覧会1">
  <span>開催中</span>
  <h3>サウンドアート展2026</h3>
  <p>東京都現代美術館</p>
  <p>東京</p>
  <p>会期：2026年03月01日～2026年05月31日</p>
</a>
<a href="https://artscape.jp/exhibitions/63466/">
  <img src="/wp-content/uploads/2026/02/exhibition2.jpg" alt="展覧会2">
  <span>開催前</span>
  <h3>キネティックアートの世界</h3>
  <p>国立新美術館</p>
  <p>東京</p>
  <p>会期：2026年06月01日～2026年08月31日</p>
</a>
<a href="https://artscape.jp/museums/123/">
  <h3>無関係なリンク</h3>
</a>
</body>
</html>
"""


class TestArtscapeScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert len(exhibitions) == 2

    @responses.activate
    def test_scrape_extracts_title(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].title == "サウンドアート展2026"

    @responses.activate
    def test_scrape_extracts_venue(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].venue == "東京都現代美術館"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 5

    @responses.activate
    def test_scrape_extracts_image_url(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].image_url == "https://artscape.jp/wp-content/uploads/2026/01/exhibition1.jpg"

    @responses.activate
    def test_scrape_sets_source(self):
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert all(e.source == "artscape" for e in exhibitions)

    @responses.activate
    def test_scrape_deduplicates(self):
        html = SAMPLE_HTML.replace(
            'href="https://artscape.jp/exhibitions/63466/"',
            'href="https://artscape.jp/exhibitions/63464/"',
        )
        responses.add(
            responses.GET,
            "https://artscape.jp/exhibitions/",
            body=html,
            status=200,
        )
        scraper = ArtscapeScraper()
        exhibitions = scraper.scrape()
        assert len(exhibitions) == 1

    def test_parse_dates(self):
        scraper = ArtscapeScraper()
        start, end = scraper._parse_dates("会期：2026年03月01日～2026年05月31日")
        assert start.year == 2026
        assert start.month == 3
        assert start.day == 1
        assert end.month == 5
        assert end.day == 31
