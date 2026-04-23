"""FastAPI router for the POST /recommendations endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..db_models import ResortRow
from ..models import SkiArea
from ..seed import load_resorts
from ..recommendations import (
    RecommendationRequest,
    RecommendationResponse,
    rank_resorts,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

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


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(
    body: RecommendationRequest,
    db: DbDep,
) -> RecommendationResponse:
    """
    Return a ranked list of ski resorts based on user preferences.

    Rules applied (in order):
    1. **Difficulty filter** — resorts with a ``difficulty_hint`` incompatible
       with ``ski_level`` are excluded; compatible ones receive a score bonus.
    2. **Country boost** — resorts in ``preferred_countries`` receive an
       additional score bonus (but are *not* excluded when absent).
    3. **Airport tiebreaker** — resorts with a known nearest airport get a
       small bonus for stable ordering.

    An empty ``results`` list is returned (with a ``warning`` message) when
    no resorts survive the difficulty filter.
    """
    if db is None:
        resorts = sorted(load_resorts(settings.seed_dir), key=lambda r: r.name)
    else:
        result = await db.execute(select(ResortRow).order_by(ResortRow.name))
        resorts = [_row_to_schema(r) for r in result.scalars()]
    return rank_resorts(resorts, body)
