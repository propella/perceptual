import responses

from scripts.scrapers.maker_faire import MakerFaireScraper

SAMPLE_HTML_WITH_EVENT_LINK = """
<html>
<body>
<a href="/event/mft2026/">Maker Faire Tokyo 2026</a>
</body>
</html>
"""

SAMPLE_EVENT_PAGE = """
<html>
<body>
<h1>Maker Faire Tokyo 2026</h1>
<article class="abstract">
  <h3>日時</h3>
  2026/4/25（土）12:00～18:00<br>
  2026/4/26（日）10:00〜17:00
  <h3>会場</h3>
  東京ビッグサイト西4ホール
</article>
</body>
</html>
"""

SAMPLE_HTML_DIRECT = """
<html>
<body>
<h1>Maker Faire Tokyo 2026</h1>
<article class="abstract">
  <h3>日時</h3>
  2026/4/25（土）12:00～18:00<br>
  2026/4/26（日）10:00〜17:00
  <h3>会場</h3>
  東京ビッグサイト西4ホール
</article>
</body>
</html>
"""


class TestMakerFaireScraper:
    @responses.activate
    def test_scrape_via_event_link(self):
        responses.add(
            responses.GET,
            "https://makezine.jp/event/",
            body=SAMPLE_HTML_WITH_EVENT_LINK,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://makezine.jp/event/mft2026/",
            body=SAMPLE_EVENT_PAGE,
            status=200,
        )

        scraper = MakerFaireScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 1
        assert "Maker Faire Tokyo 2026" in exhibitions[0].title
        assert exhibitions[0].source == "maker_faire"

    @responses.activate
    def test_scrape_fallback_direct(self):
        responses.add(
            responses.GET,
            "https://makezine.jp/event/",
            body=SAMPLE_HTML_DIRECT,
            status=200,
        )

        scraper = MakerFaireScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 1
        assert "Maker Faire" in exhibitions[0].title

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://makezine.jp/event/",
            body=SAMPLE_HTML_DIRECT,
            status=200,
        )

        scraper = MakerFaireScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2026
        assert exhibitions[0].start_date.month == 4
        assert exhibitions[0].start_date.day == 25
        assert exhibitions[0].end_date.day == 26

    @responses.activate
    def test_scrape_sets_tags(self):
        responses.add(
            responses.GET,
            "https://makezine.jp/event/",
            body=SAMPLE_HTML_DIRECT,
            status=200,
        )

        scraper = MakerFaireScraper()
        exhibitions = scraper.scrape()

        assert "メイカー" in exhibitions[0].tags

    def test_parse_slash_dates(self):
        scraper = MakerFaireScraper()
        start, end = scraper._parse_slash_dates("2026/4/25（土）\n2026/4/26（日）")

        assert start.year == 2026
        assert start.month == 4
        assert start.day == 25
        assert end.day == 26
