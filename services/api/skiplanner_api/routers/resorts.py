from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..db_models import Lift, ResortRow, Trail
from ..models import GeoJSONFeatureCollection, SkiArea
from ..seed import load_map_geojson, load_resorts

router = APIRouter(prefix="/resorts", tags=["resorts"])

DbDep = Annotated[AsyncSession | None, Depends(get_db)]


def _row_to_schema(row: ResortRow) -> SkiArea:
    return SkiArea(
        id=row.id,
        name=row.name,
        country=row.country,
        centroid_lat=row.centroid_lat,
        centroid_lon=row.centroid_lon,
        source=row.source,
        source_version=row.source_version,
        nearest_airport_iata=row.nearest_airport_iata,
        difficulty_hint=row.difficulty_hint,  # type: ignore[arg-type]
        updated_at=row.updated_at,
    )


def _json_resorts() -> list[SkiArea]:
    return sorted(load_resorts(settings.seed_dir), key=lambda r: r.name)


def _json_resort(resort_id: str) -> SkiArea:
    for r in _json_resorts():
        if r.id == resort_id:
            return r
    raise HTTPException(status_code=404, detail="Resort not found")


@router.get("", response_model=list[SkiArea])
async def list_resorts(db: DbDep) -> list[SkiArea]:
    if db is None:
        return _json_resorts()
    result = await db.execute(select(ResortRow).order_by(ResortRow.name))
    return [_row_to_schema(r) for r in result.scalars()]


@router.get("/{resort_id}", response_model=SkiArea)
async def get_resort(resort_id: str, db: DbDep) -> SkiArea:
    if db is None:
        return _json_resort(resort_id)
    row = await db.get(ResortRow, resort_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Resort not found")
    return _row_to_schema(row)


@router.get("/{resort_id}/map", response_model=GeoJSONFeatureCollection)
async def get_resort_map(resort_id: str, db: DbDep) -> GeoJSONFeatureCollection:
    if db is None:
        _json_resort(resort_id)
    else:
        row = await db.get(ResortRow, resort_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Resort not found")
    data = load_map_geojson(settings.seed_dir, resort_id)
    features = data.get("features", [])
    meta = data.get("metadata") or {"resort_id": resort_id}
    return GeoJSONFeatureCollection(features=features, metadata=meta)


@router.get("/{resort_id}/trails")
async def get_resort_trails(resort_id: str, db: DbDep) -> dict:
    if db is None:
        _json_resort(resort_id)
        return {
            "resort_id": resort_id,
            "trails": [],
            "lifts": [],
            "total_trails": 0,
            "total_lifts": 0,
            "note": "Trails/lifts require Postgres when SKIMATE_DEV_JSON_API is unset.",
        }

    row = await db.get(ResortRow, resort_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Resort not found")

    trail_result = await db.execute(select(Trail).where(Trail.resort_id == resort_id))
    lift_result = await db.execute(select(Lift).where(Lift.resort_id == resort_id))
    trails = trail_result.scalars().all()
    lifts = lift_result.scalars().all()

    def trail_to_dict(t: Trail) -> dict:
        return {
            "id": t.id,
            "name": t.name,
            "piste_type": t.piste_type,
            "piste_difficulty": t.piste_difficulty,
            "grooming": t.grooming,
            "oneway": t.oneway,
        }

    def lift_to_dict(l: Lift) -> dict:
        return {
            "id": l.id,
            "name": l.name,
            "aerialway_type": l.aerialway_type,
            "capacity": l.capacity,
        }

    return {
        "resort_id": resort_id,
        "trails": [trail_to_dict(t) for t in trails],
        "lifts": [lift_to_dict(l) for l in lifts],
        "total_trails": len(trails),
        "total_lifts": len(lifts),
    }
