"""
CLI: python -m skiplanner_api.ingest <resort_id>
     python -m skiplanner_api.ingest --all          (all resorts with bounds)
     python -m skiplanner_api.ingest --list         (list all available resort IDs)

Bounds are read automatically from data/seed/resorts.json.
"""
import asyncio
import json
import logging
import sys
import time

from ..config import settings
from ..database import AsyncSessionLocal, engine
from ..db_models import Base
from ..db_seed import seed as seed_resorts
from .overpass import fetch_overpass
from .parser import parse_overpass
from .writer import write_geojson, write_to_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_resort_bounds() -> dict[str, dict[str, float]]:
    """Load bounding boxes from resorts.json for all resorts that have bounds."""
    seed_path = settings.seed_dir / "resorts.json"
    resorts = json.loads(seed_path.read_text(encoding="utf-8"))
    result = {}
    for r in resorts:
        b = r.get("bounds")
        if b:
            result[r["id"]] = {
                "south": b["min_lat"],
                "north": b["max_lat"],
                "west":  b["min_lon"],
                "east":  b["max_lon"],
            }
    return result


async def run(resort_id: str, bounds: dict[str, float]) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_resorts()

    logger.info("Starting OSM ingest for %s", resort_id)
    raw = await fetch_overpass(bounds)
    trails, lifts = parse_overpass(raw, resort_id)
    logger.info("Parsed %d trails, %d lifts from OSM", len(trails), len(lifts))

    async with AsyncSessionLocal() as session:
        t_new, l_new = await write_to_db(session, trails, lifts)

    write_geojson(settings.seed_dir, resort_id, trails, lifts)
    logger.info("Done: %d trails (%d new), %d lifts (%d new) for %s",
                len(trails), t_new, len(lifts), l_new, resort_id)


def main() -> None:
    all_bounds = load_resort_bounds()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage:")
        print("  python -m skiplanner_api.ingest <resort_id>")
        print("  python -m skiplanner_api.ingest --all")
        print("  python -m skiplanner_api.ingest --list")
        sys.exit(0)

    if sys.argv[1] == "--list":
        print(f"{len(all_bounds)} resorts with bounds:")
        for rid in sorted(all_bounds):
            print(f"  {rid}")
        sys.exit(0)

    if sys.argv[1] == "--all":
        print(f"Running ingest for {len(all_bounds)} resorts...")
        for i, (resort_id, bounds) in enumerate(all_bounds.items(), 1):
            print(f"[{i}/{len(all_bounds)}] {resort_id}")
            try:
                asyncio.run(run(resort_id, bounds))
            except Exception as e:
                logger.error("Failed %s: %s", resort_id, e)
            time.sleep(2)  # Be polite to Overpass API
        return

    resort_id = sys.argv[1]
    if resort_id not in all_bounds:
        print(f"Resort '{resort_id}' not found or has no bounds.")
        print("Run --list to see available resorts.")
        sys.exit(1)

    asyncio.run(run(resort_id, all_bounds[resort_id]))


if __name__ == "__main__":
    main()
