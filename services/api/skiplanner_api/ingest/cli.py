"""
CLI: python -m skiplanner_api.ingest <resort_id>

Example:
    python -m skiplanner_api.ingest chamonix
    python -m skiplanner_api.ingest zermatt
    python -m skiplanner_api.ingest verbier
"""
import asyncio
import logging
import sys

from ..config import settings
from ..database import AsyncSessionLocal, engine
from ..db_models import Base
from ..db_seed import seed as seed_resorts
from .overpass import fetch_overpass
from .parser import parse_overpass
from .writer import write_geojson, write_to_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# Resort bounding boxes (south, west, north, east) — expand as needed
RESORT_BOUNDS: dict[str, dict[str, float]] = {
    "chamonix": {"south": 45.86, "west": 6.82, "north": 46.02, "east": 7.00},
    "zermatt":  {"south": 45.93, "west": 7.68, "north": 46.07, "east": 7.88},
    "verbier":  {"south": 45.98, "west": 7.15, "north": 46.12, "east": 7.42},
}


async def run(resort_id: str) -> None:
    if resort_id not in RESORT_BOUNDS:
        logger.error("Unknown resort '%s'. Known resorts: %s", resort_id, list(RESORT_BOUNDS))
        sys.exit(1)

    # Ensure DB tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure resort row exists
    await seed_resorts()

    bounds = RESORT_BOUNDS[resort_id]
    logger.info("Starting OSM ingest for %s", resort_id)

    raw = await fetch_overpass(bounds)
    trails, lifts = parse_overpass(raw, resort_id)
    logger.info("Parsed %d trails, %d lifts from OSM", len(trails), len(lifts))

    async with AsyncSessionLocal() as session:
        t_new, l_new = await write_to_db(session, trails, lifts)

    write_geojson(settings.seed_dir, resort_id, trails, lifts)

    logger.info(
        "Done: %d trails (%d new), %d lifts (%d new) for %s",
        len(trails), t_new, len(lifts), l_new, resort_id,
    )


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m skiplanner_api.ingest <resort_id>")
        print(f"Known resorts: {list(RESORT_BOUNDS)}")
        sys.exit(1)
    resort_id = sys.argv[1]
    asyncio.run(run(resort_id))


if __name__ == "__main__":
    main()
