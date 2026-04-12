from fastapi import APIRouter, HTTPException

from ..config import settings
from ..models import GeoJSONFeatureCollection, SkiArea
from ..seed import load_map_geojson, load_resorts

router = APIRouter(prefix="/resorts", tags=["resorts"])

_cache: list[SkiArea] | None = None


def _resorts() -> list[SkiArea]:
    global _cache
    if _cache is None:
        _cache = load_resorts(settings.seed_dir)
    return _cache


@router.get("", response_model=list[SkiArea])
def list_resorts() -> list[SkiArea]:
    return _resorts()


@router.get("/{resort_id}", response_model=SkiArea)
def get_resort(resort_id: str) -> SkiArea:
    for r in _resorts():
        if r.id == resort_id:
            return r
    raise HTTPException(status_code=404, detail="Resort not found")


@router.get("/{resort_id}/map", response_model=GeoJSONFeatureCollection)
def get_resort_map(resort_id: str) -> GeoJSONFeatureCollection:
    found = any(r.id == resort_id for r in _resorts())
    if not found:
        raise HTTPException(status_code=404, detail="Resort not found")
    data = load_map_geojson(settings.seed_dir, resort_id)
    features = data.get("features", [])
    meta = data.get("metadata") or {"resort_id": resort_id}
    return GeoJSONFeatureCollection(features=features, metadata=meta)
