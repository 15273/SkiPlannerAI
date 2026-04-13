"""Seed the database from data/seed/resorts.json."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select

from .config import settings
from .database import AsyncSessionLocal, engine
from .db_models import ResortRow
from .database import Base


async def seed() -> None:
    # Create tables if they don't exist (idempotent)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    path = settings.seed_dir / "resorts.json"
    rows = json.loads(path.read_text(encoding="utf-8"))

    async with AsyncSessionLocal() as session:
        for row in rows:
            existing = await session.get(ResortRow, row["id"])
            if existing:
                continue  # skip already-seeded resorts

            updated_at = None
            if row.get("updated_at"):
                updated_at = datetime.fromisoformat(row["updated_at"])
            else:
                updated_at = datetime.now(timezone.utc)

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
                updated_at=updated_at,
            )
            session.add(resort)

        await session.commit()
        print(f"Seeded {len(rows)} resorts.")


if __name__ == "__main__":
    asyncio.run(seed())
