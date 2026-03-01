#!/usr/bin/env python3
"""Main script to scrape exhibitions and generate output files."""

import logging
from pathlib import Path

from scripts.filters import filter_exhibitions
from scripts.generator import generate_ics, generate_json
from scripts.scrapers import (
    BijutsuTechoScraper,
    DesignSightScraper,
    ICCScraper,
    MoriArtMuseumScraper,
    MOTScraper,
    TokyoArtBeatScraper,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SCRAPERS = [
    TokyoArtBeatScraper,
    BijutsuTechoScraper,
    ICCScraper,
    DesignSightScraper,
    MoriArtMuseumScraper,
    MOTScraper,
]

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "data"


def main():
    """Run all scrapers and generate output files."""
    all_exhibitions = []

    for scraper_class in SCRAPERS:
        scraper = scraper_class()
        logger.info(f"Scraping {scraper.source_name}...")
        try:
            exhibitions = scraper.scrape()
            logger.info(f"  Found {len(exhibitions)} exhibitions")
            all_exhibitions.extend(exhibitions)
        except Exception as e:
            logger.error(f"  Error: {e}")

    logger.info(f"Total exhibitions: {len(all_exhibitions)}")

    # Filter by keywords
    filtered = filter_exhibitions(all_exhibitions)
    logger.info(f"After filtering: {len(filtered)} exhibitions")

    # Generate output files
    json_path = OUTPUT_DIR / "exhibitions.json"
    ics_path = OUTPUT_DIR / "exhibitions.ics"

    generate_json(filtered, json_path)
    logger.info(f"Generated {json_path}")

    generate_ics(filtered, ics_path)
    logger.info(f"Generated {ics_path}")


if __name__ == "__main__":
    main()
