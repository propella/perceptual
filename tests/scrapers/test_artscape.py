from unittest.mock import patch

from bs4 import BeautifulSoup

from scripts.scrapers.artscape import ArtscapeScraper

SAMPLE_HTML = """
<html>
<body>
<article class="item-article item-exhibitions">
  <figure class="item-img">
    <a href="https://artscape.jp/exhibitions/63464/">
      <img src="/wp-content/uploads/2026/01/exhibition1.jpg" alt="展覧会1">
    </a>
  </figure>
  <div class="item-txt">
    <ul class="item-lvs"><li><span>開催中</span></li></ul>
    <h3 class="article-title">
      <a href="https://artscape.jp/exhibitions/63464/"><span>サウンドアート展2026</span></a>
    </h3>
    <p>東京都現代美術館</p>
    <p>会期：2026年03月01日～2026年05月31日</p>
  </div>
</article>
<article class="item-article item-exhibitions">
  <figure class="item-img">
    <a href="https://artscape.jp/exhibitions/63466/">
      <img src="/wp-content/uploads/2026/02/exhibition2.jpg" alt="展覧会2">
    </a>
  </figure>
  <div class="item-txt">
    <ul class="item-lvs"><li><span>開催前</span></li></ul>
    <h3 class="article-title">
      <a href="https://artscape.jp/exhibitions/63466/"><span>キネティックアートの世界</span></a>
    </h3>
    <p>国立新美術館</p>
    <p>会期：2026年06月01日～2026年08月31日</p>
  </div>
</article>
<a href="https://artscape.jp/museums/123/">無関係なリンク</a>
</body>
</html>
"""


def _mock_fetch_js(self, url):
    return BeautifulSoup(SAMPLE_HTML, "lxml")


class TestArtscapeScraper:
    def test_scrape_returns_exhibitions(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert len(exhibitions) == 2

    def test_scrape_extracts_title(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].title == "サウンドアート展2026"

    def test_scrape_extracts_venue(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].venue == "東京都現代美術館"

    def test_scrape_extracts_dates(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 5

    def test_scrape_extracts_image_url(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].image_url == "https://artscape.jp/wp-content/uploads/2026/01/exhibition1.jpg"

    def test_scrape_sets_source(self):
        with patch.object(ArtscapeScraper, "fetch_js", _mock_fetch_js):
            scraper = ArtscapeScraper()
            exhibitions = scraper.scrape()
        assert all(e.source == "artscape" for e in exhibitions)

    def test_scrape_deduplicates(self):
        html = SAMPLE_HTML.replace(
            'href="https://artscape.jp/exhibitions/63466/"',
            'href="https://artscape.jp/exhibitions/63464/"',
        )

        def _mock_dedup(self, url):
            return BeautifulSoup(html, "lxml")

        with patch.object(ArtscapeScraper, "fetch_js", _mock_dedup):
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
