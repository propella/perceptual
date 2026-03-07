import responses

from scripts.scrapers.kanazawa21 import Kanazawa21Scraper

SAMPLE_HTML = """
<html>
<body>
<a href="../data_list.php?g=17&d=1234">
  <img src="/file.php?g=45&d=1234&n=main_image">
  <h4>SIDE CORE: Living road, Living space</h4>
  <p>2025年10月18日(土) - 2026年3月15日(日)</p>
</a>
<a href="../data_list.php?g=17&d=1235">
  <img src="/file.php?g=45&d=1235&n=main_image">
  <h4>コレクション展3：デジャ・ヴュ</h4>
  <p>2026年1月31日(土) - 2026年5月10日(日)</p>
</a>
<a href="https://www.kanazawa21.jp/about/">
  <p>無関係なリンク</p>
</a>
</body>
</html>
"""


class TestKanazawa21Scraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.kanazawa21.jp/exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = Kanazawa21Scraper()
        exhibitions = scraper.scrape()
        assert len(exhibitions) == 2

    @responses.activate
    def test_scrape_extracts_title(self):
        responses.add(
            responses.GET,
            "https://www.kanazawa21.jp/exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = Kanazawa21Scraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].title == "SIDE CORE: Living road, Living space"

    @responses.activate
    def test_scrape_sets_fixed_venue(self):
        responses.add(
            responses.GET,
            "https://www.kanazawa21.jp/exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = Kanazawa21Scraper()
        exhibitions = scraper.scrape()
        assert all(e.venue == "金沢21世紀美術館" for e in exhibitions)

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.kanazawa21.jp/exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = Kanazawa21Scraper()
        exhibitions = scraper.scrape()
        assert exhibitions[0].start_date.year == 2025
        assert exhibitions[0].start_date.month == 10
        assert exhibitions[0].end_date.year == 2026
        assert exhibitions[0].end_date.month == 3

    @responses.activate
    def test_scrape_sets_source(self):
        responses.add(
            responses.GET,
            "https://www.kanazawa21.jp/exhibition/",
            body=SAMPLE_HTML,
            status=200,
        )
        scraper = Kanazawa21Scraper()
        exhibitions = scraper.scrape()
        assert all(e.source == "kanazawa21" for e in exhibitions)

    def test_parse_dates(self):
        scraper = Kanazawa21Scraper()
        start, end = scraper._parse_dates("2025年10月18日(土) - 2026年3月15日(日)")
        assert start.year == 2025
        assert start.month == 10
        assert start.day == 18
        assert end.year == 2026
        assert end.month == 3
        assert end.day == 15
