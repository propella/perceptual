import responses

from scripts.scrapers.bijutsu_techo import BijutsuTechoScraper

SAMPLE_HTML = """
<html>
<body>
<a href="/exhibitions/12345">
    <h3>メディアアート展</h3>
    <img src="https://imgix.net/image.jpg">
    <span>2026.03.01 - 05.31</span>
</a>
<a href="/exhibitions/67890">
    <h3>インスタレーション展</h3>
    <span>2026.04.01 - 06.30</span>
</a>
</body>
</html>
"""

SAMPLE_HTML_WITH_NUXT = """
<html>
<body>
<script>
window.__NUXT__ = {"data":[{"exhibitions":[{"id":123,"title":"テスト展","museumName":"テスト美術館","imageUrl":"https://example.com/img.jpg","periods":[{"startAt":1772470800,"endAt":1780329600}]}]}]}
</script>
</body>
</html>
"""


class TestBijutsuTechoScraper:
    @responses.activate
    def test_scrape_html_fallback(self):
        responses.add(
            responses.GET,
            "https://bijutsutecho.com/exhibitions",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = BijutsuTechoScraper()
        exhibitions = scraper.scrape()

        assert len(exhibitions) == 2
        assert exhibitions[0].title == "メディアアート展"
        assert exhibitions[0].source == "bijutsu_techo"

    @responses.activate
    def test_scrape_extracts_dates_from_html(self):
        responses.add(
            responses.GET,
            "https://bijutsutecho.com/exhibitions",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = BijutsuTechoScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].start_date.month == 3
        assert exhibitions[0].end_date.month == 5

    @responses.activate
    def test_scrape_extracts_image(self):
        responses.add(
            responses.GET,
            "https://bijutsutecho.com/exhibitions",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = BijutsuTechoScraper()
        exhibitions = scraper.scrape()

        assert "imgix.net" in exhibitions[0].image_url

    @responses.activate
    def test_scrape_builds_correct_url(self):
        responses.add(
            responses.GET,
            "https://bijutsutecho.com/exhibitions",
            body=SAMPLE_HTML,
            status=200,
        )

        scraper = BijutsuTechoScraper()
        exhibitions = scraper.scrape()

        assert exhibitions[0].source_url == "https://bijutsutecho.com/exhibitions/12345"
