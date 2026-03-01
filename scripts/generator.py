import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ics import Calendar, Event

from scripts.scrapers.base import Exhibition


def generate_id(exhibition: Exhibition) -> str:
    """Generate unique ID from title and venue."""
    key = f"{exhibition.title}-{exhibition.venue}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def exhibition_to_dict(exhibition: Exhibition) -> dict:
    """Convert Exhibition to dictionary for JSON."""
    return {
        "id": generate_id(exhibition),
        "title": exhibition.title,
        "description": exhibition.description,
        "venue": exhibition.venue,
        "address": exhibition.address,
        "startDate": exhibition.start_date.isoformat(),
        "endDate": exhibition.end_date.isoformat(),
        "imageUrl": exhibition.image_url,
        "sourceUrl": exhibition.source_url,
        "source": exhibition.source,
        "tags": exhibition.tags or [],
    }


def generate_json(exhibitions: list[Exhibition], output_path: Path) -> None:
    """Generate JSON file from exhibitions."""
    data = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "exhibitions": [exhibition_to_dict(e) for e in exhibitions],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def generate_ics(exhibitions: list[Exhibition], output_path: Path) -> None:
    """Generate ICS file from exhibitions."""
    calendar = Calendar()
    calendar.creator = "perceptual-exhibition-collector"

    for exhibition in exhibitions:
        event = Event()
        event.name = exhibition.title
        event.begin = exhibition.start_date
        event.end = exhibition.end_date
        event.location = exhibition.address or exhibition.venue
        event.url = exhibition.source_url
        event.description = (
            f"{exhibition.description or ''}\n\n会場: {exhibition.venue}"
        ).strip()
        event.make_all_day()
        calendar.events.add(event)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(calendar.serialize())
