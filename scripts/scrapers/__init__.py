from scripts.scrapers.artagenda import ArtagendaScraper
from scripts.scrapers.artscape import ArtscapeScraper
from scripts.scrapers.base import BaseScraper, Exhibition
from scripts.scrapers.bijutsu_techo import BijutsuTechoScraper
from scripts.scrapers.design_sight import DesignSightScraper
from scripts.scrapers.icc import ICCScraper
from scripts.scrapers.kanazawa21 import Kanazawa21Scraper
from scripts.scrapers.mori_art_museum import MoriArtMuseumScraper
from scripts.scrapers.mot import MOTScraper
from scripts.scrapers.nmao import NMAOScraper
from scripts.scrapers.tokyo_art_beat import TokyoArtBeatScraper

__all__ = [
    "BaseScraper",
    "Exhibition",
    "TokyoArtBeatScraper",
    "BijutsuTechoScraper",
    "ICCScraper",
    "DesignSightScraper",
    "MoriArtMuseumScraper",
    "MOTScraper",
    "ArtscapeScraper",
    "ArtagendaScraper",
    "Kanazawa21Scraper",
    "NMAOScraper",
]
