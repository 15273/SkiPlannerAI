"""Seed the database from data/seed/resorts.json."""
import asyncio
import json
from datetime import datetime, timezone

from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from .config import settings
from .database import AsyncSessionLocal, Base, engine
from .db_models import ResortRow

PRICE_FIELDS = [
    "price_tier", "price_season",
    "adult_day_pass_peak_eur", "child_day_pass_peak_eur",
    "adult_6day_pass_eur", "child_6day_pass_eur",
    "ski_rental_day_eur", "snowboard_rental_day_eur", "helmet_rental_day_eur",
    "opening_hours", "peak_months", "quiet_months",
    "ticket_url", "website_url",
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    path = settings.seed_dir / "resorts.json"
    rows = json.loads(path.read_text(encoding="utf-8"))

    inserted = updated = 0
    async with AsyncSessionLocal() as session:
        for row in rows:
            existing = await session.get(ResortRow, row["id"])

            updated_at = (
                datetime.fromisoformat(row["updated_at"])
                if row.get("updated_at")
                else datetime.now(timezone.utc)
            )

            if existing:
                # Always refresh price/link fields when the seed has them
                changed = False
                for field in PRICE_FIELDS:
                    val = row.get(field)
                    if val is not None and getattr(existing, field) != val:
                        setattr(existing, field, val)
                        changed = True
                if changed:
                    existing.updated_at = updated_at
                    updated += 1
            else:
                resort = ResortRow(
                    id=row["id"],
                    name=row["name"],
                    country=row["country"],
                    centroid_lat=row["centroid_lat"],
                    centroid_lon=row["centroid_lon"],
                    centroid_geom=from_shape(
                        Point(row["centroid_lon"], row["centroid_lat"]), srid=4326
                    ),
                    source=row.get("source", "seed"),
                    source_version=row.get("source_version"),
                    nearest_airport_iata=row.get("nearest_airport_iata"),
                    difficulty_hint=row.get("difficulty_hint"),
                    venue_type=row.get("venue_type"),
                    updated_at=updated_at,
                    **{f: row.get(f) for f in PRICE_FIELDS},
                )
                session.add(resort)
                inserted += 1

        await session.commit()
        print(f"Seed complete: {inserted} inserted, {updated} updated.")


if __name__ == "__main__":
    asyncio.run(seed())


if __name__ == "__main__":
    asyncio.run(seed())
