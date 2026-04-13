"""Write parsed trails and lifts to PostgreSQL and update the seed GeoJSON file."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, mapping
from sqlalchemy.ext.asyncio import AsyncSession

from ..db_models import Lift, Trail

logger = logging.getLogger(__name__)


def _linestring(coords: list[tuple[float, float]]):
    return from_shape(LineString(coords), srid=4326)


async def write_to_db(
    session: AsyncSession,
    trails: list[dict],
    lifts: list[dict],
) -> tuple[int, int]:
    trail_count = 0
    lift_count = 0
    now = datetime.now(timezone.utc)

    for t in trails:
        coords = t["coords"]  # read without mutating — write_geojson needs it too
        db_fields = {k: v for k, v in t.items() if k != "coords"}
        existing = await session.get(Trail, db_fields["id"])
        if existing:
            for k, v in db_fields.items():
                setattr(existing, k, v)
            existing.geometry = _linestring(coords)
            existing.updated_at = now
        else:
            session.add(Trail(geometry=_linestring(coords), updated_at=now, **db_fields))
            trail_count += 1

    for l in lifts:
        coords = l["coords"]
        db_fields = {k: v for k, v in l.items() if k != "coords"}
        existing = await session.get(Lift, db_fields["id"])
        if existing:
            for k, v in db_fields.items():
                setattr(existing, k, v)
            existing.geometry = _linestring(coords)
            existing.updated_at = now
        else:
            session.add(Lift(geometry=_linestring(coords), updated_at=now, **db_fields))
            lift_count += 1

    await session.commit()
    logger.info("Wrote %d new trails, %d new lifts", trail_count, lift_count)
    return trail_count, lift_count


def write_geojson(
    seed_dir: Path,
    resort_id: str,
    trails: list[dict],
    lifts: list[dict],
) -> None:
    """Update the seed GeoJSON file with fresh OSM data."""
    features = []

    for t in trails:
        coords = t.get("coords", [])
        if len(coords) < 2:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "kind": "piste",
                "name": t.get("name"),
                "piste_type": t.get("piste_type"),
                "piste_difficulty": t.get("piste_difficulty"),
                "grooming": t.get("grooming"),
                "oneway": t.get("oneway"),
            },
        })

    for l in lifts:
        coords = l.get("coords", [])
        if len(coords) < 2:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "kind": "lift",
                "name": l.get("name"),
                "aerialway_type": l.get("aerialway_type"),
                "capacity": l.get("capacity"),
            },
        })

    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "resort_id": resort_id,
            "source": "openstreetmap",
            "feature_count": len(features),
        },
        "features": features,
    }

    out_path = seed_dir / "maps" / f"{resort_id}.geojson"
    out_path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Updated GeoJSON: %s (%d features)", out_path, len(features))
