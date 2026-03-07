#!/usr/bin/env python3
"""Main script to scrape exhibitions and generate output files."""

import json
import logging
from datetime import date
from pathlib import Path

from scripts.filters import filter_exhibitions
from scripts.generator import generate_ics, generate_json
from scripts.scrapers import (
    ArtagendaScraper,
    ArtscapeScraper,
    BijutsuTechoScraper,
    DesignSightScraper,
    ICCScraper,
    Kanazawa21Scraper,
    MoriArtMuseumScraper,
    MOTScraper,
    NMAOScraper,
    TokyoArtBeatScraper,
)
from scripts.scrapers.base import Exhibition

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
    ArtscapeScraper,
    ArtagendaScraper,
    Kanazawa21Scraper,
    NMAOScraper,
]

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "data"


def load_existing_exhibitions(json_path: Path) -> list[Exhibition]:
    """Load exhibitions from existing JSON file. Returns empty list if file doesn't exist."""
    if not json_path.exists():
        return []
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    exhibitions = []
    for item in data.get("exhibitions", []):
        try:
            exhibitions.append(
                Exhibition(
                    title=item["title"],
                    venue=item["venue"],
                    start_date=date.fromisoformat(item["startDate"]),
                    end_date=date.fromisoformat(item["endDate"]),
                    source_url=item["sourceUrl"],
                    source=item["source"],
                    description=item.get("description"),
                    address=item.get("address"),
                    image_url=item.get("imageUrl"),
                    tags=item.get("tags") or None,
                )
            )
        except (KeyError, ValueError):
            continue
    return exhibitions


def merge_exhibitions(
    existing: list[Exhibition], new: list[Exhibition], today: date
) -> list[Exhibition]:
    """Merge existing and newly scraped exhibitions.

    - Existing active exhibitions (end_date >= today) are preserved.
    - New exhibitions overwrite existing ones with the same source_url.
    - Expired exhibitions (end_date < today) are dropped.
    """
    merged: dict[str, Exhibition] = {}
    for ex in existing:
        if ex.end_date >= today:
            merged[ex.source_url] = ex
    for ex in new:
        merged[ex.source_url] = ex
    return list(merged.values())


def deduplicate_exhibitions(exhibitions: list) -> list:
    """Remove duplicate exhibitions based on source_url."""
    seen_urls: set[str] = set()
    unique = []
    for exhibition in exhibitions:
        if exhibition.source_url not in seen_urls:
            seen_urls.add(exhibition.source_url)
            unique.append(exhibition)
    return unique


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

    # Remove duplicates across all sources
    all_exhibitions = deduplicate_exhibitions(all_exhibitions)
    logger.info(f"Total exhibitions (after dedup): {len(all_exhibitions)}")

    # Merge with existing exhibitions to preserve ongoing events
    json_path = OUTPUT_DIR / "exhibitions.json"
    existing = load_existing_exhibitions(json_path)
    logger.info(f"Loaded {len(existing)} existing exhibitions")
    all_exhibitions = merge_exhibitions(existing, all_exhibitions, date.today())
    logger.info(f"After merge: {len(all_exhibitions)} exhibitions")

    # Filter by keywords
    filtered = filter_exhibitions(all_exhibitions)
    logger.info(f"After filtering: {len(filtered)} exhibitions")

    # Generate output files
    ics_path = OUTPUT_DIR / "exhibitions.ics"

    generate_json(filtered, json_path)
    logger.info(f"Generated {json_path}")

    generate_ics(filtered, ics_path)
    logger.info(f"Generated {ics_path}")


if __name__ == "__main__":
    main()
