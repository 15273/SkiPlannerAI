import json
from datetime import datetime, timezone
from pathlib import Path

from .models import SkiArea


def load_resorts(seed_dir: Path) -> list[SkiArea]:
    path = seed_dir / "resorts.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: list[SkiArea] = []
    for row in raw:
        if row.get("updated_at"):
            row["updated_at"] = datetime.fromisoformat(row["updated_at"])
        else:
            row["updated_at"] = datetime.now(timezone.utc)
        out.append(SkiArea(**row))
    return out


def load_map_geojson(seed_dir: Path, resort_id: str) -> dict:
    path = seed_dir / "maps" / f"{resort_id}.geojson"
    if not path.is_file():
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {
                "resort_id": resort_id,
                "note": "No map file; add data/seed/maps/{id}.geojson",
            },
        }
    return json.loads(path.read_text(encoding="utf-8"))
