from datetime import date
from unittest.mock import patch

from bs4 import BeautifulSoup

from scripts.scrapers.hakubutsu_fes import HakubutsuFesScraper

SAMPLE_HTML = """
<html>
<head>
  <meta property="og:image" content="https://www.hakubutufes.info/og/hakubutsu.jpg">
</head>
<body>
<table>
  <tr><td>博物ふぇすてぃばる！12</td></tr>
  <tr><td>2026年8月1日〜2026年8月2日</td></tr>
  <tr><td>東京ビッグサイト 東4・5・6ホール</td></tr>
  <tr><td>東京都江東区有明3丁目11-1</td></tr>
</table>
</body>
</html>
"""


def _mock_browser(self, url):
    return BeautifulSoup(SAMPLE_HTML, "lxml")


class TestHakubutsuFesScraper:
    def test_scrape_returns_exhibition(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert len(exhibitions) == 1

    def test_scrape_extracts_title(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert "博物ふぇすてぃばる" in exhibitions[0].title

    def test_scrape_extracts_dates(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 8
        assert exhibitions[0].end_date.day == 2

    def test_scrape_extracts_venue(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert "ビッグサイト" in exhibitions[0].venue

    def test_scrape_extracts_og_image(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].image_url == "https://www.hakubutufes.info/og/hakubutsu.jpg"

    def test_scrape_sets_source(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].source == "hakubutsu_fes"

    def test_scrape_sets_tags(self):
        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_browser):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert "博物" in exhibitions[0].tags

    def test_scrape_fallback_image_from_img_tag(self):
        """og:image がない場合はドメイン一致の img タグを使う。"""
        html_no_og = """
        <html><body>
        <table>
          <tr><td>博物ふぇすてぃばる！12</td></tr>
          <tr><td>2026年8月1日〜2026年8月2日</td></tr>
        </table>
        <img src="/images/banner.jpg">
        </body></html>
        """

        def _mock_no_og(self, url):
            return BeautifulSoup(html_no_og, "lxml")

        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock_no_og):
            scraper = HakubutsuFesScraper()
            exhibitions = scraper.scrape()
        assert exhibitions[0].image_url == "https://www.hakubutufes.info/images/banner.jpg"


MULTI_EVENT_HTML = """
<html><body>
<h2>博物ふぇすてぃばる！12</h2>
<p>いつ、どこで開催するの？</p>
<p>2026年 12月5日(土) 6日(日)東京、浅草の東京都立産業貿易センター台東館7階にて開催されます。</p>
<p>いつ、どこで開催するの？</p>
<p>2026年 7月19日(日) 20日(月・祝)東京ビッグサイト南1ホールで開催されます。</p>
</body></html>
"""


class TestHakubutsuFesMultiEvent:
    """ページに今回と前回の開催情報が並んでいる場合。"""

    def _scrape(self):
        def _mock(self, url):
            return BeautifulSoup(MULTI_EVENT_HTML, "lxml")

        with patch.object(HakubutsuFesScraper, "_fetch_with_browser", _mock):
            return HakubutsuFesScraper().scrape()

    def test_uses_first_event_dates(self):
        ex = self._scrape()[0]
        assert ex.start_date == date(2026, 12, 5)
        assert ex.end_date == date(2026, 12, 6)

    def test_uses_first_event_venue(self):
        ex = self._scrape()[0]
        assert ex.venue == "東京都立産業貿易センター台東館7階"


class TestParseDates:
    def test_range_with_tilde(self):
        start, end, _ = HakubutsuFesScraper()._parse_dates("2026年8月1日〜2026年8月2日")
        assert (start, end) == (date(2026, 8, 1), date(2026, 8, 2))

    def test_range_across_new_year(self):
        start, end, _ = HakubutsuFesScraper()._parse_dates("2026年12月30日(水)〜1月3日(日)")
        assert (start, end) == (date(2026, 12, 30), date(2027, 1, 3))

    def test_single_day(self):
        start, end, _ = HakubutsuFesScraper()._parse_dates("2026年8月1日(土)開催")
        assert start == end == date(2026, 8, 1)
