import responses

from scripts.scrapers.mori_art_museum import MoriArtMuseumScraper

SAMPLE_HTML = """
<html>
<body>
<a href="roppongicrossing2025/index.html">
    <img src="roppongicrossing2025/image.jpg">
    <h3>六本木クロッシング2025展</h3>
    <span>2025.12.3（水）～ 2026.3.29（日）</span>
</a>
<a href="anothershow/index.html">
    <h3>現代アート展</h3>
    <span>2026.4.1（木）～ 2026.6.30（火）</span>
</a>
<a href="index.html">
    <span>All Exhibitions</span>
</a>
</body>
</html>
"""


class TestMoriArtMuseumScraper:
    @responses.activate
    def test_scrape_returns_exhibitions(self):
        responses.add(
            responses.GET,
            "https://www.mori.art.museum/jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MoriArtMuseumScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "六本木クロッシング2025展"
        assert exhibitions[0].source == "mori_art_museum"

    @responses.activate
    def test_scrape_sets_venue(self):
        responses.add(
            responses.GET,
            "https://www.mori.art.museum/jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MoriArtMuseumScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].venue == "森美術館"

    @responses.activate
    def test_scrape_extracts_dates(self):
        responses.add(
            responses.GET,
            "https://www.mori.art.museum/jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MoriArtMuseumScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.year == 2025
        assert exhibitions[0].start_date.month == 12
        assert exhibitions[0].end_date.year == 2026
        assert exhibitions[0].end_date.month == 3

    @responses.activate
    def test_scrape_builds_full_urls(self):
        responses.add(
            responses.GET,
            "https://www.mori.art.museum/jp/exhibitions/",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = MoriArtMuseumScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].source_url == "https://www.mori.art.museum/jp/exhibitions/roppongicrossing2025/index.html"
        assert exhibitions[0].image_url == "https://www.mori.art.museum/jp/exhibitions/roppongicrossing2025/image.jpg"

    def test_parse_dates(self):
        scraper = MoriArtMuseumScraper()
        start, end = scraper._parse_dates(
            "2025.12.3（水）～ 2026.3.29（日）"
        )
        assert start.year == 2025
        assert start.month == 12
        assert start.day == 3
        assert end.year == 2026
        assert end.month == 3
        assert end.day == 29

    def test_parse_dates_with_tilde(self):
        scraper = MoriArtMuseumScraper()
        start, end = scraper._parse_dates(
            "2025.12.3〜2026.3.29"
        )
        assert start is not None
        assert end is not None
